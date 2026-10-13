# 📋 Référence complète : page Notion « Projets en cours »

> **Objet du document** : ce fichier décrit exhaustivement la structure du workspace Notion « Projets en cours » de l'utilisateur (Billel Boulahia). Il est destiné à être fourni comme contexte à une IA à qui l'on demandera d'effectuer une action sur ce workspace (créer, modifier, interroger des projets / tâches / notes). Toutes les propriétés, options, vues, relations, templates et identifiants y figurent.

> **Date d'analyse** : 13 octobre 2026. Dernière modification de la page principale : 12 octobre 2026 à 11:59 UTC.

---

## 1. Page principale « Projets en cours »

- **URL** : https://app.notion.com/p/2b3443d61d6781abbcfeef538e3f2af5
- **ID** : `2b3443d6-1d67-81ab-bcfe-ef538e3f2af5`
- **Icône** : image personnalisée téléversée (`V1.png`)
- **Couverture** : image externe Unsplash (`photo-1579389083078-4e7018379f7e`)
- **Page racine** (aucun parent)

### 1.1 Mise en page (de haut en bas)

1. **Rangée de 3 colonnes** (ratios ≈ 40 / 45,83 / reste) — chaque colonne contient **1 bloc bouton** (3 boutons au total, en haut de page). Le contenu de ces boutons (libellé, action) n'est pas lisible via l'API.
2. **Bloc de 2 colonnes** (ratios ≈ 31,25 / 68,75) :
   - **Colonne gauche (31,25 %)** :
     - **Callout gris** contenant **3 blocs boutons** (illisibles via l'API).
     - **Base de données inline « 📝 Vue de Notes »** → affiche la base **Notes** (voir §4).
   - **Colonne droite (68,75 %)** :
     - **Base de données inline « 💡 Vue de Projet »** → affiche la base **Projet** (voir §3).
     - **Bloc onglets (tabs)** avec **5 onglets**, chacun contenant une base de données inline « Vue de Tâches » (vues filtrées de la base **Tâches**, voir §5) :
       | # | Onglet | Icône | Base inline (URL) |
       |---|-------|-------|-------------------|
       | 1 | 40 → 30/3 | 🎾 | `https://app.notion.com/p/3f7443d61d678084b204c65e2717905b` |
       | 2 | Film - Cinema | 🎥 | `https://app.notion.com/p/3f7443d61d678045bf15dd589eefc832` |
       | 3 | PitMan | 🚦 | `https://app.notion.com/p/3f7443d61d6780d6af6dd19b14bd73eb` |
       | 4 | Notion | (icône notion grise) | `https://app.notion.com/p/3f7443d61d678026a4ebe22bbad7a214` |
       | 5 | Collect Sneak | (icône chaussure) | `https://app.notion.com/p/3f7443d61d6780afb40dfe4d29ffa46e` |
3. **Bloc repliable (toggle) gris** intitulé **« Backend (ne pas modifier) »** contenant un lien vers la sous-page **« Base de données »** (voir §2).
4. **2 blocs vides** en fin de page.

> ⚠️ Les 6 blocs boutons (3 en haut + 3 dans le callout) sont des blocs Notion de type « button » : leur libellé et leur action ne sont pas exposés par l'API de lecture. Ne pas tenter de les modifier sans vérification manuelle dans Notion.

---

## 2. Section « Backend (ne pas modifier) »

> ⚠️ **Convention de l'utilisateur** : tout ce qui se trouve sous ce bloc repliable est du backend. **Ne pas modifier ni supprimer** cette zone sans instruction explicite.

- **Page « Backend (ne pas modifier) »** — ID `2b3443d6-1d67-8145-bc44-c7655f735b8f`, enfant direct de « Projets en cours ».
- **Page « Base de données »** — URL : https://app.notion.com/p/2b3443d61d67814c8eb0d4c5af631250, enfant de « Backend (ne pas modifier) ». Contient les **3 bases de données sources** du système :
  1. **Tâches** (URL base : `https://app.notion.com/p/2b3443d61d67816b847cece763c15960`)
  2. **Projet** (URL base : `https://app.notion.com/p/2b3443d61d67817d8c1cfe6bcee30174`)
  3. **Notes** (URL base : `https://app.notion.com/p/2b3443d61d6781599c2cff719682b183`)

**Architecture générale** : la page principale n'affiche que des **vues** de ces 3 bases. Toutes les données vivent dans les 3 data sources ci-dessous.

---

## 3. Base « Projet »

- **Data source** : `collection://2b3443d6-1d67-8163-aaaf-000b42f0bfef`
- **URL de la base** : https://app.notion.com/p/2b3443d61d67817d8c1cfe6bcee30174
- **Contient 7 projets**.

### 3.1 Schéma (noms EXACTS des propriétés — respecter la casse)

| Propriété | Type | Détails |
|-----------|------|---------|
| `Nom` | Titre | Nom du projet |
| `Statut` | Statut | Options : `Pas commencé` (sans couleur) · `En cours` (bleu) · `Terminé` (vert) |
| `Priorité` | Sélection | Options : `Basse` (jaune) · `Moyenne` (orange) · `Haute` (rouge) |
| `type` | Multi-sélection | ⚠️ nom en **minuscules**. Options : `Foot` (bleu), `Tennis` (orange), `Marketing` (violet), `Code` (gris), `Design` (jaune), `Cinema` (rouge), `Photo` (marron), `Dev perso` (vert), `Muscu` (rose), `Saas` (défaut), `lycée` (marron) |
| `Date de début` | Date | Format DD/MM/YYYY |
| `Date de fin` | Date | Format DD/MM/YYYY |
| `Tâches liées` | Relation | → base **Tâches** (relation inverse de « Projet lié ») |
| `Notes liées` | Relation | → base **Notes** (relation inverse de « Projet lié ») |
| `Avancement (%)` | Rollup | Agrégation `percent_per_group` sur `Tâches liées` → `Statut`. **Lecture seule** (non modifiable, non requêtable en SQL) |

- **Template de page** : 1 template (« Sans titre »).

### 3.2 Vues affichées dans « 💡 Vue de Projet » (page principale)

| Vue | Type | Propriétés affichées |
|-----|------|----------------------|
| `Projets en cours` | Galerie (petites cartes, couverture de page) | Nom, Avancement (%), Statut, type |
| `Archives` | Galerie (petites cartes, couverture de page) | Nom, Avancement (%), Statut, Date de fin |

### 3.3 Les 7 projets (état au 13/10/2026)

| Nom | Statut | Priorité | type | Début | Fin | Notes |
|-----|--------|----------|------|--------|-----|-------|
| **Saas chaussure vintage** | En cours | Basse | Code, Saas | — | — | 1 note liée ; 5 tâches liées |
| **Youtube** | En cours | Haute | — | — | — | aucune tâche/note liée |
| **Notion** | En cours | — | Code | — | — | 1 note liée ; 47 tâches liées |
| **40 → 30/3** | En cours | Moyenne | Tennis | 07/09/2026 | 30/06/2027 | 1 note liée ; 7 tâches liées |
| **Foot Designs** | En cours | Moyenne | Foot, Design | 19/09/2026 | — | 2 tâches liées |
| **PitMan** | En cours | Moyenne | Code, Saas | 18/09/2026 | — | 5 tâches liées |
| **Film - Cinema** | En cours | Moyenne | Cinema, lycée | 15/09/2026 | 31/05/2027 | 1 tâche liée |

**URL des pages projet** (nécessaires pour les relations) :

- Saas chaussure vintage : `https://app.notion.com/2b3443d61d6780138962e3e15ac3feee`
- Youtube : `https://app.notion.com/2b3443d61d67806bb7d4d62e0606667b`
- Notion : `https://app.notion.com/301443d61d6781a79d56c085c914ea72`
- 40 → 30/3 : `https://app.notion.com/3e0443d61d6780d08399ec674a93ae0f`
- Foot Designs : `https://app.notion.com/3e0443d61d6780e89cc3e96dac5eb772`
- PitMan : `https://app.notion.com/3e0443d61d6780f98e3becbb64ce4396`
- Film - Cinema : `https://app.notion.com/3e5443d61d6780fdb653c4252797c81b`

---

## 4. Base « Notes »

- **Data source** : `collection://2b3443d6-1d67-8180-8af8-000b5bc011f9`
- **URL de la base** : https://app.notion.com/p/2b3443d61d6781599c2cff719682b183
- **Contient 4 notes**.

### 4.1 Schéma

| Propriété | Type | Détails |
|-----------|------|---------|
| `Name` | Titre | ⚠️ nom anglais, pas « Nom » |
| `Action` | Sélection | Options : `À traiter` (rose) · `Traité` (vert) |
| `Date de création` | Date | Format DD/MM/YYYY |
| `Projet lié` | Relation | → base **Projet** |

- **Templates de page** : 4 (« Sans titre »).

### 4.2 Vue affichée dans « 📝 Vue de Notes » (page principale)

| Vue | Type | Propriétés affichées |
|-----|------|----------------------|
| `Table` | Liste | Name, Action |

### 4.3 Les 4 notes

| Name | Action | Date de création | Projet lié | URL |
|------|--------|------------------|------------|-----|
| Moodboard | Traité | 25/11/2025 | — | `https://app.notion.com/2b6443d61d678015ae88d3c76d76137f` |
| Choses à faire avant la production | Traité | 28/01/2026 | Saas chaussure vintage | `https://app.notion.com/2f6443d61d6780b39f4fd2a41e0f9dca` |
| prompt | À traiter | — | Notion | `https://app.notion.com/3ec443d61d678054b28cde28f4f1f25c` |
| Zone de performance | — | — | 40 → 30/3 | `https://app.notion.com/3f5443d61d6780d9aa3be53082265f73` |

---

## 5. Base « Tâches »

- **Data source** : `collection://2b3443d6-1d67-81c5-809c-000b67ecd179`
- **URL de la base** : https://app.notion.com/p/2b3443d61d67816b847cece763c15960
- **Contient 73 tâches**.

### 5.1 Schéma

| Propriété | Type | Détails |
|-----------|------|---------|
| `Nom` | Titre | |
| `Statut` | Statut | Options : `Pas commencé` (sans couleur) · `En cours` (bleu) · `Terminé` (vert) |
| `Priorité` | Sélection | ⚠️ Options : `Haute` (rouge) · `Moyenne` (orange) · `Faible` (jaune). **Différent de la base Projet** (« Basse » ici = « Faible » là) |
| `Type` | Multi-sélection | Options : `Apprentissage` (orange), `Code` (gris), `Création` (rose), `Design` (marron), `Developpement` (rouge, sans accent), `Entraînement` (défaut), `Marketing` (jaune), `Match` (violet), `Montage` (marron), `Prospection` (vert), `Recherche` (bleu), `Tournage` (violet) |
| `Date début & fin` | Date | Format DD/MM/YYYY ; plage (début ET fin possibles) |
| `Note` | Texte | |
| `Projet lié` | Relation | → base **Projet** |
| `Parent item` | Relation (auto, limite 1) | → tâche parente |
| `Sub-item` | Relation (auto) | → sous-tâches |
| `DATE DEBUT` | Formule | Cachée sur les pages ; calculée (non requêtable en SQL) |
| `DATE FIN` | Formule | Cachée ; calculée |
| `Retard` | Formule | Cachée ; calculée (retard de la tâche) |

- **Templates de page** : 3 — « Nouvelle Tâche », « Entraînements Tennis », « Match ».
- **Mise en page des pages tâche** : couverture + titre + propriétés (Statut, Priorité, Projet lié, Type, Date début & fin, Note, Parent item, Sub-item visibles ; DATE DEBUT, DATE FIN, Retard masquées) + commentaires + contenu. Page en pleine largeur.

### 5.2 Vues par onglets (page principale)

Chaque onglet est une vue **Table** de la base Tâches, filtrée sur `Projet lié` (relation contient), affichant : Nom, Projet lié, Statut, Priorité, Type, Date début & fin, Note, Retard — sous-tâches affichées, périmètre `parents_and_subitems`.

| Onglet | Vue | Filtre (Projet lié =) | URL du projet filtré |
|--------|-----|------------------------|----------------------|
| 40 → 30/3 | `Table` | 40 → 30/3 | `https://app.notion.com/3e0443d61d6780d08399ec674a93ae0f` |
| Film - Cinema | ⚠️ nommée `40 -> 30/3` | Film - Cinema | `https://app.notion.com/3e5443d61d6780fdb653c4252797c81b` |
| PitMan | `PitMan` | PitMan | `https://app.notion.com/3e0443d61d6780f98e3becbb64ce4396` |
| Notion | `Notion` | Notion | `https://app.notion.com/301443d61d6781a79d56c085c914ea72` |
| Collect Sneak | `Collect Sneak` | ⚠️ **Saas chaussure vintage** (pas un projet « Collect Sneak ») | `https://app.notion.com/2b3443d61d6780138962e3e15ac3feee` |

### 5.3 Contenu des 73 tâches (répartition par projet)

**Projets principaux :**

- **Saas chaussure vintage (5 tâches)** — « Création de la charte graphique » (parent) et ses 4 sous-tâches : Création du logo, Choix de la typographie, Choix des couleurs, Création de la charte. Toutes **Terminé** (22/11/2025).
- **Notion (47 tâches)** — créées automatiquement le 08/02/2026 par un outil d'import GitHub→Notion (« GitNote »). Structure hiérarchique :
  - **11 tâches « branche »** (préfixées `🌿`) :
    - 3 branches racines avec commits enfants : 🌿 Notion - Création de liens entre projets et tâches dans Notion (25 commits enfants), 🌿 Notion - Intégration de GitHub à Notion avec IA (10 commits enfants), 🌿 Notion - Import GitHub vers Notion complet (1 commit enfant) ;
    - 8 branches sans enfant : fix/import-re-module, fix/notion-api-task-link, fix/notion-parent-database-id, fix/schema-matching, fix/typo-status-termine, main, refactor/single-base-parent-subitems, Optimisation de la création de projets ;
  - **36 tâches « commit »** nommées `... [SHA:xxxxxxx]`.
  - Les 47 tâches sont toutes **Terminé**.
- **40 → 30/3 (7 tâches)** — entraînements tennis :
  - Entrainement: Mercredi 08 Octobre — **Terminé** (Haute, 07/10/2026)
  - Match: Giulian 11/10 — **Terminé** (Haute, 11/10/2026)
  - Entraînements: Lundi 12 Octobre — **En cours** (Moyenne, 08/10/2026)
  - Entraînements: Renforcer la structure et les tendons 1 — Pas commencé (Moyenne, 08/10/2026)
  - Entraînements: La transition (Accumulation élastique) 3 — Pas commencé (Moyenne, 08/10/2026)
  - Entraînements: Stocker l'Impact (Travail Excentrique) 2 — Pas commencé (Moyenne, 08/10/2026)
  - Entraînements: L'explosivité pure (Pliométrie haute intensité) 4 — Pas commencé (Moyenne, 08/10/2026)
- **Foot Designs (2 tâches)** — Recherche de design pour le foot (Terminé), Création du premier design (Terminé).
- **PitMan (5 tâches)** — Préparation de l'environnement de dévellopement (Terminé, parent de 2 sous-tâches : Régler Problèmes Antigravity, Préparation des languages et frameworks — toutes Terminé), Dictionnaire de phrases pour le moteur de règles (Story 1.3) — **En cours**, Correction Story 1.2: structures blittables AC1 (Provider & Simulator) — Terminé.
- **Film - Cinema (1 tâche)** — Création du moodboard — **En cours** (08/09/2026 → 13/10/2026).

**Tâches sans projet lié (6, ⚠️ orphelines) :**

- Création du moodboard (Terminé, 02–03/12/2025)
- Tournage (Terminé, 07/12/2025)
- Montage (Terminé, 08–12/12/2025)
- 🌿 Porsche - Migration vers Vue et corrections (**En cours**) + 2 sous-tâches : Migration vers vue et quelques correctifs [SHA:57670d0] (Terminé), Deployement du code sur github [SHA:edfc72f] (Terminé)

**Statistiques exactes (vérifiées)** : 73 tâches au total — **65 Terminé**, **4 En cours**, **4 Pas commencé**.
- Les 4 « En cours » : 🌿 Porsche - Migration vers Vue et corrections (orpheline), Création du moodboard (Film - Cinema), Dictionnaire de phrases pour le moteur de règles / Story 1.3 (PitMan), Entraînements: Lundi 12 Octobre (40 → 30/3).
- Les 4 « Pas commencé » : les 4 entraînements de tennis restants de 40 → 30/3 (Renforcer la structure 1, La transition 3, Stocker l'Impact 2, L'explosivité pure 4).

---

## 6. Relations entre les 3 bases

```
PROJET (7) ──┬── Tâches liées ──→ TÂCHES (73)
             └── Notes liées ──→ NOTES (4)

TÂCHES ──┬── Projet lié ──→ PROJET
         ├── Parent item ──→ TÂCHES (auto-relation, max 1 parent)
         └── Sub-item ──→ TÂCHES (auto-relation)

NOTES ────── Projet lié ──→ PROJET
```

- « Avancement (%) » du Projet = rollup du Statut des Tâches liées (pourcentage du groupe « Terminé »).
- Créer une tâche dans un projet ⇒ renseigner `Projet lié` avec l'URL de la page projet (liste en §3.3). La relation inverse se remplit automatiquement.
- Les onglets de la page principale filtrent par `Projet lié` : une tâche correctement liée apparaîtra automatiquement dans l'onglet correspondant.

---

## 7. Décomptes et incohérences constatées (important pour une IA)

1. **Total** : 7 projets, 73 tâches, 4 notes. Toutes les tâches liées au projet Notion (47) sont « Terminé ».
2. **Priorité incohérente entre bases** : Projet utilise `Basse/Moyenne/Haute` ; Tâches utilise `Faible/Moyenne/Haute`. Ne pas confondre lors d'une création.
3. **Nom de vue erroné** : l'onglet « Film - Cinema » contient une vue nommée « 40 -> 30/3 » (copie d'un autre onglet, filtre correct cependant).
4. **Onglet « Collect Sneak »** : filtre sur le projet « Saas chaussure vintage » — le nom de l'onglet ne correspond à aucun nom de projet.
5. **6 tâches orphelines** sans `Projet lié` (3 de décembre 2025 + 3 « Porsche » de février 2026, dont la branche parente est « En cours »).
6. **Projet « Youtube »** : priorité Haute mais aucune tâche ni note liée.
7. **Vue « Archives » sans filtre** : la vue « Archives » de la base Projet n'applique aucun filtre — elle affiche actuellement les 7 projets (tous « En cours »), donc elle duplique la vue principale.
8. Les propriétés formules `DATE DEBUT`, `DATE FIN`, `Retard` ne sont pas éditables (calculées) ni disponibles en SQL.
9. Le projet « Notion » regroupe l'historique GitHub importé automatiquement (GitNote) : les noms de tâches contiennent `[SHA:…]` et `🌿` pour les branches — conventions à respecter si l'on ajoute des tâches issues de GitHub.
10. **Vérification croisée (2ᵉ itération, mode vues)** : les 5 onglets + tâches non affichées en onglet couvrent bien 73 tâches : 67 liées (40→30/3 : 7 · Film - Cinema : 1 · PitMan : 5 · Notion : 47 · Saas chaussure vintage : 5 · Foot Designs : 2 — ce dernier projet n'a pas d'onglet dédié) + 6 orphelines. Décompte par statut confirmé : **65 Terminé · 4 En cours · 4 Pas commencé**. Notes : 2 Traitées · 1 À traiter · 1 sans action.

