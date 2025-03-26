from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Esquemas para Categorías
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # 'Ingreso' o 'Gasto'

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Esquemas para Subcategorías
class SubcategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubcategoryCreate(SubcategoryBase):
    pass

class SubcategoryUpdate(SubcategoryBase):
    pass

class SubcategoryResponse(SubcategoryBase):
    id: int
    parent_id: int
    parent_name: str
    type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Esquemas para Palabras Clave de Categorías
class CategoryKeywordBase(BaseModel):
    keyword: str

class CategoryKeywordCreate(CategoryKeywordBase):
    pass

class CategoryKeywordResponse(CategoryKeywordBase):
    id: int
    category_id: int
    category_name: str
    
    class Config:
        from_attributes = True
