import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, ListGroup, Badge, Spinner, Alert } from 'react-bootstrap';
import { FaTrash } from 'react-icons/fa';
import categoryService from '../../services/categoryService';

const KeywordManager = ({ 
  show, 
  handleClose, 
  subcategory 
}) => {
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const fetchKeywords = async () => {
    if (!subcategory) return;
    
    try {
      setLoading(true);
      const data = await categoryService.getCategoryKeywords(subcategory.id);
      setKeywords(data);
      setError(null);
    } catch (err) {
      setError('Error al cargar las palabras clave: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (show && subcategory) {
      fetchKeywords();
      setNewKeyword('');
    }
  }, [show, subcategory]);

  const handleAddKeyword = async (e) => {
    e.preventDefault();
    if (!newKeyword.trim()) return;

    try {
      setLoading(true);
      await categoryService.addCategoryKeyword(subcategory.id, newKeyword.trim());
      setNewKeyword('');
      fetchKeywords();
      setSuccessMessage('Palabra clave añadida correctamente');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Error al añadir la palabra clave: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteKeyword = async (keywordId) => {
    try {
      setLoading(true);
      await categoryService.deleteCategoryKeyword(keywordId);
      fetchKeywords();
      setSuccessMessage('Palabra clave eliminada correctamente');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Error al eliminar la palabra clave: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>
          Gestionar Palabras Clave
          {subcategory && <div className="small text-muted">Subcategoría: {subcategory.name}</div>}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {successMessage && <Alert variant="success">{successMessage}</Alert>}

        <Form onSubmit={handleAddKeyword} className="mb-4">
          <Form.Group className="d-flex">
            <Form.Control
              type="text"
              placeholder="Nueva palabra clave"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={loading}
            />
            <Button 
              type="submit" 
              variant="primary" 
              className="ms-2"
              disabled={loading || !newKeyword.trim()}
            >
              Añadir
            </Button>
          </Form.Group>
        </Form>

        <h6>Palabras clave existentes:</h6>
        {loading ? (
          <div className="text-center my-3">
            <Spinner animation="border" size="sm" />
          </div>
        ) : keywords.length === 0 ? (
          <Alert variant="info">Esta subcategoría no tiene palabras clave.</Alert>
        ) : (
          <ListGroup>
            {keywords.map(keyword => (
              <ListGroup.Item key={keyword.id} className="d-flex justify-content-between align-items-center">
                <Badge bg="secondary" className="py-2 px-3">
                  {keyword.keyword}
                </Badge>
                <Button 
                  variant="outline-danger" 
                  size="sm"
                  onClick={() => handleDeleteKeyword(keyword.id)}
                  disabled={loading}
                >
                  <FaTrash /> Eliminar
                </Button>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cerrar
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default KeywordManager;
