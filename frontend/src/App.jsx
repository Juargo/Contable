import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Container, Nav, Navbar } from 'react-bootstrap';
import CategoryManagementPage from './pages/CategoryManagementPage';
// ...existing code...

function App() {
  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">Contable</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Inicio</Nav.Link>
              {/* ...existing links... */}
              <Nav.Link as={Link} to="/categorias">Categorías</Nav.Link>
              {/* ...existing links... */}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      
      <Container className="mt-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* ...existing routes... */}
          <Route path="/categorias" element={<CategoryManagementPage />} />
          {/* ...existing routes... */}
        </Routes>
      </Container>
    </Router>
  );
}

export default App;