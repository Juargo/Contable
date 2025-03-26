from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

# Cambiar a importaciones absolutas
from database import get_db
from models.budget import Budget, BudgetCategory, SubcategoryBudget
from models.category import Category
from schemas.budget_schema import (
    BudgetCreate, BudgetResponse, BudgetUpdate, BudgetDetailResponse,
    BudgetCategoryCreate, BudgetCategoryResponse,
    SubcategoryBudgetCreate, SubcategoryBudgetResponse, BudgetVsActualResponse
)

router = APIRouter(
    tags=["budgets"]
)

# Endpoints para Presupuestos
@router.post("/budgets", response_model=BudgetResponse)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    db_budget = Budget(
        name=budget.name,
        description=budget.description,
        start_date=budget.start_date,
        end_date=budget.end_date
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Budget)
    if active_only:
        from datetime import date
        today = date.today()
        query = query.filter(Budget.start_date <= today, Budget.end_date >= today)
    return query.offset(skip).limit(limit).all()

@router.get("/{budget_id}", response_model=BudgetDetailResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    # Obtener categorías asociadas con sus subcategorías y montos
    result = {
        **budget.__dict__,
        "categories": [],
        "total_budgeted": 0
    }
    
    # Obtener todas las categorías del presupuesto
    budget_categories = db.query(
        BudgetCategory.id,
        BudgetCategory.category_id,
        Category.name.label("category_name")
    ).join(
        Category, BudgetCategory.category_id == Category.id
    ).filter(
        BudgetCategory.budget_id == budget_id,
        Category.parent_id == None  # Solo categorías principales
    ).all()
    
    total_budgeted = 0
    
    # Para cada categoría, obtener sus subcategorías
    for bc in budget_categories:
        category_data = {
            "id": bc.id,
            "category_id": bc.category_id,
            "category_name": bc.category_name,
            "subcategories": []
        }
        
        # Obtener subcategorías
        subcategories = db.query(
            Category.id,
            Category.name,
            SubcategoryBudget.amount
        ).outerjoin(
            SubcategoryBudget,
            (SubcategoryBudget.category_id == Category.id) &
            (SubcategoryBudget.budget_id == budget_id)
        ).filter(
            Category.parent_id == bc.category_id
        ).all()
        
        for subcat in subcategories:
            amount = subcat.amount or 0
            total_budgeted += amount
            category_data["subcategories"].append({
                "id": subcat.id,
                "name": subcat.name,
                "amount": amount
            })
            
        result["categories"].append(category_data)
    
    result["total_budgeted"] = total_budgeted
    return result

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget: BudgetUpdate, db: Session = Depends(get_db)):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    update_data = budget.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    db.delete(db_budget)
    db.commit()
    return {"message": "Presupuesto eliminado"}

# Endpoints para Categorías del Presupuesto
@router.post("/{budget_id}/categories", response_model=BudgetCategoryResponse)
def add_category_to_budget(budget_id: int, data: BudgetCategoryCreate, db: Session = Depends(get_db)):
    # Verificar si el presupuesto existe
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    # Verificar si la categoría existe
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar que la categoría no esté ya asociada al presupuesto
    exists = db.query(BudgetCategory).filter(
        BudgetCategory.budget_id == budget_id,
        BudgetCategory.category_id == data.category_id
    ).first()
    
    if exists:
        raise HTTPException(status_code=400, detail="Esta categoría ya está asociada al presupuesto")
    
    # Verificar que sea una categoría principal y no una subcategoría
    if category.parent_id is not None:
        raise HTTPException(
            status_code=400, 
            detail="Solo se pueden asociar categorías principales al presupuesto"
        )
    
    # Crear la asociación
    db_budget_category = BudgetCategory(
        budget_id=budget_id,
        category_id=data.category_id
    )
    
    db.add(db_budget_category)
    db.commit()
    db.refresh(db_budget_category)
    
    # Enriquecer la respuesta con el nombre de la categoría
    result = {
        **db_budget_category.__dict__,
        "category_name": category.name
    }
    
    return result

@router.delete("/{budget_id}/categories/{category_id}", status_code=204)
def remove_category_from_budget(budget_id: int, category_id: int, db: Session = Depends(get_db)):
    # Verificar si existe la asociación
    db_budget_category = db.query(BudgetCategory).filter(
        BudgetCategory.budget_id == budget_id,
        BudgetCategory.category_id == category_id
    ).first()
    
    if not db_budget_category:
        raise HTTPException(
            status_code=404,
            detail="Categoría no asociada a este presupuesto"
        )
    
    # Eliminar todos los presupuestos de subcategorías asociados
    subcategories = db.query(Category).filter(Category.parent_id == category_id).all()
    for subcategory in subcategories:
        db.query(SubcategoryBudget).filter(
            SubcategoryBudget.budget_id == budget_id,
            SubcategoryBudget.category_id == subcategory.id
        ).delete()
    
    # Eliminar la asociación
    db.delete(db_budget_category)
    db.commit()
    
    return {"message": "Categoría eliminada del presupuesto"}

