import { useState, useEffect } from 'react';

export default function ContableApp() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [selectedBank, setSelectedBank] = useState('');
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/transactions');
      if (!response.ok) {
        throw new Error('Error al cargar los datos');
      }
      const data = await response.json();
      setData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleBankChange = (e) => {
    setSelectedBank(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !selectedBank) {
      setUploadStatus('Por favor selecciona un archivo y un banco');
      return;
    }

    setUploadStatus('Subiendo reporte...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_name', selectedBank);

    try {
      const response = await fetch('http://localhost:8000/api/upload-bank-report', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar el archivo');
      }

      const result = await response.json();
      setUploadStatus('Reporte procesado correctamente');
      setData(result);
      setFile(null);
      
      // Resetear el formulario
      document.getElementById('upload-form').reset();
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };

  if (loading) return <div>Cargando datos...</div>;
  if (error) return <div>Error: {error}</div>;

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
            >
              <option value="">-- Selecciona un banco --</option>
              <option value="santander">Santander</option>
              <option value="bbva">BBVA</option>
              <option value="caixabank">CaixaBank</option>
              <option value="sabadell">Sabadell</option>
              <option value="bankinter">Bankinter</option>
              <option value="ing">ING</option>
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
      
      <h2>Transacciones</h2>
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Descripción</th>
            <th>Categoría</th>
            <th>Importe</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan="4">No hay transacciones disponibles</td>
            </tr>
          ) : (
            data.map((item, index) => (
              <tr key={index}>
                <td>{item.date}</td>
                <td>{item.description}</td>
                <td>{item.category}</td>
                <td>{item.amount}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      
      <style jsx>{`
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
      `}</style>
    </div>
  );
}
