"""Archivo principal de la API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.transactions import router as transactions_router
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI(
    title="MoneyDairy API",
    description="API para la aplicación de gestión financiera MoneyDairy",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4321",
    ],  # Orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(transactions_router, prefix="/api")

# Configurar Tortoise ORM
register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['database.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
async def read_root():
    """Ruta raíz de la API"""
    return {"message": "Bienvenido a la API de MoneyDairy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)