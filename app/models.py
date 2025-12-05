from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationship
    licenses = relationship("License", back_populates="customer", cascade="all, delete")
    

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    category = Column(String(100), index=True, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    licenses = relationship("License", back_populates="product", cascade="all, delete")

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    license_key = Column(String(255), nullable=True)
    seats = Column(Integer, nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    interval = Column(String(50), nullable=True)  # monthly, yearly, etc.
    price = Column(String(50), nullable=True)     # string, weil später € oder CHF egal

    status = Column(String(50), nullable=True)    # active, expired, cancelled
    notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="licenses")
    product = relationship("Product", back_populates="licenses")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # "admin" / "user"
    is_active = Column(Integer, nullable=False, default=1)     # 1 = aktiv, 0 = gesperrt
