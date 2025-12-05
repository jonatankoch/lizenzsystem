from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import Customer, User
from app.ui import templates

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_class=HTMLResponse)
async def customers_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = request.query_params.get("q")

    query = db.query(Customer).order_by(Customer.name)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Customer.name.ilike(pattern),
                Customer.customer_number.ilike(pattern),
                Customer.contact_name.ilike(pattern),
                Customer.contact_email.ilike(pattern),
            )
        )

    customers = query.all()
    return templates.TemplateResponse(
        "customers_list.html",
        {"request": request, "customers": customers, "q": q},
    )


@router.get("/new", response_class=HTMLResponse)
async def customer_new_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "customer_form.html",
        {"request": request, "customer": None},
    )


@router.post("/new")
async def customer_create(
    customer_number: str = Form(...),
    name: str = Form(...),
    contact_name: str = Form(""),
    contact_email: str = Form(""),
    contact_phone: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = Customer(
        customer_number=customer_number,
        name=name,
        contact_name=contact_name or None,
        contact_email=contact_email or None,
        contact_phone=contact_phone or None,
        notes=notes or None,
    )
    db.add(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)


@router.get("/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    return templates.TemplateResponse(
        "customer_detail.html",
        {"request": request, "customer": customer},
    )


@router.get("/{customer_id}/edit", response_class=HTMLResponse)
async def customer_edit_form(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    return templates.TemplateResponse(
        "customer_form.html",
        {"request": request, "customer": customer},
    )


@router.post("/{customer_id}/edit")
async def customer_update(
    customer_id: int,
    customer_number: str = Form(...),
    name: str = Form(...),
    contact_name: str = Form(""),
    contact_email: str = Form(""),
    contact_phone: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    customer.customer_number = customer_number
    customer.name = name
    customer.contact_name = contact_name or None
    customer.contact_email = contact_email or None
    customer.contact_phone = contact_phone or None
    customer.notes = notes or None

    db.commit()
    return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)


@router.post("/{customer_id}/delete")
async def customer_delete(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    db.delete(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)
