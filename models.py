from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Contact (Q12)
    prenom = Column(String(100), nullable=False)
    nom = Column(String(100), nullable=False)
    entreprise = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    tel = Column(String(50), nullable=True)
    ville = Column(String(100), nullable=True)
    pays = Column(String(100), nullable=True)

    # Q1 — Secteur
    q1_secteur = Column(String(100), nullable=False)

    # Q2 — Effectif
    q2_effectif = Column(String(100), nullable=False)

    # Q3 — Machines critiques
    q3_machines = Column(String(100), nullable=False)

    # Q4 — Type de maintenance
    q4_maintenance = Column(String(200), nullable=False)

    # Q5 — Pannes non planifiées / mois
    q5_pannes_mois = Column(String(100), nullable=False)

    # Q6 — Durée arrêt non planifié
    q6_duree_arret = Column(String(100), nullable=False)

    # Q7 — CA annuel
    q7_ca = Column(String(100), nullable=False)

    # Q8 — Budget maintenance annuel
    q8_budget_maintenance = Column(String(100), nullable=False)

    # Q9 — Pénalités clients
    q9_penalites = Column(String(200), nullable=False)

    # Q10 — ERP
    q10_erp = Column(String(200), nullable=False)

    # Q11 — Capteurs
    q11_capteurs = Column(String(200), nullable=False)

    # --- Résultats du moteur de calcul ---
    cout_horaire = Column(Float, nullable=True)
    duree_panne_h = Column(Float, nullable=True)
    nb_pannes_an = Column(Float, nullable=True)
    cout_pannes_annuel = Column(Float, nullable=True)

    budget_maintenance_valeur = Column(Float, nullable=True)
    ca_valeur = Column(Float, nullable=True)

    economie_maintenance = Column(Float, nullable=True)
    economie_pannes = Column(Float, nullable=True)
    economie_energie = Column(Float, nullable=True)
    total_economies_an = Column(Float, nullable=True)

    investissement = Column(Float, nullable=True)
    formule_recommandee = Column(String(100), nullable=True)

    roi_pct = Column(Float, nullable=True)
    payback_mois = Column(Float, nullable=True)

    score_maturite = Column(Integer, nullable=True)
    niveau_maturite = Column(String(50), nullable=True)

    nb_machines_valeur = Column(Integer, nullable=True)
