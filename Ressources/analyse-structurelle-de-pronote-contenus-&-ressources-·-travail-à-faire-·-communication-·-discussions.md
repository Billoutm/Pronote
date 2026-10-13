# 🏫 Analyse structurelle de PRONOTE

> **Objet** : décrire la structure et le fonctionnement des modules pédagogiques et de communication de PRONOTE (éditeur : Index Éducation), vue principalement depuis l'Espace Élèves, avec le contexte côté enseignants/établissement quand il éclaire la logique du système.
> **Sources** : documentation officielle Index Éducation (doc.index-education.com, docs.index-education.com) — analyse du 13/10/2026.

---

## 0. Contexte général

- **PRONOTE** est le logiciel de vie scolaire dominant en France (collèges/lycées) : notes, cahier de textes, emplois du temps, absences, communication.
- Il se présente sous forme d'**Espaces distincts** selon le profil : **Espace Élèves, Espace Parents, Espace Professeurs, Espace Vie scolaire, Espace Direction** + un **Client lourd** (administration) et une **application mobile**. Les fonctionnalités visibles dépendent des **choix et autorisations de l'établissement**.
- Les modules demandés s'articulent autour de deux zones :
  - le **Cahier de textes** (module pédagogique) → *Contenu et ressources* + *Travail à faire* ;
  - l'onglet **Communication** (messagerie interne) → *Discussions, Informations, Sondages, Casier numérique*.

---

## 0.1. Les différents modes d'accès à PRONOTE

Il existe **4 façons d'accéder à PRONOTE**, avec des périmètres de fonctionnalités différents :

### 1. Client PRONOTE (logiciel installé sur un poste)
- Application « lourde » installée sur un ordinateur (poste de l'établissement, ou ordinateur personnel pour certains personnels).
- **C'est le mode de connexion qui offre le plus de fonctionnalités** (paramétrage, courriers, appels, impressions, gestion complète).
- En mode hébergé, la connexion se fait via l'adresse `RNE.index-education.net` (RNE = n° d'établissement) ; sinon, aux coordonnées du serveur fournies par le responsable PRONOTE.
- Existe en sous-modes à périmètre restreint : ex. le mode **« Dans la classe »** (accès uniquement à la saisie des absences et du cahier de textes, pour la confidentialité devant les élèves).
- Réservé en pratique aux **personnels** (vie scolaire, direction, professeurs) ; les élèves/parents n'utilisent pas le Client.

