"""Módulo para manejar operaciones relacionadas con transacciones"""

from typing import List

from fastapi import APIRouter, HTTPException

from ..database.models import Transaction
from ..database.schemas import Transaction_Pydantic

router = APIRouter(tags=["Transactions"])

@router.get("/transactions", response_model=List[Transaction_Pydantic])
async def get_all_transactions():
    """Obtiene todas las transacciones de la base de datos"""
    return await Transaction_Pydantic.from_queryset(Transaction.all())

@router.get("/transactions/{transaction_id}", response_model=Transaction_Pydantic)
async def get_transaction(transaction_id: int):
    """Obtiene una transacción por su ID"""
    transaction = await Transaction.get_or_none(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return await Transaction_Pydantic.from_tortoise_orm(transaction)

@router.post("/transactions", response_model=Transaction_Pydantic)
async def create_transaction(transaction: any):
    """Crea una nueva transacción"""
    transaction_obj = await Transaction.create(**transaction.dict(exclude_unset=True))
    return await Transaction_Pydantic.from_tortoise_orm(transaction_obj)
