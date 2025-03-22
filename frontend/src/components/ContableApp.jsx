import { useState, useEffect } from 'react';

export default function ContableApp() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
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

    fetchData();
  }, []);

  if (loading) return <div>Cargando datos...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="contable-app">
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
    </div>
  );
}
