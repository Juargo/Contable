USE moneydairy_db;

-- Tabla para transacciones de ingresos (nueva)
CREATE TABLE IF NOT EXISTS transacciones_ingresos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL COMMENT 'Fecha de la transacción',
    description VARCHAR(255) NOT NULL COMMENT 'Descripción de la transacción',
    amount DECIMAL(15, 2) NOT NULL COMMENT 'Monto de la transacción (valor positivo)',
    category VARCHAR(100) DEFAULT 'Sin clasificar' COMMENT 'Categoría de la transacción',
    bank_id INT NULL COMMENT 'ID del banco',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de actualización',
    FOREIGN KEY (bank_id) REFERENCES banks(id)
);

-- Índices para la tabla de ingresos
CREATE INDEX idx_income_transactions_date ON transacciones_ingresos(transaction_date);
CREATE INDEX idx_income_transactions_category ON transacciones_ingresos(category);
CREATE INDEX idx_income_transactions_bank_id ON transacciones_ingresos(bank_id);
