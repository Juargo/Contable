import React, { useState, useEffect } from 'react';
import { Table, Button, Badge, Spinner, Alert } from 'react-bootstrap';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import categoryService from '../../services/categoryService';

const CategoryList = ({ onEdit, onDelete, onAddSubcategory, onSelectCategory, selectedType, refresh }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const data = await categoryService.getAllCategories(selectedType);
        setCategories(data);
        setError(null);
      } catch (err) {
        setError('Error al cargar las categorías: ' + err.message);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [selectedType, refresh]);

  if (loading) {
    return <div className="text-center my-4"><Spinner animation="border" /></div>;
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <div className="mt-3">
      <h3>Categorías</h3>
      {categories.length === 0 ? (
        <Alert variant="info">No hay categorías disponibles.</Alert>
      ) : (
        <Table striped hover responsive>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Tipo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(category => (
              <tr 
                key={category.id} 
                onClick={() => onSelectCategory(category)}
                className="cursor-pointer"
              >
                <td>{category.name}</td>
                <td>{category.description || '-'}</td>
                <td>
                  <Badge bg={category.type === 'INCOME' ? 'success' : 'danger'}>
                    {category.type === 'INCOME' ? 'Ingreso' : 'Gasto'}
                  </Badge>
                </td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="me-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(category);
                    }}
                  >
                    <FaEdit /> Editar
                  </Button>
                  <Button 
                    variant="outline-danger" 
                    size="sm"
                    className="me-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(category.id);
                    }}
                  >
                    <FaTrash /> Eliminar
                  </Button>
                  <Button 
                    variant="outline-success" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAddSubcategory(category.id);
                    }}
                  >
                    <FaPlus /> Subcategoría
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

export default CategoryList;
