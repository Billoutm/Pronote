#!/usr/bin/env python3
"""Moteur de synchronisation PRONOTE -> Notion avec enrichissement IA (Mistral)."""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from models import PronoteDevoir, NotionTask, SyncState
from Selenium_version import SeleniumPronoteClient
from my_notion_client import NotionClient
from ai_client import MistralAIClient
from ai_enrich import enrich_devoir
from config import Config
import time

logger = logging.getLogger(__name__)

class SyncEngine:
    """Moteur de synchronisation entre PRONOTE et Notion."""

    def __init__(self, config: Config):
        self.config = config
        self.pronote_client = SeleniumPronoteClient(
            portal_url=config.PRONOTE_PORTAL_URL,
            username=config.PRONOTE_EDUCONNECT_USERNAME,
            password=config.PRONOTE_EDUCONNECT_PASSWORD,
            profile=config.PRONOTE_STUDENT_PROFILE,
            etablissement=config.PRONOTE_ETABLISSEMENT,
            headless=config.HEADLESS
        )
        self.notion_client = NotionClient(config)
        self.ai_client = MistralAIClient(config)
        self._init_db()

        # Options valides de type dans Notion Tâches:
        # Apprentissage, Code, Création, Design, Developpement, Entraînement, Marketing, Match, Montage, Prospection, Recherche, Tournage
        self.matiere_to_type = {
            "Mathematiques": "Entraînement",
            "Maths": "Entraînement",
            "Physique-Chimie": "Apprentissage",
            "Physique": "Apprentissage",
            "Chimie": "Apprentissage",
            "SVT": "Apprentissage",
            "Francais": "Recherche",
            "Histoire-Geographie": "Recherche",
            "Histoire": "Recherche",
            "Geographie": "Recherche",
            "Informatique": "Code",
            "NSI": "Code",
            "EPS": "Entraînement",
            "Arts Plastiques": "Création",
            "Arts": "Création",
            "Musique": "Création",
            "Technologie": "Design",
            "Anglais": "Apprentissage",
            "Espagnol": "Apprentissage",
            "Allemand": "Apprentissage",
        }

        self.difficulte_to_priority = {
            1: "Faible",
            2: "Moyenne",
            3: "Haute"
        }

    def _init_db(self):
        """Initialise la base SQLite pour le suivi de synchronisation."""
        self.conn = sqlite3.connect("pronote_sync.db")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                pronote_id TEXT PRIMARY KEY,
                notion_page_id TEXT,
                title TEXT,
                due_date TEXT,
                last_updated DATETIME,
                status TEXT
            )
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_state_pronote_id
            ON sync_state(pronote_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_state_notion_page_id
            ON sync_state(notion_page_id)
        """)
        self.conn.commit()

    def _generate_pronote_id(self, devoir: PronoteDevoir) -> str:
        """Genere une cle unique pour un devoir si ID PRONOTE non disponible."""
        matiere = devoir.matiere or "unknown"
        date_str = devoir.date_echeance.strftime('%Y-%m-%d')
        return f"{devoir.titre}|{date_str}|{matiere}"

    def _map_devoir_to_task(self, devoir: PronoteDevoir) -> NotionTask:
        """Convertit un PronoteDevoir en NotionTask avec enrichissement IA."""
        matiere = devoir.matiere or ""
        
        # Enrichissement IA (F1)
        enriched = enrich_devoir(self.ai_client, devoir)
        
        task_type = enriched.get("type_notion") or self.matiere_to_type.get(matiere)
        difficulte = enriched.get("difficulte", devoir.difficulte or 2)
        priority = self.difficulte_to_priority.get(difficulte, "Moyenne")
        status = "Terminé" if devoir.est_fait else "Pas commencé"
        titre_court = enriched.get("titre_court") or devoir.titre

        note_parts = []
        if enriched.get("temps_estime_min"):
            note_parts.append(f"Temps estimé : ~{enriched['temps_estime_min']} min")
        if enriched.get("categorie"):
            note_parts.append(f"Catégorie : {enriched['categorie']}")
        if devoir.date_donne:
            note_parts.append(f"Date de don : {devoir.date_donne}")
        if devoir.rendu_en_ligne or enriched.get("a_rendre_en_ligne"):
            note_parts.append("#rendu_en_ligne:oui")
        if devoir.details:
            note_parts.append(devoir.details)

        pronote_id = devoir.id or self._generate_pronote_id(devoir)
        note_parts.append(f"#pronote-id:{pronote_id}")

        due_date_str = devoir.date_echeance.strftime("%d/%m/%Y")
        title = f"[{devoir.matiere}] {titre_court}" if devoir.matiere else titre_court

        return NotionTask(
            title=title,
            due_date=due_date_str,
            type=task_type,
            priority=priority,
            status=status,
            note="\n".join(note_parts),
            project_id=self.config.NOTION_LYCEE_PROJECT_PAGE_ID,
            parent_id=None
        )

    def _get_sync_state(self, pronote_id: str) -> Optional[SyncState]:
        """Recupere l etat de synchronisation pour un devoir."""
        self.cursor.execute(
            "SELECT * FROM sync_state WHERE pronote_id = ?",
            (pronote_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return SyncState(
                pronote_id=row[0],
                notion_page_id=row[1],
                title=row[2],
                due_date=row[3],
                last_updated=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S") if row[4] else datetime.now(),
                status=row[5]
            )
        return None

    def _update_sync_state(self, state: SyncState):
        """Met a jour l etat de synchronisation."""
        self.cursor.execute("""
            INSERT OR REPLACE INTO sync_state
            (pronote_id, notion_page_id, title, due_date, last_updated, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            state.pronote_id,
            state.notion_page_id,
            state.title,
            state.due_date,
            state.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
            state.status
        ))
        self.conn.commit()

    def _create_or_update_task(self, devoir: PronoteDevoir) -> str:
        """Cree ou met a jour une tache dans Notion. Retourne 'created', 'updated', 'dry_run' ou 'error'."""
        pronote_id = devoir.id or self._generate_pronote_id(devoir)
        task = self._map_devoir_to_task(devoir)
        sync_state = self._get_sync_state(pronote_id)

        # Chercher par pronote_id si SQLite ne l'a pas mais Notion l'a
        if not sync_state:
            existing_notion_task = self.notion_client.search_task_by_pronote_id(pronote_id)
            if existing_notion_task:
                page_id = existing_notion_task["id"]
                sync_state = SyncState(
                    pronote_id=pronote_id,
                    notion_page_id=page_id,
                    title=task.title,
                    due_date=devoir.date_echeance.strftime("%Y-%m-%d"),
                    status="active"
                )
                self._update_sync_state(sync_state)

        if sync_state and sync_state.notion_page_id:
            task.page_id = sync_state.notion_page_id
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Mise a jour de la tache: {task.title}")
                return "dry_run"

            success = self.notion_client.update_task(task)
            if success:
                self._update_sync_state(SyncState(
                    pronote_id=pronote_id,
                    notion_page_id=task.page_id,
                    title=task.title,
                    due_date=devoir.date_echeance.strftime("%Y-%m-%d"),
                    status="active"
                ))
                return "updated"
            return "error"
        else:
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Creation de la tache: {task.title}")
                return "dry_run"

            notion_page_id = self.notion_client.create_task(task)
            if notion_page_id:
                self._update_sync_state(SyncState(
                    pronote_id=pronote_id,
                    notion_page_id=notion_page_id,
                    title=task.title,
                    due_date=devoir.date_echeance.strftime("%Y-%m-%d"),
                    status="active"
                ))
                return "created"
            return "error"

    def sync(self) -> Dict[str, int]:
        """Execute la synchronisation complete et retourne les statistiques."""
        logger.info("Debut de la synchronisation PRONOTE -> Notion")
        stats = {"created": 0, "updated": 0, "dry_run": 0, "errors": 0, "total": 0}

        try:
            devoirs = self.pronote_client.get_devoirs()
        except Exception as e:
            logger.error(f"Erreur lors de la recuperation des devoirs: {e}")
            stats["errors"] += 1
            return stats

        if not devoirs:
            logger.warning("Aucun devoir recupere depuis PRONOTE")
            return stats

        stats["total"] = len(devoirs)
        logger.info(f"Trouves {stats['total']} devoirs a synchroniser")

        for devoir in devoirs:
            result = self._create_or_update_task(devoir)
            if result in stats:
                stats[result] += 1
            else:
                stats["errors"] += 1

            if self.config.NOTION_RATE_LIMIT_DELAY > 0:
                time.sleep(self.config.NOTION_RATE_LIMIT_DELAY)

        logger.info(f"Synchronisation terminee: {stats}")
        return stats

    def close(self):
        """Fermeture propre des connexions."""
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'ai_client'):
            try:
                self.ai_client.close()
            except Exception:
                pass
        try:
            self.pronote_client.close()
        except Exception:
            pass
