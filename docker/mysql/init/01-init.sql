-- Script inicial para crear las tablas y estructuras necesarias

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS moneydairy_db;
USE moneydairy_db;

-- Tabla para bancos
CREATE TABLE IF NOT EXISTS banks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertar bancos soportados
INSERT INTO banks (name, description) VALUES 
    ('santander', 'Banco Santander'),
    ('banco-estado', 'Banco Estado'),
    ('bci', 'Banco de Crédito e Inversiones'),
    ('itau', 'Itaú'),
    ('falabella', 'Banco Falabella'),
    ('ripley', 'Banco Ripley'),
    ('scotiabank', 'Scotiabank'),
    ('bice', 'BICE'),
    ('corpbanca', 'Corpbanca'),
    ('security', 'Security'),
    ('chile', 'Banco de Chile'),
    ('consorcio', 'Consorcio'),
    ('bci-nova', 'BCI Nova'),
    ('bci-servipag', 'BCI Servipag'),
    ('bci-empresas', 'BCI Empresas'),
    ('bci-automotriz', 'BCI Automotriz'),
    ('bci-construccion', 'BCI Construcción'),
    ('bci-hipotecario', 'BCI Hipotecario'),
    ('bci-credito', 'BCI Crédito'),
    ('bbva', 'BBVA'),
    ('caixabank', 'CaixaBank'),
    ('sabadell', 'Banco Sabadell'),
    ('bankinter', 'Bankinter'),
    ('ing', 'ING Direct');

-- Tabla para transacciones
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) DEFAULT 'Sin clasificar',
    bank_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES banks(id)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_bank_id ON transactions(bank_id);

-- Tabla para categorías
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- Tabla para palabras clave de categorías
CREATE TABLE IF NOT EXISTS category_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_category_keyword (category_id, keyword)
);

-- Insertar algunas categorías de ejemplo
INSERT INTO categories (name) VALUES 
    ('Alimentación'),
    ('Servicios'),
    ('Transporte'),
    ('Ocio'),
    ('Ingresos'),
    ('Hogar');

-- Insertar algunas subcategorías de ejemplo
INSERT INTO categories (name, parent_id) VALUES 
    ('Supermercado', 1),
    ('Restaurantes', 1),
    ('Electricidad', 2),
    ('Internet', 2),
    ('Gasolina', 3),
    ('Transporte público', 3),
    ('Nómina', 5),
    ('Devoluciones', 5);

-- Insertar algunas palabras clave de ejemplo
INSERT INTO category_keywords (category_id, keyword) VALUES 
    (7, 'SUPERMERCADO'),
    (7, 'MERCADONA'),
    (7, 'CARREFOUR'),
    (8, 'RESTAURANTE'),
    (8, 'BAR'),
    (9, 'ELECTRICIDAD'),
    (9, 'LUZ'),
    (10, 'INTERNET'),
    (10, 'FIBRA'),
    (11, 'GASOLINA'),
    (11, 'COMBUSTIBLE'),
    (12, 'METRO'),
    (12, 'BUS'),
    (13, 'NOMINA'),
    (13, 'SALARIO'),
    (14, 'DEVOLUCION');

-- Permisos
GRANT ALL PRIVILEGES ON moneydairy_db.* TO 'moneydairy_user'@'%';
FLUSH PRIVILEGES;
