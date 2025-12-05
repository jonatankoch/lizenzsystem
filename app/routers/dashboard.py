from datetime import date, timedelta

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import Customer, License, User
from app.ui import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers_count = db.query(Customer).count()
    licenses_active = db.query(License).filter(License.status == "active").count()

    today = date.today()
    in_30 = today + timedelta(days=30)
    in_90 = today + timedelta(days=90)

    exp_30 = db.query(License).filter(
        License.status == "active",
        License.end_date != None,
        License.end_date >= today,
        License.end_date <= in_30,
    ).count()

    exp_90 = db.query(License).filter(
        License.status == "active",
        License.end_date != None,
        License.end_date >= today,
        License.end_date <= in_90,
    ).count()

    stats = {
        "customers_count": customers_count,
        "licenses_active": licenses_active,
        "licenses_expiring_30": exp_30,
        "licenses_expiring_90": exp_90,
    }

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stats": stats},
    )
