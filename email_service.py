"""
Service d'envoi d'emails — Kentech ROI
Email source : Yahoo SMTP
"""
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM     = os.getenv("MAIL_FROM", "")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Kentech ROI")

NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "cedric.konchie@grenoble-em.com")

COMMERCIAL_NOM    = os.getenv("COMMERCIAL_NOM", "L'équipe Kentech")
COMMERCIAL_TEL    = os.getenv("COMMERCIAL_TEL", "+33 6 XX XX XX XX")
COMMERCIAL_EMAIL  = os.getenv("COMMERCIAL_EMAIL", "contact@kentech.fr")
COMMERCIAL_REGION = os.getenv("COMMERCIAL_REGION", "France")

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def _fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", " ")


def _build_rapport_html(data: dict, roi: dict) -> str:
    today = date.today().strftime("%d/%m/%Y")
    prenom = data["prenom"]
    nom = data["nom"]
    societe = data["entreprise"]
    secteur = data["q1_secteur"]
    effectif = data["q2_effectif"]
    ville = data.get("ville", "")
    pays = data.get("pays", "France")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rapport ROI — {societe}</title>
<style>
  body {{font-family:Arial,sans-serif;background:#f4f6fa;margin:0;padding:0;color:#222;}}
  .wrap {{max-width:680px;margin:0 auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.10);}}
  .header {{background:#0D2340;padding:32px 36px 20px;text-align:center;}}
  .header h1 {{color:#fff;margin:0 0 6px;font-size:24px;letter-spacing:1px;}}
  .header p {{color:#90B4E8;margin:0;font-size:13px;}}
  .section {{padding:28px 36px;}}
  .section h2 {{color:#0D2340;font-size:16px;border-left:4px solid #2E7DD6;padding-left:10px;margin-bottom:16px;}}
  .kpi-grid {{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0;}}
  .kpi {{background:#f4f6fa;border-radius:8px;padding:16px;text-align:center;border-top:3px solid #2E7DD6;}}
  .kpi .val {{font-size:22px;font-weight:bold;color:#0D2340;}}
  .kpi .lbl {{font-size:11px;color:#64748b;margin-top:4px;}}
  .gain-box {{background:#22C55E;color:#fff;border-radius:8px;padding:16px 24px;text-align:center;margin:16px 0;}}
  .gain-box .gv {{font-size:28px;font-weight:bold;}}
  .gain-box .gl {{font-size:13px;opacity:.85;}}
  table {{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;}}
  th {{background:#0D2340;color:#fff;padding:8px 12px;text-align:left;}}
  td {{padding:8px 12px;border-bottom:1px solid #e5e7eb;}}
  tr:nth-child(even) td {{background:#f9fafb;}}
  .warn {{background:#FFF7ED;border-left:4px solid #F97316;padding:12px 16px;border-radius:4px;color:#92400E;font-size:13px;margin:12px 0;}}
  .phase {{background:#f4f6fa;border-radius:6px;margin:8px 0;overflow:hidden;}}
  .phase-header {{background:#1A4B8C;color:#fff;padding:8px 14px;font-weight:bold;font-size:13px;}}
  .phase-body {{padding:8px 14px;font-size:12px;color:#4A5568;}}
  .cta {{background:#EFF6FF;border:2px solid #2E7DD6;border-radius:8px;padding:20px;text-align:center;margin:16px 0;}}
  .cta a {{color:#1A4B8C;font-weight:bold;}}
  .footer {{background:#0D2340;color:#90B4E8;padding:16px 36px;font-size:11px;text-align:center;}}
  .conf {{background:#FFF7ED;border:1px solid #F97316;color:#92400E;padding:8px 16px;text-align:center;font-size:12px;font-weight:bold;}}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>RAPPORT D'ANALYSE ROI</h1>
    <p>Maintenance Prédictive &amp; Connectée</p>
  </div>
  <div class="conf">⚠️ DOCUMENT CONFIDENTIEL — Réservé à {prenom} {nom}</div>

  <div class="section">
    <table>
      <tr><td><b>Date</b></td><td>{today}</td></tr>
      <tr><td><b>Préparé pour</b></td><td>{societe}</td></tr>
      <tr><td><b>À l'attention de</b></td><td>{prenom} {nom}</td></tr>
      <tr><td><b>Secteur</b></td><td>{secteur}</td></tr>
      <tr><td><b>Effectif</b></td><td>{effectif}</td></tr>
      <tr><td><b>Site</b></td><td>{ville} — {pays}</td></tr>
    </table>
  </div>

  <div class="section" style="background:#f4f6fa;">
    <h2>SYNTHÈSE POUR LA DIRECTION</h2>
    <p>Bonjour <b>{prenom}</b>,</p>
    <p>Ce rapport a été préparé spécifiquement pour <b>{societe}</b> sur la base des informations que vous nous avez transmises.
    Il met en évidence le potentiel d'économies réalisables grâce à la maintenance prédictive Kentech
    sur votre site de {ville}.</p>

    <div class="kpi-grid">
      <div class="kpi">
        <div class="val">{_fmt(roi['cout_pannes_annuel'])} €</div>
        <div class="lbl">💰 Coût actuel des pannes / an</div>
      </div>
      <div class="kpi">
        <div class="val">{_fmt(roi['total_economies_an'])} €</div>
        <div class="lbl">✅ Économies annuelles estimées</div>
      </div>
      <div class="kpi">
        <div class="val">{roi['roi_pct']} %</div>
        <div class="lbl">📈 Retour sur investissement</div>
      </div>
      <div class="kpi">
        <div class="val">{roi['payback_mois']} mois</div>
        <div class="lbl">⏱️ Délai de remboursement</div>
      </div>
    </div>

    <div class="gain-box">
      <div class="gl">🏆 GAIN NET SUR 3 ANS</div>
      <div class="gv">{_fmt(roi['gain_3ans'])} €</div>
    </div>
    <p style="text-align:center;color:#0D2340;"><b>Solution recommandée : {roi['formule_recommandee']}</b></p>
  </div>

  <div class="section">
    <h2>DIAGNOSTIC DE VOTRE SITUATION ACTUELLE</h2>
    <table>
      <tr><th>Paramètre</th><th>Valeur</th></tr>
      <tr><td>Société</td><td>{societe}</td></tr>
      <tr><td>Secteur</td><td>{secteur}</td></tr>
      <tr><td>Chiffre d'affaires</td><td>{_fmt(roi['ca_valeur'])} €</td></tr>
      <tr><td>Nombre de machines critiques</td><td>{roi['nb_machines_valeur']}</td></tr>
      <tr><td>Pannes estimées / an</td><td>{roi['nb_pannes_an']:.0f}</td></tr>
      <tr><td>Durée moyenne d'une panne</td><td>{roi['duree_panne_h']} h</td></tr>
      <tr><td>Coût horaire d'arrêt</td><td>{_fmt(roi['cout_horaire'])} €/h</td></tr>
    </table>

    <div class="warn">
      ⚠️ <b>Coût total pannes / an : {_fmt(roi['cout_pannes_annuel'])} €</b><br/>
      SANS ACTION → Cette perte se répète chaque année et s'aggrave.
    </div>
  </div>

  <div class="section" style="background:#f4f6fa;">
    <h2>PROJECTION ROI</h2>
    <table>
      <tr><th>Source d'économies</th><th>Montant / an</th></tr>
      <tr><td>Réduction coûts maintenance corrective (−25 %)</td><td><b>{_fmt(roi['economie_maintenance'])} €</b></td></tr>
      <tr><td>Réduction pannes non planifiées (−35 %)</td><td><b>{_fmt(roi['economie_pannes'])} €</b></td></tr>
      <tr><td>Optimisation énergétique IA (−15 %)</td><td><b>{_fmt(roi['economie_energie'])} €</b></td></tr>
      <tr style="background:#DCFCE7;"><td><b>TOTAL ÉCONOMIES / AN</b></td><td><b style="color:#166534;">{_fmt(roi['total_economies_an'])} €</b></td></tr>
    </table>

    <table>
      <tr><th></th><th>ANNÉE 1</th><th>SUR 3 ANS</th></tr>
      <tr><td>Investissement</td><td>− {_fmt(roi['investissement'])} €</td><td>− {_fmt(roi['investissement'])} €</td></tr>
      <tr><td>Économies générées</td><td>+ {_fmt(roi['total_economies_an'])} €</td><td>+ {_fmt(roi['total_economies_3ans'])} €</td></tr>
      <tr style="font-weight:bold;"><td>Résultat net</td><td>{_fmt(roi['resultat_an1'])} €</td><td>{_fmt(roi['gain_3ans'])} €</td></tr>
      <tr><td>ROI</td><td>{roi['roi_pct']} %</td><td>—</td></tr>
      <tr><td>Délai remboursement</td><td>{roi['payback_mois']} mois</td><td>—</td></tr>
    </table>
  </div>

  <div class="section">
    <h2>AVANT / APRÈS</h2>
    <table>
      <tr><th>Critère</th><th>Avant</th><th>Après</th></tr>
      <tr><td>Pannes / an</td><td style="color:#991B1B;">{roi['nb_pannes_an']:.0f}</td><td style="color:#166534;">Réduites −70 %</td></tr>
      <tr><td>Durée arrêt moyen</td><td style="color:#991B1B;">{roi['duree_panne_h']} h</td><td style="color:#166534;">−60 %</td></tr>
      <tr><td>Coût pannes / an</td><td style="color:#991B1B;">{_fmt(roi['cout_pannes_annuel'])} €</td><td style="color:#166534;">{_fmt(roi['cout_apres'])} €</td></tr>
      <tr><td>Disponibilité machines</td><td style="color:#991B1B;">Subie</td><td style="color:#166534;">Maîtrisée</td></tr>
      <tr><td>Maintenance</td><td style="color:#991B1B;">Curative</td><td style="color:#166534;">Prédictive</td></tr>
      <tr><td>Alertes pannes</td><td style="color:#991B1B;">Aucune</td><td style="color:#166534;">Temps réel</td></tr>
      <tr><td>Tableaux de bord</td><td style="color:#991B1B;">Inexistants</td><td style="color:#166534;">Inclus</td></tr>
    </table>

    <div style="background:#EFF6FF;border-radius:6px;padding:12px;text-align:center;margin-top:12px;color:#0D2340;font-weight:bold;">
      Score de maturité digitale : {roi['score_maturite']} / 100 — Niveau {roi['niveau_maturite']}
    </div>
  </div>

  <div class="section" style="background:#f4f6fa;">
    <h2>PLAN DE DÉPLOIEMENT</h2>
    <div class="phase">
      <div class="phase-header">PHASE 1 — AUDIT &amp; CADRAGE &nbsp;·&nbsp; Semaine 1-2</div>
      <div class="phase-body">Audit technique · Identification équipements critiques · Cartographie risques</div>
    </div>
    <div class="phase">
      <div class="phase-header">PHASE 2 — INSTALLATION &nbsp;·&nbsp; Semaine 3-4</div>
      <div class="phase-body">Installation capteurs IoT · Connexion SI · Paramétrage alertes · Tests</div>
    </div>
    <div class="phase">
      <div class="phase-header">PHASE 3 — FORMATION &nbsp;·&nbsp; Semaine 5</div>
      <div class="phase-body">Formation équipe maintenance · Formation responsables · Prise en main dashboard</div>
    </div>
    <div class="phase">
      <div class="phase-header">PHASE 4 — SUIVI &amp; OPTIMISATION &nbsp;·&nbsp; Mois 2-3</div>
      <div class="phase-body">Suivi hebdomadaire · Ajustement paramètres · Premier rapport · Bilan ROI 90 jours</div>
    </div>
  </div>

  <div class="section">
    <h2>VOTRE INVESTISSEMENT</h2>
    <table>
      <tr><td><b>Solution recommandée</b></td><td>{roi['formule_recommandee']}</td></tr>
      <tr><td><b>Investissement total</b></td><td>{_fmt(roi['investissement'])} €</td></tr>
      <tr><td><b>Leasing 36 mois</b></td><td>{_fmt(roi['mensualite_leasing'])} €/mois</td></tr>
      <tr><td><b>Avec aides (BPI, CII…)</b></td><td>À partir de {_fmt(roi['investissement_net'])} €</td></tr>
    </table>

    <div class="warn" style="background:#FEF2F2;border-color:#DC2626;color:#991B1B;">
      Chaque mois sans action = <b>{_fmt(roi['cout_mensuel_inaction'])} €</b> de pertes évitables
    </div>

    <div class="cta">
      <p><b>{prenom}, passons à l'étape suivante</b></p>
      <p>📅 <a href="https://www.kentech.fr/demo">Réserver un entretien visio gratuit</a><br/>
         📞 Appeler votre conseiller : {COMMERCIAL_TEL}<br/>
         📧 Répondre à cet email : {COMMERCIAL_EMAIL}</p>
      <p><b>{COMMERCIAL_NOM}</b><br/>
      Consultant Kentech — Région {COMMERCIAL_REGION}</p>
    </div>
  </div>

  <div class="footer">
    Ce document est confidentiel et personnalisé pour {societe} — {today}
  </div>
</div>
</body>
</html>"""


def send_client_email(data: dict, roi: dict, pdf_bytes: bytes) -> None:
    """Envoie le rapport ROI + PDF à l'entreprise."""
    prenom = data["prenom"]
    societe = data["entreprise"]
    to_email = data["email"]

    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"Votre Rapport d'Analyse ROI — {societe}"
    msg["From"]    = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"]      = to_email

    # Corps HTML
    html_part = MIMEText(_build_rapport_html(data, roi), "html", "utf-8")
    msg.attach(html_part)

    # PDF en pièce jointe
    pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"Rapport_ROI_Kentech_{societe}.pdf"
    )
    msg.attach(pdf_part)

    _send(msg)


def send_notification_email(data: dict, roi: dict) -> None:
    """Envoie une notification interne à Kentech."""
    societe   = data["entreprise"]
    prenom    = data["prenom"]
    nom       = data["nom"]
    email     = data["email"]
    tel       = data.get("tel", "—")
    secteur   = data["q1_secteur"]

    html = f"""<html><body style="font-family:Arial;color:#222;">
<h2 style="color:#0D2340;">🔔 Nouveau formulaire ROI reçu</h2>
<table style="border-collapse:collapse;width:100%;max-width:600px;">
  <tr><td style="padding:8px;background:#f4f6fa;font-weight:bold;">Entreprise</td><td style="padding:8px;">{societe}</td></tr>
  <tr><td style="padding:8px;font-weight:bold;">Contact</td><td style="padding:8px;">{prenom} {nom}</td></tr>
  <tr><td style="padding:8px;background:#f4f6fa;font-weight:bold;">Email</td><td style="padding:8px;">{email}</td></tr>
  <tr><td style="padding:8px;font-weight:bold;">Téléphone</td><td style="padding:8px;">{tel}</td></tr>
  <tr><td style="padding:8px;background:#f4f6fa;font-weight:bold;">Secteur</td><td style="padding:8px;">{secteur}</td></tr>
  <tr><td style="padding:8px;font-weight:bold;">Coût pannes / an</td><td style="padding:8px;color:#DC2626;font-weight:bold;">{_fmt(roi['cout_pannes_annuel'])} €</td></tr>
  <tr><td style="padding:8px;background:#f4f6fa;font-weight:bold;">Économies potentielles</td><td style="padding:8px;color:#166534;font-weight:bold;">{_fmt(roi['total_economies_an'])} €</td></tr>
  <tr><td style="padding:8px;font-weight:bold;">ROI</td><td style="padding:8px;">{roi['roi_pct']} %</td></tr>
  <tr><td style="padding:8px;background:#f4f6fa;font-weight:bold;">Solution</td><td style="padding:8px;">{roi['formule_recommandee']}</td></tr>
  <tr><td style="padding:8px;font-weight:bold;">Score maturité</td><td style="padding:8px;">{roi['score_maturite']} / 100 — {roi['niveau_maturite']}</td></tr>
</table>
<p style="color:#666;font-size:12px;">Envoyé automatiquement par la plateforme Kentech ROI</p>
</body></html>"""

    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"[Kentech ROI] Nouveau lead : {societe} — {_fmt(roi['total_economies_an'])} €/an"
    msg["From"]    = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"]      = NOTIFICATION_EMAIL

    msg.attach(MIMEText(html, "html", "utf-8"))
    _send(msg)


def _send(msg: MIMEMultipart) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtp.send_message(msg)
