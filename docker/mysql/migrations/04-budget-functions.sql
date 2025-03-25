USE moneydairy_db;

-- Función para calcular el total presupuestado para una categoría específica
DELIMITER //
CREATE FUNCTION IF NOT EXISTS GetBudgetedAmountForCategory(p_budget_id INT, p_category_id INT) 
RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(15,2);
    
    SELECT SUM(sb.amount) INTO total
    FROM subcategory_budgets sb
    JOIN categories sc ON sb.category_id = sc.id
    WHERE sb.budget_id = p_budget_id AND sc.parent_id = p_category_id;
    
    RETURN IFNULL(total, 0);
END //
DELIMITER ;

-- Función para calcular el total gastado en una categoría para un presupuesto
DELIMITER //
CREATE FUNCTION IF NOT EXISTS GetSpentAmountForCategory(p_budget_id INT, p_category_id INT)
RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(15,2);
    DECLARE start_date DATE;
    DECLARE end_date DATE;
    
    -- Obtener las fechas del presupuesto
    SELECT start_date, end_date INTO start_date, end_date
    FROM budgets
    WHERE id = p_budget_id;
    
    -- Calcular el total gastado en las subcategorías de esta categoría
    SELECT SUM(t.amount) INTO total
    FROM transactions t
    JOIN categories sc ON t.subcategory_id = sc.id
    WHERE sc.parent_id = p_category_id
    AND t.transaction_date BETWEEN start_date AND end_date
    AND t.type = 'Gasto';
    
    RETURN IFNULL(ABS(total), 0);
END //
DELIMITER ;

-- Procedimiento para asignar una transacción a una subcategoría basada en palabras clave
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS AssignTransactionToSubcategory(IN p_transaction_id INT)
BEGIN
    DECLARE v_description VARCHAR(255);
    DECLARE v_subcategory_id INT;
    DECLARE v_keyword VARCHAR(100);
    DECLARE done INT DEFAULT FALSE;
    
    -- Cursor para recorrer las palabras clave
    DECLARE keyword_cursor CURSOR FOR
        SELECT ck.keyword, ck.category_id
        FROM category_keywords ck
        JOIN categories c ON ck.category_id = c.id
        WHERE c.parent_id IS NOT NULL; -- Solo subcategorías
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Obtener la descripción de la transacción
    SELECT description INTO v_description 
    FROM transactions 
    WHERE id = p_transaction_id;
    
    OPEN keyword_cursor;
    
    keyword_loop: LOOP
        FETCH keyword_cursor INTO v_keyword, v_subcategory_id;
        IF done THEN
            LEAVE keyword_loop;
        END IF;
        
        -- Si la descripción contiene la palabra clave
        IF v_description LIKE CONCAT('%', v_keyword, '%') THEN
            -- Asignar subcategoría y salir del bucle
            UPDATE transactions 
            SET subcategory_id = v_subcategory_id
            WHERE id = p_transaction_id;
            
            -- Una vez encontrada coincidencia, salimos del bucle
            SET done = TRUE;
        END IF;
    END LOOP;
    
    CLOSE keyword_cursor;
END //
DELIMITER ;

-- Trigger para asignar automáticamente transacciones a subcategorías al insertar
DELIMITER //
CREATE TRIGGER IF NOT EXISTS after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    CALL AssignTransactionToSubcategory(NEW.id);
END //
DELIMITER ;

-- Eliminar el trigger after_income_insert, ya que ahora se manejan los ingresos en la tabla transactions
