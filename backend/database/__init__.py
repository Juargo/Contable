from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contable.db")

# Configurar el motor de la base de datos
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear todas las tablas
def create_tables():
    # Importamos aquí para evitar problemas de importación circular
    from models.budget import Budget, BudgetCategory, SubcategoryBudget
    from models.category import Category
    from models.transaction import Transaction
    
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas o verificadas exitosamente.")
