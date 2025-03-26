import React, { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert } from 'react-bootstrap';
import { FaEdit, FaTrash, FaKey } from 'react-icons/fa';
import categoryService from '../../services/categoryService';

const SubcategoryList = ({ 
  categoryId, 
  onEdit, 
  onDelete, 
  onManageKeywords, 
  refresh 
}) => {
  const [subcategories, setSubcategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSubcategories = async () => {
      if (!categoryId) return;
      
      try {
        setLoading(true);
        const data = await categoryService.getSubcategories(categoryId);
        setSubcategories(data);
        setError(null);
      } catch (err) {
        setError('Error al cargar las subcategorías: ' + err.message);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSubcategories();
  }, [categoryId, refresh]);

  if (!categoryId) {
    return <Alert variant="info">Selecciona una categoría para ver sus subcategorías</Alert>;
  }

  if (loading) {
    return <div className="text-center my-4"><Spinner animation="border" /></div>;
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <div className="mt-4">
      <h3>Subcategorías</h3>
      {subcategories.length === 0 ? (
        <Alert variant="info">Esta categoría no tiene subcategorías.</Alert>
      ) : (
        <Table striped hover responsive>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {subcategories.map(subcategory => (
              <tr key={subcategory.id}>
                <td>{subcategory.name}</td>
                <td>{subcategory.description || '-'}</td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="me-2"
                    onClick={() => onEdit(subcategory)}
                  >
                    <FaEdit /> Editar
                  </Button>
                  <Button 
                    variant="outline-danger" 
                    size="sm"
                    className="me-2"
                    onClick={() => onDelete(subcategory.id)}
                  >
                    <FaTrash /> Eliminar
                  </Button>
                  <Button 
                    variant="outline-info" 
                    size="sm"
                    onClick={() => onManageKeywords(subcategory)}
                  >
                    <FaKey /> Palabras clave
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default SubcategoryList;
