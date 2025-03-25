from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

# Cambiar a importaciones absolutas
from database import get_db
from models.category import Category
from models.transaction import Transaction
from models.budget import BudgetCategory, SubcategoryBudget
from schemas.category_schema import (
    CategoryCreate, CategoryResponse, CategoryUpdate, 
    CategoryWithSubcategoriesResponse, SubcategoryCreate
)

router = APIRouter(
    prefix="/api/categories",
    tags=["categories"]
)

# Endpoints para Categorías
@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    parent_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Category)
    if parent_only:
        query = query.filter(Category.parent_id == None)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(
        name=category.name,
        description=category.description,
        color=category.color
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/{category_id}", response_model=CategoryWithSubcategoriesResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Si es una categoría padre, obtener sus subcategorías
    subcategories = []
    if category.parent_id is None:  # Es una categoría padre
        subcategories = db.query(Category).filter(
            Category.parent_id == category_id
        ).all()
    
    result = {
        **category.__dict__,
        "subcategories": subcategories
    }
    
    return result

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # Verificar si la categoría existe
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar si tiene subcategorías
    has_subcategories = db.query(Category).filter(Category.parent_id == category_id).first() is not None
    
    # Verificar si está siendo utilizada en transacciones
    has_transactions = db.query(Transaction).filter(
        or_(
            Transaction.category == category_id,
            Transaction.subcategory_id == category_id
        )
    ).first() is not None
    
    # Verificar si está siendo utilizada en presupuestos
    is_in_budget = db.query(BudgetCategory).filter(
        BudgetCategory.category_id == category_id
    ).first() is not None
    
    is_in_subcat_budget = db.query(SubcategoryBudget).filter(
        SubcategoryBudget.category_id == category_id
    ).first() is not None
    
    if has_subcategories or has_transactions or is_in_budget or is_in_subcat_budget:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la categoría porque está siendo utilizada"
        )
    
    # Eliminar la categoría
    db.delete(db_category)
    db.commit()
    return {"message": "Categoría eliminada"}

# Endpoints para Subcategorías
@router.get("/{parent_id}/subcategories", response_model=List[CategoryResponse])
def get_subcategories(parent_id: int, db: Session = Depends(get_db)):
    # Verificar si la categoría padre existe
    parent = db.query(Category).filter(Category.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Categoría padre no encontrada")
    
    # Obtener sus subcategorías
    return db.query(Category).filter(Category.parent_id == parent_id).all()

@router.post("/{parent_id}/subcategories", response_model=CategoryResponse)
def create_subcategory(parent_id: int, subcategory: SubcategoryCreate, db: Session = Depends(get_db)):
    # Verificar si la categoría padre existe
    parent = db.query(Category).filter(Category.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Categoría padre no encontrada")
    
    # Verificar que la categoría padre no sea a su vez una subcategoría
    if parent.parent_id is not None:
        raise HTTPException(
            status_code=400,
            detail="No se pueden crear subcategorías anidadas"
        )
    
    # Crear la subcategoría
    db_subcategory = Category(
        name=subcategory.name,
        description=subcategory.description,
        color=subcategory.color,
        parent_id=parent_id
    )
    
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory
