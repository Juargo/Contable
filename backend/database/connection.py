"""Configuración de la conexión a la base de datos"""

import os
from tortoise import Tortoise

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "moneydairy_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "moneydairy_password")
DB_NAME = os.getenv("DB_NAME", "moneydairy_db")

# URL de conexión para Tortoise ORM
DATABASE_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración de Tortoise
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Inicializar la conexión a la base de datos"""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["database.models"]}
    )
    # Genera esquemas solamente si no existen las tablas (las tablas ya se crearon con SQL)
    # await Tortoise.generate_schemas(safe=True)

async def close_db():
    """Cerrar la conexión a la base de datos"""
    await Tortoise.close_connections()
