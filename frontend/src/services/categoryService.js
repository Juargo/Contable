import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Ajusta según tu configuración

export const categoryService = {
  // Endpoints para categorías principales
  getAllCategories: async (type = null) => {
    let url = `${API_URL}/categories/`;
    if (type) url += `?type=${type}`;
    return axios.get(url).then(response => response.data);
  },
  
  getCategoryById: async (id) => {
    return axios.get(`${API_URL}/categories/${id}`).then(response => response.data);
  },
  
  createCategory: async (categoryData) => {
    return axios.post(`${API_URL}/categories/`, categoryData).then(response => response.data);
  },
  
  updateCategory: async (id, categoryData) => {
    return axios.put(`${API_URL}/categories/${id}`, categoryData).then(response => response.data);
  },
  
  deleteCategory: async (id) => {
    return axios.delete(`${API_URL}/categories/${id}`);
  },
  
  // Endpoints para subcategorías
  getSubcategories: async (parentId) => {
    return axios.get(`${API_URL}/categories/${parentId}/subcategories`).then(response => response.data);
  },
  
  getSubcategoryById: async (id) => {
    return axios.get(`${API_URL}/categories/subcategory/${id}`).then(response => response.data);
  },
  
  createSubcategory: async (parentId, subcategoryData) => {
    return axios.post(`${API_URL}/categories/${parentId}/subcategories`, subcategoryData)
      .then(response => response.data);
  },
  
  updateSubcategory: async (id, subcategoryData) => {
    return axios.put(`${API_URL}/categories/subcategory/${id}`, subcategoryData)
      .then(response => response.data);
  },
  
  deleteSubcategory: async (id) => {
    return axios.delete(`${API_URL}/categories/subcategory/${id}`);
  },
  
  // Endpoints para palabras clave
  getCategoryKeywords: async (subcategoryId) => {
    return axios.get(`${API_URL}/categories/subcategory/${subcategoryId}/keywords`)
      .then(response => response.data);
  },
  
  addCategoryKeyword: async (subcategoryId, keyword) => {
    return axios.post(`${API_URL}/categories/subcategory/${subcategoryId}/keywords`, { keyword })
      .then(response => response.data);
  },
  
  deleteCategoryKeyword: async (keywordId) => {
    return axios.delete(`${API_URL}/categories/keywords/${keywordId}`);
  }
};

export default categoryService;
