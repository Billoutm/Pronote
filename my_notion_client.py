#!/usr/bin/env python3
"""Client pour interagir avec l'API Notion."""

import logging
from typing import Optional, Dict, Any, List

from notion_client import Client as NotionClientLibrary
from models import NotionTask
from config import Config

logger = logging.getLogger(__name__)

class NotionClient:
    """Client pour interagir avec l'API Notion."""

    def __init__(self, config: Config):
        self.config = config
        self.client = NotionClientLibrary(auth=config.NOTION_API_KEY)
        self.tasks_db_id = config.NOTION_TASK_DATABASE_ID
        self.tasks_data_source_id = getattr(config, "NOTION_TASKS_DATA_SOURCE_ID", "2b3443d6-1d67-81c5-809c-000b67ecd179")
        self.lycee_project_id = config.NOTION_LYCEE_PROJECT_PAGE_ID

    def _format_date_for_notion(self, date_str: str) -> Optional[str]:
        """Convertit une date en format ISO 8601 pour Notion (YYYY-MM-DD)."""
        from datetime import datetime
        try:
            if len(date_str) == 10 and date_str.count('-') == 2:
                return date_str
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def create_task(self, task: NotionTask) -> Optional[str]:
        """Cree une nouvelle tache dans la base Notion."""
        try:
            due_date_iso = self._format_date_for_notion(task.due_date)

            properties = {
                "Nom": {"title": [{"text": {"content": task.title[:2000]}}]},
                "Date début & fin": {"date": {"start": due_date_iso}} if due_date_iso else None,
                "Type": {"multi_select": [{"name": task.type}] if task.type else []},
                "Priorité": {"select": {"name": task.priority}},
                "Statut": {"status": {"name": task.status}},
                "Note": {"rich_text": [{"text": {"content": task.note[:2000]}}]},
            }

            if self.lycee_project_id:
                properties["Projet lié"] = {"relation": [{"id": self.lycee_project_id}]}

            properties = {k: v for k, v in properties.items() if v is not None}

            response = self.client.pages.create(
                parent={"database_id": self.tasks_db_id},
                properties=properties,
            )
            page_id = response.get("id")
            logger.info(f"Tache creee dans Notion: {task.title} (ID: {page_id})")
            return page_id
        except Exception as e:
            logger.error(f"Echec de la creation de la tache {task.title}: {e}")
            return None

    def update_task(self, task: NotionTask) -> bool:
        """Met a jour une tache existante dans Notion."""
        if not task.page_id:
            logger.error("Impossible de mettre a jour une tache sans page_id")
            return False

        try:
            due_date_iso = self._format_date_for_notion(task.due_date)

            properties = {
                "Nom": {"title": [{"text": {"content": task.title[:2000]}}]},
                "Date début & fin": {"date": {"start": due_date_iso}} if due_date_iso else None,
                "Type": {"multi_select": [{"name": task.type}] if task.type else []},
                "Priorité": {"select": {"name": task.priority}},
                "Statut": {"status": {"name": task.status}},
                "Note": {"rich_text": [{"text": {"content": task.note[:2000]}}]},
            }

            properties = {k: v for k, v in properties.items() if v is not None}

            self.client.pages.update(
                page_id=task.page_id,
                properties=properties,
            )
            logger.info(f"Tache mise a jour dans Notion: {task.title} (ID: {task.page_id})")
            return True
        except Exception as e:
            logger.error(f"Echec de la mise a jour de la tache {task.title}: {e}")
            return False

    def get_task_by_title(self, title: str, due_date: str) -> Optional[Dict[str, Any]]:
        """Recherche une tache par son titre et sa date d'echeance."""
        try:
            due_date_iso = self._format_date_for_notion(due_date)
            response = self.client.data_sources.query(
                data_source_id=self.tasks_data_source_id,
                filter={
                    "and": [
                        {"property": "Nom", "title": {"equals": title}},
                        {"property": "Date début & fin", "date": {"equals": due_date_iso}}
                    ]
                }
            )
            results = response.get("results", [])
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Echec de la recherche de la tache {title}: {e}")
            return None

    def search_task_by_pronote_id(self, pronote_id: str) -> Optional[Dict[str, Any]]:
        """Recherche une tache par son ID PRONOTE (dans la propriete Note)."""
        try:
            response = self.client.data_sources.query(
                data_source_id=self.tasks_data_source_id,
                filter={
                    "property": "Note",
                    "rich_text": {
                        "contains": f"#pronote-id:{pronote_id}"
                    }
                }
            )
            results = response.get("results", [])
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Echec de la recherche par pronote_id {pronote_id}: {e}")
            return None

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Recupere toutes les taches de la base Notion."""
        try:
            response = self.client.data_sources.query(
                data_source_id=self.tasks_data_source_id,
                page_size=100
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Echec de la recuperation de toutes les taches: {e}")
            return []
