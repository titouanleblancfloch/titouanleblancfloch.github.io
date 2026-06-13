# Rapport de projet — Bibliométrie LIAS

**Projet :** Analyse bibliométrique d'un laboratoire de recherche à partir de données ouvertes
**Cadre :** SAE BUT2 Science des Données — IUT Poitiers-Niort — Année 2025–2026
**Laboratoire étudié :** LIAS (Laboratoire d'Informatique et d'Automatique pour les Systèmes)
**Rédigé par :** Membre 3 (Frontend Developer)

---

## Table des matières

1. [Présentation générale du projet](#1-présentation-générale-du-projet)
2. [Périmètre et enjeux stratégiques](#2-périmètre-et-enjeux-stratégiques)
3. [Sources de données](#3-sources-de-données)
4. [Indicateurs bibliométriques à produire](#4-indicateurs-bibliométriques-à-produire)
5. [Architecture applicative](#5-architecture-applicative)
6. [Structure des fichiers et dossiers](#6-structure-des-fichiers-et-dossiers)
7. [Répartition des tâches par membre](#7-répartition-des-tâches-par-membre)
8. [Mon rôle — Membre 3 : Frontend & Enrichissement qualité](#8-mon-rôle--membre-3--frontend--enrichissement-qualité)
9. [Questions d'analyse stratégique](#9-questions-danalyse-stratégique)
10. [Livrables attendus](#10-livrables-attendus)
11. [Critères d'évaluation](#11-critères-dévaluation)
12. [Planning et points de synchronisation](#12-planning-et-points-de-synchronisation)
13. [Limites et biais connus](#13-limites-et-biais-connus)
14. [Fichiers clés à consulter](#14-fichiers-clés-à-consulter)

---

## 1. Présentation générale du projet

### 1.1 Contexte académique

Ce projet est une SAE (Situation d'Apprentissage et d'Évaluation) du BUT2 Science des Données de l'IUT de Poitiers-Niort. Il s'inscrit dans la ressource "Développement d'un composant d'une solution décisionnelle" et mobilise l'intégralité de la chaîne de valeur d'un projet data : collecte, nettoyage, enrichissement, modélisation, développement applicatif et analyse critique.

### 1.2 Objet de l'étude

Le laboratoire **LIAS** (Laboratoire d'Informatique et d'Automatique pour les Systèmes) est une unité de recherche rattachée à l'Université de Poitiers et à l'ISAE-ENSMA. Il regroupe **41 chercheurs permanents** répartis en trois équipes :

| Équipe | Effectif | Thématiques |
|--------|----------|-------------|
| **IDD** (Data Engineering) | **11** | Bases de données, Web sémantique, IA explicable, Big Data |
| **SETR** (Systèmes Temps Réel) | **8** | Ordonnancement temps réel, réseaux embarqués, avionique |
| A&S (Automatique & Systèmes) | 22 | Commande, identification, systèmes fractionnaires, diagnostic |

**Périmètre du projet :** uniquement les équipes **IDD et SETR** (19 chercheurs permanents), sur la période **janvier 2021 – décembre 2025**. L'équipe A&S est hors périmètre car ses publications relèvent de domaines peu couverts par DBLP.

### 1.3 Ce que produit le projet

L'équipe développe une **application web complète** composée de :
- Un **backend API REST** (FastAPI) qui expose toutes les données et calcule tous les indicateurs
- Un **dashboard interactif** (Streamlit) qui consomme l'API et permet des simulations en temps réel
- Une **infrastructure Docker** permettant de lancer l'ensemble en une seule commande

Le tout est accompagné d'une **note de synthèse** de 2–3 pages répondant aux questions stratégiques de la direction du LIAS.

---

## 2. Périmètre et enjeux stratégiques

### 2.1 Enjeu principal : la fusion IDD + SETR

La direction du LIAS envisage de **fusionner les équipes IDD et SETR** en une seule entité de 19 membres. Ce projet place les étudiants dans un rôle de data analyst au service de cette décision stratégique. Les questions auxquelles il faut répondre avec des données sont :

- La fusion est-elle **équilibrée** en termes de productivité et de thématiques ?
- Y a-t-il déjà des **collaborations** entre IDD et SETR qui faciliteraient la fusion ?
- Existe-t-il un risque que SETR soit "absorbée" plutôt que réellement intégrée ?

### 2.2 Enjeu complémentaire : simulation d'impact

Au-delà de la fusion, la direction souhaite un **outil de simulation** pour évaluer l'impact de :
- La **marginalisation** d'un chercheur clé (réduction de sa production de 50%, 75% ou 100%)
- Le **transfert** d'un chercheur d'une équipe vers l'autre
- L'**effet de lest** : que se passe-t-il si on retire les membres inactifs du calcul ?

Certains membres ont un poids disproportionné dans la production scientifique ("locomotives"). Leur marginalisation dans une nouvelle organisation pourrait fragiliser une équipe entière.

### 2.3 Contrainte temporelle stricte

**Toute publication ou indicateur doit concerner exclusivement la période janvier 2021 – décembre 2025.** Les publications antérieures ou postérieures sont exclues.

---

## 3. Sources de données

### 3.1 DBLP — Source principale

**DBLP** (`dblp.org`) est la principale base bibliographique en informatique. C'est la source principale du projet pour IDD et SETR.

**API disponibles (format XML) :**
```
Recherche d'auteur :  GET /search/author/api?q={nom}&format=xml
Publications par PID: GET /pid/{id}.xml  ← méthode recommandée (évite les homonymes)
```

**Filtrage requis :**
- **Garder** : `article` (journaux peer-reviewed), `inproceedings` (conférences peer-reviewed)
- **Exclure** : `editorship` (éditoriaux), `informal`/`CoRR` (prépublications arXiv), `books`, `incollection`

**Problème des homonymes :** DBLP attribue des PIDs uniques (ex: `b/LadjelBellatreche`). La désambiguation par PID est indispensable, notamment pour des noms courants (ex: Patrick Girard → 6 chercheurs différents sur DBLP).

**Rate-limiting :** attendre 2–3 secondes entre chaque requête. Stocker les réponses en cache local (`data/cache/dblp/`).

### 3.2 Theses.fr — Thèses de doctorat

Base nationale des thèses de doctorat françaises. Permet d'identifier les thèses dirigées ou co-dirigées par chaque chercheur (soutenues entre 2021–2025 et en cours).

```
GET https://www.theses.fr/api/v1/theses/?q=directeur:{nom}&periode=2021-2025
```

### 3.3 CORE Rankings — Qualité des conférences

Le portail **CORE** (`portal.core.edu.au`) classe les conférences en informatique selon ce barème :

| Rang | Libellé | Description |
|------|---------|-------------|
| **A\*** | Flagship | Conférence phare, très sélective (top ~5% des soumissions) |
| **A** | Excellent | Très haut niveau, large reconnaissance internationale |
| **B** | Good | Bonne conférence, visibilité significative |
| **C** | Other | Conférence reconnue, portée plus limitée |
| NC | — | Conférence absente du référentiel CORE |

Le portail ne propose **pas d'export CSV**. Les rangs doivent être récupérés manuellement ou par scraping. Stratégie : extraire les acronymes des conférences depuis DBLP (balise `<booktitle>`), puis chercher chaque acronyme sur le portail CORE.

### 3.4 SCImago — Qualité des journaux

**SCImago** (`scimagojr.com`) classe les revues scientifiques par quartiles (Q1–Q4) en se basant sur les données Scopus :

| Quartile | Signification |
|----------|--------------|
| **Q1** | Top 25% — les meilleures revues du domaine |
| **Q2** | 25–50% — revues de bon niveau |
| **Q3** | 50–75% — niveau intermédiaire |
| **Q4** | 75–100% — visibilité plus faible |
| NC | — | Journal absent de Scopus / SCImago |

Le fichier complet (~30 000 journaux) est téléchargeable en CSV/Excel :
```
https://www.scimagojr.com/journalrank.php?out=xls
```

### 3.5 Sources hors périmètre (pour extension A&S)

HAL, Scopus, IEEE Xplore et OpenAlex seraient nécessaires pour une extension à l'équipe A&S, mais **ne sont pas dans le périmètre actuel**.

---

## 4. Indicateurs bibliométriques à produire

### 4.1 Indicateurs de volume

| Indicateur | Définition | Granularité |
|-----------|-----------|-------------|
| Nombre total de publications | Journaux + Conférences peer-reviewed | Équipe, membre, an |
| Productivité par membre | Total / nombre de permanents | Par équipe |
| Productivité par membre actif | Total / membres avec ≥1 publication | Par équipe |
| Taux de membres actifs | % membres avec ≥1 publication | Par équipe |
| Ratio journaux / conférences | Proportion d'articles de journaux | Équipe, membre |
| Évolution annuelle | Tendance 2021 → 2025 | Par équipe |

### 4.2 Indicateurs de qualité et d'impact

| Indicateur | Définition | Source |
|-----------|-----------|--------|
| Rang CORE | Distribution A*, A, B, C, NC | CORE |
| Quartile SCImago | Distribution Q1–Q4, NC. % de Q1 | SCImago |
| Score qualité pondéré | A\*=4, A=3, B=2, C=1, NC=0 (conf.) ; Q1=4, Q2=3, Q3=2, Q4=1 (journaux) | CORE + SCImago |
| Top venues | Publications dans A\*/A ou Q1/Q2 | CORE + SCImago |
| Diversité des venues | Indice de Shannon sur les venues | DBLP |
| SJR moyen | Moyenne du SCImago Journal Rank des revues | SCImago |

### 4.3 Indicateurs de collaboration

| Indicateur | Définition |
|-----------|-----------|
| Collaborations intra-équipe | Co-publications entre membres de la même équipe |
| Collaborations inter-équipes | Co-publications entre membres d'équipes différentes |
| Taux d'ouverture | % publications avec au moins un co-auteur externe au LIAS |
| Graphe de collaboration | Réseau de co-publications (nœuds = chercheurs, arêtes = co-publications) |

### 4.4 Indicateurs doctoraux

| Indicateur | Définition | Source |
|-----------|-----------|--------|
| Thèses soutenues | Nombre par équipe (2021–2025) | theses.fr |
| Thèses en cours | Nombre par équipe | theses.fr |
| Taux d'encadrement | Nombre de HDR/PR encadrant ≥1 thèse | Croisement |
| Co-publications doctorant/directeur | Publications issues de travaux de thèse | DBLP + theses.fr |

### 4.5 Indicateurs d'importance individuelle et de risque

**Impact positif — chercheurs clés :**

| Indicateur | Définition | Usage |
|-----------|-----------|-------|
| Part de production (%) | Publications du membre / Total équipe. >30% = risque | Dépendance |
| Score qualité individuel | Score CORE/SCImago vs. moyenne de l'équipe | Impact qualitatif |
| Indice de centralité | Betweenness centrality dans le graphe de co-publication | Rôle structurant |
| Impact simulé de la marginalisation | Recalcul des indicateurs avec réduction de −50% ou −100% | Simulation |
| Impact simulé du transfert | Déplacement d'un membre : recalcul pour les deux équipes | Simulation |

**Impact négatif — membres peu impliqués :**

| Indicateur | Définition |
|-----------|-----------|
| Statut d'activité | Actif (≥3 publis), Peu actif (1–2), Inactif (0) |
| Impact sur la productivité | Écart entre productivité par membre (avec inactifs) et par membre actif |
| Effet de lest | Recalcul des indicateurs en excluant les membres inactifs |
| Indice de Gini | Mesure d'inégalité de production (proche de 1 = très concentrée) |

---

## 5. Architecture applicative

### 5.1 Vue d'ensemble

L'application est une architecture **microservices à deux couches** orchestrée par Docker Compose :

```
┌─────────────────────────────────────────────────┐
│                Docker Compose                    │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │   API FastAPI   │◄───│ Dashboard Streamlit  │ │
│  │   Port 8000     │    │   Port 8501          │ │
│  │                 │    │                      │ │
│  │ /docs (Swagger) │    │ 5 pages interactives │ │
│  └────────┬────────┘    └──────────────────────┘ │
│           │                                       │
│           ▼                                       │
│  ┌─────────────────┐                             │
│  │  data/ (volume) │                             │
│  │  membres.csv    │                             │
│  │  consolidated   │                             │
│  │  core_ranks.csv │                             │
│  │  scimago.csv    │                             │
│  └─────────────────┘                             │
└─────────────────────────────────────────────────┘
```

**Règle fondamentale :** toute la logique métier (calculs, indicateurs, simulation) est dans l'API. Streamlit ne fait que consommer l'API via des requêtes HTTP.

### 5.2 Backend FastAPI

**Endpoints attendus :**

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/membres` | GET | Liste des membres (filtre par équipe, statut) |
| `/api/membres/{id}` | GET | Fiche complète d'un membre |
| `/api/publications` | GET | Publications avec filtres multicritères |
| `/api/equipes/{id}/indicateurs` | GET | Indicateurs calculés d'une équipe |
| `/api/equipes/comparaison` | GET | IDD vs SETR en parallèle |
| `/api/simulation/marginalisation` | POST | Simule la réduction de production d'un/plusieurs membres |
| `/api/simulation/transfert` | POST | Simule le déplacement d'un membre vers une autre équipe |
| `/api/collaboration/graphe` | GET | Graphe de co-publications en JSON |

**Modèles Pydantic :**
- `Membre` / `MembreDetail`
- `Publication`
- `IndicateursEquipe`
- `SimulationRequest` / `SimulationResult`
- `GrapheCollaboration` (nodes + edges)

### 5.3 Frontend Streamlit (5 pages)

| Page | Fichier | Contenu principal |
|------|---------|------------------|
| 1 — Vue d'ensemble | `1_vue_ensemble.py` | KPIs globaux, évolution temporelle 2021–2025, répartition par équipe |
| 2 — Comparaison IDD vs SETR | `2_comparaison.py` | Graphiques côte à côte, distribution CORE/SCImago |
| 3 — Fiche chercheur | `3_fiche_chercheur.py` | Profil individuel, publications, co-auteurs fréquents |
| 4 — Graphe collaboration | `4_collaboration.py` | Réseau interactif PyVis, filtres par équipe, betweenness centrality |
| 5 — Simulation | `5_simulation.py` | **OBLIGATOIRE** — marginalisation et transfert avec affichage des deltas |

### 5.4 Module de simulation (livrable obligatoire)

**Scénario 1 — Marginalisation :**
- L'utilisateur sélectionne un ou plusieurs membres et un taux de réduction (−25%, −50%, −75%, −100%)
- L'API recalcule tous les indicateurs de l'équipe
- Streamlit affiche les deltas avec `st.metric` (valeurs rouge/vert)
- Alerte si un indicateur passe sous un seuil critique

**Scénario 2 — Transfert :**
- L'utilisateur sélectionne un membre et une équipe de destination
- L'API recalcule les indicateurs des deux équipes simultanément
- Streamlit affiche côte à côte : équipe source (avant/après) et équipe d'accueil (avant/après)

**Exemples de questions auxquelles le module répond :**
- Si Ladjel Bellatreche est marginalisé dans IDD (−50%), quel est l'impact sur la productivité de l'équipe ?
- Si on transfère un membre de SETR vers IDD, l'équipe fusionnée est-elle plus équilibrée ?
- Quels sont les 3 chercheurs dont la marginalisation aurait le plus fort impact négatif ?

### 5.5 Infrastructure Docker

```yaml
# docker-compose.yml (simplifié)
services:
  api:
    build: ./api
    ports: ["8000:8000"]
    volumes: ["./data:/app/data"]
    environment: ["DATA_PATH=/app/data"]

  dashboard:
    build: ./dashboard
    ports: ["8501:8501"]
    volumes: ["./data:/app/data"]
    environment: ["API_URL=http://api:8000"]
    depends_on: [api]
```

Lancement en une commande : `docker compose up --build`

---

## 6. Structure des fichiers et dossiers

### 6.1 Structure actuelle du projet (après réorganisation)

```
Mesmoud/
├── CLAUDE.md                          # Instructions pour Claude Code (ce projet)
├── rapport_projet.md                  # Ce fichier
├── docs/                              # Documents PDF de référence
│   ├── Projet_Bibliometrie_LIAS_BUT2SD.pdf    # Sujet complet (21 pages)
│   └── Repartition_Taches_Bibliometrie_LIAS.pdf  # Répartition des tâches (13 pages)
└── projet/                            # Dossier racine de l'application
    ├── docker-compose.yml             # Orchestration Docker (fourni)
    ├── api/                           # Service FastAPI
    │   ├── Dockerfile                 # (fourni)
    │   ├── requirements.txt           # fastapi, uvicorn, pandas, openpyxl, networkx, pydantic
    │   ├── models/                    # (vide — à créer par M2)
    │   ├── routers/                   # (vide — à créer par M2)
    │   └── services/                  # (vide — à créer par M2)
    ├── dashboard/                     # Service Streamlit
    │   ├── Dockerfile                 # (fourni)
    │   ├── requirements.txt           # streamlit, requests, pandas, plotly, pyvis
    │   └── pages/                     # (vide — à créer par M3)
    ├── data/                          # Volume Docker partagé
    │   ├── membres.csv                # Template (à remplir par M1 — 19 membres)
    │   ├── overrides.csv              # Template (à remplir par M1 — corrections manuelles)
    │   ├── cache/dblp/                # (vide — cache XML DBLP)
    │   └── output/chercheurs/         # (vide — fichiers .xlsx par chercheur)
    ├── notebooks/                     # (vide — Jupyter pour M4)
    └── scripts/                       # (vide — pipeline de collecte)
```

### 6.2 Structure cible complète (à atteindre)

```
donnees a disposition/
├── docker-compose.yml
├── .env
├── .gitignore
├── README.md
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                        # Point d'entrée FastAPI
│   ├── models/
│   │   ├── membre.py
│   │   ├── publication.py
│   │   ├── equipe.py
│   │   └── simulation.py
│   ├── routers/
│   │   ├── membres.py
│   │   ├── publications.py
│   │   ├── equipes.py
│   │   ├── simulation.py
│   │   └── collaboration.py
│   └── services/
│       ├── data_loader.py
│       ├── indicators.py
│       ├── collaboration.py
│       └── simulation.py
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                         # Navigation multi-pages
│   ├── api_client.py                  # Client HTTP vers FastAPI
│   └── pages/
│       ├── 1_vue_ensemble.py
│       ├── 2_comparaison.py
│       ├── 3_fiche_chercheur.py
│       ├── 4_collaboration.py
│       └── 5_simulation.py            # OBLIGATOIRE
├── scripts/
│   ├── 01_collect_dblp.py             # M1 — Collecte via API DBLP
│   ├── 02_parse_dblp.py               # M1 — Parsing XML
│   ├── 03_collect_theses.py           # M1 — Collecte theses.fr
│   ├── 04_enrich_core.py              # M3 — Enrichissement CORE Rankings
│   ├── 05_enrich_scimago.py           # M3 — Enrichissement SCImago
│   ├── 06_generate_excel.py           # M1 — Génération fichiers Excel
│   └── utils.py
├── notebooks/
│   └── exploration.ipynb              # M4 — Analyse et projections
└── data/
    ├── membres.csv                    # M1 — 19 membres avec PIDs DBLP validés
    ├── overrides.csv                  # M1 — corrections manuelles
    ├── core_ranks.csv                 # M3 — table conférence→rang CORE
    ├── scimago.csv                    # M3 — référentiel SCImago complet (~30k journaux)
    ├── cache/
    │   └── dblp/                      # Cache XML par chercheur ({pid}.xml)
    └── output/
        ├── chercheurs/                # 19 fichiers .xlsx individuels
        └── consolidated.xlsx          # Fichier consolidé toutes publications
```

---

## 7. Répartition des tâches par membre

### Membre 1 — Data Engineer (Collecte & Fiabilisation des données)

**Rôle :** garant de la qualité des données — prérequis absolu pour les 3 autres membres.

**Tâches principales :**
1. **Identification des membres** — scraping de `lias-lab.fr/members/`, extraction des 19 membres IDD et SETR avec leurs grades et emails
2. **Désambiguation DBLP** — recherche et validation des PIDs DBLP pour chacun des 19 membres. Gestion des homonymes (ex: Patrick Girard → 6 profils DBLP distincts)
3. **Collecte DBLP** — script `01_collect_dblp.py` avec cache local, `02_parse_dblp.py` pour parser le XML et filtrer par type et période
4. **Collecte theses.fr** — script `03_collect_theses.py` pour les thèses dirigées ou co-dirigées
5. **Génération Excel** — `06_generate_excel.py` : 19 fichiers `.xlsx` individuels (5 onglets : Journaux, Conférences, Thèses, Résumé, Métadonnées) + `consolidated.xlsx`

**Livrables :**
- `data/membres.csv` (19 membres, PIDs DBLP validés)
- `data/overrides.csv` (corrections manuelles justifiées)
- 19 fichiers `.xlsx` dans `data/output/chercheurs/`
- `data/output/consolidated.xlsx`

### Membre 2 — Backend Developer (API FastAPI & Moteur de calcul)

**Rôle :** construit le cerveau de l'application — toute la logique métier est dans l'API.

**Tâches principales :**
1. **Modèles Pydantic** — `Membre`, `MembreDetail`, `Publication`, `IndicateursEquipe`, `SimulationRequest`, `SimulationResult`, `GrapheCollaboration`
2. **Service data loader** — chargement des fichiers Excel au démarrage de l'API, mise en cache mémoire
3. **Endpoints REST** — membres, publications, indicateurs d'équipe, comparaison
4. **Service calcul indicateurs** — toutes les fonctions de calcul (volume, qualité, Gini, etc.)
5. **Moteur de simulation** — `POST /api/simulation/marginalisation` et `POST /api/simulation/transfert`
6. **Graphe de collaboration** — construction NetworkX, calcul betweenness centrality, sérialisation JSON

**Livrables :**
- `api/` complet (models/, routers/, services/)
- API démarrée sur port 8000 avec documentation Swagger sur `/docs`
- Module de simulation fonctionnel (tests sur Ladjel Bellatreche)

### Membre 3 — Frontend Developer (Streamlit & Enrichissement qualité) — **MOI**

**Rôle :** double mission — enrichissement qualitatif des données + interface utilisateur complète.

**Tâches principales :**
1. **Enrichissement CORE** — extraire les conférences des Excel M1, normaliser les acronymes, scraper/consulter le portail CORE, produire `core_ranks.csv`, remplir la colonne `rang_core` dans les Excel
2. **Enrichissement SCImago** — télécharger le CSV SCImago, jointure fuzzy avec les journaux DBLP, remplir `quartile_scimago` et `sjr_score`
3. **Client API** — `api_client.py` : wrapper Python sur tous les endpoints FastAPI
4. **Dashboard 5 pages** — `app.py` + 5 pages Streamlit complètes
5. **Module de simulation (obligatoire)** — page 5 avec scénarios marginalisation et transfert

**Livrables :**
- `data/core_ranks.csv`
- `data/scimago.csv` (téléchargé et nettoyé)
- Colonnes `rang_core`, `quartile_scimago`, `sjr_score` remplies dans tous les Excel
- Dashboard Streamlit (5 pages) sur port 8501
- Module de simulation opérationnel (scénarios marginalisation ET transfert)

### Membre 4 — Data Analyst (Analyse stratégique & Infrastructure Docker)

**Rôle :** infrastructure de déploiement + analyse stratégique + note de synthèse.

**Tâches principales :**
1. **Docker** — Dockerfiles optimisés, `docker-compose.yml` avec health checks, `.env`, `.gitignore`, `.dockerignore`
2. **Git** — initialisation dépôt, convention de commits, branches par membre, coordination
3. **README.md** — documentation exhaustive pour lancement par un tiers
4. **Analyse stratégique** — réponses chiffrées aux questions 6.1 à 6.5 du sujet
5. **Projection 2026–2030** — notebook avec 3 scénarios (tendanciel, optimiste, pessimiste)
6. **Note de synthèse** — 2–3 pages PDF répondant aux 5 questions stratégiques

**Livrables :**
- `docker-compose.yml` fonctionnel (lancement en une commande)
- `README.md` exhaustif
- `notebooks/exploration.ipynb` avec projections documentées
- `note_synthese.pdf` (2–3 pages)

---

## 8. Mon rôle — Membre 3 : Frontend & Enrichissement qualité

### 8.1 Enrichissement CORE Rankings

**Étape 1 — Extraction des conférences depuis les fichiers Excel M1 :**
- Lire tous les fichiers Excel produits par M1
- Extraire la liste des `booktitle` (noms de conférences) uniques
- Normaliser : extraire l'acronyme (ex: "Proceedings of VLDB 2023" → "VLDB")
- Obtenir ~50–100 conférences triées par fréquence d'apparition

**Étape 2 — Recherche sur le portail CORE :**
- Pour chaque conférence : rechercher sur `https://portal.core.edu.au/conf-ranks/?search=ACRONYME&source=CORE2023`
- Récupérer le rang : A*, A, B, C ou "Non classé"
- Option automatisée : `requests` + `BeautifulSoup` pour le scraping
- Option manuelle pour les conférences fréquentes

**Étape 3 — Enrichissement des Excel :**
- Jointure entre les données M1 et `core_ranks.csv`
- Remplir la colonne `rang_core` dans chaque fichier Excel
- Documenter les cas non trouvés ("NC" + justification)

**Format de `core_ranks.csv` :**
```csv
acronyme,nom_complet,rang,source,notes
VLDB,Very Large Data Bases,A*,CORE2023,
EDBT,Extending Database Technology,A,CORE2023,
...
```

### 8.2 Enrichissement SCImago

**Étape 1 — Téléchargement :**
```
https://www.scimagojr.com/journalrank.php?out=xls
```
Sauvegarder dans `data/scimago.csv` (~30 000 journaux, ~30 Mo).

**Étape 2 — Jointure fuzzy :**
- Extraire les noms de journaux uniques des Excel M1
- Jointure fuzzy (bibliothèque `fuzzywuzzy` ou `rapidfuzz`) avec les titres SCImago
- En cas de plusieurs catégories : choisir la plus pertinente (Computer Science, Engineering...)
- En cas d'ambiguïté de quartile : utiliser le `Best Quartile` fourni par SCImago

**Étape 3 — Enrichissement des Excel :**
- Remplir `quartile_scimago` (Q1/Q2/Q3/Q4/NC) et `sjr_score` (valeur continue) dans tous les Excel
- Calculer le SJR moyen par équipe

### 8.3 Architecture du dashboard Streamlit

**`api_client.py` — Fonctions à implémenter :**
```python
def get_membres(equipe=None, statut=None) -> List[dict]
def get_membre(membre_id: str) -> dict
def get_publications(equipe=None, annee_debut=None, annee_fin=None, type_pub=None) -> List[dict]
def get_indicateurs(equipe_id: str, annee_debut=None, annee_fin=None) -> dict
def get_comparaison() -> dict
def get_graphe_collaboration(equipe=None) -> dict
def post_simulation_marginalisation(membre_ids, taux_reduction) -> dict
def post_simulation_transfert(membre_id, equipe_destination) -> dict
```

**Page 5 — Simulation (OBLIGATOIRE) :**
```
Scénario 1 — Marginalisation :
  - st.multiselect : choix du/des membres
  - st.slider : taux de réduction (0% → 100%)
  - Appel : POST /api/simulation/marginalisation
  - Affichage : st.metric avec deltas rouge/vert

Scénario 2 — Transfert :
  - st.selectbox : choix du membre
  - st.selectbox : équipe de destination
  - Appel : POST /api/simulation/transfert
  - st.columns(2) : avant/après des deux équipes
```

---

## 9. Questions d'analyse stratégique

Ces 5 questions constituent le cœur de l'analyse. Elles sont traitées par le Membre 4 mais **tous les membres doivent les comprendre** (QCM individuel le 05/03/2026).

### Q6.1 — La fusion IDD + SETR est-elle équilibrée ?

- Quel est l'écart de productivité (par membre) entre IDD et SETR ?
- Existe-t-il déjà des co-publications entre membres IDD et SETR (chercheurs "ponts") ?
- La fusion créerait une équipe de 19 membres : quelle serait sa productivité globale ?
- Y a-t-il un risque que SETR soit "absorbée" ? Quels indicateurs le détecteraient a posteriori ?

### Q6.2 — Qualité des publications : qui publie dans les meilleures venues ?

- Distribution des rangs CORE (A*, A, B, C) par équipe
- Distribution des quartiles SCImago (Q1, Q2, Q3, Q4) par équipe
- Le score qualité pondéré change-t-il les conclusions basées uniquement sur le volume ?

### Q6.3 — Importance individuelle et risque de dépendance

- Identifier les chercheurs "locomotives" (part de production > 25%)
- Simulation de marginalisation à −50% et −100% sur le plus productif de chaque équipe
- Quelle équipe est la plus vulnérable ?
- Identifier les membres inactifs (0 publication) et peu actifs (1–2 publications)
- Effet de lest : la productivité s'améliore-t-elle significativement sans les inactifs ?

### Q6.4 — Dynamiques et tendances

- Quelles équipes sont en croissance, stables ou en déclin sur 2021–2025 ?
- Le taux d'encadrement doctoral est-il corrélé à la production scientifique ?
- La qualité des publications s'améliore-t-elle ou se dégrade-t-elle au fil des années ?

### Q6.5 — Projection à 5 ans : quel avenir pour l'équipe fusionnée ?

Construire 3 scénarios de projection pour 2026–2030 :

| Scénario | Hypothèses |
|---------|-----------|
| **Tendanciel** (baseline) | Chaque membre poursuit sa tendance actuelle, sans effet de fusion |
| **Optimiste** | Fusion génère +10–20% de co-publications inter-équipes, membres peu actifs stimulés |
| **Pessimiste** | Chercheur clé marginalisé (−50%), membres inactifs restent inactifs, pas de synergie |

**Indicateurs projetés par scénario :** publications/an, productivité/membre, score qualité moyen, indice de Gini.

---

## 10. Livrables attendus

| N° | Description | Format | Responsable |
|----|------------|--------|-------------|
| 1 | Dépôt Git complet avec README | GitHub / GitLab | M4 (+ tous) |
| 2 | Données validées — 19 fichiers Excel chercheurs + consolidated.xlsx | `.xlsx` | M1 + M3 (enrichissement) |
| 3 | Référentiels qualité — core_ranks.csv + scimago.csv | `.csv` | M3 |
| 4 | Environnement Docker fonctionnel | Docker | M4 |
| 5 | API REST FastAPI documentée (Swagger /docs) | Python / FastAPI | M2 |
| 6 | Dashboard Streamlit avec module de simulation | Python / Streamlit | M3 |
| 7 | Note de synthèse — 2–3 pages, questions stratégiques | `.pdf` | M4 |
| 8 | QCM individuel (UPdago) — **05 mars 2026** | UPdago | Tous |

---

## 11. Critères d'évaluation

| Critère | Poids | Ce que ça évalue |
|---------|-------|-----------------|
| Qualité des données | 20% | Fiabilité collecte, gestion homonymes, enrichissement CORE/SCImago, documentation des limites |
| Analyse et indicateurs | 20% | Pertinence des indicateurs, rigueur des calculs, interprétation critique |
| Application (FastAPI + Streamlit + Docker) | 25% | Architecture API, Swagger, module simulation fonctionnel, UX, Docker |
| Réponses aux questions stratégiques | 25% | Profondeur, argumentation data-driven, scénarios pertinents, nuance |
| Qualité technique et collaboration | 10% | Code propre, dépôt Git structuré, travail en équipe |
| QCM individuel | À définir | Compréhension globale du projet par chaque membre |

---

## 12. Planning et points de synchronisation

| Phase | M1 — Data Engineer | M2 — Backend | M3 — Frontend | M4 — Analyst |
|-------|------------------|-------------|--------------|-------------|
| **Jours 1–2** (Collecte) | Scraping LIAS, PIDs DBLP, `membres.csv` | Modèles Pydantic, structure API, `data_loader.py` | Download SCImago, recherche CORE, `core_ranks.csv` | Init dépôt Git, Dockerfiles, `docker-compose.yml` |
| **Jours 3–4** (Développement) | Collecte DBLP, parsing XML, fichiers Excel | Endpoints REST, indicateurs, simulation | Enrichissement Excel CORE/SCImago, pages 1–2 Streamlit | `README.md`, tests Docker, début analyse |
| **Jours 5–6** (Intégration) | Validation Excel, theses.fr, `consolidated.xlsx` | Tests endpoints, simulation finalisée, Swagger `/docs` | Pages 3–4–5, module simulation, graphe collaboration | Analyse Q6.1–6.3, projection 2026–2030, note de synthèse |
| **Jour 7** (Finalisation) | Corrections, documentation des limites | Revue code, tests intégration | UX finale, tests simulation | Q6.4–6.5 + bonus, note de synthèse finale |

**Point de synchronisation critique :** M1 doit partager les fichiers Excel avec M2 et M3 **dès que la collecte est terminée** (fin jours 1–2). Le dashboard peut être développé en parallèle avec des données mockées.

---

## 13. Limites et biais connus

| Limite | Impact | Mitigation |
|--------|--------|-----------|
| DBLP centré informatique | Couverture insuffisante pour A&S | Hors périmètre du projet |
| Rate-limiting API DBLP | Collecte lente (~2–3 sec/requête) | Cache local dans `data/cache/dblp/` |
| Certains chercheurs absents de DBLP | Données manquantes pour ces membres | Documenter dans `overrides.csv` |
| SCImago : un journal peut avoir plusieurs quartiles | Ambiguïté dans le classement | Utiliser le "Best Quartile" fourni |
| CORE ne propose pas d'export CSV | Récupération manuelle ou par scraping | Script BeautifulSoup ou saisie manuelle |
| Projection 2026–2030 repose sur hypothèses fortes | Prédictions incertaines | Documenter et discuter les limites explicitement |
| Données DBLP en XML uniquement (endpoints PID) | Nécessite un parseur XML | Utiliser `xml.etree.ElementTree` |

---

## 14. Fichiers clés à consulter

### Documents de référence (PDF)

| Fichier | Contenu | Où le trouver |
|---------|---------|--------------|
| `Projet_Bibliometrie_LIAS_BUT2SD.pdf` | Sujet complet (21 pages) — contexte, sources, indicateurs, architecture, questions stratégiques, livrables, critères | `docs/` |
| `Repartition_Taches_Bibliometrie_LIAS.pdf` | Répartition détaillée des tâches pour les 4 membres avec sous-tâches et livrables (13 pages) | `docs/` |

### Fichiers de configuration fournis

| Fichier | Contenu | Où le trouver |
|---------|---------|--------------|
| `docker-compose.yml` | Orchestration Docker (fourni, à enrichir) | `projet/` |
| `api/Dockerfile` | Container FastAPI (fourni) | `projet/api/` |
| `api/requirements.txt` | Dépendances API (fastapi, uvicorn, pandas, openpyxl, networkx, pydantic) | `projet/api/` |
| `dashboard/Dockerfile` | Container Streamlit (fourni) | `projet/dashboard/` |
| `dashboard/requirements.txt` | Dépendances dashboard (streamlit, requests, pandas, plotly, pyvis) | `projet/dashboard/` |

### Fichiers de données templates

| Fichier | Contenu | Où le trouver |
|---------|---------|--------------|
| `data/membres.csv` | Template à remplir (19 membres IDD et SETR) | `projet/data/` |
| `data/overrides.csv` | Template pour corrections manuelles | `projet/data/` |

### Fichiers à créer (mon périmètre M3)

| Fichier | Contenu | Priorité |
|---------|---------|---------|
| `data/core_ranks.csv` | Table conférence → rang CORE | Haute (bloque l'enrichissement) |
| `data/scimago.csv` | Référentiel SCImago complet (~30k journaux) | Haute (bloque l'enrichissement) |
| `scripts/04_enrich_core.py` | Script d'enrichissement CORE | Haute |
| `scripts/05_enrich_scimago.py` | Script d'enrichissement SCImago | Haute |
| `dashboard/api_client.py` | Client HTTP vers FastAPI | Haute |
| `dashboard/app.py` | Point d'entrée Streamlit (navigation) | Haute |
| `dashboard/pages/1_vue_ensemble.py` | Page 1 du dashboard | Moyenne |
| `dashboard/pages/2_comparaison.py` | Page 2 du dashboard | Moyenne |
| `dashboard/pages/3_fiche_chercheur.py` | Page 3 du dashboard | Moyenne |
| `dashboard/pages/4_collaboration.py` | Page 4 du dashboard | Moyenne |
| `dashboard/pages/5_simulation.py` | Page 5 — **OBLIGATOIRE** | Critique |

---

*Rapport rédigé par le Membre 3 (Frontend Developer) — dernière mise à jour : 23 février 2026*
