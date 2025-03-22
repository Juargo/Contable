from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any
import sys
import os

# Añadir la ruta de los scripts actuales para poder importarlos
sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))

# Importar funciones necesarias de los scripts existentes
try:
    from services.transaction_service import get_transactions
    from services.bank_report_service import process_bank_report
except ImportError:
    # Funciones provisionales si aún no existen los módulos
    def get_transactions() -> List[Dict[str, Any]]:
        # Datos de ejemplo
        return [
            {"date": "2023-01-01", "description": "Compra en supermercado", "category": "Alimentación", "amount": -50.25},
            {"date": "2023-01-05", "description": "Nómina", "category": "Ingresos", "amount": 1200.00},
        ]
    
    def process_bank_report(file_content: bytes, bank_name: str) -> List[Dict[str, Any]]:
        # Función provisional
        return [
            {"date": "2023-01-01", "description": "Dato de ejemplo", "category": "Sin clasificar", "amount": -100.00},
        ]

router = APIRouter(tags=["transactions"])

@router.get("/transactions", response_model=List[Dict[str, Any]])
async def read_transactions():
    try:
        transactions = get_transactions()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")

@router.post("/upload-bank-report", response_model=List[Dict[str, Any]])
async def upload_bank_report(
    file: UploadFile = File(...),
    bank_name: str = Form(...)
):
    """
    Endpoint para subir y procesar un archivo de reporte bancario.
    - file: Archivo del reporte bancario (CSV, PDF, XLS, etc.)
    - bank_name: Nombre del banco emisor del reporte para determinar el formato
    """
    try:
        # Leer el contenido del archivo
        contents = await file.read()
        
        # Validar tipo de banco
        valid_banks = ["santander", "bbva", "caixabank", "sabadell", "bankinter", "ing"]
        if bank_name.lower() not in valid_banks:
            raise HTTPException(
                status_code=400, 
                detail=f"Banco no soportado. Bancos disponibles: {', '.join(valid_banks)}"
            )
        
        # Procesar el reporte basado en el banco
        transactions = process_bank_report(contents, bank_name.lower())
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")
