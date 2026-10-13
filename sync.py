import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict
from models import PronoteDevoir, NotionTask, SyncState
from pronote_client import PronoteClient
from notion_client import NotionClient
from config import Config

logger = logging.getLogger(__name__)

class SyncEngine:
    def __init__(self, config: Config):
        self.config = config
        self.pronote_client = PronoteClient(
            portal_url=config.PRONOTE_PORTAL_URL,
            username=config.PRONOTE_EDUCONNECT_USERNAME,
            password=config.PRONOTE_EDUCONNECT_PASSWORD,
            profile=config.PRONOTE_STUDENT_PROFILE
        )
        self.notion_client = NotionClient(config)
        self._init_db()

        # Tables de correspondance
        self.matiere_to_type = {
            "Mathématiques": "Apprentissage",
            "Physique-Chimie": "Recherche",
            "SVT": "Recherche",
            "Français": "Apprentissage",
            "Histoire-Géographie": "Apprentissage",
            "Informatique": "Code",
            "EPS": "Entraînement",
            "Arts Plastiques": "Création",
            "Musique": "Création",
            "Technologie": "Design",
            "Anglais": "Apprentissage",
            "Espagnol": "Apprentissage",
            "Allemand": "Apprentissage",
        }

        self.difficulte_to_priority = {
            1: "Faible",    # ⭐
            2: "Moyenne",   # ⭐⭐
            3: "Haute"      # ⭐⭐⭐
        }

    def _init_db(self):
        """Initialise la base SQLite pour le suivi de synchronisation."""
        self.conn = sqlite3.connect("pronote_sync.db")
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
        self.conn.commit()

    def _generate_pronote_id(self, devoir: PronoteDevoir) -> str:
        """Génère une clé unique pour un devoir si ID PRONOTE non disponible."""
        return f"{devoir.titre}|{devoir.date_echeance.strftime('%Y-%m-%d')}|{devoir.matiere or 'unknown'}"

    def _map_devoir_to_task(self, devoir: PronoteDevoir) -> NotionTask:
        """Convertit un PronoteDevoir en NotionTask."""
        # Mapping matière → Type
        task_type = self.matiere_to_type.get(devoir.matiere)

        # Mapping difficulté → Priorité
        priority = self.difficulte_to_priority.get(devoir.difficulte, "Moyenne")

        # Statut
        status = "Terminé" if devoir.est_fait else "Pas commencé"

        # Construction de la note
        note_parts = []
        if devoir.temps_estime:
            note_parts.append(f"⏳ Temps : {devoir.temps_estime}")
        if devoir.rendu_en_ligne:
            note_parts.append("#rendu_en_ligne:oui")
        if devoir.details:
            note_parts.append(devoir.details)
        note_parts.append(f"#pronote-id:{devoir.id or self._generate_pronote_id(devoir)}")

        # Date au format DD/MM/YYYY pour Notion
        due_date_str = devoir.date_echeance.strftime("%d/%m/%Y")

        return NotionTask(
            title=devoir.titre,
            due_date=due_date_str,
            type=task_type,
            priority=priority,
            status=status,
            note="\n".join(note_parts),
            project_id=self.config.NOTION_LYCEE_PROJECT_PAGE_ID,
            parent_id=None
        )

    def _get_sync_state(self, pronote_id: str) -> Optional[SyncState]:
        """Récupère l'état de synchronisation pour un devoir."""
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
                last_updated=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S"),
                status=row[5]
            )
        return None

    def _update_sync_state(self, state: SyncState):
        """Met à jour l'état de synchronisation."""
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

    def _create_or_update_task(self, devoir: PronoteDevoir) -> bool:
        """Crée ou met à jour une tâche dans Notion."""
        pronote_id = devoir.id or self._generate_pronote_id(devoir)
        task = self._map_devoir_to_task(devoir)
        sync_state = self._get_sync_state(pronote_id)

        if sync_state:
            # Mise à jour de la tâche existante
            task.page_id = sync_state.notion_page_id
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Mise à jour de la tâche: {task.title}")
                return True
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
            # Création d'une nouvelle tâche
            if self.config.DRY_RUN:
                logger.info(f"[DRY-RUN] Création de la tâche: {task.title}")
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

    def sync(self):
        """Exécute la synchronisation complète."""
        logger.info("Début de la synchronisation PRONOTE → Notion")

        # 1. Récupérer les devoirs depuis PRONOTE
        devoirs = self.pronote_client.get_devoirs()
        if not devoirs:
            logger.warning("Aucun devoir récupéré depuis PRONOTE")
            return

        logger.info(f"Trouvés {len(devoirs)} devoirs à synchroniser")

        # 2. Synchroniser chaque devoir
        success_count = 0
        for devoir in devoirs:
            if self._create_or_update_task(devoir):
                success_count += 1

        logger.info(f"Synchronisation terminée: {success_count}/{len(devoirs)} devoirs traités")