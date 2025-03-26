from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Cambiar a importación absoluta
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(50), nullable=True)  # Para representación visual
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    
    # Corregir la relación recursiva para subcategorías
    subcategories = relationship(
        "Category", 
        backref="parent",
        remote_side=[id],
        cascade="all"  # Eliminar "delete-orphan" de la cascada
    )
