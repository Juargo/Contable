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
    SubcategoryCreate, SubcategoryResponse, SubcategoryUpdate,
    CategoryKeywordCreate, CategoryKeywordResponse
)

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

# Endpoints para Categorías principales
@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(
        name=category.name,
        description=category.description,
        type=category.type,
        parent_id=None  # Asegurar que sea una categoría principal
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Category).filter(Category.parent_id == None)  # Solo categorías principales
    if type:
        query = query.filter(Category.type == type)
    return query.offset(skip).limit(limit).all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id, Category.parent_id == None).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id, Category.parent_id == None).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    update_data = category.dict(exclude_unset=True)
    # Asegurar que parent_id siga siendo None para categorías principales
    if "parent_id" in update_data:
        update_data.pop("parent_id")
    
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # Primero verificar si hay subcategorías dependientes
    subcategories = db.query(Category).filter(Category.parent_id == category_id).count()
    if subcategories > 0:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar una categoría con subcategorías. Elimine primero las subcategorías."
        )
    
    db_category = db.query(Category).filter(Category.id == category_id, Category.parent_id == None).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Categoría eliminada"}

# Endpoints para Subcategorías
@router.post("/{parent_id}/subcategories", response_model=SubcategoryResponse)
def create_subcategory(parent_id: int, subcategory: SubcategoryCreate, db: Session = Depends(get_db)):
    # Verificar si la categoría padre existe
    parent = db.query(Category).filter(Category.id == parent_id, Category.parent_id == None).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Categoría padre no encontrada")
    
    db_subcategory = Category(
        name=subcategory.name,
        description=subcategory.description,
        type=parent.type,  # Heredar el tipo de la categoría padre
        parent_id=parent_id
    )
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    
    # Enriquecer la respuesta con el nombre de la categoría padre
    return {
        **db_subcategory.__dict__,
        "parent_name": parent.name
    }

@router.get("/{parent_id}/subcategories", response_model=List[SubcategoryResponse])
def get_subcategories(
    parent_id: int, 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Verificar si la categoría padre existe
    parent = db.query(Category).filter(Category.id == parent_id, Category.parent_id == None).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Categoría padre no encontrada")
    
    subcategories = db.query(Category).filter(Category.parent_id == parent_id).offset(skip).limit(limit).all()
    
    # Enriquecer la respuesta con el nombre de la categoría padre
    return [{
        **subcategory.__dict__,
        "parent_name": parent.name
    } for subcategory in subcategories]

@router.get("/subcategory/{subcategory_id}", response_model=SubcategoryResponse)
def get_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    subcategory = db.query(Category).filter(Category.id == subcategory_id).filter(Category.parent_id != None).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    # Obtener el nombre de la categoría padre
    parent = db.query(Category).filter(Category.id == subcategory.parent_id).first()
    
    return {
        **subcategory.__dict__,
        "parent_name": parent.name if parent else None
    }

@router.put("/subcategory/{subcategory_id}", response_model=SubcategoryResponse)
def update_subcategory(subcategory_id: int, subcategory: SubcategoryUpdate, db: Session = Depends(get_db)):
    db_subcategory = db.query(Category).filter(Category.id == subcategory_id, Category.parent_id != None).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    # No permitir cambiar la categoría padre desde este endpoint
    update_data = subcategory.dict(exclude={"parent_id"}, exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_subcategory, key, value)
    
    db.commit()
    db.refresh(db_subcategory)
    
    # Obtener el nombre de la categoría padre
    parent = db.query(Category).filter(Category.id == db_subcategory.parent_id).first()
    
    return {
        **db_subcategory.__dict__,
        "parent_name": parent.name if parent else None
    }

@router.delete("/subcategory/{subcategory_id}", status_code=204)
def delete_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    # Verificar si hay presupuestos o transacciones que usen esta subcategoría
    # (Esta verificación depende de la estructura exacta de tus modelos)
    
    db_subcategory = db.query(Category).filter(Category.id == subcategory_id, Category.parent_id != None).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    db.delete(db_subcategory)
    db.commit()
    return {"message": "Subcategoría eliminada"}

# Endpoints para Palabras Clave de Categorías
@router.post("/subcategory/{subcategory_id}/keywords", response_model=CategoryKeywordResponse)
def add_category_keyword(subcategory_id: int, keyword: CategoryKeywordCreate, db: Session = Depends(get_db)):
    # Verificar si la subcategoría existe
    subcategory = db.query(Category).filter(Category.id == subcategory_id, Category.parent_id != None).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    # Verificar si la palabra clave ya existe para esta categoría
    from sqlalchemy import text
    existing = db.execute(text(
        "SELECT id FROM category_keywords WHERE category_id = :category_id AND keyword = :keyword"
    ), {
        "category_id": subcategory_id,
        "keyword": keyword.keyword
    }).fetchone()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Esta palabra clave ya existe para esta categoría"
        )
    
    # Insertar la palabra clave
    result = db.execute(text(
        """
        INSERT INTO category_keywords (category_id, keyword)
        VALUES (:category_id, :keyword)
        """
    ), {
        "category_id": subcategory_id,
        "keyword": keyword.keyword
    })
    
    db.commit()
    
    # Obtener el ID recién creado
    new_id = db.execute(text(
        """
        SELECT LAST_INSERT_ID() as id
        """
    )).fetchone()[0]
    
    return {
        "id": new_id,
        "category_id": subcategory_id,
        "keyword": keyword.keyword,
        "category_name": subcategory.name
    }

@router.get("/subcategory/{subcategory_id}/keywords", response_model=List[CategoryKeywordResponse])
def get_category_keywords(subcategory_id: int, db: Session = Depends(get_db)):
    # Verificar si la subcategoría existe
    subcategory = db.query(Category).filter(Category.id == subcategory_id, Category.parent_id != None).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    
    # Obtener todas las palabras clave
    from sqlalchemy import text
    keywords = db.execute(text(
        """
        SELECT id, category_id, keyword
        FROM category_keywords
        WHERE category_id = :category_id
        """
    ), {"category_id": subcategory_id}).fetchall()
    
    return [{
        "id": keyword[0],
        "category_id": keyword[1],
        "keyword": keyword[2],
        "category_name": subcategory.name
    } for keyword in keywords]

@router.delete("/keywords/{keyword_id}", status_code=204)
def delete_category_keyword(keyword_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text
    result = db.execute(text(
        """
        DELETE FROM category_keywords
        WHERE id = :keyword_id
        """
    ), {"keyword_id": keyword_id})
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Palabra clave no encontrada")
    
    db.commit()
    return {"message": "Palabra clave eliminada"}
