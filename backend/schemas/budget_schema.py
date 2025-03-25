from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# Schemas for Budget
class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BudgetResponse(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Cambiado de 'orm_mode' a 'from_attributes'

# Schemas for BudgetCategory
class BudgetCategoryBase(BaseModel):
    category_id: int

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategoryResponse(BudgetCategoryBase):
    id: int
    budget_id: int
    category_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Cambiado de 'orm_mode' a 'from_attributes'

# Schemas for SubcategoryBudget
class SubcategoryBudgetBase(BaseModel):
    category_id: int  # ID de la subcategoría
    amount: float = Field(..., gt=0)  # El monto debe ser positivo

class SubcategoryBudgetCreate(SubcategoryBudgetBase):
    pass

class SubcategoryBudgetResponse(BaseModel):
    id: int
    budget_id: int
    category_id: int  # ID de la categoría padre
    category_name: str  # Nombre de la categoría padre
    subcategory_name: str  # Nombre de la subcategoría
    amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Cambiado de 'orm_mode' a 'from_attributes'

# Schema for Subcategory with Budget Amount
class SubcategoryWithBudget(BaseModel):
    id: int
    name: str
    amount: float

# Schema for Category with its Subcategories and Budget Amounts
class BudgetCategoryDetail(BaseModel):
    id: int
    category_id: int
    category_name: str
    subcategories: List[SubcategoryWithBudget]

# Schema for Budget Detail (with Categories and Subcategories)
class BudgetDetailResponse(BudgetResponse):
    categories: List[BudgetCategoryDetail]
    total_budgeted: float

# Schema for Budget vs Actual Comparison
class BudgetVsActualResponse(BaseModel):
    category_id: int
    category_name: str
    budgeted_amount: float
    actual_spent: float
    difference: float
    
    class Config:
        from_attributes = True  # Cambiado de 'orm_mode' a 'from_attributes'
