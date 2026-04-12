"""
Kentech ROI — Application principale
FastAPI backend + templates Jinja2
"""
import os
import threading
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, get_db, Base, wait_for_db
from models import Response as ResponseModel
from calculator import compute_roi
from pdf_generator import build_pdf
from email_service import send_client_email, send_notification_email

load_dotenv()

# Attendre MySQL puis créer les tables
wait_for_db()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kentech ROI", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def fmt_eur(value: float) -> str:
    """Filtre Jinja2 pour formater les montants."""
    if value is None:
        return "—"
    return f"{value:,.0f} €".replace(",", " ")


def fmt_num(value: float) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}".replace(",", " ")


templates.env.filters["eur"] = fmt_eur
templates.env.filters["num"] = fmt_num


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    db: Session = Depends(get_db),
    # Contact
    prenom: str = Form(...),
    nom: str = Form(...),
    entreprise: str = Form(...),
    email: str = Form(...),
    tel: Optional[str] = Form(None),
    ville: Optional[str] = Form(None),
    pays: Optional[str] = Form(None),
    # Q1-Q11
    q1_secteur: str = Form(...),
    q2_effectif: str = Form(...),
    q3_machines: str = Form(...),
    q4_maintenance: str = Form(...),
    q5_pannes_mois: str = Form(...),
    q6_duree_arret: str = Form(...),
    q7_ca: str = Form(...),
    q8_budget_maintenance: str = Form(...),
    q9_penalites: str = Form(...),
    q10_erp: str = Form(...),
    q11_capteurs: str = Form(...),
):
    form_data = {
        "prenom": prenom.strip(),
        "nom": nom.strip(),
        "entreprise": entreprise.strip(),
        "email": email.strip(),
        "tel": tel.strip() if tel else "",
        "ville": ville.strip() if ville else "",
        "pays": pays.strip() if pays else "France",
        "q1_secteur": q1_secteur,
        "q2_effectif": q2_effectif,
        "q3_machines": q3_machines,
        "q4_maintenance": q4_maintenance,
        "q5_pannes_mois": q5_pannes_mois,
        "q6_duree_arret": q6_duree_arret,
        "q7_ca": q7_ca,
        "q8_budget_maintenance": q8_budget_maintenance,
        "q9_penalites": q9_penalites,
        "q10_erp": q10_erp,
        "q11_capteurs": q11_capteurs,
    }

    # Calcul ROI
    roi = compute_roi(form_data)

    # Enregistrement en base
    record = ResponseModel(
        prenom=form_data["prenom"],
        nom=form_data["nom"],
        entreprise=form_data["entreprise"],
        email=form_data["email"],
        tel=form_data["tel"],
        ville=form_data["ville"],
        pays=form_data["pays"],
        q1_secteur=q1_secteur,
        q2_effectif=q2_effectif,
        q3_machines=q3_machines,
        q4_maintenance=q4_maintenance,
        q5_pannes_mois=q5_pannes_mois,
        q6_duree_arret=q6_duree_arret,
        q7_ca=q7_ca,
        q8_budget_maintenance=q8_budget_maintenance,
        q9_penalites=q9_penalites,
        q10_erp=q10_erp,
        q11_capteurs=q11_capteurs,
        # Résultats
        cout_horaire=roi["cout_horaire"],
        duree_panne_h=roi["duree_panne_h"],
        nb_pannes_an=roi["nb_pannes_an"],
        cout_pannes_annuel=roi["cout_pannes_annuel"],
        budget_maintenance_valeur=roi["budget_maintenance_valeur"],
        ca_valeur=roi["ca_valeur"],
        economie_maintenance=roi["economie_maintenance"],
        economie_pannes=roi["economie_pannes"],
        economie_energie=roi["economie_energie"],
        total_economies_an=roi["total_economies_an"],
        investissement=roi["investissement"],
        formule_recommandee=roi["formule_recommandee"],
        roi_pct=roi["roi_pct"],
        payback_mois=roi["payback_mois"],
        score_maturite=roi["score_maturite"],
        niveau_maturite=roi["niveau_maturite"],
        nb_machines_valeur=roi["nb_machines_valeur"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Envoi emails en arrière-plan (non bloquant)
    def send_emails():
        try:
            pdf_bytes = build_pdf(form_data, roi)
            send_client_email(form_data, roi, pdf_bytes)
            send_notification_email(form_data, roi)
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    threading.Thread(target=send_emails, daemon=True).start()

    return RedirectResponse(url=f"/merci?id={record.id}", status_code=303)


@app.get("/merci", response_class=HTMLResponse)
async def merci(request: Request, id: int, db: Session = Depends(get_db)):
    record = db.query(ResponseModel).filter(ResponseModel.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Réponse introuvable")
    return templates.TemplateResponse("merci.html", {"request": request, "r": record})


@app.get("/entreprises", response_class=HTMLResponse)
async def list_companies(request: Request, db: Session = Depends(get_db)):
    records = db.query(ResponseModel).order_by(ResponseModel.created_at.desc()).all()
    return templates.TemplateResponse("companies.html", {"request": request, "records": records})


@app.get("/entreprises/{record_id}", response_class=HTMLResponse)
async def company_detail(request: Request, record_id: int, db: Session = Depends(get_db)):
    record = db.query(ResponseModel).filter(ResponseModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return templates.TemplateResponse("detail.html", {"request": request, "r": record})
