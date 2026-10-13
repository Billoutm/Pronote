from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class PronoteDevoir:
    """Représente un devoir récupéré depuis PRONOTE."""
    id: str                          # ID unique dans PRONOTE (si disponible)
    titre: str                       # Titre du devoir
    date_echeance: datetime          # Date d'échéance
    matiere: Optional[str] = None    # Matière (ex: "Mathématiques")
    difficulte: Optional[int] = None # 1=⭐, 2=⭐⭐, 3=⭐⭐⭐
    temps_estime: Optional[str] = None # Ex: "30 min"
    est_fait: bool = False           # Statut "Fait" dans PRONOTE
    rendu_en_ligne: bool = False    # Si le rendu est en ligne
    details: Optional[str] = None    # Détails supplémentaires

@dataclass
class NotionTask:
    """Représente une tâche dans Notion."""
    page_id: Optional[str] = None     # ID de la page Notion (None si nouvelle)
    title: str                       # Titre
    due_date: str                     # Date au format DD/MM/YYYY
    type: Optional[str] = None        # Type (ex: "Apprentissage")
    priority: str = "Moyenne"         # "Faible", "Moyenne", "Haute"
    status: str = "Pas commencé"      # "Pas commencé", "En cours", "Terminé"
    note: str = ""                    # Contenu de la propriété "Note"
    project_id: str = ""              # ID du projet lié (ex: projet "Lycée")
    parent_id: Optional[str] = None   # ID de la tâche parente (pour les sous-tâches)

@dataclass
class SyncState:
    """État de synchronisation stocké en SQLite."""
    pronote_id: str                  # Clé unique (ID PRONOTE ou clé générée)
    notion_page_id: Optional[str]    # ID de la page Notion
    title: str                       # Titre du devoir
    due_date: str                    # Date d'échéance (format ISO)
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = "active"           # "active" ou "archived"