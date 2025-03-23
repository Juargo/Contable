"""Archivo principal de la API"""

import os
import sys
# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from contextlib import asynccontextmanager

import uvicorn
from api.banks import router as banks_router
from api.transactions import router as transactions_router
from database.connection import close_db, init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from config.cors import setup_cors


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manejador de eventos de ciclo de vida de la aplicación"""
    # Código que se ejecuta al iniciar la aplicación
    await init_db()
    yield
    # Código que se ejecuta al detener la aplicación
    await close_db()

app = FastAPI(
    title="Contable API",
    description="API para la aplicación de gestión financiera MoneyDairy",
    lifespan=lifespan
)

# Configurar CORS
setup_cors(app)

# Registrar Tortoise
register_tortoise(
    app,
    db_url="mysql://moneydairy_user:moneydairy_password@localhost:3306/moneydairy_db",
    modules={"models": ["database.models"]},
    generate_schemas=False,  # No generamos esquemas porque ya existen
    add_exception_handlers=True,
)

# Incluir routers
app.include_router(transactions_router, prefix="/api")
app.include_router(banks_router, prefix="/api")


@app.get("/")
async def read_root():
    """Ruta raíz de la API"""
    return {"message": "Bienvenido a la API de MoneyDairy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
