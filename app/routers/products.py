from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import Product, User
from app.ui import templates

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_class=HTMLResponse)
async def product_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).order_by(Product.name).all()
    return templates.TemplateResponse(
        "products_list.html",
        {"request": request, "products": products},
    )


@router.get("/new", response_class=HTMLResponse)
async def product_new_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "product": None},
    )


@router.post("/new")
async def product_create(
    name: str = Form(...),
    category: str = Form(""),
    manufacturer: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = Product(
        name=name,
        category=category or None,
        manufacturer=manufacturer or None,
        notes=notes or None,
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303)


@router.get("/{product_id}", response_class=HTMLResponse)
async def product_detail(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    return templates.TemplateResponse(
        "product_detail.html",
        {"request": request, "product": product},
    )


@router.get("/{product_id}/edit", response_class=HTMLResponse)
async def product_edit_form(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "product": product},
    )


@router.post("/{product_id}/edit")
async def product_update(
    product_id: int,
    name: str = Form(...),
    category: str = Form(""),
    manufacturer: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    product.name = name
    product.category = category or None
    product.manufacturer = manufacturer or None
    product.notes = notes or None

    db.commit()
    return RedirectResponse(url=f"/products/{product_id}", status_code=303)


@router.post("/{product_id}/delete")
async def product_delete(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    db.delete(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303)
