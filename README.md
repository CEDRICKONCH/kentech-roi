# Kentech ROI — Diagnostic Maintenance Prédictive

> Outil de calcul du potentiel d'économies IA pour l'industrie.
> Questionnaire 12 questions → Rapport ROI personnalisé → Email + PDF automatique.

---

## Aperçu

L'application permet à un industriel de remplir un formulaire en 3 minutes et de recevoir instantanément par email un **rapport d'analyse ROI complet** (HTML + PDF) estimant le retour sur investissement d'une solution de maintenance prédictive Kentech.

```
Formulaire (12 questions)
       ↓
Moteur de calcul ROI (backend)
       ↓
┌──────────────────────────────┐
│  Email client : rapport HTML │
│  + PDF 6 pages en pièce      │
│    jointe                    │
└──────────────────────────────┘
       ↓
Notification interne Kentech
```

---

## Stack technique

| Couche          | Technologie                  |
|-----------------|------------------------------|
| Backend         | Python 3.11 + FastAPI        |
| Base de données | MySQL 8.0 + SQLAlchemy       |
| Templates HTML  | Jinja2                       |
| Génération PDF  | ReportLab                    |
| Email           | Gmail SMTP (App Password)    |
| Conteneurisation| Docker + Docker Compose      |

---

## Démarrage rapide (Docker)

**Prérequis :** Docker Desktop installé et lancé.

### 1. Cloner le projet

```bash
git clone https://github.com/CEDRICKONCH/kentech-roi.git
cd kentech-roi
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
```

Éditez `.env` avec vos valeurs :

```env
# Base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kentech_roi
DB_USER=root
DB_PASSWORD=votre_mot_de_passe

# Email Gmail
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Mot de passe d'application Gmail
MAIL_FROM=votre.email@gmail.com
MAIL_FROM_NAME=Kentech ROI

# Notification interne
NOTIFICATION_EMAIL=cedric.konchie@grenoble-em.com

# Infos commercial (affichées dans les rapports)
COMMERCIAL_NOM=Cédric Konchie
COMMERCIAL_TEL=+33 7 59 61 52 92
COMMERCIAL_EMAIL=cedric.konchie@grenoble-em.com
COMMERCIAL_REGION=France
```

