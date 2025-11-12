import pyodbc
import pandas as pd
from pathlib import Path


# Config
SERVER = 'LAPTOP-MTPJVFI5\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Rutas
BASE_DIR = Path(__file__).parent
SCHEMA_SQL = BASE_DIR / 'schema.sql'
PRODUCTS_CSV = BASE_DIR / 'csv_generator' / 'products.csv'

#Columnas en csv:
nombre= 'product_name'
categoria= 'category'

# Conectar a la database
conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
        autocommit=True
    )
cursor = conn.cursor() #Es para ejecutar las consultas SQL
##Ingredientes para comida
cursor.execute("""
IF EXISTS (SELECT 1 FROM dbo.Platos) AND EXISTS (SELECT 1 FROM dbo.Ingredientes) AND NOT EXISTS (SELECT 1 FROM dbo.Receta)
BEGIN
	PRINT 'Insertando recetas...';

	-- Recetas para cafés
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Platos.Nombre = 'Espresso' THEN 0.020  -- 20g de café
	        WHEN Platos.Nombre = 'Long Black' THEN 0.020
	        WHEN Platos.Nombre = 'Flat White' THEN 0.020
	        WHEN Platos.Nombre = 'Cappuccino' THEN 0.020
	        WHEN Platos.Nombre = 'Latte' THEN 0.020
	        WHEN Platos.Nombre = 'Iced Latte' THEN 0.020
	        WHEN Platos.Nombre = 'Iced Coffee' THEN 0.030
	        WHEN Platos.Nombre = 'Mocha' THEN 0.020
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre IN ('Flat White', 'Cappuccino', 'Latte', 'Espresso', 'Long Black', 'Mocha', 'Iced Latte', 'Iced Coffee')
	AND Ingredientes.Nombre = 'Café en grano';

	-- Leche para cafés con leche
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad,Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Platos.Nombre = 'Flat White' THEN 0.160  -- 160ml de leche
	        WHEN Platos.Nombre = 'Cappuccino' THEN 0.120  -- 120ml de leche
	        WHEN Platos.Nombre = 'Latte' THEN 0.180       -- 180ml de leche
	        WHEN Platos.Nombre = 'Iced Latte' THEN 0.200  -- 200ml (con hielo)
	        WHEN Platos.Nombre = 'Mocha' THEN 0.150       -- 150ml + chocolate
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre IN ('Flat White', 'Cappuccino', 'Latte', 'Iced Latte', 'Mocha')
	AND Ingredientes.Nombre = 'Leche entera';

	-- Hielo para bebidas frías
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 0.150 ,Ingredientes.Unidad -- 150g de hielo
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre IN ('Iced Latte', 'Iced Coffee')
	AND Ingredientes.Nombre = 'Hielo';

	-- Chocolate para Mocha
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 0.015,Ingredientes.Unidad  -- 15g de chocolate en polvo
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Mocha'
	AND Ingredientes.Nombre = 'Chocolate en polvo';

	-- Hot Chocolate
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Leche entera' THEN 0.250
	        WHEN Ingredientes.Nombre = 'Chocolate en polvo' THEN 0.025
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Hot Chocolate'
	AND Ingredientes.Nombre IN ('Leche entera', 'Chocolate en polvo', 'Azúcar blanca');

	-- Chai Latte
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Leche entera' THEN 0.200
	        WHEN Ingredientes.Nombre = 'Especias Chai' THEN 0.005
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Chai Latte'
	AND Ingredientes.Nombre IN ('Leche entera', 'Especias Chai', 'Azúcar blanca');

	-- Croissant
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Mantequilla' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 0.5  -- medio huevo
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.003
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.008
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Croissant'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura');

	-- Almond Croissant
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Mantequilla' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 0.5
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.003
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.008
	        WHEN Ingredientes.Nombre = 'Almendras' THEN 0.030
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Almond Croissant'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura', 'Almendras');

	-- Pain au Chocolat
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Mantequilla' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 0.5
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.010
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.003
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.008
	        WHEN Ingredientes.Nombre = 'Chocolate amargo' THEN 0.040
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Pain au Chocolat'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Mantequilla', 'Huevos', 'Azúcar blanca', 'Sal', 'Levadura', 'Chocolate amargo');

	-- Muffin Blueberry
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.120
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Aceite vegetal' THEN 0.040
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 1.0
	        WHEN Ingredientes.Nombre = 'Arándanos' THEN 0.080
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.003
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.008
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Muffin Blueberry'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Arándanos', 'Sal', 'Levadura');

	-- Muffin Choc Chip
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.120
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Aceite vegetal' THEN 0.040
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 1.0
	        WHEN Ingredientes.Nombre = 'Chocolate amargo' THEN 0.050
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.003
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.008
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Muffin Choc Chip'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Chocolate amargo', 'Sal', 'Levadura');

	-- Banana Bread
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Harina de trigo' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Plátanos' THEN 0.200
	        WHEN Ingredientes.Nombre = 'Azúcar blanca' THEN 0.080
	        WHEN Ingredientes.Nombre = 'Aceite vegetal' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Huevos' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.005
	        WHEN Ingredientes.Nombre = 'Levadura' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Banana Bread'
	AND Ingredientes.Nombre IN ('Harina de trigo', 'Plátanos', 'Azúcar blanca', 'Aceite vegetal', 'Huevos', 'Sal', 'Levadura');

	-- Avocado Toast
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Pan de molde' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Aguacate' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Aceite de oliva' THEN 0.010
	        WHEN Ingredientes.Nombre = 'Sal' THEN 0.002
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Avocado Toast'
	AND Ingredientes.Nombre IN ('Pan de molde', 'Aguacate', 'Aceite de oliva', 'Sal');

	-- Bacon & Egg Roll
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Pan de molde' THEN 1.0
	        WHEN Ingredientes.Nombre = 'Huevos frescos' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Tocino' THEN 0.080
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Bacon & Egg Roll'
	AND Ingredientes.Nombre IN ('Pan de molde', 'Huevos frescos', 'Tocino');

	-- Ham & Cheese Toastie
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Pan de molde' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Jamón cocido' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Queso cheddar' THEN 0.080
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Ham & Cheese Toastie'
	AND Ingredientes.Nombre IN ('Pan de molde', 'Jamón cocido', 'Queso cheddar');

	-- Vegetarian Wrap
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Tortilla de harina' THEN 1.0
	        WHEN Ingredientes.Nombre = 'Vegetales mixtos' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Lechuga' THEN 0.050
	        WHEN Ingredientes.Nombre = 'Tomate' THEN 0.060
	        WHEN Ingredientes.Nombre = 'Aceite de oliva' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Vegetarian Wrap'
	AND Ingredientes.Nombre IN ('Tortilla de harina', 'Vegetales mixtos', 'Lechuga', 'Tomate', 'Aceite de oliva');

	-- Caesar Salad
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Lechuga' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Aderezo César' THEN 0.030
	        WHEN Ingredientes.Nombre = 'Queso cheddar' THEN 0.040
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Caesar Salad'
	AND Ingredientes.Nombre IN ('Lechuga', 'Aderezo César', 'Queso cheddar');

	-- Greek Salad
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Lechuga' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Tomate' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Cebolla' THEN 0.050
	        WHEN Ingredientes.Nombre = 'Aceitunas' THEN 0.040
	        WHEN Ingredientes.Nombre = 'Queso feta' THEN 0.080
	        WHEN Ingredientes.Nombre = 'Aceite de oliva' THEN 0.020
	        WHEN Ingredientes.Nombre = 'Vinagre balsámico' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Greek Salad'
	AND Ingredientes.Nombre IN ('Lechuga', 'Tomate', 'Cebolla', 'Aceitunas', 'Queso feta', 'Aceite de oliva', 'Vinagre balsámico');

	-- Chicken Sandwich
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Pan de molde' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Pechuga de pollo' THEN 0.150
	        WHEN Ingredientes.Nombre = 'Lechuga' THEN 0.040
	        WHEN Ingredientes.Nombre = 'Tomate' THEN 0.050
	        WHEN Ingredientes.Nombre = 'Aceite de oliva' THEN 0.010
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Chicken Sandwich'
	AND Ingredientes.Nombre IN ('Pan de molde', 'Pechuga de pollo', 'Lechuga', 'Tomate', 'Aceite de oliva');

	-- BLT Sandwich
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 
	    CASE 
	        WHEN Ingredientes.Nombre = 'Pan de molde' THEN 2.0
	        WHEN Ingredientes.Nombre = 'Tocino' THEN 0.100
	        WHEN Ingredientes.Nombre = 'Lechuga' THEN 0.050
	        WHEN Ingredientes.Nombre = 'Tomate' THEN 0.080
	    END
        ,Ingredientes.Unidad
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'BLT Sandwich'
	AND Ingredientes.Nombre IN ('Pan de molde', 'Tocino', 'Lechuga', 'Tomate');

	-- Orange Juice
	INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad,Unidad)
	SELECT Platos.Nombre, Ingredientes.Nombre, 0.250,Ingredientes.Unidad  -- 250ml de jugo
	FROM dbo.Platos
	CROSS JOIN dbo.Ingredientes
	WHERE Platos.Nombre = 'Orange Juice'
	AND Ingredientes.Nombre = 'Jugo de naranja';

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
""")

#commit de la transacción
conn.commit() 

#cerrar la conexión
cursor.close()
conn.close()
