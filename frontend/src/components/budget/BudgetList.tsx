import React, { useState, useEffect } from 'react';
import { API_URL } from '../../config/constants';

interface Budget {
  id: number;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
}

interface BudgetListProps {
  onSelectBudget: (budgetId: number) => void;
  onCreateBudget: () => void;
}

export default function BudgetList({ onSelectBudget, onCreateBudget }: BudgetListProps) {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/budgets`);
      
      if (!response.ok) {
        throw new Error('Error al cargar la lista de presupuestos');
      }
      
      const data = await response.json();
      setBudgets(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBudget = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('¿Estás seguro que deseas eliminar este presupuesto?')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/budgets/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar el presupuesto');
      }
      
      // Actualizar la lista
      fetchBudgets();
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

  if (loading) {
    return <div className="loading">Cargando presupuestos...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="budget-list">
      <div className="budget-list-header">
        <h2>Presupuestos</h2>
        <button className="create-budget-btn" onClick={onCreateBudget}>
          Crear Nuevo Presupuesto
        </button>
      </div>
      
      {budgets.length === 0 ? (
        <div className="empty-state">
          <p>No hay presupuestos creados.</p>
          <button onClick={onCreateBudget} className="create-budget-btn">
            Crear mi primer presupuesto
          </button>
        </div>
      ) : (
        <div className="budget-cards">
          {budgets.map(budget => (
            <div 
              key={budget.id} 
              className="budget-card"
              onClick={() => onSelectBudget(budget.id)}
            >
              <div className="budget-card-header">
                <h3>{budget.name}</h3>
                <button 
                  className="delete-btn"
                  onClick={(e) => handleDeleteBudget(budget.id, e)}
                >
                  ✕
                </button>
              </div>
              <div className="budget-card-content">
                <p className="budget-description">
                  {budget.description || 'Sin descripción'}
                </p>
                <div className="budget-dates">
                  <div className="date-label">Periodo:</div>
                  <div className="date-range">
                    {formatDate(budget.start_date)} - {formatDate(budget.end_date)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .budget-list {
          width: 100%;
        }
        
        .budget-list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .create-budget-btn {
          background-color: #4caf50;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.5rem 1rem;
          cursor: pointer;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .create-budget-btn:hover {
          background-color: #388e3c;
        }
        
        .empty-state {
          background-color: #f5f5f5;
          border-radius: 8px;
          padding: 2rem;
          text-align: center;
        }
        
        .empty-state p {
          margin-bottom: 1rem;
          color: #666;
        }
        
        .budget-cards {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }
        
        .budget-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1rem;
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        
        .budget-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        .budget-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .budget-card h3 {
          margin: 0;
        }
        
        .delete-btn {
          background-color: #f44336;
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 12px;
          transition: background-color 0.2s;
        }
        
        .delete-btn:hover {
          background-color: #d32f2f;
        }
        
        .budget-description {
          color: #666;
          margin-bottom: 1rem;
        }
        
        .budget-dates {
          display: flex;
          flex-direction: column;
          font-size: 0.85rem;
          color: #333;
        }
        
        .date-label {
          font-weight: 600;
          margin-bottom: 0.2rem;
        }
        
        .date-range {
          color: #555;
        }
        
        .loading {
          text-align: center;
          padding: 2rem;
        }
        
        .error-message {
          background-color: #ffebee;
          color: #c62828;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1rem;
        }
      `}</style>
    </div>
  );
}
