from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import User
from .security import SESSION_IDLE_MINUTES, SESSION_MAX_HOURS


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Liest den eingeloggten User aus der Session und prüft Timeouts."""
    user_id = request.session.get("user_id")
    if not user_id:
        # nicht eingeloggt
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    now = datetime.utcnow()
    login_at_str = request.session.get("login_at")
    last_seen_str = request.session.get("last_seen")

    # maximale Sessiondauer
    if login_at_str:
        login_at = datetime.fromisoformat(login_at_str)
        if now - login_at > timedelta(hours=SESSION_MAX_HOURS):
            request.session.clear()
            raise HTTPException(status_code=303, headers={"Location": "/login"})

    # Inaktivitäts-Timeout
    if last_seen_str:
        last_seen = datetime.fromisoformat(last_seen_str)
        if now - last_seen > timedelta(minutes=SESSION_IDLE_MINUTES):
            request.session.clear()
            raise HTTPException(status_code=303, headers={"Location": "/login"})

    # last_seen aktualisieren
    request.session["last_seen"] = now.isoformat()

    user = db.query(User).filter(User.id == user_id, User.is_active == 1).first()
    if not user:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Nicht genügend Rechte")
    return current_user
