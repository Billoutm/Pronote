import logging
from typing import List, Optional
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
        self.client: Optional[Client] = None

    def connect(self) -> bool:
        """Établit la connexion à PRONOTE."""
        try:
            # Version basique sans paramètre ENT
            self.client = Client(
                self.portal_url,
                username=self.username,
                password=self.password
            )
            user = self.client.info
            logger.info(f"Connecté à PRONOTE en tant que {user.get('nom', '')} {user.get('prenom', '')}")
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

            logger.info(f"Récupérés {len(devoirs)} devoirs depuis PRONOTE")
            return devoirs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des devoirs: {e}")
            return []