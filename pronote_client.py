import logging
from typing import List, Optional

from models import PronoteDevoir
from datetime import datetime

logger = logging.getLogger(__name__)

class PronoteAPIError(Exception):
    pass

class MockPronoteClient:
    def __init__(self, portal_url: str, username: str, password: str, student: bool = True):
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.student = student
        self.info = {"nom": "Test", "prenom": "User"}

    def travail_a_faire(self) -> List[dict]:
        return []

class PronoteClient:
    def __init__(self, portal_url: str, username: str, password: str, profile: str = "eleve"):
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.profile = profile
        self.client: Optional[MockPronoteClient] = None

    def connect(self) -> bool:
        try:
            self.client = MockPronoteClient(
                self.portal_url,
                username=self.username,
                password=self.password,
                student=self.profile == "eleve"
            )
            user = self.client.info
            logger.info(f"Connecte a PRONOTE en tant que {user.get('nom', '')} {user.get('prenom', '')}")
            return True
        except Exception as e:
            logger.error(f"Echec de la connexion a PRONOTE: {e}")
            return False

    def get_devoirs(self) -> List[PronoteDevoir]:
        if not self.client:
            if not self.connect():
                raise RuntimeError("Impossible de se connecter a PRONOTE")

        devoirs = []
        try:
            travaux = self.client.travail_a_faire()

            for travail in travaux:
                try:
                    titre = travail.get("titre", travail.get("libelle", "Sans titre"))

                    date_str = travail.get("date") or travail.get("date_rendu") or travail.get("date_fin")
                    if date_str:
                        try:
                            date_echeance = datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            try:
                                date_echeance = datetime.strptime(date_str, "%d/%m/%Y")
                            except ValueError:
                                date_echeance = datetime.now()
                    else:
                        date_echeance = datetime.now()

                    matiere = travail.get("matiere") or travail.get("matiere_libelle")
                    if isinstance(matiere, dict):
                        matiere = matiere.get("libelle", matiere.get("nom", None))

                    difficulte = travail.get("difficulte")
                    if difficulte and isinstance(difficulte, str):
                        try:
                            difficulte = int(difficulte)
                        except ValueError:
                            difficulte = None

                    temps_estime = travail.get("duree") or travail.get("duree_estimee")
                    est_fait = travail.get("fait", False) or travail.get("est_fait", False)
                    rendu_en_ligne = travail.get("rendu_en_ligne", False) or travail.get("a_rendre", False)
                    details = travail.get("details") or travail.get("description", "")

                    devoir = PronoteDevoir(
                        id=str(travail.get("id", travail.get("N", ""))),
                        titre=str(titre),
                        date_echeance=date_echeance,
                        matiere=str(matiere) if matiere else None,
                        difficulte=difficulte,
                        temps_estime=str(temps_estime) if temps_estime else None,
                        est_fait=bool(est_fait),
                        rendu_en_ligne=bool(rendu_en_ligne),
                        details=str(details) if details else None
                    )
                    devoirs.append(devoir)
                except Exception as e:
                    logger.warning(f"Erreur lors du traitement d'un travail: {e}")
                    continue

            logger.info(f"Recuperes {len(devoirs)} devoirs depuis PRONOTE")
            return devoirs
        except Exception as e:
            logger.error(f"Erreur lors de la recuperation des devoirs: {e}")
            return []