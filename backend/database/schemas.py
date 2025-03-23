"""Schemas para validación y serialización usando Pydantic"""

from typing import Optional
from datetime import date
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
]
