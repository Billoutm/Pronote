# Plan — Importer les devoirs PRONOTE via ÉduConnect dans Notion

## Objectif

Préparer un programme Python qui récupère les devoirs de l'Espace Élève PRONOTE et les synchronise comme tâches dans la base Notion **Tâches**, liées au projet **lycée**. Ce document décrit le travail envisagé; il ne constitue pas une implémentation.

Le périmètre initial se limite au module **Travail à faire**. Les contenus de cours, ressources, discussions, informations, sondages et casier numérique sont hors périmètre.

## Parcours de connexion observé

L'authentification n'est pas une connexion directe au formulaire PRONOTE :

1. Le portail de l'établissement affiche une page Skolengo de choix du fournisseur d'identité.
2. Le choix `EDU` (« Élève ou parent ») redirige vers ÉduConnect via un flux SAML.
3. Sur ÉduConnect, l'utilisateur sélectionne le profil **Élève**, puis saisit son identifiant et son mot de passe.
4. ÉduConnect renvoie le navigateur vers l'Espace Élève PRONOTE.
5. L'URL finale comprend un paramètre `identifiant` qui change à chaque connexion. C'est une donnée de session temporaire, pas une valeur à mettre dans la configuration.

Le formulaire d'authentification comprend également un jeton CSRF et un état d'exécution SAML temporaires. Il ne faut ni les coder en dur ni les réutiliser d'une connexion à l'autre.

### Validation préalable du connecteur

Avant de choisir l'architecture du scraper, vérifier si la bibliothèque Python [`bain3/pronotepy`](https://github.com/bain3/pronotepy) prend en charge **ce portail Skolengo précis**, le fournisseur ÉduConnect `EDU` et le profil élève. Le dépôt de cette bibliothèque mentionne des connecteurs ÉduConnect, mais indique aussi être en mode maintenance; cette mention ne prouve pas que le parcours fourni est compatible.

- Si le connecteur existant fonctionne avec ce portail, le privilégier plutôt que de réimplémenter le protocole.
- Vérifier sa compatibilité avec la version Python du projet et son mode de gestion de session.
- Si le connecteur ne couvre pas ce parcours, arrêter la conception à ce point et décider séparément d'une alternative (par exemple un connecteur compatible ou une automatisation navigateur avec interaction utilisateur).
- Ne pas contourner un CAPTCHA, une authentification multifacteur ou une autre protection. Si une étape nécessite une intervention humaine, l'expliquer clairement.

## Configuration envisagée

Les paramètres secrets et les identifiants nécessaires seront configurés dans `.env` plutôt que codés dans les sources :

| Variable indicative | Utilité |
|---|---|
| `PRONOTE_URL` | URL du portail PRONOTE de l'établissement |
| `PRONOTE_USERNAME` | Identifiant ÉduConnect de l'élève |
| `PRONOTE_PASSWORD` | Mot de passe ÉduConnect |
| `NOTION_API_KEY` | Clé d'intégration Notion déjà créée |
| `NOTION_TASKS_DATA_SOURCE_ID` | ID de la source de données de la base Tâches |
| `NOTION_LYCEE_PROJECT_PAGE_ID` | ID de la page du projet « lycée » |

Les noms définitifs dépendront des exigences du connecteur retenu. Un `.env.example` pourra documenter les variables avec des valeurs factices, jamais avec des identifiants réels. Le `.env` existant ne devra pas être lu, imprimé, remplacé ou ajouté à Git; il faudra l'exclure explicitement du suivi Git.

## Correspondance vers la base Notion Tâches

Respecter les propriétés déjà présentes dans la base documentée, sans modifier le schéma ni intervenir dans la zone **Backend (ne pas modifier)** :

