from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import sys
import os

# Añadir la ruta de los scripts actuales para poder importarlos
sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))

# Importar funciones necesarias de los scripts existentes
# Asumiendo que tenemos un módulo que procesa las transacciones
try:
    from services.transaction_service import get_transactions
except ImportError:
    # Función provisional si aún no existe el módulo
    def get_transactions() -> List[Dict[str, Any]]:
        # Datos de ejemplo
        return [
            {"date": "2023-01-01", "description": "Compra en supermercado", "category": "Alimentación", "amount": -50.25},
            {"date": "2023-01-05", "description": "Nómina", "category": "Ingresos", "amount": 1200.00},
        ]

router = APIRouter(tags=["transactions"])

@router.get("/transactions", response_model=List[Dict[str, Any]])
async def read_transactions():
    try:
        transactions = get_transactions()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")
