#!/usr/bin/env python3
"""Moteur de synchronisation PRONOTE -> Notion."""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict
from models import PronoteDevoir, NotionTask, SyncState
from Selenium_version import SeleniumPronoteClient
from my_notion_client import NotionClient
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
        self._init_db()

        self.matiere_to_type = {
            "Mathematiques": "Devoirs",
            "Maths": "Devoirs",
            "Physique-Chimie": "Devoirs",
            "Physique": "Devoirs",
            "Chimie": "Devoirs",
            "SVT": "Devoirs",
            "Francais": "Devoirs",
            "Histoire-Geographie": "Devoirs",
            "Histoire": "Devoirs",
            "Geographie": "Devoirs",
            "Informatique": "Devoirs",
            "NSI": "Devoirs",
            "EPS": "Devoirs",
            "Arts Plastiques": "Devoirs",
            "Arts": "Devoirs",
            "Musique": "Devoirs",
            "Technologie": "Devoirs",
            "Anglais": "Devoirs",
            "Espagnol": "Devoirs",
            "Allemand": "Devoirs",
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
        """Convertit un PronoteDevoir en NotionTask."""
        matiere = devoir.matiere or ""
        task_type = self.matiere_to_type.get(matiere)
        priority = self.difficulte_to_priority.get(devoir.difficulte, "Moyenne")
        status = "Termine" if devoir.est_fait else "Pas commence"

        note_parts = []
        if devoir.date_donne:
            note_parts.append(f"Date de don: {devoir.date_donne}")
        if devoir.temps_estime:
            note_parts.append(f"Temps: {devoir.temps_estime}")
        if devoir.rendu_en_ligne:
            note_parts.append("#rendu_en_ligne:oui")
        if devoir.details:
            note_parts.append(devoir.details)

        pronote_id = devoir.id or self._generate_pronote_id(devoir)
        note_parts.append(f"#pronote-id:{pronote_id}")

        due_date_str = devoir.date_echeance.strftime("%d/%m/%Y")
        title = f"[{devoir.matiere}] {devoir.titre}" if devoir.matiere else devoir.titre

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

    def _archive_old_tasks(self, current_pronote_ids: List[str]):
        """Archive les taches qui n existent plus dans PRONOTE."""
        current_ids = set(current_pronote_ids)
        self.cursor.execute("SELECT pronote_id, notion_page_id FROM sync_state WHERE status = 'active'")
        existing_states = self.cursor.fetchall()

        for pronote_id, notion_page_id in existing_states:
            if pronote_id not in current_ids and notion_page_id:
                try:
                    self.notion_client.client.pages.update(
                        page_id=notion_page_id,
                        properties={"Statut": {"select": {"name": "Archive"}}}
                    )
                    self.cursor.execute(
                        "UPDATE sync_state SET status = 'archived' WHERE pronote_id = ?",
                        (pronote_id,)
                    )
                    logger.info(f"Tache archivee: {pronote_id}")
                except Exception as e:
                    logger.error(f"Erreur lors de l archivage de {pronote_id}: {e}")
        self.conn.commit()

    def _create_or_update_task(self, devoir: PronoteDevoir) -> bool:
        """Cree ou met a jour une tache dans Notion."""
        pronote_id = devoir.id or self._generate_pronote_id(devoir)
        task = self._map_devoir_to_task(devoir)
        sync_state = self._get_sync_state(pronote_id)

        if sync_state:
            task.page_id = sync_state.notion_page_id
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Mise a jour de la tache: {task.title}")
                return True

            if sync_state.notion_page_id:
                existing_task = self.notion_client.get_task_by_title(task.title, task.due_date)
                if not existing_task:
                    logger.warning(f"Tache {task.title} introuvable dans Notion, recreation...")
                    sync_state = None
                else:
                    success = self.notion_client.update_task(task)
                    if success:
                        self._update_sync_state(SyncState(
                            pronote_id=pronote_id,
                            notion_page_id=task.page_id,
                            title=task.title,
                            due_date=devoir.date_echeance.strftime("%Y-%m-%d"),
                            status="active"
                        ))
                    return success
            else:
                sync_state = None

        if not sync_state:
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Creation de la tache: {task.title}")
                return True

            notion_page_id = self.notion_client.create_task(task)
            if notion_page_id:
                self._update_sync_state(SyncState(
                    pronote_id=pronote_id,
                    notion_page_id=notion_page_id,
                    title=task.title,
                    due_date=devoir.date_echeance.strftime("%Y-%m-%d"),
                    status="active"
                ))
                return True
            return False

        return False

    def sync(self):
        """Execute la synchronisation complete."""
        logger.info("Debut de la synchronisation PRONOTE -> Notion")

        try:
            devoirs = self.pronote_client.get_devoirs()
        except Exception as e:
            logger.error(f"Erreur lors de la recuperation des devoirs: {e}")
            return

        if not devoirs:
            logger.warning("Aucun devoir recupere depuis PRONOTE")
            return

        logger.info(f"Trouves {len(devoirs)} devoirs a synchroniser")

        success_count = 0
        current_pronote_ids = []

        for devoir in devoirs:
            pronote_id = devoir.id or self._generate_pronote_id(devoir)
            current_pronote_ids.append(pronote_id)

            if self._create_or_update_task(devoir):
                success_count += 1

            if self.config.NOTION_RATE_LIMIT_DELAY > 0:
                time.sleep(self.config.NOTION_RATE_LIMIT_DELAY)

        if not self.config.DRY_RUN:
            self._archive_old_tasks(current_pronote_ids)

        logger.info(f"Synchronisation terminee: {success_count}/{len(devoirs)} devoirs traites")

    def close(self):
        """Fermeture propre des connexions."""
        if hasattr(self, 'conn'):
            self.conn.close()
        self.pronote_client.close()