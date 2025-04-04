import { useState, useEffect } from 'react';
import { API_URL } from '../config/constants';

interface Transaction {
  date: string;
  description: string;
  category?: string;
  amount?: number;
  Fecha?: string;
  Descripción?: string;
  Cargo?: number;
  Abono?: number;
  Monto?: number;
  Tipo?: string;
  "N° Operación"?: string;
}

interface Bank {
  id: number;
  name: string;
  description: string;
  code?: string;
}

interface BankReport {
  bank_id: number;
  balance: number;
  transactions: Transaction[];
}

export default function ContableApp() {
  const [data, setData] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [selectedBank, setSelectedBank] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loadingBanks, setLoadingBanks] = useState(true);
  const [balance, setBalance] = useState<number | null>(null);
  const [selectedBankId, setSelectedBankId] = useState<number | null>(null);
  const [savingTransactions, setSavingTransactions] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false); // Nuevo estado para controlar la visibilidad de la tabla

  useEffect(() => {
    // No cargar transacciones al iniciar, solo bancos
    // fetchTransactions();
    fetchBanks();
    setLoading(false); // Indicar que la carga inicial ha terminado
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/transactions`);
      if (!response.ok) {
        throw new Error('Error al cargar los datos');
      }
      const data = await response.json();
      setData(data);
      
      // Solo mostrar la tabla si hay datos
      setShowTable(data.length > 0);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchBanks = async () => {
    try {
      setLoadingBanks(true);
      const response = await fetch(`${API_URL}/banks`);
      if (!response.ok) {
        throw new Error('Error al cargar los bancos');
      }
      const banksData = await response.json();
      setBanks(banksData);
    } catch (err) {
      console.error('Error fetching banks:', err);
    } finally {
      setLoadingBanks(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleBankChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedBank(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!file || !selectedBank) {
      setUploadStatus('Por favor selecciona un archivo y un banco');
      return;
    }

    setUploadStatus('Subiendo reporte...');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_id', selectedBank);

    try {
      const response = await fetch(`${API_URL}/upload-bank-report`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar el archivo');
      }

      const result: BankReport = await response.json();
      setUploadStatus('Reporte procesado correctamente');
      
      // Actualiza el estado con los datos del reporte
      setData(result.transactions);
      setBalance(result.balance);
      setSelectedBankId(result.bank_id);
      setFile(null);
      
      // Mostrar tabla cuando hay datos del reporte
      setShowTable(result.transactions.length > 0);

      // Resetear el formulario
      const form = document.getElementById('upload-form') as HTMLFormElement;
      if (form) form.reset();
    } catch (err: any) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };

  const handleSaveTransactions = async () => {
    if (!data.length) {
      setSaveStatus('No hay transacciones para guardar');
      return;
    }

    setSavingTransactions(true);
    setSaveStatus('Guardando transacciones...');

    try {
      // Convertir el formato de las transacciones para el endpoint bulk-transactions
      const transactionsToSave = data.map(item => {
        // Determinar el tipo (Ingreso/Gasto) de la transacción
        const tipo = item.Tipo || 'Gasto'; // Por defecto es gasto si no se especifica
        
        // Obtener el monto de la transacción
        let monto;
        if (item.Monto !== undefined) {
          monto = item.Monto;
        } else if (item.amount !== undefined) {
          monto = item.amount;
        } else if (tipo === 'Ingreso') {
          monto = item.Abono || 0;
        } else {
          monto = item.Cargo || 0;
        }
        
        // Ajustar el signo del monto según el tipo
        // Para gastos: valores negativos, para ingresos: valores positivos
        const montoAjustado = tipo === 'Gasto' 
          ? -Math.abs(Number(monto)) 
          : Math.abs(Number(monto));
        
        console.log(`Procesando transacción: ${item.Descripción || item.description}, Tipo: ${tipo}, Monto: ${montoAjustado}`);
        
        return {
          fecha: item.Fecha || item.date,
          descripcion: item.Descripción || item.description,
          monto: montoAjustado,
          categoria: "Sin clasificar",
          banco_id: banks.find(b => b.name === selectedBank)?.id,
          tipo: tipo
        };
      });

      // Verificar que hay transacciones para guardar
      if (transactionsToSave.length === 0) {
        setSaveStatus('No hay transacciones válidas para guardar');
        return;
      }

      const response = await fetch(`${API_URL}/bulk-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionsToSave),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar las transacciones');
      }

      const result = await response.json();
      setSaveStatus(`Transacciones guardadas: ${result.insertadas} de ${result.total_recibidas} (${result.duplicadas} duplicadas)`);
      
      // Opcional: Limpiar la tabla después de guardar exitosamente
      if (result.insertadas > 0) {
        setData([]);
        setShowTable(false);
        setBalance(null);
      }
    } catch (err: any) {
      setSaveStatus(`Error: ${err.message}`);
    } finally {
      setSavingTransactions(false);
    }
  };

  // Formatear los montos en CLP
  const formatAmount = (amount: number | undefined) => {
    if (amount === undefined) return "-";
    return amount.toLocaleString('es-CL', { 
      style: 'currency', 
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  if (loading) return <div className="loading-container">Cargando datos...</div>;
  if (error) return <div className="error-container">Error: {error}</div>;

  return (
    <div className="contable-app">
      <div className="upload-section">
        <h2>Subir Reporte Bancario</h2>
        <form id="upload-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="bank-select">Seleccionar Banco:</label>
            <select 
              id="bank-select" 
              value={selectedBank} 
              onChange={handleBankChange}
              required
              disabled={loadingBanks}
            >
              <option value="">-- Selecciona un banco --</option>
              {loadingBanks ? (
                <option value="" disabled>Cargando bancos...</option>
              ) : (
                banks.map(bank => (
                  <option key={bank.id} value={bank.name.toString()}>
                    {bank.description}
                  </option>
                ))
              )}
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="file-input">Archivo de Reporte:</label>
            <input 
              id="file-input"
              type="file" 
              onChange={handleFileChange}
              accept=".csv,.xls,.xlsx,.pdf"
              required
            />
          </div>
          
          <button type="submit" className="submit-button">Procesar Reporte</button>
        </form>
        
        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.includes('Error') ? 'error' : ''}`}>
            {uploadStatus}
          </div>
        )}
      </div>
      
      {balance !== null && (
        <div className="balance-info">
          <h3>Información del Reporte</h3>
          <p>Banco: {banks.find(b => b.id === selectedBankId)?.name || `ID: ${selectedBankId}`}</p>
          <p>Saldo: {formatAmount(balance)}</p>
        </div>
      )}
      
      {showTable && data.length > 0 && (
        <>
          <div className="transactions-header">
            <h2>Transacciones</h2>
            <button 
              onClick={handleSaveTransactions} 
              disabled={savingTransactions}
              className="save-button"
            >
              {savingTransactions ? 'Guardando...' : 'Guardar en Base de Datos'}
            </button>
          </div>
          
          {saveStatus && (
            <div className={`save-status ${saveStatus.includes('Error') ? 'error' : 'success'}`}>
              {saveStatus}
            </div>
          )}
          
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Monto</th>
                <th>Tipo</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index} className={item.Tipo?.toLowerCase() || ''}>
                  <td>{item.Fecha || item.date}</td>
                  <td>{item.Descripción || item.description}</td>
                  <td>{formatAmount(item.Monto || item.amount || item.Cargo || item.Abono)}</td>
                  <td>{item.Tipo || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      
      {!showTable && !uploadStatus && (
        <div className="info-message">
          <p>Selecciona un banco y sube un archivo para procesar transacciones.</p>
        </div>
      )}
      
      <style>{`
        .upload-section {
          background-color: #f0f0f0;
          padding: 1.5rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: bold;
        }
        
        select, input[type="file"] {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ccc;
          border-radius: 4px;
          margin-bottom: 0.5rem;
        }
        
        .submit-button {
          background-color: #4a66d8;
          color: white;
          border: none;
          padding: 0.6rem 1.2rem;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
          transition: background-color 0.2s;
        }
        
        .submit-button:hover {
          background-color: #3a56c8;
        }
        
        .upload-status {
          margin-top: 1rem;
          padding: 0.5rem;
          background-color: #e8f5e9;
          border-radius: 4px;
        }
        
        .upload-status.error {
          background-color: #ffebee;
          color: #c62828;
        }
        
        .transactions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .save-button {
          background-color: #4caf50;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
          transition: background-color 0.2s;
        }
        
        .save-button:hover {
          background-color: #388e3c;
        }
        
        .save-button:disabled {
          background-color: #a5d6a7;
          cursor: not-allowed;
        }
        
        .save-status {
          margin: 0.5rem 0 1rem;
          padding: 0.5rem;
          border-radius: 4px;
        }
        
        .save-status.success {
          background-color: #e8f5e9;
          border-left: 4px solid #4caf50;
        }
        
        .save-status.error {
          background-color: #ffebee;
          border-left: 4px solid #f44336;
          color: #c62828;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 1rem;
          font-size: 0.9rem;
        }
        
        th, td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }
        
        th {
          background-color: #f5f5f5;
          font-weight: bold;
        }
        
        tr:hover {
          background-color: #f5f5f5;
        }

        .balance-info {
          background-color: #e3f2fd;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1.5rem;
          border-left: 4px solid #2196f3;
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

        .loading-container, 
        .error-container,
        .info-message {
          padding: 2rem;
          text-align: center;
          background-color: #f5f5f5;
          border-radius: 8px;
          margin-top: 1rem;
        }

        .error-container {
          background-color: #ffebee;
          color: #c62828;
        }

        .info-message {
          background-color: #e3f2fd;
          color: #1565c0;
          padding: 2rem;
          font-weight: 500;
          border-left: 4px solid #1976d2;
        }
      `}</style>
    </div>
  );
}