### 2. Espaces web (depuis un navigateur, PRONOTE.net)
- Accessible depuis **n'importe quel navigateur**, sans installation, à l'adresse du **portail PRONOTE de l'établissement** (elle se termine par `index-education.net/pronote/` dans la plupart des cas).
- Le portail propose un choix de **profil** : Élèves, Parents, Professeurs, Vie scolaire.
- Connexion avec **identifiant + mot de passe fournis par l'établissement** (personnalisation du mot de passe à la première connexion ; identifiants susceptibles de changer chaque année / en changeant d'établissement).
- Nombreuses fonctionnalités communes avec le Client, mais **certaines restent exclusives au Client** (ex. côté vie scolaire : appels non effectués, courriers prédéfinis) et d'autres à l'Espace web (ex. envoi d'e-mails, téléchargement du Client).

### 3. Application mobile PRONOTE (iOS / Android)
- Installable depuis les stores ; version **optimisée smartphone** de l'Espace (élèves et parents surtout).
- **Messagerie contextuelle avec notifications push** : chaque événement est annoncé (message, information, sondage, casier numérique…).
- Fonctionnalités élèves adaptées au mobile : **envoyer une photo de son travail** (devoir manuscrit), consulter le travail à faire, etc.
- **Connexion par QR code** : QR code fourni par l'établissement ou généré depuis l'Espace Web (*Mes données / Informations personnelles > Compte*), + **code à 4 chiffres** ; possibilité de connexion automatique par la suite.

### 4. Via l'ENT (Espace Numérique de Travail) / EduConnect
- Beaucoup d'établissements font passer la connexion par **l'ENT régional** (souvent avec identifiants **EduConnect**) : dans ce cas, les identifiants PRONOTE sont ceux de l'ENT, et PRONOTE s'ouvre via un **raccourci dans l'espace personnel ENT**.
- La procédure d'identifiants/mot de passe directe (mode 2) ne s'applique alors pas.

> 💡 **Règle de cohérence** : quel que soit le mode d'accès, on retrouve la même base de données et les mêmes modules ; seule l'**étendue des fonctionnalités** varie (Client > Espaces web ; mobile = sous-ensemble optimisé). L'établissement définit ce qui est publié sur chaque espace.

---

## 1. Contenu et ressources (Cahier de textes)

**Rôle** : consulter le contenu des cours et les documents mis à disposition par les professeurs.

### Structure de l'affichage (Espace Élèves)

| Élément | Détail |
|---------|--------|
| **Vue chronologique** | Liste des dernières entrées du cahier de textes ; clic pour déplier/replier le détail ; filtrage par **matière** dans la liste de gauche (toutes par défaut) |
| **Vue hebdomadaire** | Planning de la semaine en cours ; navigation par flèches ou calendrier ; clic sur un cours pour ouvrir le détail |
| **Contenu d'une entrée** | Contenu du cours saisi par le professeur (+ éventuels QCM, liens et pièces jointes attachés au cours) |
| **Ressources pédagogiques** | Par matière ; un clic **télécharge la ressource ou l'ouvre dans un nouvel onglet** |
| **Thèmes** (nouveauté) | Les ressources peuvent être **classées par thème** pour faciliter la recherche ; thèmes partagés dans PRONOTE → utiles aux projets interdisciplinaires |

### Logique côté enseignant
- Le contenu est saisi **pour chaque cours** dans le cahier de textes (Client, Espace Professeurs ou mobile).
- Le cahier de textes est **publié à la fin du cours** par défaut.
- Recommandation officielle : joindre les cours **en PDF** — QCM, liens et pièces jointes restent ensuite accessibles via les *Ressources pédagogiques* de l'élève.
- Gestion documentaire : un document est **stocké une fois et réutilisé** (mise à jour en un seul endroit) ; possibilité de partager ses pièces jointes avec les autres enseignants.
- Les **manuels numériques** des éditeurs interconnectés (si hébergement Index) sont accessibles directement depuis l'Espace.

---

## 2. Travail à faire (Cahier de textes)

**Rôle** : consulter les devoirs et rendre les travaux en ligne.

### Structure de l'affichage (Espace Élèves)

| Élément | Détail |
|---------|--------|
| **Vue chronologique** | Liste des devoirs ; filtrage par matière ; clic pour déplier le détail |
| **Vue hebdomadaire** | Planning semaine par semaine (flèches/calendrier) ; clic sur un cours pour le détail |
| **Métadonnées du devoir** | **Temps estimé** et **difficulté en étoiles** (★ facile → ★★★ difficile), si le professeur les a renseignées |
| **Rendu en ligne** | Bouton **« Déposer ma copie »** dans le détail du devoir → un seul document ; possible de **« Remplacer »** le fichier jusqu'à la date de rendu (tant que le professeur ne l'a pas récupéré) |
| **Photo depuis l'app mobile** | Possibilité d'envoyer une photo d'un travail manuscrit |
| **Suivi personnel** | Case **« Fait »** pour marquer un travail réalisé ; décocher « Fait » en haut pour **ne voir que ce qui reste à faire** |

### Logique côté enseignant / établissement
- Saisie dans le cahier de textes avec **mode de rendu « À déposer dans l'Espace Élève »** si un rendu en ligne est attendu.
- Le professeur peut cibler **quelques élèves seulement**, et renseigner **durée + difficulté** (valeurs par défaut paramétrables dans ses préférences).
- Le prof peut **vérifier la charge de travail d'une classe** avant d'ajouter un devoir.
- ⚠️ Cas limite : les **élèves détachés** ne reçoivent pas par défaut le travail à faire de leur cours d'origine.
- Les cahiers de textes peuvent être **visés** par la direction/vie scolaire (contrôle institutionnel).

