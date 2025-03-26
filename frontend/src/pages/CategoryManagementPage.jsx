import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, ButtonGroup, ToggleButton, Alert } from 'react-bootstrap';
// Importación específica de los íconos de Font Awesome
import { FaPlus } from 'react-icons/fa';
// Importaciones relativas correctas
import CategoryList from '../components/categories/CategoryList';
import SubcategoryList from '../components/categories/SubcategoryList';
import CategoryForm from '../components/categories/CategoryForm';
import SubcategoryForm from '../components/categories/SubcategoryForm';
import KeywordManager from '../components/categories/KeywordManager';
import categoryService from '../services/categoryService';

const CategoryManagementPage = () => {
  // Estado para filtrar por tipo de categoría
  const [selectedType, setSelectedType] = useState(null);
  
  // Estado para manejar la categoría seleccionada
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  // Estado para formularios
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showSubcategoryForm, setShowSubcategoryForm] = useState(false);
  const [showKeywordManager, setShowKeywordManager] = useState(false);
  
  // Estado para la edición
  const [editCategory, setEditCategory] = useState(null);
  const [editSubcategory, setEditSubcategory] = useState(null);
  const [subcategoryForKeywords, setSubcategoryForKeywords] = useState(null);
  const [parentIdForSubcategory, setParentIdForSubcategory] = useState(null);
  
  // Estado para feedback
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Estado para forzar actualizaciones
  const [refreshCategories, setRefreshCategories] = useState(0);
  const [refreshSubcategories, setRefreshSubcategories] = useState(0);

  // Handlers para mostrar/ocultar modales
  const handleOpenCategoryForm = (category = null) => {
    setEditCategory(category);
    setShowCategoryForm(true);
  };

  const handleOpenSubcategoryForm = (parentId, subcategory = null) => {
    setEditSubcategory(subcategory);
    setParentIdForSubcategory(parentId);
    setShowSubcategoryForm(true);
  };

  const handleOpenKeywordManager = (subcategory) => {
    setSubcategoryForKeywords(subcategory);
    setShowKeywordManager(true);
  };

  // Funciones para manejar los CRUD de categorías
  const handleCreateCategory = async (formData) => {
    try {
      setIsLoading(true);
      await categoryService.createCategory(formData);
      setShowCategoryForm(false);
      setRefreshCategories(prev => prev + 1);
      showSuccess('Categoría creada exitosamente');
    } catch (err) {
      setError('Error al crear la categoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateCategory = async (formData) => {
    try {
      setIsLoading(true);
      await categoryService.updateCategory(editCategory.id, formData);
      setShowCategoryForm(false);
      setRefreshCategories(prev => prev + 1);
      showSuccess('Categoría actualizada exitosamente');
    } catch (err) {
      setError('Error al actualizar la categoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta categoría?')) return;
    
    try {
      setIsLoading(true);
      await categoryService.deleteCategory(categoryId);
      if (selectedCategory && selectedCategory.id === categoryId) {
        setSelectedCategory(null);
      }
      setRefreshCategories(prev => prev + 1);
      showSuccess('Categoría eliminada exitosamente');
    } catch (err) {
      setError('Error al eliminar la categoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Funciones para manejar los CRUD de subcategorías
  const handleCreateSubcategory = async (formData) => {
    try {
      setIsLoading(true);
      await categoryService.createSubcategory(parentIdForSubcategory, formData);
      setShowSubcategoryForm(false);
      setRefreshSubcategories(prev => prev + 1);
      showSuccess('Subcategoría creada exitosamente');
    } catch (err) {
      setError('Error al crear la subcategoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateSubcategory = async (formData) => {
    try {
      setIsLoading(true);
      await categoryService.updateSubcategory(editSubcategory.id, formData);
      setShowSubcategoryForm(false);
      setRefreshSubcategories(prev => prev + 1);
      showSuccess('Subcategoría actualizada exitosamente');
    } catch (err) {
      setError('Error al actualizar la subcategoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSubcategory = async (subcategoryId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta subcategoría?')) return;
    
    try {
      setIsLoading(true);
      await categoryService.deleteSubcategory(subcategoryId);
      setRefreshSubcategories(prev => prev + 1);
      showSuccess('Subcategoría eliminada exitosamente');
    } catch (err) {
      setError('Error al eliminar la subcategoría: ' + err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Función para mostrar mensajes de éxito
  const showSuccess = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  // Función para manejar el envío del formulario de categoría
  const handleCategoryFormSubmit = (formData) => {
    if (editCategory) {
      handleUpdateCategory(formData);
    } else {
      handleCreateCategory(formData);
    }
  };

  // Función para manejar el envío del formulario de subcategoría
  const handleSubcategoryFormSubmit = (formData) => {
    if (editSubcategory) {
      handleUpdateSubcategory(formData);
    } else {
      handleCreateSubcategory(formData);
    }
  };

  return (
    <Container fluid className="py-4">
      <h1 className="mb-4">Administración de Categorías</h1>
      
      {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}
      {successMessage && <Alert variant="success" onClose={() => setSuccessMessage(null)} dismissible>{successMessage}</Alert>}
      
      <Row>
        <Col md={12} className="mb-3">
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <ButtonGroup>
                    <ToggleButton
                      type="radio"
                      variant="outline-primary"
                      name="typeFilter"
                      value={null}
                      checked={selectedType === null}
                      onChange={() => setSelectedType(null)}
                    >
                      Todos
                    </ToggleButton>
                    <ToggleButton
                      type="radio"
                      variant="outline-success"
                      name="typeFilter"
                      value="INCOME"
                      checked={selectedType === "INCOME"}
                      onChange={() => setSelectedType("INCOME")}
                    >
                      Ingresos
                    </ToggleButton>
                    <ToggleButton
                      type="radio"
                      variant="outline-danger"
                      name="typeFilter"
                      value="EXPENSE"
                      checked={selectedType === "EXPENSE"}
                      onChange={() => setSelectedType("EXPENSE")}
                    >
                      Gastos
                    </ToggleButton>
                  </ButtonGroup>
                </div>
                <Button 
                  variant="primary" 
                  onClick={() => handleOpenCategoryForm()}
                >
                  <FaPlus /> Nueva Categoría
                </Button>
              </div>

              <CategoryList
                selectedType={selectedType}
                refresh={refreshCategories}
                onEdit={handleOpenCategoryForm}
                onDelete={handleDeleteCategory}
                onAddSubcategory={(parentId) => handleOpenSubcategoryForm(parentId)}
                onSelectCategory={setSelectedCategory}
              />
            </Card.Body>
          </Card>
        </Col>

        {selectedCategory && (
          <Col md={12} className="mt-2">
            <Card>
              <Card.Body>
                <SubcategoryList
                  categoryId={selectedCategory.id}
                  refresh={refreshSubcategories}
                  onEdit={(subcategory) => handleOpenSubcategoryForm(selectedCategory.id, subcategory)}
                  onDelete={handleDeleteSubcategory}
                  onManageKeywords={handleOpenKeywordManager}
                />
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Modales */}
      <CategoryForm
        show={showCategoryForm}
        handleClose={() => setShowCategoryForm(false)}
        category={editCategory}
        onSubmit={handleCategoryFormSubmit}
        isLoading={isLoading}
      />

      <SubcategoryForm
        show={showSubcategoryForm}
        handleClose={() => setShowSubcategoryForm(false)}
        subcategory={editSubcategory}
        parentId={parentIdForSubcategory}
        parentName={selectedCategory?.name}
        onSubmit={handleSubcategoryFormSubmit}
        isLoading={isLoading}
      />

      <KeywordManager
        show={showKeywordManager}
        handleClose={() => setShowKeywordManager(false)}
        subcategory={subcategoryForKeywords}
      />
    </Container>
  );
};

export default CategoryManagementPage;
