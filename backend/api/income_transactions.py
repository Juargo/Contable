"""Módulo para manejar operaciones relacionadas con transacciones de ingresos"""

import logging
from typing import List, Optional
from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import calendar

from database.models import IncomeTransaction
from database.schemas import IncomeTransaction_Pydantic, IncomeTransactionIn_Pydantic

router = APIRouter(tags=["Income Transactions"])

@router.get("/income-transactions", response_model=List[IncomeTransaction_Pydantic])
async def get_all_income_transactions():
    """Obtiene todas las transacciones de ingresos"""
    return await IncomeTransaction_Pydantic.from_queryset(IncomeTransaction.all())

@router.get("/income-transactions/{transaction_id}", response_model=IncomeTransaction_Pydantic)
async def get_income_transaction(transaction_id: int):
    """Obtiene una transacción de ingreso por su ID"""
    transaction = await IncomeTransaction.get_or_none(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción de ingreso no encontrada")
    return await IncomeTransaction_Pydantic.from_tortoise_orm(transaction)

@router.post("/income-transactions", response_model=IncomeTransaction_Pydantic)
async def create_income_transaction(transaction: IncomeTransactionIn_Pydantic):
    """Crea una nueva transacción de ingreso"""
    # Asegurar que el monto sea positivo
    transaction_dict = transaction.dict(exclude_unset=True)
    if transaction_dict.get("amount", 0) < 0:
        transaction_dict["amount"] = abs(transaction_dict["amount"])
        
    transaction_obj = await IncomeTransaction.create(**transaction_dict)
    return await IncomeTransaction_Pydantic.from_tortoise_orm(transaction_obj)

@router.put("/income-transactions/{transaction_id}", response_model=IncomeTransaction_Pydantic)
async def update_income_transaction(transaction_id: int, transaction: IncomeTransactionIn_Pydantic):
    """Actualiza una transacción de ingreso existente"""
    transaction_obj = await IncomeTransaction.get_or_none(id=transaction_id)
    if not transaction_obj:
        raise HTTPException(status_code=404, detail="Transacción de ingreso no encontrada")
    
    transaction_data = transaction.dict(exclude_unset=True)
    # Asegurar que el monto sea positivo
    if "amount" in transaction_data and transaction_data["amount"] < 0:
        transaction_data["amount"] = abs(transaction_data["amount"])
    
    await transaction_obj.update_from_dict(transaction_data)
    await transaction_obj.save()
    return await IncomeTransaction_Pydantic.from_tortoise_orm(transaction_obj)

@router.delete("/income-transactions/{transaction_id}")
async def delete_income_transaction(transaction_id: int):
    """Elimina una transacción de ingreso"""
    deleted_count = await IncomeTransaction.filter(id=transaction_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Transacción de ingreso no encontrada")
    return {"message": "Transacción de ingreso eliminada correctamente"}

@router.get("/income-transactions-by-month", response_model=List[IncomeTransaction_Pydantic])
async def get_income_transactions_by_month(
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., ge=2000, le=2100, description="Año (2000-2100)")
):
    """
    Obtiene las transacciones de ingreso de un mes específico.
    
    - **month**: Número del mes (1-12)
    - **year**: Año (formato YYYY)
    
    Returns:
        Lista de transacciones de ingreso correspondientes al mes y año especificados.
    """
    try:
        # Calcular el último día del mes
        last_day = calendar.monthrange(year, month)[1]
        
        # Crear fechas de inicio y fin para el filtro
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Filtrar transacciones por el rango de fechas
        query = IncomeTransaction.filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).order_by('transaction_date')
        
        # Obtener transacciones
        transactions = await IncomeTransaction_Pydantic.from_queryset(query)
        
        # Eliminar decimales en el campo amount para consistencia con el frontend
        for transaction in transactions:
            transaction.amount = int(transaction.amount)
        
        return transactions
    
    except Exception as e:
        logging.error(f"Error al obtener transacciones de ingreso por mes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener transacciones de ingreso: {str(e)}"
        )

# Modelo para transacciones en masa
class BulkIncomeTransactionResponse(BaseModel):
    total_recibidas: int
    insertadas: int
    duplicadas: int
    transacciones_insertadas: List[IncomeTransaction_Pydantic]

class IncomeTransactionInput(BaseModel):
    fecha: str
    descripcion: str
    monto: float
    categoria: Optional[str] = "Sin clasificar"
    banco_id: Optional[int] = None

@router.post("/bulk-income-transactions", response_model=BulkIncomeTransactionResponse)
async def create_bulk_income_transactions(transactions: List[IncomeTransactionInput] = Body(...)):
    """
    Inserta múltiples transacciones de ingreso evitando duplicados.
    
    Recibe un array de transacciones y las inserta en la base de datos,
    verificando que no existan duplicados por fecha, descripción y monto.
    
    Returns:
        Un resumen con el total de transacciones recibidas, insertadas y duplicadas.
    """
    if not transactions:
        raise HTTPException(status_code=400, detail="No se recibieron transacciones")
    
    # Convertimos todas las fechas al formato de la base de datos
    processed_transactions = []
    for t in transactions:
        # Convertir la fecha si viene como string
        try:
            # Intentar varios formatos de fecha comunes
            for date_format in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    parsed_date = datetime.strptime(t.fecha, date_format).date()
                    break
                except ValueError:
                    continue
            else:  # Si ningún formato funciona
                raise ValueError(f"Formato de fecha no reconocido: {t.fecha}")
        except Exception as e:
            logging.error(f"Error al procesar fecha {t.fecha}: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Error en formato de fecha: {t.fecha}. Use formato YYYY-MM-DD."
            )
        
        # Asegurar que el monto sea positivo
        monto = abs(float(t.monto))
                
        processed_transactions.append({
            "transaction_date": parsed_date,
            "description": t.descripcion,
            "amount": monto,  # Aseguramos que sea positivo
            "category": t.categoria,
            "bank_id": t.banco_id
        })
    
    # Verificar duplicados y crear nuevas transacciones
    inserted_transactions = []
    duplicates_count = 0
    
    for trans_data in processed_transactions:
        # Buscar si ya existe una transacción igual por fecha, descripción y monto
        existing = await IncomeTransaction.filter(
            transaction_date=trans_data["transaction_date"],
            description=trans_data["description"],
            amount=trans_data["amount"]
        ).first()
        
        if existing:
            duplicates_count += 1
            logging.info(f"Transacción de ingreso duplicada: {trans_data}")
            continue
        
        # Si no existe, crear nueva transacción
        transaction_obj = await IncomeTransaction.create(**trans_data)
        trans_pydantic = await IncomeTransaction_Pydantic.from_tortoise_orm(transaction_obj)
        inserted_transactions.append(trans_pydantic)
        
    return {
        "total_recibidas": len(transactions),
        "insertadas": len(inserted_transactions),
        "duplicadas": duplicates_count,
        "transacciones_insertadas": inserted_transactions
    }
