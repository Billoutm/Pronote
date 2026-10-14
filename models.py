from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class PronoteDevoir:
    id: str
    titre: str
    date_echeance: datetime
    matiere: Optional[str] = None
    difficulte: Optional[int] = None
    temps_estime: Optional[str] = None
    est_fait: bool = False
    rendu_en_ligne: bool = False
    details: Optional[str] = None

@dataclass
class NotionTask:
    title: str
    due_date: str
    page_id: Optional[str] = None
    type: Optional[str] = None
    priority: str = "Moyenne"
    status: str = "Pas commence"
    note: str = ""
    project_id: str = ""
    parent_id: Optional[str] = None

@dataclass
class SyncState:
    pronote_id: str
    notion_page_id: Optional[str]
    title: str
    due_date: str
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = "active"