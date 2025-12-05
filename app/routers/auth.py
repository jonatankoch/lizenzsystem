from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.security import verify_password
from app.ui import templates

router = APIRouter()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash) or user.is_active != 1:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Benutzername oder Passwort ist falsch."},
        )

    now = datetime.utcnow()
    request.session["user_id"] = user.id
    request.session["login_at"] = now.isoformat()
    request.session["last_seen"] = now.isoformat()
    request.session["role"] = user.role

    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
