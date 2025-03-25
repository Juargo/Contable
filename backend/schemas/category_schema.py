from pydantic import BaseModel
from typing import List, Optional

# Base Schema for Category
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None  # Para representación visual

class CategoryCreate(CategoryBase):
    pass

class SubcategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class CategoryWithSubcategoriesResponse(CategoryResponse):
    subcategories: List[CategoryResponse] = []
