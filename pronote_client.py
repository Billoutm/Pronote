import logging
from typing import List
from pronotepy import Client, PronoteAPIError
from models import PronoteDevoir
from datetime import datetime

logger = logging.getLogger(__name__)

class PronoteClient:
    def __init__(self, portal_url: str, username: str, password: str, profile: str = "eleve"):
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.profile = profile
        self.client = None

    def connect(self) -> bool:
        """Établit la connexion à PRONOTE via ÉduConnect."""
        try:
            self.client = Client(
                self.portal_url,
                username=self.username,
                password=self.password,
                student=self.profile == "eleve"
            )
            # Tester la connexion en récupérant l'utilisateur
            user = self.client.info
            logger.info(f"Connecté à PRONOTE en tant que {user['nom']} {user['prenom']}")
            return True
        except PronoteAPIError as e:
            logger.error(f"Échec de la connexion à PRONOTE: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue avec pronotepy: {e}")
            return False

    def get_devoirs(self) -> List[PronoteDevoir]:
        """Récupère la liste des devoirs depuis PRONOTE."""
        if not self.client:
            if not self.connect():
                raise RuntimeError("Impossible de se connecter à PRONOTE")

        devoirs = []
        try:
            # Récupérer les devoirs (à adapter selon la structure de pronotepy)
            # Exemple : self.client.cahier_de_texte.travail_a_faire
            travaux = self.client.travail_a_faire()
            for travail in travaux:
                devoir = PronoteDevoir(
                    id=str(travail.get("id", "")),  # À vérifier selon pronotepy
                    titre=travail.get("titre", "Sans titre"),
                    date_echeance=datetime.strptime(travail["date"], "%Y-%m-%d") if "date" in travail else datetime.now(),
                    matiere=travail.get("matiere"),
                    difficulte=travail.get("difficulte"),  # 1, 2 ou 3
                    temps_estime=travail.get("duree"),
                    est_fait=travail.get("fait", False),
                    rendu_en_ligne=travail.get("rendu_en_ligne", False),
                    details=travail.get("details")
                )
                devoirs.append(devoir)
            logger.info(f"Récupérés {len(devoirs)} devoirs depuis PRONOTE")
            return devoirs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des devoirs: {e}")
            return []