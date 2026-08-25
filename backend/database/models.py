from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    businesses = relationship("Business", back_populates="owner")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=True)  # retail / ecommerce / wholesale...
    currency = Column(String(10), default="PKR")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="businesses")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="business", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="business", cascade="all, delete-orphan")
    insights = relationship("AiInsight", back_populates="business", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    sku = Column(String(100), index=True, nullable=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("Business", back_populates="products")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    order_id = Column(String(100), index=True, nullable=True)
    product_name = Column(String(255), nullable=False, index=True)
    customer_name = Column(String(255), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    sale_date = Column(Date, nullable=False, index=True)

    business = relationship("Business", back_populates="sales")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    total_spent = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    first_purchase = Column(Date, nullable=True)
    last_purchase = Column(Date, nullable=True)

    business = relationship("Business", back_populates="customers")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True, index=True)  # rent / marketing / salaries...
    amount = Column(Float, default=0.0)
    expense_date = Column(Date, nullable=False, index=True)

    business = relationship("Business", back_populates="expenses")


class AiInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    severity = Column(String(20), default="info")  # critical / warning / info / success
    category = Column(String(50))                  # inventory / sales / expenses / customers
    title = Column(String(255))
    message = Column(Text)
    recommendation = Column(Text, nullable=True)
    priority = Column(String(20), default="MEDIUM")  # HIGH / MEDIUM / LOW
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="insights")
