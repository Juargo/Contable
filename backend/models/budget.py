from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='check_dates'),
    )

    # Relaciones
    budget_categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete-orphan")
    subcategory_budgets = relationship("SubcategoryBudget", back_populates="budget", cascade="all, delete-orphan")

class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    budget = relationship("Budget", back_populates="budget_categories")
    category = relationship("Category")

    __table_args__ = (
        UniqueConstraint('budget_id', 'category_id', name='unique_budget_category'),
    )

class SubcategoryBudget(Base):
    __tablename__ = "subcategory_budgets"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    budget = relationship("Budget", back_populates="subcategory_budgets")
    category = relationship("Category")

    __table_args__ = (
        UniqueConstraint('budget_id', 'category_id', name='unique_subcategory_budget'),
    )
