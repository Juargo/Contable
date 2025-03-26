from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Si este modelo ya existe, mantener su estructura original
# Estamos creándolo como ejemplo mínimo para las referencias en category_routes.py
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255))
    amount = Column(Float)
    date = Column(Date)
    category = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    # Agregar otros campos según sea necesario
    created_at = Column(DateTime(timezone=True), server_default=func.now())
