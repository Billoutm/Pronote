import logging
from typing import Optional, Dict, Any
from notion_client import Client
from models import NotionTask
from config import Config

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = Client(auth=config.NOTION_API_KEY)
        self.tasks_db_id = config.NOTION_TASK_DATABASE_ID
        self.lycee_project_id = config.NOTION_LYCEE_PROJECT_PAGE_ID

    def create_task(self, task: NotionTask) -> Optional[str]:
        """Crée une nouvelle tâche dans la base Notion."""
        try:
            response = self.client.pages.create(
                parent={"database_id": self.tasks_db_id},
                properties={
                    "Nom": {"title": [{"text": {"content": task.title}}]},
                    "Date début & fin": {"date": {"end": task.due_date}},  # Format: "2026-10-15"
                    "Type": {"multi_select": [{"name": task.type}] if task.type else []},
                    "Priorité": {"select": {"name": task.priority}},
                    "Statut": {"status": {"name": task.status}},
                    "Projet lié": {"relation": [{"id": self.lycee_project_id}]},
                    "Note": {"rich_text": [{"text": {"content": task.note}}]},
                }
            )
            logger.info(f"Tâche créée dans Notion: {task.title} (ID: {response['id']})")
            return response["id"]
        except Exception as e:
            logger.error(f"Échec de la création de la tâche {task.title}: {e}")
            return None

    def update_task(self, task: NotionTask) -> bool:
        """Met à jour une tâche existante dans Notion."""
        if not task.page_id:
            logger.error("Impossible de mettre à jour une tâche sans page_id")
            return False

        try:
            self.client.pages.update(
                page_id=task.page_id,
                properties={
                    "Nom": {"title": [{"text": {"content": task.title}}]},
                    "Date début & fin": {"date": {"end": task.due_date}},
                    "Type": {"multi_select": [{"name": task.type}] if task.type else []},
                    "Priorité": {"select": {"name": task.priority}},
                    "Statut": {"status": {"name": task.status}},
                    "Note": {"rich_text": [{"text": {"content": task.note}}]},
                }
            )
            logger.info(f"Tâche mise à jour dans Notion: {task.title} (ID: {task.page_id})")
            return True
        except Exception as e:
            logger.error(f"Échec de la mise à jour de la tâche {task.title}: {e}")
            return False

    def get_task_by_title(self, title: str, due_date: str) -> Optional[Dict[str, Any]]:
        """Recherche une tâche par son titre et sa date d'échéance."""
        try:
            response = self.client.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "and": [
                        {"property": "Nom", "title": {"equals": title}},
                        {"property": "Date début & fin", "date": {"equals": due_date}}
                    ]
                }
            )
            if response["results"]:
                return response["results"][0]
            return None
        except Exception as e:
            logger.error(f"Échec de la recherche de la tâche {title}: {e}")
            return None

    def search_task_by_pronote_id(self, pronote_id: str) -> Optional[Dict[str, Any]]:
        """Recherche une tâche par son ID PRONOTE (dans la propriété Note)."""
        try:
            response = self.client.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "property": "Note",
                    "rich_text": {
                        "contains": f"#pronote-id:{pronote_id}"
                    }
                }
            )
            if response["results"]:
                return response["results"][0]
            return None
        except Exception as e:
            logger.error(f"Échec de la recherche par pronote_id {pronote_id}: {e}")
            return None