---

## 8. Guide d'action pour une IA intervenant sur ce workspace

- **Créer une tâche** : data source `collection://2b3443d6-1d67-81c5-809c-000b67ecd179` ; renseigner `Nom` (titre), `Statut` (`Pas commencé`/`En cours`/`Terminé`), `Priorité` (`Haute`/`Moyenne`/`Faible`), `Type` (multi-select), `Date début & fin` (JJ/MM/AAAA), `Projet lié` (URL page projet). Optionnel : `Note`, `Parent item`.
- **Créer un projet** : data source `collection://2b3443d6-1d67-8163-aaaf-000b42f0bfef` ; propriété type = `type` (minuscules), options listées §3.1.
- **Créer une note** : data source `collection://2b3443d6-1d67-8180-8af8-000b5bc011f9` ; titre = `Name`, `Action` = `À traiter`/`Traité`.
- **Dates** : format d'affichage DD/MM/YYYY ; en API, ISO 8601.
- **Ne jamais modifier** : le bloc « Backend (ne pas modifier) », la page « Base de données », les propriétés formules, le rollup `Avancement (%)`.
- **Statuts en français** : toujours les valeurs exactes `Pas commencé`, `En cours`, `Terminé` (accentué).
- Pour ajouter un nouvel onglet projet sur la page principale, reproduire le motif existant : base inline « Vue de Tâches » avec vue Table filtrée `Projet lié relation_contains <URL projet>`.

*Fin du document — généré à partir d'une analyse API complète de la page Notion.*