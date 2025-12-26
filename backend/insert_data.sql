-- ============================================
-- Script unificado para insertar datos
-- ============================================
-- Este script asume que:
-- 1. La BD 'Restaurante' y las tablas ya existen (ejecutar schema.sql primero)
-- 2. Los Platos ya fueron cargados desde products.csv (ejecutado por setup_db.py)
-- 3. Este script completa con Ingredientes y Recetas con cantidades realistas
--
-- Uso: Ejecutar después de cargar los Platos desde el CSV
-- ============================================

USE Restaurante;
GO

SET NOCOUNT ON;
GO

-- ============================================
-- 1. INSERTAR INGREDIENTES (idempotente)
-- ============================================
IF NOT EXISTS (SELECT 1 FROM dbo.Ingredientes)
BEGIN
	PRINT 'Insertando ingredientes...';

	-- Ingredientes base para café y bebidas
	INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, GlutenFree, DairyFree) VALUES
	('Café en grano', 12.50, 8, 'kg', 1, 1),
	('Leche entera', 3.80, 10, 'litro', 1, 0),
	('Leche descremada', 3.60, 10, 'litro', 1, 0),
	('Leche de almendras', 5.20, 5, 'litro', 1, 1),
	('Leche de soja', 4.90, 5, 'litro', 1, 1),
	('Azúcar blanca', 2.50, 10, 'kg', 1, 1),
	('Chocolate en polvo', 8.50, 3, 'kg', 1, 1),
	('Especias Chai', 25.00, 1, 'kg', 1, 1),
	('Hielo', 0.50, 20, 'kg', 1, 1),
	('Vainilla', 45.00, 1, 'litro', 1, 1),
	('Canela en polvo', 18.00, 2, 'kg', 1, 1);

	-- Ingredientes para pasteles
	INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, GlutenFree, DairyFree) VALUES
	('Harina de trigo', 3.20, 10, 'kg', 0, 1),
	('Harina sin gluten', 6.50, 5, 'kg', 1, 1),
	('Mantequilla', 8.50, 5, 'kg', 1, 0),
	('Margarina vegetal', 6.20, 5, 'kg', 1, 1),
	('Huevos', 18.00, 30, 'unidad', 1, 1),
	('Chocolate amargo', 12.00, 4, 'kg', 1, 1),
	('Almendras', 15.00, 3, 'kg', 1, 1),
	('Arándanos', 18.00, 3, 'kg', 1, 1),
	('Plátanos', 4.50, 8, 'kg', 1, 1),
	('Levadura', 5.50, 1, 'kg', 1, 1),
	('Sal', 1.20, 5, 'kg', 1, 1),
	('Aceite vegetal', 4.80, 5, 'litro', 1, 1);

	-- Ingredientes para comida
	INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, GlutenFree, DairyFree) VALUES
	('Pan de molde', 4.50, 10, 'unidad', 0, 1),
	('Pan sin gluten', 8.50, 6, 'unidad', 1, 1),
	('Aguacate', 8.00, 8, 'kg', 1, 1),
	('Huevos frescos', 18.00, 30, 'unidad', 1, 1),
	('Tocino', 15.00, 5, 'kg', 1, 1),
	('Jamón cocido', 12.50, 5, 'kg', 1, 1),
	('Queso cheddar', 14.00, 5, 'kg', 1, 0),
	('Queso feta', 16.00, 3, 'kg', 1, 0),
	('Lechuga', 6.00, 5, 'kg', 1, 1),
	('Tomate', 5.50, 8, 'kg', 1, 1),
	('Cebolla', 3.50, 6, 'kg', 1, 1),
	('Pechuga de pollo', 11.00, 8, 'kg', 1, 1),
	('Aderezo César', 8.50, 2, 'litro', 1, 0),
	('Aceitunas', 9.00, 2, 'kg', 1, 1),
	('Aceite de oliva', 12.00, 5, 'litro', 1, 1),
	('Vinagre balsámico', 15.00, 2, 'litro', 1, 1),
	('Tortilla de harina', 3.20, 10, 'unidad', 0, 1),
	('Tortilla sin gluten', 6.00, 6, 'unidad', 1, 1),
	('Vegetales mixtos', 7.50, 6, 'kg', 1, 1);

	-- Ingredientes para bebidas
	INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, GlutenFree, DairyFree) VALUES
	('Jugo de naranja', 6.50, 10, 'litro', 1, 1);

	PRINT 'Ingredientes insertados correctamente.';
