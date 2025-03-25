import React, { useState, useEffect } from 'react';
import { API_URL } from '../../config/constants';
import BudgetForm from './BudgetForm';
import CategorySelector from './CategorySelector';

interface Subcategory {
  id: number;
  name: string;
  amount: number;
}

interface CategoryWithSubcategories {
  id: number;
  category_id: number;
  category_name: string;
  subcategories: Subcategory[];
}

interface BudgetDetail {
  id: number;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
  categories: CategoryWithSubcategories[];
  total_budgeted: number;
}

interface BudgetVsActual {
  category_id: number;
  category_name: string;
  budgeted_amount: number;
  actual_spent: number;
  difference: number;
}

interface BudgetDetailProps {
  budgetId: number;
  onBack: () => void;
  onRefresh: () => void;
}

export default function BudgetDetail({ budgetId, onBack, onRefresh }: BudgetDetailProps) {
  const [budget, setBudget] = useState<BudgetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [actualData, setActualData] = useState<BudgetVsActual[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  
  useEffect(() => {
    fetchBudgetDetail();
  }, [budgetId]);
  
  const fetchBudgetDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}`);
      
      if (!response.ok) {
        throw new Error('Error al cargar el detalle del presupuesto');
      }
      
      const data = await response.json();
      setBudget(data);
      
      // También cargar los datos de comparación
      fetchActualData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchActualData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}/vs-actual`);
      if (!response.ok) {
        throw new Error('Error al cargar datos comparativos');
      }
      const data = await response.json();
      setActualData(data);
    } catch (err) {
      console.error('Error al cargar datos comparativos:', err);
    }
  };
  
  const handleEditBudget = () => {
    setIsEditing(true);
  };
  
  const handleBudgetUpdated = () => {
    setIsEditing(false);
    fetchBudgetDetail();
    onRefresh();
  };
  
  const handleAddCategory = () => {
    setShowAddCategory(true);
  };
  
  const handleCategorySelected = async (categoryId: number, categoryName: string) => {
    try {
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ category_id: categoryId })
      });
      
      if (!response.ok) {
        throw new Error('Error al añadir la categoría al presupuesto');
      }
      
      setShowAddCategory(false);
      fetchBudgetDetail();
    } catch (err: any) {
      setError(err.message);
    }
  };
  
  const handleRemoveCategory = async (categoryId: number) => {
    if (!window.confirm('¿Estás seguro que deseas eliminar esta categoría del presupuesto?')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}/categories/${categoryId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar la categoría del presupuesto');
      }
      
      fetchBudgetDetail();
    } catch (err: any) {
      setError(err.message);
    }
  };
  
  const handleSetSubcategoryBudget = async (subcategoryId: number, amount: number) => {
    try {
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}/subcategories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          category_id: subcategoryId,
          amount: amount
        })
      });
      
      if (!response.ok) {
        throw new Error('Error al asignar monto a la subcategoría');
      }
      
      fetchBudgetDetail();
    } catch (err: any) {
      setError(err.message);
    }
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    // Usar formateo nativo en lugar de date-fns
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };
  
  const formatAmount = (amount: number) => {
    return amount.toLocaleString('es-CL', {
      style: 'currency',
      currency: 'CLP',
      maximumFractionDigits: 0
    });
  };
  
  if (loading) {
    return <div className="loading">Cargando presupuesto...</div>;
  }
  
  if (error) {
    return <div className="error-message">{error}</div>;
  }
  
  if (!budget) {
    return <div className="error-message">No se pudo cargar el presupuesto</div>;
  }
  
  if (isEditing) {
    return (
      <BudgetForm
        budgetId={budgetId}
        onSave={handleBudgetUpdated}
        onCancel={() => setIsEditing(false)}
      />
    );
  }
  
  if (showAddCategory) {
    return (
      <div className="category-selection">
        <div className="header-actions">
          <button className="back-btn" onClick={() => setShowAddCategory(false)}>
            ← Volver al presupuesto
          </button>
        </div>
        <h3>Añadir categoría al presupuesto</h3>
        <CategorySelector
          budgetId={budgetId}
          onSelectCategory={handleCategorySelected}
          excludedCategories={budget.categories.map(c => c.category_id)}
        />
      </div>
    );
  }
  
  return (
    <div className="budget-detail">
      <div className="header-actions">
        <button className="back-btn" onClick={onBack}>
          ← Volver a la lista
        </button>
        <div className="action-buttons">
          <button 
            className="compare-btn" 
            onClick={() => setShowComparison(!showComparison)}
          >
            {showComparison ? 'Ver Detalle' : 'Ver vs. Real'}
          </button>
          <button className="edit-btn" onClick={handleEditBudget}>
            Editar
          </button>
        </div>
      </div>
      
      <div className="budget-header">
        <h2>{budget.name}</h2>
        {budget.description && <p className="description">{budget.description}</p>}
        
        <div className="budget-meta">
          <div className="meta-item">
            <span className="meta-label">Periodo:</span>
            <span className="meta-value">
              {formatDate(budget.start_date)} - {formatDate(budget.end_date)}
            </span>
          </div>
          
          <div className="meta-item">
            <span className="meta-label">Total Presupuestado:</span>
            <span className="meta-value total-budget">
              {formatAmount(budget.total_budgeted)}
            </span>
          </div>
        </div>
      </div>
      
      {showComparison ? (
        <div className="comparison-section">
          <h3>Comparación Presupuesto vs. Gasto Real</h3>
          
          {actualData.length === 0 ? (
            <div className="no-data">
              No hay datos de comparación disponibles
            </div>
          ) : (
            <div className="comparison-table-container">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Categoría</th>
                    <th>Presupuestado</th>
                    <th>Gastado</th>
                    <th>Diferencia</th>
                  </tr>
                </thead>
                <tbody>
                  {actualData.map(item => (
                    <tr key={item.category_id} className={item.difference < 0 ? 'negative' : 'positive'}>
                      <td>{item.category_name}</td>
                      <td>{formatAmount(item.budgeted_amount)}</td>
                      <td>{formatAmount(Math.abs(item.actual_spent))}</td>
                      <td className={item.difference < 0 ? 'negative' : 'positive'}>
                        {formatAmount(item.difference)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <div className="budget-content">
          <div className="section-header">
            <h3>Categorías y Subcategorías</h3>
            <button className="add-btn" onClick={handleAddCategory}>
              Añadir Categoría
            </button>
          </div>
          
          {budget.categories.length === 0 ? (
            <div className="no-categories">
              <p>Este presupuesto no tiene categorías asignadas.</p>
              <button className="add-btn" onClick={handleAddCategory}>
                Añadir Primera Categoría
              </button>
            </div>
          ) : (
            <div className="categories-list">
              {budget.categories.map(category => (
                <div key={category.id} className="category-card">
                  <div className="category-header">
                    <h4>{category.category_name}</h4>
                    <button 
                      className="remove-btn"
                      onClick={() => handleRemoveCategory(category.category_id)}
                    >
                      Eliminar
                    </button>
                  </div>
                  
                  <div className="subcategories">
                    <table className="subcategories-table">
                      <thead>
                        <tr>
                          <th>Subcategoría</th>
                          <th>Monto</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {category.subcategories.map(sub => (
                          <tr key={sub.id}>
                            <td>{sub.name}</td>
                            <td>{formatAmount(sub.amount)}</td>
                            <td>
                              <button 
                                className="edit-amount-btn"
                                onClick={() => {
                                  const amount = prompt('Ingrese el nuevo monto:', sub.amount.toString());
                                  if (amount !== null) {
                                    const numAmount = parseFloat(amount);
                                    if (!isNaN(numAmount) && numAmount > 0) {
                                      handleSetSubcategoryBudget(sub.id, numAmount);
                                    } else {
                                      alert('Por favor ingrese un monto válido mayor a 0');
                                    }
                                  }
                                }}
                              >
                                Editar
                              </button>
                            </td>
                          </tr>
                        ))}
                        {category.subcategories.length === 0 && (
                          <tr>
                            <td colSpan={3} className="no-subcats">
                              No hay subcategorías con montos asignados
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <style jsx>{`
        .budget-detail {
          width: 100%;
        }
        
        .header-actions {
          display: flex;
          justify-content: space-between;
          margin-bottom: 1.5rem;
        }
        
        .back-btn {
          background-color: transparent;
          border: 1px solid #ddd;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
        }
        
        .action-buttons {
          display: flex;
          gap: 0.75rem;
        }
        
        .compare-btn {
          background-color: #3f51b5;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .edit-btn {
          background-color: #ff9800;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .budget-header {
          background-color: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 1.5rem;
        }
        
        .description {
          margin-top: 0.5rem;
          color: #666;
        }
        
        .budget-meta {
          display: flex;
          justify-content: space-between;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #eee;
          flex-wrap: wrap;
        }
        
        .meta-item {
          margin-bottom: 0.5rem;
        }
        
        .meta-label {
          font-weight: 600;
          margin-right: 0.5rem;
        }
        
        .total-budget {
          font-weight: 700;
          color: #4caf50;
          font-size: 1.1rem;
        }
        
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .add-btn {
          background-color: #4caf50;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .no-categories {
          background-color: #f5f5f5;
          padding: 2rem;
          text-align: center;
          border-radius: 8px;
        }
        
        .no-categories button {
          margin-top: 1rem;
        }
        
        .categories-list {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1rem;
        }
        
        .category-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }
        
        .category-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #f5f5f5;
          border-bottom: 1px solid #eee;
        }
        
        .category-header h4 {
          margin: 0;
        }
        
        .remove-btn {
          background-color: #f44336;
          color: white;
          border: none;
          padding: 0.4rem 0.8rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
        }
        
        .subcategories {
          padding: 1rem;
        }
        
        .subcategories-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .subcategories-table th,
        .subcategories-table td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #eee;
        }
        
        .subcategories-table th {
          font-weight: 600;
          color: #555;
        }
        
        .edit-amount-btn {
          background-color: #2196f3;
          color: white;
          border: none;
          padding: 0.3rem 0.6rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
        }
        
        .no-subcats {
          text-align: center;
          color: #666;
          padding: 1rem 0;
          font-style: italic;
        }
        
        .comparison-section {
          background-color: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .comparison-section h3 {
          margin-top: 0;
          margin-bottom: 1rem;
        }
        
        .comparison-table-container {
          overflow-x: auto;
        }
        
        .comparison-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .comparison-table th,
        .comparison-table td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #eee;
        }
        
        .comparison-table th {
          font-weight: 600;
          color: #555;
        }
        
        .comparison-table .positive {
          color: #4caf50;
        }
        
        .comparison-table .negative {
          color: #f44336;
        }
        
        .no-data {
          text-align: center;
          padding: 2rem;
          color: #666;
          font-style: italic;
        }
        
        .loading, .error-message {
          text-align: center;
          padding: 2rem;
        }
        
        .error-message {
          color: #f44336;
          background-color: #ffebee;
          border-radius: 8px;
        }
        
        .category-selection {
          width: 100%;
        }
      `}</style>
    </div>
  );
}
