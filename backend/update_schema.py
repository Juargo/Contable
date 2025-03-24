"""Script para actualizar el esquema de la base de datos"""
import asyncio
from tortoise import Tortoise

async def update_db_schema():
    """Actualiza el esquema de la base de datos"""
    # Conecta a la base de datos
    await Tortoise.init(
        db_url="mysql://moneydairy_user:moneydairy_password@localhost:3306/moneydairy_db",
        modules={"models": ["database.models"]}
    )
    
    # Genera esquemas solo para las tablas que no existen
    print("Actualizando esquema de la base de datos...")
    await Tortoise.generate_schemas(safe=True)
    
    print("Esquema actualizado correctamente")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(update_db_schema())