> **Mot de passe d'application Gmail :**
> [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> → Validation en 2 étapes requise → Créer → copier le code 16 caractères

### 3. Démarrer

```bash
docker compose up -d --build
```

L'application est accessible sur **http://localhost:8080**

### Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f

# Arrêter
docker compose down

# Arrêter et supprimer les données MySQL
docker compose down -v

# Redémarrer uniquement l'app (après modif .env)
docker compose up -d --force-recreate app
```

---

## Pages

| URL | Description |
|-----|-------------|
| `http://localhost:8080/` | Formulaire questionnaire (12 questions) |
| `http://localhost:8080/entreprises` | Liste de toutes les entreprises enregistrées |
| `http://localhost:8080/entreprises/{id}` | Détail complet d'une réponse avec calculs ROI |
| `http://localhost:8080/merci?id={id}` | Page de confirmation après soumission |

---

## Formulaire — Les 12 questions

| Bloc | Questions |
|------|-----------|
| **1 — Profil Usine** | Secteur d'activité · Effectif · Machines critiques |
| **2 — Maintenance actuelle** | Type de maintenance · Pannes/mois · Durée arrêt |
| **3 — Impact financier** | CA annuel · Budget maintenance · Pénalités clients |
| **4 — Maturité digitale** | ERP · Capteurs installés |
| **Contact (Q12)** | Prénom · Nom · Email · Entreprise · Téléphone · Ville · Pays |

---

## Moteur de calcul ROI

### Variables de base

| Réponse | Valeur centrale utilisée |
|---------|--------------------------|
| CA < 2 M€ | Coût/heure = 800 € |
| CA 2–10 M€ | Coût/heure = 2 500 € |
| CA 10–30 M€ | Coût/heure = 5 000 € |
| CA 30–100 M€ | Coût/heure = 10 000 € |
| CA > 100 M€ | Coût/heure = 20 000 € |

### Formules

```
COÛT_PANNE_ANNUEL    = Coût/heure × Durée_moy × Nb_pannes_an × 1,35

ÉCONOMIE_MAINTENANCE = Budget_maintenance × 25 %
ÉCONOMIE_PANNES      = COÛT_PANNE_ANNUEL × 35 %
ÉCONOMIE_ENERGIE     = CA × 0,8 % × 15 %
TOTAL_ÉCONOMIES_AN   = somme des 3 économies

ROI (%)              = (TOTAL_ÉCONOMIES_AN − Investissement) / Investissement × 100
PAYBACK (mois)       = Investissement / (TOTAL_ÉCONOMIES_AN / 12)
```

### Investissement recommandé selon effectif

| Effectif | Investissement | Solution |
|----------|---------------|----------|
| < 20 personnes | 30 000 € | Pack Essentiel |
| 20–50 personnes | 50 000 € | Pack Standard |
| 50–150 personnes | 75 000 € | Pack Avancé |
| 150–500 personnes | 120 000 € | Pack Entreprise |
| > 500 personnes | 200 000 € | Pack Grand Compte |

### Score de maturité digitale (0–100)

| Critère | Points |
|---------|--------|
| ERP accessible | +20 pts |
| Données historiques disponibles | +20 pts |
| Capteurs existants (plupart) | +25 pts |
| Maintenance préventive ou mixte | +15 pts |
| Équipe tech interne (prédictif partiel) | +20 pts |

- **< 30 pts** → Niveau Débutant
- **30–60 pts** → Niveau Intermédiaire
- **> 60 pts** → Niveau Avancé

---

## Emails générés automatiquement

### 1. Email client
Envoyé à l'adresse saisie dans le formulaire, contient :
- Corps HTML : Rapport d'Analyse ROI complet (synthèse, diagnostic, projection, avant/après, plan de déploiement, investissement)
- Pièce jointe : PDF 6 pages généré dynamiquement avec ReportLab

### 2. Notification interne
Envoyée à `NOTIFICATION_EMAIL` (configurable dans `.env`), contient :
- Résumé du lead (entreprise, contact, chiffres clés ROI)

---

## Structure du projet

```
kentech-roi/
├── main.py              # Routes FastAPI
├── calculator.py        # Moteur de calcul ROI
├── pdf_generator.py     # Génération PDF ReportLab (6 pages)
├── email_service.py     # Envoi emails Gmail SMTP
├── models.py            # Modèle SQLAlchemy (table responses)
├── database.py          # Connexion MySQL + wait_for_db
├── templates/
│   ├── base.html        # Layout commun (navbar, footer)
│   ├── form.html        # Formulaire 12 questions
│   ├── companies.html   # Liste des entreprises
│   ├── detail.html      # Détail ROI par entreprise
│   └── merci.html       # Page de confirmation
├── static/
│   └── style.css        # Design Kentech
├── Dockerfile           # Image Python 3.11-slim
├── docker-compose.yml   # Services MySQL + FastAPI
├── .env.example         # Template de configuration
├── .gitignore
└── requirements.txt
```

---

## Base de données

Table `responses` créée automatiquement au démarrage :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | INT AUTO_INCREMENT | Identifiant unique |
| `created_at` | DATETIME | Date de soumission (automatique) |
| `prenom`, `nom`, `entreprise`, `email`, `tel`, `ville`, `pays` | VARCHAR | Informations contact |
| `q1_secteur` … `q11_capteurs` | VARCHAR | Réponses aux 11 questions |
| `cout_pannes_annuel`, `total_economies_an`, `roi_pct`, … | FLOAT | Résultats calculés |
| `score_maturite`, `niveau_maturite` | INT / VARCHAR | Score de maturité digitale |

---

*Développé pour Kentech — Maintenance Prédictive & Connectée*
