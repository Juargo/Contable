USE moneydairy_db;

-- Tabla para presupuestos
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT 'Nombre del presupuesto',
    description VARCHAR(255) COMMENT 'Descripción del presupuesto',
    start_date DATE NOT NULL COMMENT 'Fecha de inicio del presupuesto',
    end_date DATE NOT NULL COMMENT 'Fecha de finalización del presupuesto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT check_dates CHECK (end_date >= start_date)
);

-- Tabla para asignar categorías a presupuestos
CREATE TABLE IF NOT EXISTS budget_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_id INT NOT NULL COMMENT 'ID del presupuesto',
    category_id INT NOT NULL COMMENT 'ID de la categoría',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_budget_category (budget_id, category_id) COMMENT 'Evita duplicados de categoría en un mismo presupuesto'
);

-- Tabla para almacenar los valores de presupuesto por subcategoría
CREATE TABLE IF NOT EXISTS subcategory_budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_id INT NOT NULL COMMENT 'ID del presupuesto',
    category_id INT NOT NULL COMMENT 'ID de la subcategoría',
    amount DECIMAL(15, 2) NOT NULL COMMENT 'Monto presupuestado para la subcategoría',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_subcategory_budget (budget_id, category_id) COMMENT 'Una subcategoría solo puede tener un valor en un presupuesto'
);

-- Modificar la tabla de transacciones para incluir la relación con subcategorías
ALTER TABLE transactions 
ADD COLUMN subcategory_id INT NULL COMMENT 'ID de la subcategoría a la que pertenece la transacción' AFTER category,
ADD CONSTRAINT fk_transaction_subcategory FOREIGN KEY (subcategory_id) REFERENCES categories(id);

-- Vista para calcular el total presupuestado por categoría principal
CREATE OR REPLACE VIEW category_budget_totals AS
SELECT 
    bc.budget_id,
    c.id AS category_id,
    c.name AS category_name,
    c.parent_id,
    SUM(sb.amount) AS total_amount
FROM budget_categories bc
JOIN categories c ON bc.category_id = c.id
JOIN subcategory_budgets sb ON sb.budget_id = bc.budget_id
JOIN categories sc ON sb.category_id = sc.id
WHERE sc.parent_id = c.id
GROUP BY bc.budget_id, c.id, c.name, c.parent_id;

-- Vista para calcular el total presupuestado por presupuesto
CREATE OR REPLACE VIEW budget_totals AS
SELECT 
    b.id AS budget_id,
    b.name AS budget_name,
    b.start_date,
    b.end_date,
    SUM(sb.amount) AS total_budget_amount
FROM budgets b
JOIN subcategory_budgets sb ON sb.budget_id = b.id
GROUP BY b.id, b.name, b.start_date, b.end_date;

-- Vista para calcular el gasto actual por subcategoría para un presupuesto específico
CREATE OR REPLACE VIEW budget_subcategory_spending AS
SELECT 
    b.id AS budget_id,
    t.subcategory_id,
    c.name AS subcategory_name,
    c.parent_id AS category_id,
    pc.name AS category_name,
    SUM(t.amount) AS total_spent
FROM budgets b
JOIN transactions t ON t.transaction_date BETWEEN b.start_date AND b.end_date
JOIN categories c ON t.subcategory_id = c.id
JOIN categories pc ON c.parent_id = pc.id
WHERE t.type = 'Gasto'
GROUP BY b.id, t.subcategory_id, c.name, c.parent_id, pc.name;

-- Vista para calcular el gasto actual por categoría para un presupuesto específico
CREATE OR REPLACE VIEW budget_category_spending AS
SELECT 
    budget_id,
    category_id,
    category_name,
    SUM(total_spent) AS total_spent
FROM budget_subcategory_spending
GROUP BY budget_id, category_id, category_name;

-- Vista para comparar presupuesto vs gasto real
CREATE OR REPLACE VIEW budget_vs_actual AS
SELECT 
    b.id AS budget_id,
    b.name AS budget_name,
    b.start_date,
    b.end_date,
    c.id AS category_id,
    c.name AS category_name,
    COALESCE(cbt.total_amount, 0) AS budgeted_amount,
    COALESCE(bcs.total_spent, 0) AS actual_spent,
    COALESCE(cbt.total_amount, 0) - COALESCE(bcs.total_spent, 0) AS difference
FROM budgets b
JOIN budget_categories bc ON b.id = bc.budget_id
JOIN categories c ON bc.category_id = c.id
LEFT JOIN category_budget_totals cbt ON b.id = cbt.budget_id AND c.id = cbt.category_id
LEFT JOIN budget_category_spending bcs ON b.id = bcs.budget_id AND c.id = bcs.category_id;

-- Índices para optimizar consultas
CREATE INDEX idx_transactions_subcategory ON transactions(subcategory_id);
CREATE INDEX idx_transactions_date_subcategory ON transactions(transaction_date, subcategory_id);
CREATE INDEX idx_subcategory_budgets_budget ON subcategory_budgets(budget_id);
