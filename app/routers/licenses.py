from datetime import date, timedelta

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import License, Customer, Product, User
from app.ui import templates

router = APIRouter(prefix="/licenses", tags=["licenses"])


@router.get("", response_class=HTMLResponse)
async def licenses_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    params = request.query_params

    expiring = params.get("expiring")
    status = params.get("status")
    customer_id = params.get("customer_id")
    product_id = params.get("product_id")
    q = params.get("q")

    today = date.today()

    query = db.query(License).join(Customer).join(Product)

    # Ablauf-Filter
    if expiring in ("30", "60", "90"):
        days = int(expiring)
        limit_date = today + timedelta(days=days)
        query = query.filter(
            License.end_date != None,
            License.end_date >= today,
            License.end_date <= limit_date,
        )
    elif expiring == "expired":
        query = query.filter(
            License.end_date != None,
            License.end_date < today,
        )

    # Status
    if status and status != "all":
        query = query.filter(License.status == status)

    # Kunde / Produkt
    if customer_id:
        try:
            cid = int(customer_id)
            query = query.filter(License.customer_id == cid)
        except ValueError:
            pass

    if product_id:
        try:
            pid = int(product_id)
            query = query.filter(License.product_id == pid)
        except ValueError:
            pass

    # Textsuche
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                License.license_key.ilike(pattern),
                Customer.name.ilike(pattern),
                Product.name.ilike(pattern),
                License.notes.ilike(pattern),
            )
        )

    licenses = query.all()

    customers = db.query(Customer).order_by(Customer.name).all()
    products = db.query(Product).order_by(Product.name).all()

    return templates.TemplateResponse(
        "licenses_list.html",
        {
            "request": request,
            "licenses": licenses,
            "expiring": expiring,
            "status": status,
            "customer_id": customer_id,
            "product_id": product_id,
            "q": q,
            "customers": customers,
            "products": products,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def license_new_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    products = db.query(Product).order_by(Product.name).all()

    return templates.TemplateResponse(
        "license_form.html",
        {
            "request": request,
            "customers": customers,
            "products": products,
            "license": None,
        },
    )


@router.post("/new")
async def license_create(
    customer_id: int = Form(...),
    product_id: int = Form(...),
    license_key: str = Form(""),
    seats: int | None = Form(None),
    start_date: str = Form(""),
    end_date: str = Form(""),
    interval: str = Form(""),
    price: str = Form(""),
    status: str = Form("active"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    lic = License(
        customer_id=customer_id,
        product_id=product_id,
        license_key=license_key or None,
        seats=seats,
        start_date=start,
        end_date=end,
        interval=interval or None,
        price=price or None,
        status=status or None,
        notes=notes or None,
    )
    db.add(lic)
    db.commit()
    return RedirectResponse(url="/licenses", status_code=303)


@router.get("/{license_id}", response_class=HTMLResponse)
async def license_detail(
    license_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lic = db.query(License).filter(License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")

    return templates.TemplateResponse(
        "license_detail.html",
        {"request": request, "license": lic},
    )


@router.get("/{license_id}/edit", response_class=HTMLResponse)
async def license_edit_form(
    license_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lic = db.query(License).filter(License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")

    customers = db.query(Customer).order_by(Customer.name).all()
    products = db.query(Product).order_by(Product.name).all()

    return templates.TemplateResponse(
        "license_form.html",
        {
            "request": request,
            "customers": customers,
            "products": products,
            "license": lic,
        },
    )


@router.post("/{license_id}/edit")
async def license_update(
    license_id: int,
    customer_id: int = Form(...),
    product_id: int = Form(...),
    license_key: str = Form(""),
    seats: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    interval: str = Form(""),
    price: str = Form(""),
    status: str = Form("active"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lic = db.query(License).filter(License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")

    lic.customer_id = customer_id
    lic.product_id = product_id
    lic.license_key = license_key or None
    lic.seats = int(seats) if seats else None
    lic.start_date = date.fromisoformat(start_date) if start_date else None
    lic.end_date = date.fromisoformat(end_date) if end_date else None
    lic.interval = interval or None
    lic.price = price or None
    lic.status = status or None
    lic.notes = notes or None

    db.commit()
    return RedirectResponse(url=f"/licenses/{license_id}", status_code=303)


@router.post("/{license_id}/delete")
async def license_delete(
    license_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lic = db.query(License).filter(License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")

    db.delete(lic)
    db.commit()
    return RedirectResponse(url="/licenses", status_code=303)
