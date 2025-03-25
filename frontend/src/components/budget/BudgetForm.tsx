import React, { useState, useEffect } from 'react';
import { API_URL } from '../../config/constants';

interface BudgetFormProps {
  budgetId?: number;
  onSave: () => void;
  onCancel: () => void;
}

export default function BudgetForm({ budgetId, onSave, onCancel }: BudgetFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar datos del presupuesto si estamos en modo edición
  useEffect(() => {
    if (budgetId) {
      loadBudget();
    } else {
      // Para un nuevo presupuesto, establecer fechas por defecto
      const today = new Date();
      const nextMonth = new Date(today);
      nextMonth.setMonth(today.getMonth() + 1);
      
      setFormData({
        name: '',
        description: '',
        start_date: formatDateForInput(today),
        end_date: formatDateForInput(nextMonth)
      });
    }
  }, [budgetId]);

  const formatDateForInput = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  const loadBudget = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/budgets/${budgetId}`);
      
      if (!response.ok) {
        throw new Error('Error al cargar los datos del presupuesto');
      }
      
      const data = await response.json();
      
      setFormData({
        name: data.name,
        description: data.description || '',
        start_date: formatDateForInput(new Date(data.start_date)),
        end_date: formatDateForInput(new Date(data.end_date))
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validaciones básicas
    if (!formData.name.trim()) {
      setError('El nombre del presupuesto es obligatorio');
      return;
    }
    
    if (!formData.start_date || !formData.end_date) {
      setError('Las fechas de inicio y fin son obligatorias');
      return;
    }
    
    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);
    
    if (endDate < startDate) {
      setError('La fecha de fin debe ser posterior a la fecha de inicio');
      return;
    }
    
    try {
      setSaving(true);
      
      const url = budgetId 
        ? `${API_URL}/api/budgets/${budgetId}`
        : `${API_URL}/api/budgets`;
      
      const method = budgetId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar el presupuesto');
      }
      
      // Notificar al componente padre que el guardado fue exitoso
      onSave();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando datos del presupuesto...</div>;
  }

  return (
    <div className="budget-form">
      <h2>{budgetId ? 'Editar Presupuesto' : 'Crear Nuevo Presupuesto'}</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Nombre*</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Ej: Presupuesto Mensual"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Descripción</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Descripción opcional"
            rows={3}
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="start_date">Fecha de Inicio*</label>
            <input
              type="date"
              id="start_date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="end_date">Fecha de Fin*</label>
            <input
              type="date"
              id="end_date"
              name="end_date"
              value={formData.end_date}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className="actions">
          <button 
            type="button"
            onClick={onCancel}
            className="cancel-btn"
            disabled={saving}
          >
            Cancelar
          </button>
          
          <button 
            type="submit" 
            className="save-btn"
            disabled={saving}
          >
            {saving 
              ? 'Guardando...' 
              : (budgetId ? 'Actualizar Presupuesto' : 'Crear Presupuesto')
            }
          </button>
        </div>
      </form>
      
      <style jsx>{`
        .budget-form {
          background-color: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          color: #333;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        input, textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
          font-family: inherit;
        }
        
        input:focus, textarea:focus {
          outline: none;
          border-color: #3f51b5;
          box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
        }
        
        .actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 1.5rem;
        }
        
        button {
          padding: 0.75rem 1rem;
          border-radius: 4px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .cancel-btn {
          background-color: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .cancel-btn:hover {
          background-color: #eee;
        }
        
        .save-btn {
          background-color: #4caf50;
          color: white;
          border: none;
        }
        
        .save-btn:hover {
          background-color: #388e3c;
        }
        
        .save-btn:disabled {
          background-color: #a5d6a7;
          cursor: not-allowed;
        }
        
        .error-message {
          background-color: #ffebee;
          color: #c62828;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          border-left: 4px solid #f44336;
        }
        
        .loading {
          text-align: center;
          padding: 2rem;
        }
      `}</style>
    </div>
  );
}
