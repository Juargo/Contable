"""Esquemas para bancos"""

from ..database.schemas import Bank_Pydantic, BankIn_Pydantic

# Utilizamos los esquemas generados automáticamente por Tortoise
BankSchema = Bank_Pydantic
BankCreateSchema = BankIn_Pydantic