---

## 3. Communication (messagerie interne)

**Rôle** : l'onglet Communication regroupe **4 canaux internes** + l'e-mail ; une **notification persistante** y reste active tant que les éléments reçus ne sont pas consultés.

### Les 4 canaux de la messagerie interne

| Canal | Direction | Réponse ? | Signature / reçu | Usage typique |
|-------|-----------|-----------|------------------|---------------|
| **Discussion** | 2 ↔ n participants | ✅ Droit de réponse entre **tous** les participants | — | Échange en petit comité |
| **Information** | 1 → large public | ❌ Aucune réponse possible | ✅ **Accusé de réception** optionnel (« J'ai pris connaissance ») | Diffuser largement sans engager d'échange |
| **Sondage** | 1 → ensemble ciblé | Réponses à questions | Nominatif ou **anonyme** | Poser une question, analyser les réponses |
| **Casier numérique** | Dépôt de documents | — | Suivi du **% de documents ouverts** (côté émetteur) | Remettre/collecter des documents |

### Détails par canal

**Information**
- Destinataires par **classes** (responsables/élèves/professeurs/personnels/maîtres de stage) ou **à titre individuel** ou via **listes de diffusion**.
- Objet + contenu + pièce jointe ; **semaines de visibilité** sur les Espaces ; accusés de réception classés par type de destinataire ; « Marquer comme lu » ; classable par **catégorie** (nouveauté 2026).
- Les dernières informations reçues s'affichent sur la **page d'accueil**.

**Sondage**
- Types : **nominatif** ou **anonyme**.
- Questions : **choix unique** (Oui/Non par défaut), **choix multiple**, **réponse libre à saisir** (nominatif uniquement).
- **Période de publication** ; résultats **cumulés par type de destinataire** avec détail nominatif ; modèles de sondages réutilisables ; envoi par élève ou par responsable.

**Casier numérique**
- Affichages **Envoi** (déposer/gérer : ajouter destinataires, consulter, mettre à jour sans renvoyer, supprimer pour tous) et **Réception** (ouvrir, filtrer « non lus », trier par nom/envoyeur/date).
- **Mémo** possible en accompagnement du document.
- Ajout possible depuis un **cloud personnel** : Box, Dropbox, Google Drive, OneDrive, Office 365, Digiposte.
- **Ouvert aux élèves depuis PRONOTE 2025** : les professeurs/personnels peuvent collecter ou remettre des documents aux élèves et suivre le taux d'ouverture ; filtre par **groupe** en plus de la classe (2026).

### Canaux complémentaires (établissement)
- **Message instantané (tchat)** : les échanges atterrissent dans Discussions, rubrique « Conversation ».
- **Contacter la vie scolaire** : message instantané vers les CPE/AED identifiés comme contacts (rubrique dédiée).
- **E-mail** et **SMS** : selon autorisations et préférences de contact.
- **Alerte PPMS** (Plan Particulier de Mise en Sûreté) : notification plein écran, mention « Exercice », trace dans Discussions, rubrique « Alerte ».

---

## 4. Discussions

**Définition officielle** : « un échange de messages entre au moins deux participants via la messagerie interne de PRONOTE ». Chaque utilisateur ayant l'option *Discussions* cochée dans sa fiche peut l'utiliser.

### Cycle de vie d'une discussion

| Action | Détail |
|--------|--------|
| **Initier** | « Nouvelle discussion » (ou bouton global en haut à droite) ; destinataires individuels ou **liste de diffusion** ; objet + contenu + pièce jointe |
| **Répondre** | Fil de messages dépliable ; réponse à une seule personne possible dans un groupe ; infobulle des participants |
| **Fenêtre flottante** | « Isoler la discussion dans une fenêtre » pour la garder visible en changeant d'affichage |
| **Transférer** | À un autre utilisateur, avec message d'accompagnement |
| **Se retirer** | Ne plus recevoir les réponses (réintégrable manuellement par l'initiateur) |
| **Clôturer** | Uniquement par l'**initiateur** : bloque toute nouvelle réponse sans effacer l'historique |
| **Signaler** | Message inapproprié au **SPR** (point d'exclamation dans sa liste) ; ou discussion entière au superviseur pour **suppression** (disparaît alors chez tous les participants) |

### Tri, archivage, nettoyage

- **Archivage** : impératif pour conserver une discussion — les discussions sont **automatiquement supprimées après un nombre de jours défini par l'administrateur**.
- **Catégories** : classer les discussions (catégories personnalisables : couleur, nom, abréviation).
- **Corbeille** : « Mettre à la corbeille » ; vidée automatiquement après **3 à 90 jours** (**45 jours par défaut**).
- **Purge** : garder uniquement les N messages les plus récents d'une discussion trop longue.

### Paramétrage et contrôle

- **Horaires** : discussions activées par défaut **de 7h à 20h** (Paramètres > Communication > Courriers/SMS/Messagerie).
- **Autorisations** : par fiche utilisateur ; **préférences de contact** dans Mes Données > Compte (choisir les classes avec qui échanger : parents, élèves, professeurs, personnels).
- **Modération** : le SPR (superviseur) peut modérer et supprimer.

### Règle d'or (logique de conception)
> Une discussion **ouvre un droit de réponse** entre tous les participants → petit comité. Pour diffuser largement **sans** engager d'échange → **Information**. Pour questionner → **Sondage**.

---

## 5. Vue d'ensemble architecturale

```
PRONOTE
├── Cahier de textes (module pédagogique)
│   ├── Contenu et ressources (cours, QCM, pièces jointes, thèmes, manuels numériques)
│   └── Travail à faire (devoirs, temps estimé, difficulté ★, rendu en ligne, "Fait")
└── Communication (messagerie interne + notifications persistantes)
    ├── Discussions (2↔n, droit de réponse, archivage, catégories, modération SPR)
    ├── Informations (1→n, sans réponse, accusé de réception, visibilité temporelle)
    ├── Sondages (questions à choix unique/multiple/libre, nominatif/anonyme)
    ├── Casier numérique (dépôt de documents, mémo, cloud, % ouverts)
    └── Canaux annexes : tchat, contact vie scolaire, e-mail, SMS, alertes PPMS
```

**Principes de conception transversaux** :
1. **Séparation stricte échange ↔ diffusion ↔ collecte** (discussion / information / casier).
2. **Tout est notifié** dans l'onglet Communication jusqu'à consultation.
3. **Droits granulaires** : chaque fonction dépend d'autorisations (fiche utilisateur, préférences de contact, paramètres d'établissement).
4. **Rétention limitée** : messagerie à durée de vie courte (suppression auto, corbeille 45 j par défaut) — l'archivage est l'exception, pas la norme.
5. **Le professeur décide de la richesse** : temps/difficulté des devoirs, thèmes, rendu en ligne — l'élève voit ces métadonnées **uniquement si elles sont saisies**.

---

## 6. Pistes de correspondance avec un système Notion (optionnel)

Si l'on veut modéliser ces structures dans Notion (ex. pour un projet type « lycée ») :

| Concept Pronote | Équivalent Notion possible |
|-----------------|----------------------------|
| Travail à faire (devoir + date + matière + difficulté) | Tâche avec `Date début & fin`, `Type` = matière, `Priorité` (★→Faible/Moyenne/Haute), case `Fait` → Statut |
| Ressources pédagogiques par matière/thème | Base « Notes » ou page projet avec fichiers joints, propriété thème |
| Discussion / Information | Distinction à préserver : canal « réponse possible » vs « lecture seule » |
| Accusé de réception | Pas d'équivalent natif Notion |

*Fin du document — analyse basée sur la documentation officielle Index Éducation.*