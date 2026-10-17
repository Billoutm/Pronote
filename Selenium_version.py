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
        self.timeout = 30

    def _log_current_page(self):
        if self.driver:
            logger.info("Titre: " + self.driver.title)
            logger.info("URL: " + self.driver.current_url)

    def _find_element_fast(self, by, value, max_wait=1.0):
        """Recherche un élément de manière ultra-rapide avec un polling court (max_wait secondes max)"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                elements = self.driver.find_elements(by, value)
                for el in elements:
                    if el.is_displayed():
                        return el
            except Exception:
                pass
            time.sleep(0.1)
        return None

    def _find_first_existing_fast(self, selectors, max_wait_per_selector=0.3):
        """Parcourt une liste de sélecteurs et retourne le premier élément visible trouvé rapidement"""
        for by, value in selectors:
            el = self._find_element_fast(by, value, max_wait=max_wait_per_selector)
            if el:
                return el
        return None

    def _wait_for_any_element(self, selectors, timeout=12):
        """Attend qu'au moins un élément parmi une liste de sélecteurs soit visible (timeout global en secondes)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for by, value in selectors:
                try:
                    elements = self.driver.find_elements(by, value)
                    for el in elements:
                        if el.is_displayed():
                            return el
                except Exception:
                    pass
            time.sleep(0.3)
        return None

    def _close_pronote_cookie_modal(self):
        """Ferme la modale d'information cookies de Pronote (bouton 'Fermer') si elle est présente"""
        modal_selectors = [
            (By.XPATH, '//button[contains(text(), "Fermer")]'),
            (By.XPATH, '//span[contains(text(), "Fermer")]/parent::button'),
            (By.CSS_SELECTOR, '.BoutonFermeture, button[class*="Fermer"]'),
            (By.XPATH, '//div[contains(@class, "Fenetre")]//button[contains(text(), "Fermer")]'),
        ]
        btn = self._find_first_existing_fast(modal_selectors, max_wait_per_selector=0.2)
        if btn:
            if self._safe_click(btn, "fermer modale cookies Pronote"):
                return True
        return False

    def _accept_cookies(self):
        """Accepte les cookies sur toutes les pages avec polling rapide"""
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

        cookie_btn = self._find_first_existing_fast(cookie_selectors, max_wait_per_selector=0.3)
        if cookie_btn:
            if self._safe_click(cookie_btn, "bouton cookies"):
                logger.info("Cookies acceptes")
                return True
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
                self.driver.execute_script("arguments[0].click();", element)
                logger.info("Clic JS reussi sur: " + description)
                return True
            except Exception:
                return False
        except (ElementNotInteractableException, StaleElementReferenceException):
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                return False
        except Exception as e:
            logger.error("Click error: " + str(e))
            return False

    def _wait_and_click(self, by, value, timeout=10, description=""):
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

    def _wait_for_element(self, by, value, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def _wait_for_url_contains(self, text, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: text in d.current_url
            )
            return True
        except TimeoutException:
            return False

    def _wait_for_url_not_contains(self, text, timeout=20):
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
            self._log_current_page()

            radio = self._wait_for_element(By.ID, "idp-EDU", 10)
            if not radio:
                radio = self._wait_for_element(By.CSS_SELECTOR, 'input[value="EDU"]', 5)

            if not radio:
                logger.error("Radio EDU introuvable")
                return False

            if not self._safe_click(radio, "radio Eleve ou parent"):
                label = self._wait_for_element(By.CSS_SELECTOR, "label[for='idp-EDU']", 3)
                if label:
                    if not self._safe_click(label, "label Eleve ou parent"):
                        logger.error("Impossible de selectionner EDU")
                        return False
                else:
                    logger.error("Label EDU introuvable")
                    return False

            if not self._wait_and_click(By.ID, "button-submit", 8, "button Valider"):
                if not self._wait_and_click(By.CSS_SELECTOR, 'input[type="submit"]', 8, "submit"):
                    logger.error("Bouton Valider introuvable")
                    return False

            if not self._wait_for_url_contains("educonnect.education.gouv.fr", 20):
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

            eleve_button = self._wait_for_element(By.ID, "bouton_eleve", 15)
            if not eleve_button:
                eleve_button = self._wait_for_element(By.CSS_SELECTOR, 'button[onclick*="eleve"]', 15)

            if not eleve_button:
                logger.error("Bouton Eleve introuvable")
                return False

            if not self._safe_click(eleve_button, "bouton Eleve"):
                logger.error("Impossible de cliquer sur Eleve")
                return False

            self._wait_for_url_contains("j_username", 10) or self._wait_for_url_not_contains("authentification", 10)
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

            try:
                WebDriverWait(self.driver, 15).until(
                    lambda d: "fr-hidden" not in d.find_element(By.ID, "div_connexion").get_attribute("class")
                )
            except Exception:
                pass

            username_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "j_username"))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "j_password"))
            )

            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)

            logger.info("Identifiants saisis")

            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "_eventId_proceed"))
            )

            if not self._safe_click(submit_button, "bouton Se connecter"):
                logger.error("Impossible de cliquer sur Se connecter")
                return False

            if not self._wait_for_url_not_contains("educonnect.education.gouv.fr/idp", 25):
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

            etablissement_link = self._find_first_existing_fast(etablissement_selectors, max_wait_per_selector=0.5)

            if not etablissement_link:
                etablissement_link = self._wait_for_element(By.PARTIAL_LINK_TEXT, self.etablissement, 8)

            if not etablissement_link:
                logger.error("Etablissement introuvable: " + self.etablissement)
                return False

            if not self._safe_click(etablissement_link, "etablissement"):
                logger.error("Impossible de cliquer sur etablissement")
                return False

            self._wait_for_url_not_contains("portail", 10)
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

            # Accept ENT portal cookies banner immediately upon landing on the dashboard
            cookie_btn_selectors = [
                (By.XPATH, '//button[contains(text(), "Tout accepter")]'),
                (By.XPATH, '//*[contains(text(), "Tout accepter")]'),
                (By.CSS_SELECTOR, 'button:not([disabled])[class*="accept"], button:not([disabled])[id*="accept"]'),
            ]
            cookie_btn = self._find_first_existing_fast(cookie_btn_selectors, max_wait_per_selector=0.5)
            if cookie_btn:
                self._safe_click(cookie_btn, "Tout accepter cookies ENT")

            self._accept_cookies()

            try:
                close_btn = self._find_first_existing_fast([
                    (By.XPATH, '//button[contains(text(), "Fermer") or contains(@class, "close")]')
                ], max_wait_per_selector=0.3)
                if close_btn:
                    self._safe_click(close_btn, "fermer popup")
            except Exception:
                pass

            pronote_selectors = [
                (By.CSS_SELECTOR, 'a[href*="index-education.net/pronote"]'),
                (By.CSS_SELECTOR, 'a[href*="pronote"] span.icon--pronote'),
                (By.CSS_SELECTOR, 'span.icon--pronote'),
                (By.XPATH, '//a[contains(@href, "index-education.net/pronote")]'),
                (By.XPATH, '//span[@class="services-shortcut__label" and contains(text(), "Pronote")]'),
                (By.XPATH, '//a[contains(@href, "pronote")]'),
                (By.CSS_SELECTOR, 'a[title*="PRONOTE" i]'),
                (By.CSS_SELECTOR, 'a[title*="Pronote" i]'),
                (By.PARTIAL_LINK_TEXT, "Pronote"),
                (By.PARTIAL_LINK_TEXT, "PRONOTE"),
                (By.XPATH, '//*[contains(text(), "PRONOTE") or contains(text(), "Pronote")]/ancestor::a'),
            ]

            def find_pronote_link():
                return self._find_first_existing_fast(pronote_selectors, max_wait_per_selector=0.3)

            pronote_link = find_pronote_link()

            if not pronote_link:
                logger.info("Lien PRONOTE non trouvé sur le tableau de bord, essai d'ouverture du menu Services...")
                service_menu_selectors = [
                    (By.ID, 'services-launcher'),
                    (By.CSS_SELECTOR, '.header__menu-button'),
                    (By.CSS_SELECTOR, 'button[title*="Services" i]'),
                    (By.CSS_SELECTOR, 'button[title*="Applications" i]'),
                    (By.XPATH, '//button[.//span[contains(text(), "Services")]]'),
                ]
                menu_btn = self._find_first_existing_fast(service_menu_selectors, max_wait_per_selector=0.5)
                if menu_btn:
                    self._safe_click(menu_btn, "menu Services")
                    pronote_link = find_pronote_link()

            if not pronote_link:
                logger.error("Lien PRONOTE introuvable après tous les essais")
                return False

            try:
                parent_a = pronote_link.find_element(By.XPATH, './ancestor::a')
                if parent_a:
                    pronote_link = parent_a
            except Exception:
                pass

            try:
                self.driver.execute_script("arguments[0].click();", pronote_link)
                logger.info("Clic JS direct réussi sur: PRONOTE")
            except Exception as e:
                logger.warning(f"Clic JS direct échoué, essai _safe_click: {e}")
                if not self._safe_click(pronote_link, "PRONOTE"):
                    logger.error("Impossible de cliquer sur PRONOTE")
                    return False

            start_handles = len(self.driver.window_handles)
            for _ in range(15):
                if len(self.driver.window_handles) > start_handles:
                    break
                time.sleep(0.1)

            if len(self.driver.window_handles) > 1:
                logger.info("Nouvel onglet détecté, basculement vers le dernier onglet...")
                self.driver.switch_to.window(self.driver.window_handles[-1])

            if not self._wait_for_url_contains("index-education.net", 15):
                if "index-education.net" not in self.driver.current_url:
                    logger.error("Pas sur PRONOTE (URL actuelle: " + self.driver.current_url + ")")
                    return False

            self._log_current_page()
            self._accept_cookies()
            self._close_pronote_cookie_modal()

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

            cahier_selectors = [
                (By.XPATH, '//span[contains(translate(text(),"CAHIER DE TEXTES","cahier de textes"), "cahier de textes")]'),
                (By.XPATH, '//div[contains(translate(text(),"CAHIER DE TEXTES","cahier de textes"), "cahier de textes")]'),
                (By.XPATH, '//td[contains(translate(text(),"CAHIER DE TEXTES","cahier de textes"), "cahier de textes")]'),
                (By.CSS_SELECTOR, '.BoutonVignette[title*="Cahier" i], .BoutonVignette[alt*="Cahier" i], [id*="Cahier" i]'),
                (By.XPATH, '//*[contains(@title, "Cahier de textes") or contains(@alt, "Cahier de textes")]'),
                (By.PARTIAL_LINK_TEXT, "Cahier de textes"),
                (By.PARTIAL_LINK_TEXT, "cahier de textes"),
                (By.XPATH, '//*[contains(translate(text(),"CAHIER","cahier"), "cahier")]'),
            ]

            cahier_tab = self._wait_for_any_element(cahier_selectors, timeout=12)
            if not cahier_tab:
                raise RuntimeError("Impossible de trouver le menu 'Cahier de textes' sur PRONOTE")

            travail_selectors = [
                (By.XPATH, '//span[contains(translate(text(),"TRAVAIL À FAIRE","travail à faire"), "travail à faire")]'),
                (By.XPATH, '//div[contains(translate(text(),"TRAVAIL À FAIRE","travail à faire"), "travail à faire")]'),
                (By.XPATH, '//a[contains(translate(text(),"TRAVAIL À FAIRE","travail à faire"), "travail à faire")]'),
                (By.PARTIAL_LINK_TEXT, "Travail à faire"),
                (By.PARTIAL_LINK_TEXT, "travail à faire"),
                (By.XPATH, '//span[contains(text(), "A faire")]'),
                (By.XPATH, '//button[contains(text(), "A faire")]'),
                (By.CSS_SELECTOR, 'button[id*="AFaire"], .Bouton[title*="Travail à faire" i]'),
            ]

            # Boucle de tentative pour survoler 'Cahier de textes' et cliquer sur 'Travail à faire'
            page_loaded = False
            for attempt in range(3):
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(cahier_tab).perform()
                    logger.info(f"Survol de 'Cahier de textes' (tentative {attempt+1})")
                    time.sleep(1.0)
                except Exception as e:
                    logger.warning(f"Survol échoué sur 'Cahier de textes': {e}")
                    try:
                        self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", cahier_tab)
                        time.sleep(0.8)
                    except:
                        pass

                travail_tab = self._wait_for_any_element(travail_selectors, timeout=4.0)
                if travail_tab:
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(travail_tab).click().perform()
                        logger.info("Clic ActionChains réussi sur 'Travail à faire' dans le sous-menu")
                    except Exception as e:
                        logger.warning(f"Clic ActionChains échoué, essai JS: {e}")
                        try:
                            self.driver.execute_script("arguments[0].click();", travail_tab)
                            logger.info("Clic JS réussi sur 'Travail à faire' dans le sous-menu")
                        except Exception as e2:
                            logger.warning(f"Clic JS échoué: {e2}")
                else:
                    logger.warning("Élément 'Travail à faire' non visible dans le sous-menu après survol")

                # Vérifier si on a bien basculé sur la page complète 'Travail à faire'
                logger.info("Vérification du chargement de la page complète 'Travail à faire'...")
                for _ in range(15):
                    html_source = self.driver.page_source
                    if "Travail à faire" in html_source or "Toutes les matières" in html_source or "Vue chronologique" in html_source or "A faire" in html_source:
                        page_loaded = True
                        logger.info("Page complète 'Travail à faire' confirmée !")
                        break
                    time.sleep(0.5)

                if page_loaded:
                    break
                else:
                    logger.warning(f"Tentative {attempt+1}: Pas encore sur la page 'Travail à faire', nouvelle tentative...")

            if not page_loaded:
                raise RuntimeError("Impossible de confirmer l'accès à la page 'Travail à faire' sur PRONOTE après plusieurs tentatives")

            time.sleep(1.0)

            devoirs_dict = {}

            logger.info("Défilement (scroll) en haut et en bas pour récupérer tous les devoirs...")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)

            for step in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.driver.execute_script("""
                    let divs = document.querySelectorAll('div, section, article');
                    for(let d of divs) {
                        if(d.scrollHeight > d.clientHeight) {
                            d.scrollTop = d.scrollHeight;
                        }
                    }
                """)
                time.sleep(0.6)
                self._extract_devoirs_from_page(devoirs_dict)

            self.driver.execute_script("window.scrollTo(0, 0);")
            self.driver.execute_script("""
                let divs = document.querySelectorAll('div, section, article');
                for(let d of divs) {
                    if(d.scrollHeight > d.clientHeight) {
                        d.scrollTop = 0;
                    }
                }
            """)
            time.sleep(0.5)
            self._extract_devoirs_from_page(devoirs_dict)

            devoirs = list(devoirs_dict.values())
            logger.info(f"{len(devoirs)} devoirs récupérés depuis PRONOTE après défilement")
            return devoirs

        except ImportError:
            logger.error("BeautifulSoup non installé - pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Erreur récupération devoirs: {e}")
            return []

    def _is_valid_devoir(self, text: str) -> bool:
        if not text or len(text) < 5:
            return False
        lower_txt = text.lower().strip()
        excluded_phrases = [
            'travail à faire', 'de textes', 'contenus et ressources',
            'forums pédagogiques', 'cahier de textes', 'vue chronologique',
            'vue hebdomadaire', 'toutes les matières'
        ]
        if lower_txt in excluded_phrases:
            return False
        if any(lower_txt == p or lower_txt.startswith(p + '\n') for p in excluded_phrases):
            if len(text) < 35:
                return False

        has_indicator = any(kw in text for kw in [
            'Devoir', 'Travail', 'Fait', 'Non Fait', 'rendre', 'Donné',
            'pour', 'Pour', 'séance', 'Leçon', 'Exercice', 'page', 'chapitre',
            '3D Printing', 'DNL', 'ANGLAIS', 'FRANCAIS', 'MATHEMATIQUES', 'HISTOIRE',
            'PHYSIQUE', 'SVT', 'ALLEMAND', 'ESPAGNOL', 'EPS'
        ])
        return has_indicator

    def _parse_pronote_date(self, text: str) -> Optional[datetime]:
        try:
            text_lower = text.lower()
            months = {
                'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
            }
            import re
            match = re.search(r'(\d{1,2})\s+([a-zéû]+)', text_lower)
            if match:
                day = int(match.group(1))
                month_str = match.group(2)
                month = months.get(month_str, datetime.now().month)
                year = datetime.now().year
                return datetime(year, month, day)
        except Exception:
            pass
        return None

    def _extract_devoirs_from_page(self, devoirs_dict):
        try:
            self.driver.switch_to.default_content()
        except:
            pass

        try:
            html = self.driver.page_source
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            items = soup.select('div.conteneur-item')
            for item in items:
                try:
                    matiere_el = item.select_one('h3.titre-matiere')
                    matiere = matiere_el.get_text(strip=True) if matiere_el else ""

                    soustitre_el = item.select_one('p.ie-sous-titre')
                    date_donne = soustitre_el.get_text(strip=True) if soustitre_el else ""

                    desc_el = item.select_one('div.description')
                    if not desc_el:
                        continue
                    details = desc_el.get_text(separator=' ', strip=True)
                    if not details or len(details) < 2:
                        continue

                    item_text = item.get_text(separator=' ', strip=True)
                    est_fait = False
                    if "Fait" in item_text and "Non Fait" not in item_text:
                        est_fait = True
                    if "is-checked" in str(item) or "colored-label is-checked" in str(item):
                        est_fait = True

                    date_echeance = datetime.now()
                    date_container = item.find_parent('li')
                    while date_container:
                        h2_el = date_container.select_one('h2.ie-titre-gros')
                        if h2_el:
                            date_text = h2_el.get_text(separator=' ', strip=True)
                            parsed_dt = self._parse_pronote_date(date_text)
                            if parsed_dt:
                                date_echeance = parsed_dt
                                break
                        date_container = date_container.find_parent('li')

                    if date_echeance == datetime.now():
                        parent_div = item.find_parent(attrs={"data-iddate": True})
                        if parent_div and parent_div.get("data-iddate"):
                            iddate = parent_div.get("data-iddate")
                            try:
                                date_echeance = datetime.strptime(iddate, "%d%m%Y")
                            except:
                                pass

                    titre = details[:150] if len(details) > 0 else "Sans titre"
                    devoir_id = f"{matiere}|{titre[:40]}|{date_echeance.strftime('%Y-%m-%d')}"

                    if devoir_id not in devoirs_dict:
                        devoirs_dict[devoir_id] = PronoteDevoir(
                            id=devoir_id,
                            titre=titre,
                            date_echeance=date_echeance,
                            matiere=matiere if len(matiere) < 30 else "",
                            est_fait=est_fait,
                            details=details,
                            date_donne=date_donne
                        )
                except Exception as e:
                    logger.warning(f"Erreur parsing item individuel Pronote: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Erreur BeautifulSoup extraction ciblée: {e}")

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            logger.info("Driver Selenium ferme")
