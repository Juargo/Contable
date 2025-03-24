import { useState, useEffect } from 'react';
import { API_URL } from '../config/constants';

interface Transaction {
  id: number;
  transaction_date: string;
  description: string;
  amount: number;
  category: string;
  bank_id: number | null;
}

interface TransactionGroup {
  description: string;
  total_amount: number;
  count: number;
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
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(transaction => (
                      <tr key={transaction.id}>
                        <td>{formatDate(transaction.transaction_date)}</td>
                        <td>{transaction.description}</td>
                        <td>{transaction.category}</td>
                        <td>{getBankName(transaction.bank_id)}</td>
                        <td className="amount">{formatAmount(transaction.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <table className="grouped-table">
                  <thead>
                    <tr>
                      <th>Descripción</th>
                      <th>Cantidad</th>
                      <th>Monto Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {groupedTransactions.map((group, index) => (
                      <tr key={index}>
                        <td>{group.description}</td>
                        <td className="count">{group.count}</td>
                        <td className="amount">{formatAmount(group.total_amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
        .grouped-table {
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
      `}</style>
    </div>
  );
}