| Donnée du devoir PRONOTE | Propriété Notion | Règle envisagée |
|---|---|---|
| Intitulé | `Nom` | Titre de la tâche |
| Échéance | `Date début & fin` | Renseigner la date de fin connue; ne pas inventer de date de début |
| Matière | `Type` | Renseigner seulement si elle correspond à une option existante |
| Temps estimé, difficulté, détails utiles | `Note` | Texte complémentaire; conserver les informations déjà présentes lors d'une mise à jour |
| État « Fait » | `Statut` | `Terminé` si fait, sinon `Pas commencé`, selon une règle à tester |
| Projet cible | `Projet lié` | Relation vers la page de projet dont l'ID est fourni dans `.env` |

La priorité des **tâches** doit utiliser les options exactes `Haute`, `Moyenne` ou `Faible` (et non `Basse`, option de la base Projet). La correspondance de la difficulté PRONOTE en étoiles vers cette priorité reste à fixer et à documenter avant les écritures réelles. Aucun statut, type ou niveau de priorité ne doit être supposé valide sans comparaison avec les options de la base.

Ne pas écrire dans les propriétés calculées `DATE DEBUT`, `DATE FIN`, `Retard` ni dans le rollup `Avancement (%)`.

## Déduplication et mises à jour

Une exécution répétée ne doit pas créer une nouvelle tâche pour chaque devoir déjà importé. L'identifiant PRONOTE stable, s'il existe dans la bibliothèque, est à privilégier. Sinon, définir une clé déterministe à partir des champs disponibles, documenter les risques de collision et tester les changements d'intitulé ou d'échéance.

La propriété `Note` contient du contenu métier; ne pas y ajouter discrètement un marqueur technique. Évaluer un petit stockage local SQLite pour associer une clé source à un identifiant de page Notion et détecter les changements. Ce stockage devra être exclu de Git. Définir une stratégie de reprise si une page Notion est créée mais que l'état local n'est pas enregistré, afin de limiter les doublons après interruption.

Les devoirs existants devront être actualisés lorsqu'une modification de la source est détectée, sans écraser les annotations qui ne proviennent pas de PRONOTE. La règle de fusion devra être définie et testée avant d'activer la synchronisation en écriture.

## Sécurité et confidentialité

- Utiliser HTTPS pour les échanges PRONOTE et Notion.
- Ne jamais journaliser les identifiants, mots de passe, jetons CSRF, réponses SAML, cookies, URL de session contenant `identifiant` ou clés d'API.
- Ne pas persister les cookies ou sessions d'authentification sans décision explicite.
- Exclure `.env` et l'éventuelle base SQLite locale de Git.
- En cas d'échec d'authentification ou de changement du parcours SSO, afficher une erreur explicite et expurgée plutôt que de poursuivre avec une session partielle.
- Prévoir un mode prévisualisation (« dry-run ») qui montre les créations et changements envisagés sans écrire dans Notion.

## Étapes de réalisation ultérieures

1. Confirmer l'URL du portail, le connecteur correspondant et la compatibilité avec le flux Skolengo → ÉduConnect → profil Élève.
2. Vérifier les versions Python et dépendances prises en charge par les bibliothèques retenues.
3. Définir un modèle typé de devoir et les règles de correspondance pour dates, statut, matière et difficulté.
4. Tester le scraping et le mapping avec des données simulées, sans compte réel.
5. Implémenter l'accès à la source de données Notion et la relation vers le projet « lycée » fourni par ID.
6. Ajouter déduplication, mise à jour prudente et mode dry-run.
7. Documenter les variables `.env`, la CLI et les erreurs possibles avec un `.env.example` factice.
8. Faire un essai réel uniquement après validation du connecteur, confirmation des IDs Notion et revue de la prévisualisation.

## Références du projet

- `Ressources/analyse-structurelle-de-pronote-contenus-&-ressources-·-travail-à-faire-·-communication-·-discussions.md`
- `Ressources/structure-notion-projets-en-cours-référence-complète-pour-ia.md`
- [`bain3/pronotepy`](https://github.com/bain3/pronotepy) — candidat à vérifier, pas une dépendance déjà sélectionnée.

## État

Ce document est un plan uniquement. Aucun scraper, fichier de configuration, dépendance ou contenu Notion n'est créé ou modifié par cette étape.
