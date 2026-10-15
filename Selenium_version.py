from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from models import PronoteDevoir
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class SeleniumPronoteClient:
    def __init__(self, portal_url, username, password,
                 profile="eleve", headless=False,
                 etablissement="Lycée polyvalent Aragon - Picasso"):
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.profile = profile
        self.headless = headless
        self.etablissement = etablissement
        self.driver = None
        self.timeout = 60

    def _log_current_page(self):
        if self.driver:
            logger.info("Titre: " + self.driver.title)
            logger.info("URL: " + self.driver.current_url)

    def _accept_cookies(self):
        """Accepte les cookies sur toutes les pages"""
        cookie_selectors = [
            (By.ID, "cookie-accept"),
            (By.ID, "btn-accept-cookies"),
            (By.ID, "accept-cookies"),
            (By.CSS_SELECTOR, "button[class*='cookie' i]"),
            (By.CSS_SELECTOR, "button[class*='accept' i]"),
            (By.XPATH, '//button[contains(text(), "Accepter") or contains(text(), "Tout accepter") or contains(text(), "OK")]'),
            (By.XPATH, '//*[contains(text(), "Accepter") or contains(text(), "Tout accepter")]'),
            (By.CSS_SELECTOR, "#cookie_consent button"),
            (By.CSS_SELECTOR, ".cookie-banner button"),
            (By.CSS_SELECTOR, "button.cookie-btn"),
        ]

        for selector in cookie_selectors:
            try:
                by, value = selector
                cookie_btn = self._wait_for_element(by, value, 5)
                if cookie_btn:
                    if self._safe_click(cookie_btn, "bouton cookies"):
                        logger.info("Cookies acceptes")
                        time.sleep(1)
                        return True
            except Exception:
                continue
        return False

    def _init_driver(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")

            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning("ChromeDriverManager failed: " + str(e))
                chrome_options.binary_location = "/usr/bin/google-chrome"
                self.driver = webdriver.Chrome(options=chrome_options)

            logger.info("Chrome demarre - Fenetre visible")
            return True
        except Exception as e:
            logger.error("Echec de l'initialisation de Selenium: " + str(e))
            return False

    def _safe_click(self, element, description=""):
        try:
            element.click()
            logger.info("Clic reussi sur: " + description)
            return True
        except ElementClickInterceptedException:
            logger.warning("Clic normal echoue: " + description)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info("Clic JS reussi sur: " + description)
                return True
            except Exception:
                return False
        except (ElementNotInteractableException, StaleElementReferenceException):
            time.sleep(1)
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                return False
        except Exception as e:
            logger.error("Click error: " + str(e))
            return False

    def _wait_and_click(self, by, value, timeout=20, description=""):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return self._safe_click(element, description)
        except TimeoutException:
            logger.error("Timeout: " + description + " introuvable")
            return False
        except Exception as e:
            logger.error("Erreur: " + str(e))
            return False

    def _wait_for_element(self, by, value, timeout=20):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def _wait_for_url_contains(self, text, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: text in d.current_url
            )
            return True
        except TimeoutException:
            return False

    def _wait_for_url_not_contains(self, text, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: text not in d.current_url
            )
            return True
        except TimeoutException:
            return False

    def _step_1_cas_page(self):
        logger.info("[ETAPE 1/5] Acces a CAS...")
        try:
            self.driver.get(self.portal_url)
            time.sleep(2)
            self._log_current_page()

            radio = self._wait_for_element(By.ID, "idp-EDU", 15)
            if not radio:
                radio = self._wait_for_element(By.CSS_SELECTOR, 'input[value="EDU"]', 10)

            if not radio:
                logger.error("Radio EDU introuvable")
                return False

            if not self._safe_click(radio, "radio Eleve ou parent"):
                label = self._wait_for_element(By.CSS_SELECTOR, "label[for='idp-EDU']", 5)
                if label:
                    if not self._safe_click(label, "label Eleve ou parent"):
                        logger.error("Impossible de selectionner EDU")
                        return False
                else:
                    logger.error("Label EDU introuvable")
                    return False

            time.sleep(1)

            if not self._wait_and_click(By.ID, "button-submit", 10, "button Valider"):
                if not self._wait_and_click(By.CSS_SELECTOR, 'input[type="submit"]', 10, "submit"):
                    logger.error("Bouton Valider introuvable")
                    return False

            if not self._wait_for_url_contains("educonnect.education.gouv.fr", 30):
                logger.error("Redirection vers EduConnect echouee")
                return False

            self._log_current_page()
            logger.info("OK ETAPE 1")
            return True
        except Exception as e:
            logger.error("Etape 1 echouee: " + str(e))
            return False

    def _step_2_educonnect_profil(self):
        logger.info("[ETAPE 2/5] Attente page selection profil EduConnect...")
        try:
            self._log_current_page()

            eleve_button = self._wait_for_element(By.ID, "bouton_eleve", 30)
            if not eleve_button:
                eleve_button = self._wait_for_element(By.CSS_SELECTOR, 'button[onclick*="eleve"]', 30)

            if not eleve_button:
                logger.error("Bouton Eleve introuvable")
                return False

            if not self._safe_click(eleve_button, "bouton Eleve"):
                logger.error("Impossible de cliquer sur Eleve")
                return False

            time.sleep(3)
            self._log_current_page()

            logger.info("OK ETAPE 2")
            return True
        except Exception as e:
            logger.error("Etape 2 echouee: " + str(e))
            return False

    def _step_3_educonnect_login(self):
        logger.info("[ETAPE 3/5] Attente champs login...")
        try:
            self._log_current_page()

            logger.info("Attente que les champs soient interactifs...")

            WebDriverWait(self.driver, self.timeout).until(
                lambda d: "fr-hidden" not in d.find_element(By.ID, "div_connexion").get_attribute("class")
            )

            username_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "j_username"))
            )
            password_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "j_password"))
            )

            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)

            logger.info("Identifiants saisis")

            submit_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "_eventId_proceed"))
            )

            if not self._safe_click(submit_button, "bouton Se connecter"):
                logger.error("Impossible de cliquer sur Se connecter")
                return False

            if not self._wait_for_url_not_contains("educonnect.education.gouv.fr/idp", 30):
                logger.error("Toujours sur EduConnect")
                return False

            self._log_current_page()
            logger.info("OK ETAPE 3")
            return True
        except Exception as e:
            logger.error("Erreur EduConnect: " + str(e))
            logger.info("URL: " + self.driver.current_url if self.driver else "N/A")
            return False

    def _step_4_select_etablissement(self):
        logger.info("[ETAPE 4/5] Selection etablissement...")
        try:
            self._log_current_page()

            etablissement_selectors = [
                (By.PARTIAL_LINK_TEXT, self.etablissement),
                (By.LINK_TEXT, self.etablissement),
                (By.XPATH, '//*[contains(text(), "Lycée polyvalent Aragon - Picasso")]'),
                (By.XPATH, '//*[contains(text(), "Aragon") and contains(text(), "Picasso")]'),
                (By.XPATH, '//*[contains(text(), "Lycée polyvalent")]'),
                (By.XPATH, '//*[contains(text(), "Aragon")]'),
                (By.CSS_SELECTOR, 'a[href*="aragon" i]'),
                (By.CSS_SELECTOR, 'a[href*="picasso" i]'),
            ]

            etablissement_link = None
            for selector in etablissement_selectors:
                by, value = selector
                etablissement_link = self._wait_for_element(by, value, 15)
                if etablissement_link:
                    break

            if not etablissement_link:
                logger.error("Etablissement introuvable: " + self.etablissement)
                return False

            if not self._safe_click(etablissement_link, "etablissement"):
                logger.error("Impossible de cliquer sur etablissement")
                return False

            time.sleep(3)
            self._log_current_page()
            logger.info("OK ETAPE 4")
            return True
        except Exception as e:
            logger.error("Etape 4 echouee: " + str(e))
            return False

    def _step_5_access_pronote(self):
        logger.info("[ETAPE 5/5] Acces a PRONOTE...")
        try:
            self._log_current_page()

            # APPEL COOKIES
            self._accept_cookies()

            pronote_selectors = [
                (By.PARTIAL_LINK_TEXT, "PRONOTE"),
                (By.XPATH, '//a[contains(@href, "pronote")]'),
                (By.XPATH, '//*[contains(text(), "PRONOTE")]'),
                (By.CSS_SELECTOR, 'a[href*="pronote" i]'),
                (By.CSS_SELECTOR, 'img[alt*="PRONOTE" i]'),
            ]

            pronote_link = None
            for selector in pronote_selectors:
                by, value = selector
                pronote_link = self._wait_for_element(by, value, 20)
                if pronote_link:
                    break

            if not pronote_link:
                logger.error("Lien PRONOTE introuvable")
                return False

            if not self._safe_click(pronote_link, "PRONOTE"):
                logger.error("Impossible de cliquer sur PRONOTE")
                return False

            if not self._wait_for_url_contains("index-education.net/pronote", 30):
                time.sleep(5)
                if "index-education.net/pronote" not in self.driver.current_url:
                    logger.error("Pas sur PRONOTE")
                    return False

            self._log_current_page()

            # ⚡ ACCEPTER LES COOKIES UNIQUEMENT ICI (après avoir cliqué sur PRONOTE)
            self._accept_cookies()

            logger.info("OK ETAPE 5")
            return True
        except Exception as e:
            logger.error("Etape 5 echouee: " + str(e))
            return False

    def connect(self):
        if not self._init_driver():
            return False

        try:
            logger.info("==================================================")
            logger.info("DEBUT FLUX DE CONNEXION PRONOTE")
            logger.info("==================================================")

            if not self._step_1_cas_page(): return False
            if not self._step_2_educonnect_profil(): return False
            if not self._step_3_educonnect_login(): return False
            if not self._step_4_select_etablissement(): return False
            if not self._step_5_access_pronote(): return False

            logger.info("CONNEXION REUSSIE !")
            logger.info("URL finale: " + self.driver.current_url)
            return True
        except Exception as e:
            logger.error("Erreur de connexion: " + str(e))
            return False

    def get_devoirs(self):
        if not self.driver:
            if not self.connect():
                raise RuntimeError("Impossible de se connecter a PRONOTE")

        try:
            logger.info("Recherche des devoirs sur PRONOTE...")

            self._log_current_page()

            time.sleep(3)

            devoirs = []

            try:
                self.driver.switch_to.default_content()
            except:
                pass

            try:
                iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[src*='pronote']")
                self.driver.switch_to.frame(iframe)
                logger.info("Basculé vers iframe PRONOTE")
            except:
                logger.info("Pas d'iframe trouvé, recherche directe")

            html = self.driver.page_source

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            devoir_rows = soup.select('table.TravailAFaire tr:not(:first-child)')
            if not devoir_rows:
                devoir_rows = soup.select('table.travailAFaire tr:not(:first-child)')

            if not devoir_rows:
                devoir_rows = soup.select('tr.devoir, tr.travail')

            for row in devoir_rows:
                try:
                    titre_elem = row.select_one('td[class*="titre"] a, td[class*="Titre"] a, td:nth-child(2) a')
                    if not titre_elem:
                        titre_elem = row.select_one('td a')

                    titre = titre_elem.get_text(strip=True) if titre_elem else "Sans titre"

                    date_elem = row.select_one('td[class*="date"]')
                    if not date_elem:
                        date_elem = row.select_one('td:nth-child(3)')

                    date_str = date_elem.get_text(strip=True) if date_elem else ""

                    try:
                        date_echeance = datetime.strptime(date_str, "%d/%m/%Y")
                    except:
                        try:
                            date_echeance = datetime.strptime(date_str, "%d/%m")
                        except:
                            date_echeance = datetime.now()

                    matiere_elem = row.select_one('td[class*="matiere"]')
                    if not matiere_elem:
                        matiere_elem = row.select_one('td:nth-child(1)')

                    matiere = matiere_elem.get_text(strip=True) if matiere_elem else ""

                    statut_elem = row.select_one('td[class*="statut"]')
                    if not statut_elem:
                        statut_elem = row.select_one('td:nth-child(4)')

                    statut = statut_elem.get_text(strip=True) if statut_elem else ""
                    est_fait = "fait" in statut.lower() or "termin" in statut.lower()

                    details_elem = row.select_one('td[class*="details"]')
                    details = details_elem.get_text(strip=True) if details_elem else ""

                    devoir = PronoteDevoir(
                        id=f"{titre}|{date_str}|{matiere}",
                        titre=titre,
                        date_echeance=date_echeance,
                        matiere=matiere,
                        est_fait=est_fait,
                        details=details
                    )
                    devoirs.append(devoir)
                    logger.info(f"Devoir trouvé: {titre} ({date_str})")

                except Exception as e:
                    logger.warning(f"Erreur traitement devoir: {e}")
                    continue

            if not devoirs:
                logger.warning("Aucun devoir trouvé - vérification alternative...")

                alt_selectors = [
                    'div.devoir, div.travail',
                    'li.devoir, li.travail',
                    'div[class*="travail"]',
                    'div[class*="devoir"]',
                ]

                for selector in alt_selectors:
                    elements = soup.select(selector)
                    for el in elements:
                        try:
                            titre_elem = el.select_one('h3, h4, .titre, strong')
                            titre = titre_elem.get_text(strip=True) if titre_elem else "Sans titre"

                            date_elem = el.select_one('.date, [class*="date"]')
                            date_str = date_elem.get_text(strip=True) if date_elem else ""

                            try:
                                date_echeance = datetime.strptime(date_str, "%d/%m/%Y")
                            except:
                                date_echeance = datetime.now()

                            matiere_elem = el.select_one('.matiere, [class*="matiere"]')
                            matiere = matiere_elem.get_text(strip=True) if matiere_elem else ""

                            devoir = PronoteDevoir(
                                id=f"{titre}|{date_str}|{matiere}",
                                titre=titre,
                                date_echeance=date_echeance,
                                matiere=matiere
                            )
                            devoirs.append(devoir)
                            logger.info(f"Devoir alternatif trouvé: {titre}")
                        except:
                            continue

            self.driver.switch_to.default_content()

            logger.info(f"{len(devoirs)} devoirs récupérés depuis PRONOTE")
            return devoirs

        except ImportError:
            logger.error("BeautifulSoup non installé - pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Erreur récupération devoirs: {e}")
            return []

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            logger.info("Driver Selenium ferme")