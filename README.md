# Kentech ROI — Application Web

Application de calcul du potentiel d'économies IA pour l'industrie.

## Stack technique

| Couche      | Technologie           |
|-------------|-----------------------|
| Backend     | Python 3.11 + FastAPI |
| Base de données | MySQL + SQLAlchemy |
| Templates   | Jinja2 (HTML)         |
| PDF         | ReportLab             |
| Email       | SMTP Yahoo            |

## Installation

### 1. Prérequis

- Python 3.11+
- MySQL 8.0+

### 2. Créer la base de données

```bash
mysql -u root -p < init_db.sql
```

### 3. Configurer l'environnement

Éditez le fichier `.env` :

```env
# Base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kentech_roi
DB_USER=root
DB_PASSWORD=votre_mot_de_passe

# Email Yahoo
MAIL_USERNAME=konchiecc@yahoo.fr
MAIL_PASSWORD=votre_mot_de_passe_app_yahoo   # ← Mot de passe d'application Yahoo
MAIL_FROM=konchiecc@yahoo.fr
MAIL_FROM_NAME=Kentech ROI

# Notification interne
NOTIFICATION_EMAIL=cedric.konchie@grenoble-em.com

# Infos commercial (affiché dans les rapports)
COMMERCIAL_NOM=Cédric Konchie
COMMERCIAL_TEL=+33 6 XX XX XX XX
COMMERCIAL_EMAIL=cedric.konchie@grenoble-em.com
COMMERCIAL_REGION=France
```

> **Note Yahoo :** Pour obtenir un mot de passe d'application Yahoo :
> Compte Yahoo → Sécurité → Mots de passe d'application → Générer

### 4. Installer les dépendances

```bash
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Démarrer l'application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

L'application est accessible sur **http://localhost:8000**

## Pages

| URL                       | Description                              |
|---------------------------|------------------------------------------|
| `/`                       | Formulaire questionnaire (12 questions)  |
| `/entreprises`            | Liste de toutes les entreprises          |
| `/entreprises/{id}`       | Détail d'une réponse avec calculs ROI    |
| `/merci?id={id}`          | Page de confirmation après soumission    |

## Moteur de calcul

Le backend applique automatiquement les règles suivantes :

### Coût des pannes annuel
```
COÛT_PANNE_ANNUEL = Coût/heure × Durée_moy × Nb_pannes_an × 1,35
```

### Économies estimées
```
ÉCONOMIE_MAINTENANCE = Budget_maintenance × 25%
ÉCONOMIE_PANNES      = COÛT_PANNE_ANNUEL × 35%
ÉCONOMIE_ENERGIE     = CA × 0,8% × 15%
TOTAL_ÉCONOMIES_AN   = somme des 3 économies
```

### ROI
```
ROI (%)       = (TOTAL_ÉCONOMIES_AN - Investissement) / Investissement × 100
PAYBACK (mois) = Investissement / (TOTAL_ÉCONOMIES_AN / 12)
```

### Score de maturité (0-100)
- ERP accessible → +20 pts
- Données historiques → +20 pts
- Capteurs existants → +25 pts
- Maintenance préventive → +15 pts
- Équipe tech interne → +20 pts

## Emails envoyés

1. **Client** : Rapport d'Analyse ROI complet (HTML) + PDF en pièce jointe
2. **Notification interne** : Résumé du lead envoyé à `cedric.konchie@grenoble-em.com`
