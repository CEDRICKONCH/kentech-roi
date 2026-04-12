"""
Génération du rapport PDF automatique — Kentech
"""
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ── Palette couleurs Kentech ───────────────────────────────────────────────
BLUE_DARK = colors.HexColor("#0D2340")
BLUE_MED  = colors.HexColor("#1A4B8C")
BLUE_LIGHT = colors.HexColor("#2E7DD6")
ORANGE    = colors.HexColor("#F97316")
GREY_BG   = colors.HexColor("#F4F6FA")
GREY_TEXT = colors.HexColor("#4A5568")
WHITE     = colors.white
GREEN     = colors.HexColor("#22C55E")


def fmt(n: float) -> str:
    """Formate un nombre avec séparateur milliers."""
    return f"{n:,.0f}".replace(",", " ")


def build_pdf(data: dict, roi: dict) -> bytes:
    """
    Construit le PDF et retourne les bytes.
    data  : dict avec prenom, nom, entreprise, email, ville, pays, q1..q11
    roi   : dict retourné par calculator.compute_roi()
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Rapport ROI — {data['entreprise']}",
        author="Kentech",
    )

    styles = getSampleStyleSheet()
    today = date.today().strftime("%d/%m/%Y")

    # ── Styles personnalisés ───────────────────────────────────────────────
    def S(name, **kw):
        base = styles["Normal"]
        return ParagraphStyle(name, parent=base, **kw)

    title_style = S("TitleK", fontSize=22, textColor=WHITE, alignment=TA_CENTER,
                    fontName="Helvetica-Bold", spaceAfter=4)
    sub_style   = S("SubK",   fontSize=13, textColor=WHITE, alignment=TA_CENTER,
                    fontName="Helvetica", spaceAfter=2)
    section_style = S("Sec",  fontSize=13, textColor=BLUE_DARK,
                       fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body_style  = S("Body",   fontSize=10, textColor=GREY_TEXT,
                    leading=15, spaceAfter=4)
    kpi_label   = S("KL",     fontSize=9,  textColor=GREY_TEXT,
                    fontName="Helvetica", alignment=TA_CENTER)
    kpi_val     = S("KV",     fontSize=16, textColor=BLUE_DARK,
                    fontName="Helvetica-Bold", alignment=TA_CENTER)
    kpi_unit    = S("KU",     fontSize=9,  textColor=BLUE_LIGHT,
                    alignment=TA_CENTER)
    caption     = S("Cap",    fontSize=8,  textColor=GREY_TEXT,
                    alignment=TA_RIGHT, spaceBefore=2)

    story = []

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 1 — COUVERTURE
    # ══════════════════════════════════════════════════════════════════════
    # Bandeau titre
    cover_data = [[
        Paragraph("RAPPORT D'ANALYSE ROI", title_style),
    ]]
    cover_tbl = Table(cover_data, colWidths=[17 * cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [8, 8, 8, 8]),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.3 * cm))

    sub_data = [[Paragraph("Maintenance Prédictive &amp; Connectée", sub_style)]]
    sub_tbl = Table(sub_data, colWidths=[17 * cm])
    sub_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_MED),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sub_tbl)
    story.append(Spacer(1, 0.6 * cm))

    # Info entreprise
    info_rows = [
        ["Préparé pour :", data["entreprise"]],
        ["À l'attention de :", f"{data['prenom']} {data['nom']}"],
        ["Secteur :", data["q1_secteur"]],
        ["Effectif :", data["q2_effectif"]],
        ["Site :", f"{data.get('ville', '')} — {data.get('pays', 'France')}"],
        ["Date :", today],
    ]
    info_tbl = Table(info_rows, colWidths=[5 * cm, 12 * cm])
    info_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE_DARK),
        ("TEXTCOLOR", (1, 0), (1, -1), GREY_TEXT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.5 * cm))

    # Bandeau confidentiel
    conf_tbl = Table([[Paragraph(
        f"⚠️  DOCUMENT CONFIDENTIEL — Réservé à {data['prenom']} {data['nom']}",
        S("Conf", fontSize=9, textColor=ORANGE, fontName="Helvetica-Bold",
          alignment=TA_CENTER)
    )]], colWidths=[17 * cm])
    conf_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1, ORANGE),
    ]))
    story.append(conf_tbl)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 2 — KPIs CLÉS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SYNTHÈSE POUR LA DIRECTION", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LIGHT, spaceAfter=10))

    story.append(Paragraph(
        f"Bonjour {data['prenom']},",
        S("Greet", fontSize=11, textColor=BLUE_DARK, fontName="Helvetica-Bold", spaceAfter=6)
    ))
    story.append(Paragraph(
        f"Ce rapport a été préparé spécifiquement pour <b>{data['entreprise']}</b> sur la base "
        f"de vos réponses. Il met en évidence le potentiel d'économies réalisables grâce à la "
        f"maintenance prédictive Kentech sur votre site de {data.get('ville', 'votre site')}.",
        body_style
    ))
    story.append(Spacer(1, 0.4 * cm))

    # KPIs en tableau
    kpi_data = [
        [
            Paragraph("💰 Coût actuel des pannes", kpi_label),
            Paragraph("✅ Économies annuelles estimées", kpi_label),
            Paragraph("📈 ROI", kpi_label),
            Paragraph("⏱️ Retour sur invest.", kpi_label),
        ],
        [
            Paragraph(f"{fmt(roi['cout_pannes_annuel'])} €", kpi_val),
            Paragraph(f"{fmt(roi['total_economies_an'])} €", kpi_val),
            Paragraph(f"{roi['roi_pct']} %", kpi_val),
            Paragraph(f"{roi['payback_mois']} mois", kpi_val),
        ],
        [
            Paragraph("par an", kpi_unit),
            Paragraph("par an", kpi_unit),
            Paragraph("sur investissement", kpi_unit),
            Paragraph("délai remboursement", kpi_unit),
        ],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[4.25 * cm] * 4, rowHeights=[1 * cm, 1.2 * cm, 0.7 * cm])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREY_BG),
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.3 * cm))

    # Gain 3 ans
    gain_tbl = Table([[
        Paragraph("🏆 GAIN NET SUR 3 ANS", S("GL", fontSize=11, textColor=WHITE,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f"{fmt(roi['gain_3ans'])} €", S("GV", fontSize=18, textColor=WHITE,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]], colWidths=[8.5 * cm, 8.5 * cm])
    gain_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(gain_tbl)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Solution recommandée : <b>{roi['formule_recommandee']}</b>",
        S("Rec", fontSize=10, textColor=BLUE_DARK, alignment=TA_CENTER, spaceAfter=4)
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 3 — DIAGNOSTIC ACTUEL
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("DIAGNOSTIC DE VOTRE SITUATION ACTUELLE", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LIGHT, spaceAfter=10))

    diag_rows = [
        ["Société", data["entreprise"]],
        ["Secteur", data["q1_secteur"]],
        ["Effectif", data["q2_effectif"]],
        ["Chiffre d'affaires", f"{fmt(roi['ca_valeur'])} €"],
        ["Type de maintenance", data["q4_maintenance"]],
        ["Pannes / mois déclarées", data["q5_pannes_mois"]],
        ["Durée arrêt moyen", data["q6_duree_arret"]],
        ["ERP", data["q10_erp"]],
        ["Capteurs installés", data["q11_capteurs"]],
    ]
    diag_tbl = Table(diag_rows, colWidths=[6 * cm, 11 * cm])
    diag_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE_DARK),
        ("TEXTCOLOR", (1, 0), (1, -1), GREY_TEXT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(diag_tbl)
    story.append(Spacer(1, 0.5 * cm))

    # Impact financier
    story.append(Paragraph("⚠️  IMPACT FINANCIER ACTUEL", section_style))
    impact_rows = [
        ["Coût horaire d'arrêt", f"{fmt(roi['cout_horaire'])} €/h"],
        ["Nombre de machines critiques", str(roi['nb_machines_valeur'])],
        ["Pannes estimées / an", f"{roi['nb_pannes_an']:.0f}"],
        ["Durée moyenne d'une panne", f"{roi['duree_panne_h']} h"],
        ["COÛT TOTAL PANNES / AN", f"{fmt(roi['cout_pannes_annuel'])} €"],
    ]
    impact_tbl = Table(impact_rows, colWidths=[9 * cm, 8 * cm])
    impact_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica"),
        ("FONTNAME",  (0, 4), (1, 4), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 4), (-1, 4), WHITE),
        ("BACKGROUND", (0, 4), (-1, 4), ORANGE),
        ("ROWBACKGROUNDS", (0, 0), (-1, 3), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(impact_tbl)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "SANS ACTION → Cette perte se répète chaque année et s'aggrave avec la vétusté des équipements.",
        S("Warn", fontSize=9, textColor=ORANGE, fontName="Helvetica-BoldOblique",
          borderColor=ORANGE, borderWidth=1, borderPadding=8, spaceAfter=4)
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 4 — PROJECTION ROI
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("PROJECTION ROI", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LIGHT, spaceAfter=10))

    story.append(Paragraph(
        f"Grâce à nos solutions de maintenance prédictive, voici ce que "
        f"<b>{data['entreprise']}</b> peut espérer :",
        body_style
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Décomposition économies
    eco_rows = [
        ["SOURCE D'ÉCONOMIES", "CALCUL", "MONTANT ANNUEL"],
        ["Réduction coûts maintenance corrective",
         f"Budget maint. {fmt(roi['budget_maintenance_valeur'])}€ × 25 %",
         f"{fmt(roi['economie_maintenance'])} €"],
        ["Réduction pannes non planifiées",
         f"Coût pannes {fmt(roi['cout_pannes_annuel'])}€ × 35 %",
         f"{fmt(roi['economie_pannes'])} €"],
        ["Optimisation énergétique IA",
         f"CA {fmt(roi['ca_valeur'])}€ × 0,8 % × 15 %",
         f"{fmt(roi['economie_energie'])} €"],
        ["TOTAL ÉCONOMIES / AN", "", f"{fmt(roi['total_economies_an'])} €"],
    ]
    eco_tbl = Table(eco_rows, colWidths=[7 * cm, 5.5 * cm, 4.5 * cm])
    eco_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",   (0, 4), (-1, 4), "Helvetica-Bold"),
        ("BACKGROUND", (0, 4), (-1, 4), GREEN),
        ("TEXTCOLOR",  (0, 4), (-1, 4), WHITE),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, 3), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(eco_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # Tableau ROI
    roi_rows = [
        ["", "ANNÉE 1", "SUR 3 ANS"],
        ["Investissement", f"- {fmt(roi['investissement'])} €", f"- {fmt(roi['investissement'])} €"],
        ["Économies générées", f"+ {fmt(roi['total_economies_an'])} €", f"+ {fmt(roi['total_economies_3ans'])} €"],
        ["Résultat net", f"{fmt(roi['resultat_an1'])} €", f"{fmt(roi['gain_3ans'])} €"],
        ["ROI", f"{roi['roi_pct']} %", "—"],
        ["Délai de remboursement", f"{roi['payback_mois']} mois", "—"],
    ]
    roi_tbl = Table(roi_rows, colWidths=[7 * cm, 5 * cm, 5 * cm])
    roi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_MED),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",  (0, 1), (0, -1), BLUE_DARK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (2, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(roi_tbl)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"⏱️  Votre investissement est remboursé en seulement <b>{roi['payback_mois']} mois</b>",
        S("PB", fontSize=11, textColor=BLUE_DARK, fontName="Helvetica-Bold",
          alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 5 — AVANT / APRÈS + SCORE MATURITÉ
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("AVANT / APRÈS — IMPACT DE LA SOLUTION", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LIGHT, spaceAfter=10))

    avap_rows = [
        ["CRITÈRE", "AVANT", "APRÈS"],
        ["Pannes / an", f"{roi['nb_pannes_an']:.0f}", "Réduites −70 %"],
        ["Durée arrêt moyen", f"{roi['duree_panne_h']} h", "−60 %"],
        ["Coût pannes / an", f"{fmt(roi['cout_pannes_annuel'])} €", f"{fmt(roi['cout_apres'])} €"],
        ["Disponibilité machines", "Subie", "Maîtrisée"],
        ["Maintenance", "Curative", "Prédictive"],
        ["Alertes pannes", "Aucune", "Temps réel"],
        ["Tableaux de bord", "Inexistants", "Inclus"],
        ["Rapport mensuel", "Manuel", "Automatique"],
    ]
    avap_tbl = Table(avap_rows, colWidths=[6 * cm, 5.5 * cm, 5.5 * cm])
    avap_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("BACKGROUND", (1, 1), (1, -1), colors.HexColor("#FEE2E2")),
        ("BACKGROUND", (2, 1), (2, -1), colors.HexColor("#DCFCE7")),
        ("TEXTCOLOR",  (1, 1), (1, -1), colors.HexColor("#991B1B")),
        ("TEXTCOLOR",  (2, 1), (2, -1), colors.HexColor("#166534")),
        ("ROWBACKGROUNDS", (0, 1), (0, -1), [GREY_BG, WHITE]),
        ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, 1), (0, -1), BLUE_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(avap_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # Score maturité
    score = roi["score_maturite"]
    niveau = roi["niveau_maturite"]
    score_color = (
        colors.HexColor("#DC2626") if score < 30
        else colors.HexColor("#D97706") if score < 60
        else GREEN
    )
    story.append(Paragraph("SCORE DE MATURITÉ DIGITALE", section_style))
    score_rows = [[
        Paragraph(f"{score} / 100", S("SC", fontSize=28, textColor=score_color,
                  fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f"Niveau : <b>{niveau}</b><br/>"
                  f"<font size=9 color='#4A5568'>Ce score évalue votre capacité à déployer "
                  f"une solution IA rapidement et efficacement.</font>",
                  S("SN", fontSize=11, textColor=BLUE_DARK, leading=16)),
    ]]
    score_tbl = Table(score_rows, colWidths=[5 * cm, 12 * cm])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREY_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(score_tbl)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 6 — PLAN DE DÉPLOIEMENT + INVESTISSEMENT
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("PLAN DE DÉPLOIEMENT", section_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LIGHT, spaceAfter=10))

    phases = [
        ("PHASE 1 — AUDIT & CADRAGE", "Semaine 1-2",
         "Audit technique · Identification équipements critiques · Cartographie risques · Validation plan"),
        ("PHASE 2 — INSTALLATION", "Semaine 3-4",
         "Installation capteurs IoT · Connexion SI existant · Paramétrage alertes · Tests"),
        ("PHASE 3 — FORMATION", "Semaine 5",
         "Formation équipe maintenance · Formation responsables site · Prise en main dashboard"),
        ("PHASE 4 — SUIVI & OPTIMISATION", "Mois 2-3",
         "Suivi hebdomadaire · Ajustement paramètres · Rapport performance · Bilan ROI 90 jours"),
    ]
    for phase_title, phase_timing, phase_desc in phases:
        phase_rows = [[
            Paragraph(phase_title, S("PT", fontSize=10, textColor=WHITE,
                      fontName="Helvetica-Bold")),
            Paragraph(phase_timing, S("PTi", fontSize=9, textColor=WHITE,
                      alignment=TA_RIGHT)),
        ], [
            Paragraph(phase_desc, S("PD", fontSize=9, textColor=GREY_TEXT, leading=14)),
            Paragraph("", body_style),
        ]]
        phase_tbl = Table(phase_rows, colWidths=[11 * cm, 6 * cm])
        phase_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE_MED),
            ("BACKGROUND", (0, 1), (-1, 1), GREY_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("SPAN", (0, 1), (1, 1)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(phase_tbl)
        story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.4 * cm))

    # Investissement
    story.append(Paragraph("VOTRE INVESTISSEMENT", section_style))
    inv_rows = [
        ["Solution", roi["formule_recommandee"]],
        ["Investissement total", f"{fmt(roi['investissement'])} €"],
        ["Leasing 36 mois", f"{fmt(roi['mensualite_leasing'])} €/mois"],
        ["Avec aides (BPI, CII…)", f"À partir de {fmt(roi['investissement_net'])} €"],
        ["Chaque mois sans action =", f"{fmt(roi['cout_mensuel_inaction'])} € de pertes évitables"],
    ]
    inv_tbl = Table(inv_rows, colWidths=[8 * cm, 9 * cm])
    inv_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE_DARK),
        ("TEXTCOLOR", (1, 0), (1, -1), GREY_TEXT),
        ("TEXTCOLOR", (1, 4), (1, 4), ORANGE),
        ("FONTNAME",  (1, 4), (1, 4), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GREY_BG, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE3EE")),
    ]))
    story.append(inv_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # CTA
    cta_tbl = Table([[Paragraph(
        f"📅  Réserver un entretien visio gratuit → www.kentech.fr/demo<br/>"
        f"📞  Appeler votre conseiller → +33 6 XX XX XX XX<br/>"
        f"📧  Répondre à cet email → cedric.konchie@grenoble-em.com",
        S("CTA", fontSize=10, textColor=BLUE_DARK, leading=18, alignment=TA_CENTER)
    )]], colWidths=[17 * cm])
    cta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("BOX", (0, 0), (-1, -1), 1.5, BLUE_LIGHT),
    ]))
    story.append(cta_tbl)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Ce document est confidentiel et personnalisé pour {data['entreprise']} — {today}",
        caption
    ))

    doc.build(story)
    return buffer.getvalue()
