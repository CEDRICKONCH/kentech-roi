"""
Moteur de calcul ROI — Kentech
Basé sur les règles définies dans Document sans titre.docx
"""


# ── Coût horaire selon CA ──────────────────────────────────────────────────
CA_COUT_HORAIRE = {
    "Moins de 2 M€": (1_000_000, 800),
    "2 à 10 M€":    (6_000_000, 2_500),
    "10 à 30 M€":   (20_000_000, 5_000),
    "30 à 100 M€":  (65_000_000, 10_000),
    "Plus de 100 M€": (150_000_000, 20_000),
}

# ── Durée moyenne panne (valeur centrale en heures) ───────────────────────
DUREE_PANNE = {
    "Moins de 2 heures": 1.5,
    "2 à 8 heures": 4.0,
    "8 à 24 heures": 14.0,
    "Plus de 24 heures": 30.0,
}

# ── Fréquence pannes (valeur centrale × 12 mois) ─────────────────────────
FREQ_PANNES_AN = {
    "Moins de 2": 1.5 * 12,    # 18/an
    "2 à 5": 3.5 * 12,         # 42/an
    "5 à 10": 7.5 * 12,        # 90/an
    "Plus de 10": 12.0 * 12,   # 144/an
}

# ── Budget maintenance (valeur centrale) ──────────────────────────────────
BUDGET_MAINTENANCE = {
    "Moins de 50 K€": 25_000,
    "50 à 150 K€": 100_000,
    "150 à 500 K€": 325_000,
    "Plus de 500 K€": 750_000,
}

# ── Investissement selon effectif ─────────────────────────────────────────
INVESTISSEMENT = {
    "Moins de 20 personnes": (30_000, "Pack Essentiel"),
    "20 à 50 personnes":     (50_000, "Pack Standard"),
    "50 à 150 personnes":    (75_000, "Pack Avancé"),
    "150 à 500 personnes":   (120_000, "Pack Entreprise"),
    "Plus de 500 personnes": (200_000, "Pack Grand Compte"),
}

# ── Nombre de machines (valeur centrale) ─────────────────────────────────
NB_MACHINES = {
    "Moins de 5": 3,
    "5 à 15": 10,
    "15 à 40": 28,
    "Plus de 40": 50,
}


def compute_roi(data: dict) -> dict:
    """
    Calcule les indicateurs ROI à partir des réponses du formulaire.
    data: dict avec les champs q1..q11 et les infos contact
    Retourne un dict avec tous les résultats calculés.
    """

    # --- Variables de base ---
    ca_valeur, cout_horaire = CA_COUT_HORAIRE.get(data["q7_ca"], (6_000_000, 2_500))
    duree_panne_h = DUREE_PANNE.get(data["q6_duree_arret"], 4.0)
    nb_pannes_an = FREQ_PANNES_AN.get(data["q5_pannes_mois"], 42.0)
    budget_maintenance_valeur = BUDGET_MAINTENANCE.get(data["q8_budget_maintenance"], 100_000)
    investissement, formule_recommandee = INVESTISSEMENT.get(
        data["q2_effectif"], (75_000, "Pack Avancé")
    )
    nb_machines_valeur = NB_MACHINES.get(data["q3_machines"], 10)

    # --- Coût des pannes annuel ---
    cout_pannes_annuel = round(cout_horaire * duree_panne_h * nb_pannes_an * 1.35, 2)

    # --- Économies ---
    economie_maintenance = round(budget_maintenance_valeur * 0.25, 2)
    economie_pannes = round(cout_pannes_annuel * 0.35, 2)
    economie_energie = round(ca_valeur * 0.008 * 0.15, 2)
    total_economies_an = round(economie_maintenance + economie_pannes + economie_energie, 2)

    # --- ROI ---
    roi_pct = round(
        (total_economies_an - investissement) / investissement * 100, 1
    )
    payback_mois = round(investissement / (total_economies_an / 12), 1)

    # --- Projections 3 ans ---
    total_economies_3ans = round(total_economies_an * 3, 2)
    gain_3ans = round(total_economies_3ans - investissement, 2)
    resultat_an1 = round(total_economies_an - investissement, 2)
    cout_apres = round(cout_pannes_annuel * 0.65, 2)
    mensualite_leasing = round(investissement / 36, 2)
    investissement_net = round(investissement * 0.60, 2)
    cout_mensuel_inaction = round(cout_pannes_annuel / 12, 2)

    # --- Score de maturité ---
    score = 0
    # ERP accessible → +20
    if data["q10_erp"] == "Oui, avec données accessibles":
        score += 20
    # Données historiques → +20
    if data["q10_erp"] in ("Oui, avec données accessibles", "Oui, mais données difficiles à extraire"):
        score += 20
    # Capteurs existants → +25
    if data["q11_capteurs"] == "Oui, sur la plupart":
        score += 25
    elif data["q11_capteurs"] == "Oui, sur quelques-unes":
        score += 12
    # Maintenance préventive → +15
    if data["q4_maintenance"] in (
        "Préventive planifiée (révisions à intervalles fixes)",
        "Mixte (les deux selon les machines)",
        "Prédictive partielle (déjà quelques capteurs)",
    ):
        score += 15
    # Équipe tech interne → +20 (prédictive partielle = déjà une équipe)
    if data["q4_maintenance"] == "Prédictive partielle (déjà quelques capteurs)":
        score += 20

    score = min(score, 100)

    if score < 30:
        niveau_maturite = "Débutant"
    elif score < 60:
        niveau_maturite = "Intermédiaire"
    else:
        niveau_maturite = "Avancé"

    return {
        "ca_valeur": ca_valeur,
        "cout_horaire": cout_horaire,
        "duree_panne_h": duree_panne_h,
        "nb_pannes_an": nb_pannes_an,
        "budget_maintenance_valeur": budget_maintenance_valeur,
        "nb_machines_valeur": nb_machines_valeur,
        "cout_pannes_annuel": cout_pannes_annuel,
        "economie_maintenance": economie_maintenance,
        "economie_pannes": economie_pannes,
        "economie_energie": economie_energie,
        "total_economies_an": total_economies_an,
        "investissement": investissement,
        "formule_recommandee": formule_recommandee,
        "roi_pct": roi_pct,
        "payback_mois": payback_mois,
        "total_economies_3ans": total_economies_3ans,
        "gain_3ans": gain_3ans,
        "resultat_an1": resultat_an1,
        "cout_apres": cout_apres,
        "mensualite_leasing": mensualite_leasing,
        "investissement_net": investissement_net,
        "cout_mensuel_inaction": cout_mensuel_inaction,
        "score_maturite": score,
        "niveau_maturite": niveau_maturite,
    }
