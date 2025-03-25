import { useState, useEffect } from 'react';
import { API_URL } from '../config/constants';

interface Transaction {
  id: number;
  transaction_date: string;
  description: string;
  amount: number;
  category: string;
  bank_id: number | null;
  tipo: string; // Campo nuevo para el tipo (Ingreso/Gasto)
}

interface TransactionDetail {
  id: number;
  transaction_date: string;
  description: string;
  amount: number;
  category: string;
}

interface TransactionGroup {
  description: string;
  total_amount: number;
  count: number;
  bank_id: number | null;
  bank_name: string | null;
  transactions: TransactionDetail[];
}

interface Bank {
  id: number;
  name: string;
}

type TabType = 'all' | 'grouped';

export default function TransactionsList() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [groupedTransactions, setGroupedTransactions] = useState<TransactionGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1); // Mes actual (1-12)
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [banks, setBanks] = useState<Bank[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchTransactionsByMonth();
    fetchGroupedTransactions();
    fetchBanks();
  }, [month, year]);

  const fetchTransactionsByMonth = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/transactions-by-month?month=${month}&year=${year}`);
      
      if (!response.ok) {
        throw new Error('Error al cargar las transacciones');
      }
      
      const data = await response.json();
      setTransactions(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroupedTransactions = async () => {
    try {
      const response = await fetch(`${API_URL}/transactions-grouped-by-month?month=${month}&year=${year}`);
      
      if (!response.ok) {
        throw new Error('Error al cargar transacciones agrupadas');
      }
      
      const data = await response.json();
      setGroupedTransactions(data);
    } catch (err) {
      console.error('Error al cargar transacciones agrupadas:', err);
      // No establecemos error global para no afectar la visualización principal
    }
  };

  const fetchBanks = async () => {
    try {
      const response = await fetch(`${API_URL}/banks`);
      if (response.ok) {
        const data = await response.json();
        setBanks(data);
      }
    } catch (err) {
      console.error('Error al cargar los bancos:', err);
    }
  };

  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setMonth(parseInt(e.target.value));
  };

  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setYear(parseInt(e.target.value));
  };

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  const getBankName = (bankId: number | null) => {
    if (!bankId) return 'No especificado';
    const bank = banks.find(b => b.id === bankId);
    return bank ? bank.name : `Banco ID: ${bankId}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    });
  };

  const formatAmount = (amount: number) => {
    return amount.toLocaleString('es-CL', { 
      style: 'currency', 
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0 
    });
  };

  // Manejar la expansión/contracción de grupos
  const toggleGroupExpansion = (groupKey: string) => {
    const newExpandedGroups = new Set(expandedGroups);
    if (newExpandedGroups.has(groupKey)) {
      newExpandedGroups.delete(groupKey);
    } else {
      newExpandedGroups.add(groupKey);
    }
    setExpandedGroups(newExpandedGroups);
  };

  // Generar opciones para el selector de meses
  const monthOptions = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' }
  ];

  // Generar opciones para el selector de años
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

  // Calcular el total gastado
  const totalAmount = transactions.reduce((sum, transaction) => sum + transaction.amount, 0);

  if (loading) return <div className="loading">Cargando transacciones...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="transactions-list">
      <div className="filter-controls">
        <div className="filter-group">
          <label htmlFor="month-select">Mes:</label>
          <select 
            id="month-select" 
            value={month} 
            onChange={handleMonthChange}
          >
            {monthOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="year-select">Año:</label>
          <select 
            id="year-select" 
            value={year} 
            onChange={handleYearChange}
          >
            {yearOptions.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>
      
      {(transactions.length > 0 || groupedTransactions.length > 0) ? (
        <>
          <div className="summary-card">
            <div className="summary-item">
              <span className="summary-label">Total de transacciones:</span>
              <span className="summary-value">{transactions.length}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total gastado:</span>
              <span className="summary-value">{formatAmount(totalAmount)}</span>
            </div>
          </div>
          
          <div className="tabs-container">
            <div className="tabs">
              <button 
                className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => handleTabChange('all')}
              >
                Transacciones
              </button>
              <button 
                className={`tab ${activeTab === 'grouped' ? 'active' : ''}`}
                onClick={() => handleTabChange('grouped')}
              >
                Gastos Agrupados
              </button>
            </div>
            
            <div className="tab-content">
              {activeTab === 'all' ? (
                <table className="transactions-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Descripción</th>
                      <th>Categoría</th>
                      <th>Banco</th>
                      <th>Monto</th>
                      <th>Tipo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(transaction => (
                      <tr key={transaction.id} className={transaction.tipo.toLowerCase()}>
                        <td>{formatDate(transaction.transaction_date)}</td>
                        <td>{transaction.description}</td>
                        <td>{transaction.category}</td>
                        <td>{getBankName(transaction.bank_id)}</td>
                        <td className="amount">{formatAmount(transaction.amount)}</td>
                        <td className={`tipo ${transaction.tipo.toLowerCase()}`}>{transaction.tipo}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="accordion-container">
                  {groupedTransactions.map((group, index) => {
                    // Determinar el tipo basado en el monto total
                    const tipo = group.total_amount >= 0 ? "Ingreso" : "Gasto";
                    
                    // Crear un identificador único para este grupo
                    const groupKey = `group-${index}-${group.description}`;
                    
                    // Verificar si el grupo está expandido
                    const isExpanded = expandedGroups.has(groupKey);
                    
                    return (
                      <div key={groupKey} className={`accordion-item ${tipo.toLowerCase()}`}>
                        <div 
                          className="accordion-header" 
                          onClick={() => toggleGroupExpansion(groupKey)}
                        >
                          <div className="accordion-title">
                            <span className="group-description">{group.description}</span>
                            <span className="group-bank">
                              {group.bank_name || getBankName(group.bank_id)}
                            </span>
                          </div>
                          <div className="accordion-summary">
                            <span className="group-count">{group.count} transacción{group.count !== 1 ? 'es' : ''}</span>
                            <span className="group-amount">{formatAmount(group.total_amount)}</span>
                            <span className={`group-tipo ${tipo.toLowerCase()}`}>{tipo}</span>
                            <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                              &#9660;
                            </span>
                          </div>
                        </div>
                        
                        {isExpanded && (
                          <div className="accordion-content">
                            <table className="details-table">
                              <thead>
                                <tr>
                                  <th>Fecha</th>
                                  <th>Categoría</th>
                                  <th>Monto</th>
                                </tr>
                              </thead>
                              <tbody>
                                {group.transactions.map(transaction => (
                                  <tr key={transaction.id}>
                                    <td>{formatDate(transaction.transaction_date)}</td>
                                    <td>{transaction.category || 'Sin categoría'}</td>
                                    <td className="amount">{formatAmount(transaction.amount)}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="no-data">
          No hay transacciones registradas para {monthOptions.find(m => m.value === month)?.label} de {year}
        </div>
      )}
      
      <style jsx>{`
        .transactions-list {
          width: 100%;
        }
        
        .filter-controls {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
          background-color: #f5f5f5;
          padding: 1rem;
          border-radius: 8px;
        }
        
        .filter-group {
          display: flex;
          flex-direction: column;
          min-width: 150px;
        }
        
        label {
          font-weight: 600;
          margin-bottom: 0.3rem;
        }
        
        select {
          padding: 0.5rem;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .summary-card {
          display: flex;
          justify-content: space-between;
          background-color: #e3f2fd;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
          border-left: 4px solid #2196f3;
        }
        
        .summary-item {
          display: flex;
          flex-direction: column;
        }
        
        .summary-label {
          font-weight: 600;
          font-size: 0.9rem;
          color: #555;
        }
        
        .summary-value {
          font-size: 1.2rem;
          font-weight: 700;
          color: #1a237e;
        }
        
        .tabs-container {
          margin-top: 1rem;
        }
        
        .tabs {
          display: flex;
          border-bottom: 2px solid #e0e0e0;
          margin-bottom: 1rem;
        }
        
        .tab {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          font-weight: 600;
          color: #757575;
          font-size: 1rem;
          transition: all 0.2s ease;
        }
        
        .tab:hover {
          color: #1a237e;
          background-color: #f5f5f5;
        }
        
        .tab.active {
          color: #1a237e;
          border-bottom-color: #1a237e;
        }
        
        .tab-content {
          padding: 1rem 0;
        }
        
        .transactions-table,
        .details-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }
        
        th, td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }
        
        th {
          background-color: #f5f5f5;
          font-weight: 600;
        }
        
        tr:hover {
          background-color: #f5f5f5;
        }
        
        .amount {
          font-weight: 600;
          text-align: right;
        }
        
        .count {
          text-align: center;
        }
        
        tr.ingreso {
          background-color: rgba(76, 175, 80, 0.1);
        }
        
        tr.ingreso:hover {
          background-color: rgba(76, 175, 80, 0.2);
        }
        
        tr.gasto {
          background-color: rgba(244, 67, 54, 0.05);
        }
        
        tr.gasto:hover {
          background-color: rgba(244, 67, 54, 0.1);
        }
        
        .tipo, .group-tipo {
          font-weight: 600;
          text-align: center;
        }
        
        .tipo.ingreso, .group-tipo.ingreso {
          color: #4caf50;
        }
        
        .tipo.gasto, .group-tipo.gasto {
          color: #f44336;
        }
        
        .loading, .error, .no-data {
          padding: 2rem;
          text-align: center;
          background-color: #f5f5f5;
          border-radius: 8px;
          margin-top: 1rem;
        }
        
        .error {
          color: #c62828;
          background-color: #ffebee;
        }
        
        .no-data {
          color: #555;
          font-style: italic;
        }
        
        /* Estilos para el acordeón */
        .accordion-container {
          display: flex;
          flex-direction: column;
          gap: 0.8rem;
          width: 100%;
        }
        
        .accordion-item {
          border: 1px solid #eee;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          transition: all 0.3s ease;
        }
        
        .accordion-item.ingreso {
          border-left: 4px solid #4caf50;
        }
        
        .accordion-item.gasto {
          border-left: 4px solid #f44336;
        }
        
        .accordion-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #fff;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .accordion-header:hover {
          background-color: #f9f9f9;
        }
        
        .accordion-title {
          display: flex;
          flex-direction: column;
        }
        
        .group-description {
          font-weight: 600;
          font-size: 1rem;
        }
        
        .group-bank {
          font-size: 0.8rem;
          color: #757575;
          margin-top: 0.3rem;
        }
        
        .accordion-summary {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .group-count {
          font-size: 0.85rem;
          color: #757575;
          white-space: nowrap;
        }
        
        .group-amount {
          font-weight: 700;
          font-size: 1rem;
        }
        
        .expand-icon {
          font-size: 0.8rem;
          transition: transform 0.3s ease;
          margin-left: 0.5rem;
        }
        
        .expand-icon.expanded {
          transform: rotate(180deg);
        }
        
        .accordion-content {
          padding: 0.5rem 1rem;
          border-top: 1px solid #eee;
          background-color: #fafafa;
        }
        
        .details-table {
          margin: 0.5rem 0;
        }
        
        .details-table th, .details-table td {
          padding: 0.6rem;
          font-size: 0.85rem;
        }
      `}</style>
    </div>
  );
}
