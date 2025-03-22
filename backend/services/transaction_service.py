"""
Este módulo contiene la lógica para obtener las transacciones procesadas.
"""

# import os
from typing import List, Dict, Any


def get_transactions() -> List[Dict[str, Any]]:
    """
    Obtiene todas las transacciones procesadas.
    Este método puede integrar el código existente para procesar los datos.
    """
    try:
        # Ruta a los archivos de datos (ajustar según la estructura real)
        # data_path = os.path.join(os.path.dirname(__file__), '../../data')

        # Aquí se implementaría la lógica para cargar y procesar los datos
        # utilizando el código existente

        # Datos de ejemplo por ahora
        data = [
            {
                "date": "2023-01-01",
                "description": "Compra en supermercado",
                "category": "Alimentación",
                "amount": -50.25,
            },
            {
                "date": "2023-01-05",
                "description": "Nómina",
                "category": "Ingresos",
                "amount": 1200.00,
            },
            {
                "date": "2023-01-10",
                "description": "Factura luz",
                "category": "Servicios",
                "amount": -75.50,
            },
            {
                "date": "2023-01-15",
                "description": "Devolución",
                "category": "Ingresos",
                "amount": 25.00,
            },
        ]

        return data
    except Exception as e:
        print(f"Error al procesar transacciones: {str(e)}")
        raise
