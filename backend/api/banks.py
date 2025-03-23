"""Módulo para manejar operaciones relacionadas con bancos"""

from typing import List

from fastapi import APIRouter, HTTPException

from database.models import Bank
from database.schemas import Bank_Pydantic, BankIn_Pydantic

router = APIRouter(tags=["Banks"])

@router.get("/banks", response_model=List[Bank_Pydantic])
async def get_all_banks():
    """Obtiene todos los bancos de la base de datos"""
    return await Bank_Pydantic.from_queryset(Bank.all())

@router.get("/banks/{bank_id}", response_model=Bank_Pydantic)
async def get_bank(bank_id: int):
    """Obtiene un banco por su ID"""
    bank = await Bank.get_or_none(id=bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    return await Bank_Pydantic.from_tortoise_orm(bank)