# Endpoints para Subcategorías/Montos del Presupuesto
@router.post("/{budget_id}/subcategories", response_model=SubcategoryBudgetResponse)
def set_subcategory_budget(budget_id: int, data: SubcategoryBudgetCreate, db: Session = Depends(get_db)):
    # Verificar si el presupuesto existe
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    # Verificar si la subcategoría existe
    subcategory = db.query(Category).filter(Category.id == data.category_id).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    # Verificar que sea una subcategoría
    if subcategory.parent_id is None:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden asignar montos a subcategorías, no a categorías principales"
        )
    
    # Verificar que la categoría padre esté asociada al presupuesto
    parent_associated = db.query(BudgetCategory).filter(
        BudgetCategory.budget_id == budget_id,
        BudgetCategory.category_id == subcategory.parent_id
    ).first()
    
    if not parent_associated:
        raise HTTPException(
            status_code=400,
            detail="La categoría padre debe estar asociada al presupuesto primero"
        )
    
    # Verificar si ya existe un presupuesto para esta subcategoría
    existing = db.query(SubcategoryBudget).filter(
        SubcategoryBudget.budget_id == budget_id,
        SubcategoryBudget.category_id == data.category_id
    ).first()
    
    if existing:
        # Actualizar el existente
        existing.amount = data.amount
        db.commit()
        db.refresh(existing)
        result = existing
    else:
        # Crear nuevo
        db_subcategory_budget = SubcategoryBudget(
            budget_id=budget_id,
            category_id=data.category_id,
            amount=data.amount
        )
        db.add(db_subcategory_budget)
        db.commit()
        db.refresh(db_subcategory_budget)
        result = db_subcategory_budget
    
    # Enriquecer la respuesta con nombres
    return {
        **result.__dict__,
        "subcategory_name": subcategory.name,
        "category_id": subcategory.parent_id,
        "category_name": db.query(Category.name).filter(Category.id == subcategory.parent_id).scalar()
    }

@router.put("/{budget_id}/subcategories/{subcategory_id}", response_model=SubcategoryBudgetResponse)
def update_subcategory_budget(
    budget_id: int, subcategory_id: int, data: SubcategoryBudgetCreate, db: Session = Depends(get_db)
):
    # Verificar si existe
    db_subcategory_budget = db.query(SubcategoryBudget).filter(
        SubcategoryBudget.budget_id == budget_id,
        SubcategoryBudget.category_id == subcategory_id
    ).first()
    
    if not db_subcategory_budget:
        raise HTTPException(
            status_code=404,
            detail="No hay presupuesto asignado para esta subcategoría"
        )
    
    # Actualizar monto
    db_subcategory_budget.amount = data.amount
    db.commit()
    db.refresh(db_subcategory_budget)
    
    # Obtener información de la subcategoría
    subcategory = db.query(Category).filter(Category.id == subcategory_id).first()
    
    # Enriquecer la respuesta
    return {
        **db_subcategory_budget.__dict__,
        "subcategory_name": subcategory.name,
        "category_id": subcategory.parent_id,
        "category_name": db.query(Category.name).filter(Category.id == subcategory.parent_id).scalar()
    }

@router.delete("/{budget_id}/subcategories/{subcategory_id}", status_code=204)
def delete_subcategory_budget(budget_id: int, subcategory_id: int, db: Session = Depends(get_db)):
    deleted = db.query(SubcategoryBudget).filter(
        SubcategoryBudget.budget_id == budget_id,
        SubcategoryBudget.category_id == subcategory_id
    ).delete()
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No hay presupuesto asignado para esta subcategoría"
        )
    
    db.commit()
    return {"message": "Presupuesto de subcategoría eliminado"}

# Endpoint para obtener el reporte comparativo
@router.get("/{budget_id}/vs-actual", response_model=List[BudgetVsActualResponse])
def get_budget_vs_actual(budget_id: int, db: Session = Depends(get_db)):
    # Verificar si el presupuesto existe
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    # Ejecutar consulta SQL directa a la vista budget_vs_actual
    from sqlalchemy import text
    result = db.execute(text(
        """
        SELECT 
            category_id, 
            category_name,
            budgeted_amount,
            actual_spent,
            difference
        FROM budget_vs_actual
        WHERE budget_id = :budget_id
        """
    ), {"budget_id": budget_id}).fetchall()
    
    # Convertir resultados de la consulta a la estructura esperada
    return [
        {
            "category_id": row[0],
            "category_name": row[1],
            "budgeted_amount": float(row[2]) if row[2] is not None else 0.0,
            "actual_spent": float(row[3]) if row[3] is not None else 0.0,
            "difference": float(row[4]) if row[4] is not None else 0.0
        }
        for row in result
    ]
