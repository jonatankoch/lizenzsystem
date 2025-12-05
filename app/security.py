import os
from passlib.context import CryptContext

# Passwort-Hasher
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Session-Timeouts
SESSION_IDLE_MINUTES = 30   # nach 30 Min Inaktivität ausloggen
SESSION_MAX_HOURS = 8       # max. Sessiondauer

# Secret Key für Session-Cookies
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)
