from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.deps import get_db, require_admin
from app.models import User
from app.security import hash_password
from app.ui import templates

router = APIRouter(prefix="/admin", tags=["admin-users"])


@router.get("/users", response_class=HTMLResponse)
async def admin_users_list(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.username).all()
    return templates.TemplateResponse(
        "users_list.html",
        {"request": request, "users": users},
    )


@router.get("/users/new", response_class=HTMLResponse)
async def admin_user_new_form(
    request: Request,
    admin_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        "user_form.html",
        {"request": request, "user_obj": None},
    )


@router.post("/users/new")
async def admin_user_create(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    is_active: int = Form(1),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")

    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def admin_user_edit_form(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    return templates.TemplateResponse(
        "user_form.html",
        {"request": request, "user_obj": user},
    )


@router.post("/users/{user_id}/edit")
async def admin_user_update(
    user_id: int,
    username: str = Form(...),
    role: str = Form("user"),
    is_active: int = Form(1),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    existing = db.query(User).filter(User.username == username, User.id != user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")

    user.username = username
    user.role = role
    user.is_active = is_active

    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.get("/users/{user_id}/reset-password", response_class=HTMLResponse)
async def admin_user_reset_pw_form(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    return templates.TemplateResponse(
        "user_reset_password.html",
        {"request": request, "user_obj": user},
    )


@router.post("/users/{user_id}/reset-password")
async def admin_user_reset_pw(
    user_id: int,
    password: str = Form(...),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    user.password_hash = hash_password(password)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