END
ELSE
BEGIN
	PRINT 'Ingredientes ya existen. Omitiendo inserción.';
END
GO

-- ============================================
-- 2. INSERTAR RECETAS (idempotente, depende de Platos e Ingredientes)
-- ============================================
IF EXISTS (SELECT 1 FROM dbo.Platos) AND EXISTS (SELECT 1 FROM dbo.Ingredientes) AND NOT EXISTS (SELECT 1 FROM dbo.Recetas)
BEGIN
	PRINT 'Insertando recetas...';

	-- Recetas para cafés
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN p.Nombre = 'Espresso' THEN 0.020  -- 20g de café
	        WHEN p.Nombre = 'Long Black' THEN 0.020
	        WHEN p.Nombre = 'Flat White' THEN 0.020
	        WHEN p.Nombre = 'Cappuccino' THEN 0.020
	        WHEN p.Nombre = 'Latte' THEN 0.020
	        WHEN p.Nombre = 'Iced Latte' THEN 0.020
	        WHEN p.Nombre = 'Iced Coffee' THEN 0.030
	        WHEN p.Nombre = 'Mocha' THEN 0.020
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre IN ('Flat White', 'Cappuccino', 'Latte', 'Espresso', 'Long Black', 'Mocha', 'Iced Latte', 'Iced Coffee')
	AND i.Nombre = 'Café en grano';

	-- Leche para cafés con leche
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN p.Nombre = 'Flat White' THEN 0.160  -- 160ml de leche
	        WHEN p.Nombre = 'Cappuccino' THEN 0.120  -- 120ml de leche
	        WHEN p.Nombre = 'Latte' THEN 0.180       -- 180ml de leche
	        WHEN p.Nombre = 'Iced Latte' THEN 0.200  -- 200ml (con hielo)
	        WHEN p.Nombre = 'Mocha' THEN 0.150       -- 150ml + chocolate
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre IN ('Flat White', 'Cappuccino', 'Latte', 'Iced Latte', 'Mocha')
	AND i.Nombre = 'Leche entera';

	-- Hielo para bebidas frías
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 0.150  -- 150g de hielo
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre IN ('Iced Latte', 'Iced Coffee')
	AND i.Nombre = 'Hielo';

	-- Chocolate para Mocha
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 0.015  -- 15g de chocolate en polvo
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Mocha'
	AND i.Nombre = 'Chocolate en polvo';

	-- Hot Chocolate
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Leche entera' THEN 0.250
	        WHEN i.Nombre = 'Chocolate en polvo' THEN 0.025
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Hot Chocolate'
	AND i.Nombre IN ('Leche entera', 'Chocolate en polvo', 'Azúcar blanca');

	-- Chai Latte
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Leche entera' THEN 0.200
	        WHEN i.Nombre = 'Especias Chai' THEN 0.005
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Chai Latte'
	AND i.Nombre IN ('Leche entera', 'Especias Chai', 'Azúcar blanca');

	-- Croissant
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN i.Nombre = 'Mantequilla' THEN 0.060
	        WHEN i.Nombre = 'Huevos' THEN 0.5  -- medio huevo
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN i.Nombre = 'Sal' THEN 0.003
	        WHEN i.Nombre = 'Levadura' THEN 0.008
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Croissant'
	AND i.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura');

	-- Almond Croissant
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN i.Nombre = 'Mantequilla' THEN 0.060
	        WHEN i.Nombre = 'Huevos' THEN 0.5
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN i.Nombre = 'Sal' THEN 0.003
	        WHEN i.Nombre = 'Levadura' THEN 0.008
	        WHEN i.Nombre = 'Almendras' THEN 0.030
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Almond Croissant'
	AND i.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura', 'Almendras');

	-- Pain au Chocolat
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN i.Nombre = 'Mantequilla' THEN 0.060
	        WHEN i.Nombre = 'Huevos' THEN 0.5
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN i.Nombre = 'Sal' THEN 0.003
	        WHEN i.Nombre = 'Levadura' THEN 0.008
	        WHEN i.Nombre = 'Chocolate amargo' THEN 0.040
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Pain au Chocolat'
	AND i.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura', 'Chocolate amargo');

	-- Muffin Blueberry
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.120
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.060
	        WHEN i.Nombre = 'Aceite vegetal' THEN 0.040
	        WHEN i.Nombre = 'Huevos' THEN 1.0
	        WHEN i.Nombre = 'Arándanos' THEN 0.080
	        WHEN i.Nombre = 'Sal' THEN 0.003
	        WHEN i.Nombre = 'Levadura' THEN 0.008
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Muffin Blueberry'
	AND i.Nombre IN ('Harina de trigo', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Arándanos', 'Sal', 'Levadura');

	-- Muffin Choc Chip
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.120
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.060
	        WHEN i.Nombre = 'Aceite vegetal' THEN 0.040
	        WHEN i.Nombre = 'Huevos' THEN 1.0
	        WHEN i.Nombre = 'Chocolate amargo' THEN 0.050
	        WHEN i.Nombre = 'Sal' THEN 0.003
	        WHEN i.Nombre = 'Levadura' THEN 0.008
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Muffin Choc Chip'
	AND i.Nombre IN ('Harina de trigo', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Chocolate amargo', 'Sal', 'Levadura');

	-- Banana Bread
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Harina de trigo' THEN 0.150
	        WHEN i.Nombre = 'Plátanos' THEN 0.200
	        WHEN i.Nombre = 'Azúcar blanca' THEN 0.080
	        WHEN i.Nombre = 'Aceite vegetal' THEN 0.060
	        WHEN i.Nombre = 'Huevos' THEN 2.0
	        WHEN i.Nombre = 'Sal' THEN 0.005
	        WHEN i.Nombre = 'Levadura' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Banana Bread'
	AND i.Nombre IN ('Harina de trigo', 'Plátanos', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Sal', 'Levadura');

	-- Avocado Toast
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Pan de molde' THEN 2.0
	        WHEN i.Nombre = 'Aguacate' THEN 0.150
	        WHEN i.Nombre = 'Aceite de oliva' THEN 0.010
	        WHEN i.Nombre = 'Sal' THEN 0.002
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Avocado Toast'
	AND i.Nombre IN ('Pan de molde', 'Aguacate', 'Aceite de oliva', 'Sal');

	-- Bacon & Egg Roll
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Pan de molde' THEN 1.0
	        WHEN i.Nombre = 'Huevos frescos' THEN 2.0
	        WHEN i.Nombre = 'Tocino' THEN 0.080
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Bacon & Egg Roll'
	AND i.Nombre IN ('Pan de molde', 'Huevos frescos', 'Tocino');

	-- Ham & Cheese Toastie
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Pan de molde' THEN 2.0
	        WHEN i.Nombre = 'Jamón cocido' THEN 0.100
	        WHEN i.Nombre = 'Queso cheddar' THEN 0.080
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Ham & Cheese Toastie'
	AND i.Nombre IN ('Pan de molde', 'Jamón cocido', 'Queso cheddar');

	-- Vegetarian Wrap
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Tortilla de harina' THEN 1.0
	        WHEN i.Nombre = 'Vegetales mixtos' THEN 0.150
	        WHEN i.Nombre = 'Lechuga' THEN 0.050
	        WHEN i.Nombre = 'Tomate' THEN 0.060
	        WHEN i.Nombre = 'Aceite de oliva' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Vegetarian Wrap'
	AND i.Nombre IN ('Tortilla de harina', 'Vegetales mixtos', 'Lechuga', 'Tomate', 'Aceite de oliva');

	-- Caesar Salad
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Lechuga' THEN 0.150
	        WHEN i.Nombre = 'Aderezo César' THEN 0.030
	        WHEN i.Nombre = 'Queso cheddar' THEN 0.040
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Caesar Salad'
	AND i.Nombre IN ('Lechuga', 'Aderezo César', 'Queso cheddar');

	-- Greek Salad
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Lechuga' THEN 0.100
	        WHEN i.Nombre = 'Tomate' THEN 0.150
	        WHEN i.Nombre = 'Cebolla' THEN 0.050
	        WHEN i.Nombre = 'Aceitunas' THEN 0.040
	        WHEN i.Nombre = 'Queso feta' THEN 0.080
	        WHEN i.Nombre = 'Aceite de oliva' THEN 0.020
	        WHEN i.Nombre = 'Vinagre balsámico' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Greek Salad'
	AND i.Nombre IN ('Lechuga', 'Tomate', 'Cebolla', 'Aceitunas', 'Queso feta', 'Aceite de oliva', 'Vinagre balsámico');

	-- Chicken Sandwich
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Pan de molde' THEN 2.0
	        WHEN i.Nombre = 'Pechuga de pollo' THEN 0.150
	        WHEN i.Nombre = 'Lechuga' THEN 0.040
	        WHEN i.Nombre = 'Tomate' THEN 0.050
	        WHEN i.Nombre = 'Aceite de oliva' THEN 0.010
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Chicken Sandwich'
	AND i.Nombre IN ('Pan de molde', 'Pechuga de pollo', 'Lechuga', 'Tomate', 'Aceite de oliva');

	-- BLT Sandwich
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 
	    CASE 
	        WHEN i.Nombre = 'Pan de molde' THEN 2.0
	        WHEN i.Nombre = 'Tocino' THEN 0.100
	        WHEN i.Nombre = 'Lechuga' THEN 0.050
	        WHEN i.Nombre = 'Tomate' THEN 0.080
	    END
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'BLT Sandwich'
	AND i.Nombre IN ('Pan de molde', 'Tocino', 'Lechuga', 'Tomate');

	-- Orange Juice
	INSERT INTO dbo.Recetas (PlatoId, IngredienteId, Cantidad)
	SELECT p.PlatoId, i.IngredienteId, 0.250  -- 250ml de jugo
	FROM dbo.Platos p
	CROSS JOIN dbo.Ingredientes i
	WHERE p.Nombre = 'Orange Juice'
	AND i.Nombre = 'Jugo de naranja';

	PRINT 'Recetas insertadas correctamente.';
END
ELSE
BEGIN
	IF NOT EXISTS (SELECT 1 FROM dbo.Platos)
		PRINT 'Recetas no insertadas: faltan Platos (cargar desde products.csv primero).';
	ELSE IF NOT EXISTS (SELECT 1 FROM dbo.Ingredientes)
		PRINT 'Recetas no insertadas: faltan Ingredientes.';
	ELSE
		PRINT 'Recetas ya existen. Omitiendo inserción.';
END
GO

-- ============================================
-- 3. VERIFICACIÓN
-- ============================================
PRINT 'Verificando datos insertados...';
GO

SELECT TOP 10 
    p.Nombre AS Plato,
    p.Categoria,
    p.Costo,
    p.GlutenFree,
    p.DairyFree,
    (SELECT COUNT(*) FROM dbo.Recetas r WHERE r.PlatoId = p.PlatoId) AS CantidadIngredientes
FROM dbo.Platos p
ORDER BY p.Nombre;
GO

PRINT 'Script completado exitosamente!';
GO
