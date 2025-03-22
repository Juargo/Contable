"""Esquemas para bancos"""

from pydantic import BaseModel
from database.models import Bank_Pydantic, BankIn_Pydantic

# Utilizamos los esquemas generados automáticamente por Tortoise
BankSchema = Bank_Pydantic
BankCreateSchema = BankIn_Pydantic
