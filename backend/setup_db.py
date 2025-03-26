"""Script para inicializar la base de datos"""

import sys
import os
# Añadir el directorio actual al path de Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar los modelos y la función para crear tablas
from models.budget import Budget, BudgetCategory, SubcategoryBudget
from models.category import Category
from models.transaction import Transaction
from database import Base, engine

def setup_database():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    setup_database()
