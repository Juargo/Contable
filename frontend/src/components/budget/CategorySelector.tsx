import React, { useState, useEffect } from 'react';
import { API_URL } from '../../config/constants';

interface Category {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
}

interface CategorySelectorProps {
  budgetId: number;
  onSelectCategory: (categoryId: number, categoryName: string) => void;
  excludedCategories?: number[];
}

export default function CategorySelector({
  budgetId,
  onSelectCategory,
  excludedCategories = []
}: CategorySelectorProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/categories?parent_only=true`);  // Cambiar "/api/categories" a solo "/categories"
      
      if (!response.ok) {
        throw new Error('Error al cargar las categorías');
      }
      
      const data = await response.json();
      
      // Filtrar las categorías que ya están excluidas
      const filteredCategories = data.filter(
        (cat: Category) => !excludedCategories.includes(cat.id)
      );
      
      setCategories(filteredCategories);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (category: Category) => {
    onSelectCategory(category.id, category.name);
  };

  if (loading) {
    return <div className="loading">Cargando categorías...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="category-selector">
      <h3>Seleccionar Categoría</h3>
      
      {categories.length === 0 ? (
        <div className="empty-state">
          <p>No hay categorías disponibles</p>
          <a href="/categorias" className="create-link">Crear categorías</a>
        </div>
      ) : (
        <div className="categories-grid">
          {categories.map(category => (
            <div
              key={category.id}
              className="category-item"
              style={{ borderColor: category.color || '#ddd' }}
              onClick={() => handleCategoryClick(category)}
            >
              <div 
                className="color-indicator" 
                style={{ backgroundColor: category.color || '#ddd' }}
              />
              <div className="category-info">
                <div className="category-name">{category.name}</div>
                {category.description && (
                  <div className="category-description">{category.description}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      <style jsx>{`
        .category-selector {
          padding: 1rem;
        }
        
        h3 {
          margin-top: 0;
          margin-bottom: 1rem;
        }
        
        .empty-state {
          text-align: center;
          padding: 1.5rem;
          background-color: #f5f5f5;
          border-radius: 4px;
        }
        
        .create-link {
          display: inline-block;
          margin-top: 0.5rem;
          color: #3f51b5;
          text-decoration: underline;
          font-weight: 500;
        }
        
        .categories-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
        }
        
        .category-item {
          display: flex;
          align-items: center;
          padding: 1rem;
          border: 1px solid #ddd;
          border-left-width: 3px;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .category-item:hover {
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }
        
        .color-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 1rem;
        }
        
        .category-info {
          flex: 1;
        }
        
        .category-name {
          font-weight: 500;
          color: #333;
        }
        
        .category-description {
          font-size: 0.85rem;
          color: #666;
          margin-top: 0.25rem;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .error-message {
          background-color: #ffebee;
          color: #c62828;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1rem;
        }
        
        .loading {
          text-align: center;
          padding: 1rem;
        }
      `}</style>
    </div>
  );
}
