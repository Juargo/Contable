"""Schemas para validación y serialización usando Pydantic"""

from typing import Optional
from datetime import date, datetime
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from database.models import Transaction, Bank, Category, CategoryKeyword

# Crea schemas Pydantic a partir de modelos Tortoise
Transaction_Pydantic = pydantic_model_creator(Transaction, name="Transaction")
TransactionIn_Pydantic = pydantic_model_creator(
    Transaction, 
    name="TransactionIn", 
    exclude_readonly=True
)

Bank_Pydantic = pydantic_model_creator(Bank, name="Bank")
BankIn_Pydantic = pydantic_model_creator(Bank, name="BankIn", exclude_readonly=True)

Category_Pydantic = pydantic_model_creator(Category, name="Category")
CategoryIn_Pydantic = pydantic_model_creator(
    Category, 
    name="CategoryIn", 
    exclude_readonly=True
)

# Esquemas para CategoryKeyword
CategoryKeyword_Pydantic = pydantic_model_creator(
    CategoryKeyword, name="CategoryKeyword"
)
CategoryKeywordIn_Pydantic = pydantic_model_creator(
    CategoryKeyword, name="CategoryKeywordIn", exclude_readonly=True
)

class IncomeTransactionIn_Pydantic(BaseModel):
    """Esquema para crear/actualizar transacciones de ingresos"""
    transaction_date: date
    description: str
    amount: float
    category: Optional[str] = "Sin clasificar"
    bank_id: Optional[int] = None

    class Config:
        orm_mode = True

class IncomeTransaction_Pydantic(BaseModel):
    """Esquema para respuestas de transacciones de ingresos"""
    id: int
    transaction_date: date
    description: str
    amount: float
    category: str
    bank_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Para facilitar las importaciones
__all__ = [
    "Bank_Pydantic",
    "BankIn_Pydantic",
    "Category_Pydantic",
    "CategoryIn_Pydantic",
    "CategoryKeyword_Pydantic",
    "CategoryKeywordIn_Pydantic",
    "Transaction_Pydantic",
    "TransactionIn_Pydantic",
    "IncomeTransaction_Pydantic",
    "IncomeTransactionIn_Pydantic",
]
