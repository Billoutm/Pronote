from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from models import PronoteDevoir
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class SeleniumPronoteClient:
    def __init__(self, portal_url: str, username: str, password: str, profile: str = "eleve"):
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.profile = profile
        self.driver: Optional[webdriver.Chrome] = None

    def connect(self) -> bool:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(self.portal_url)
            logger.info("Selenium: Page de connexion chargee")
            return True
        except Exception as e:
            logger.error(f"Echec de l'initialisation de Selenium: {e}")
            return False

    def _wait_and_click(self, by: By, value: str, timeout: int = 10) -> bool:
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def login(self) -> bool:
        if not self.driver:
            if not self.connect():
                return False

        try:
            time.sleep(2)

            username_field = None
            password_field = None

            try:
                username_field = self.driver.find_element(By.ID, "username")
                password_field = self.driver.find_element(By.ID, "password")
            except NoSuchElementException:
                try:
                    username_field = self.driver.find_element(By.NAME, "username")
                    password_field = self.driver.find_element(By.NAME, "password")
                except NoSuchElementException:
                    try:
                        username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    except NoSuchElementException:
                        pass

            if username_field and password_field:
                username_field.send_keys(self.username)
                password_field.send_keys(self.password)

                submit_button = None
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                except NoSuchElementException:
                    try:
                        submit_button = self.driver.find_element(By.ID, "submit")
                    except NoSuchElementException:
                        try:
                            submit_button = self.driver.find_element(By.NAME, "submit")
                        except NoSuchElementException:
                            pass

                if submit_button:
                    submit_button.click()
                    logger.info("Selenium: Clic sur le bouton de connexion")
                    time.sleep(3)
                    return True

            logger.error("Selenium: Champs de connexion introuvables")
            return False
        except Exception as e:
            logger.error(f"Selenium: Erreur lors de la connexion: {e}")
            return False

    def get_devoirs(self) -> List[PronoteDevoir]:
        if not self.driver:
            if not self.login():
                raise RuntimeError("Impossible de se connecter via Selenium")

        try:
            time.sleep(3)

            travail_link = None
            try:
                travail_link = self.driver.find_element(By.LINK_TEXT, "Travail à faire")
            except NoSuchElementException:
                try:
                    travail_link = self.driver.find_element(By.LINK_TEXT, "Cahier de texte")
                except NoSuchElementException:
                    try:
                        travail_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Travail")
                    except NoSuchElementException:
                        pass

            if travail_link:
                travail_link.click()
                time.sleep(3)

            devoirs = []
            try:
                devoir_elements = self.driver.find_elements(By.CSS_SELECTOR, ".devoir, .travail, tr[class*='travail'], li[class*='devoir']")
            except Exception:
                devoir_elements = []

            if not devoir_elements:
                logger.warning("Selenium: Aucun element de devoir trouve")
                return []

            for element in devoir_elements:
                try:
                    titre = ""
                    try:
                        titre_element = element.find_element(By.CSS_SELECTOR, ".titre, h3, h4, .libelle")
                        titre = titre_element.text.strip()
                    except NoSuchElementException:
                        pass

                    if not titre:
                        continue

                    date_str = ""
                    try:
                        date_element = element.find_element(By.CSS_SELECTOR, ".date, .echeance, .date-rendu")
                        date_str = date_element.text.strip()
                    except NoSuchElementException:
                        pass

                    matiere = None
                    try:
                        matiere_element = element.find_element(By.CSS_SELECTOR, ".matiere, .subject")
                        matiere = matiere_element.text.strip()
                    except NoSuchElementException:
                        pass

                    date_echeance = datetime.now()
                    if date_str:
                        try:
                            date_echeance = datetime.strptime(date_str, "%d/%m/%Y")
                        except ValueError:
                            try:
                                date_echeance = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                pass

                    devoir = PronoteDevoir(
                        id="",
                        titre=titre,
                        date_echeance=date_echeance,
                        matiere=matiere,
                        difficulte=None,
                        temps_estime=None,
                        est_fait=False,
                        rendu_en_ligne=False,
                        details=None
                    )
                    devoirs.append(devoir)
                except Exception as e:
                    logger.warning(f"Selenium: Erreur lors du traitement d'un devoir: {e}")
                    continue

            logger.info(f"Selenium: Recuperes {len(devoirs)} devoirs")
            return devoirs
        except Exception as e:
            logger.error(f"Selenium: Erreur avec Selenium: {e}")
            return []

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Selenium: Erreur lors de la fermeture: {e}")