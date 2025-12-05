from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .database import Base, engine, SessionLocal
from .models import Customer, Product, License, User
from .security import SECRET_KEY, hash_password
from .routers import auth, dashboard, customers, products, licenses, admin_users


app = FastAPI()

# Session-Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="lm_session",
)

# Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Router registrieren
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(licenses.router)
app.include_router(admin_users.router)



# Startup: Tabellen + Demo-Daten
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Demo-Kunden
        if db.query(Customer).count() == 0:
            demo_customers = [
                Customer(
                    customer_number="K1000",
                    name="Musterkunde GmbH",
                    contact_name="Max Mustermann",
                    contact_email="it@musterkunde.de",
                    contact_phone="01234 567890",
                    notes="Demo-Kunde, zum Testen angelegt.",
                ),
                Customer(
                    customer_number="K1001",
                    name="Beispiel AG",
                    contact_name="Erika Beispiel",
                    contact_email="admin@beispiel-ag.de",
                    contact_phone="09876 543210",
                    notes=None,
                ),
            ]
            db.add_all(demo_customers)
            db.commit()

        # Demo-Produkte
        if db.query(Product).count() == 0:
            products = [
                Product(
                    name="ESET Endpoint Security",
                    category="Antivirus",
                    manufacturer="ESET",
                ),
                Product(
                    name="Securepoint UTM",
                    category="Firewall",
                    manufacturer="Securepoint",
                ),
                Product(
                    name="Monitoring Basic",
                    category="Monitoring",
                    manufacturer="Inhouse",
                ),
            ]
            db.add_all(products)
            db.commit()

        # Demo-Lizenz
        if db.query(License).count() == 0:
            demo_customer = db.query(Customer).first()
            demo_product = db.query(Product).first()

            if demo_customer and demo_product:
                demo_license = License(
                    customer_id=demo_customer.id,
                    product_id=demo_product.id,
                    license_key="ABC-123-XYZ",
                    seats=25,
                    start_date=date.today() - timedelta(days=300),
                    end_date=date.today() + timedelta(days=60),
                    interval="yearly",
                    price="150€/Jahr",
                    status="active",
                    notes="Demo-Lizenz",
                )
                db.add(demo_license)
                db.commit()

        # Admin-User
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                is_active=1,
            )
            db.add(admin)
            db.commit()
