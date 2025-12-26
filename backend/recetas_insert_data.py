import pyodbc
import pandas as pd
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

BASE_DIR = Path(__file__).parent
PRODUCTS_CSV = BASE_DIR / 'csv_generator' / 'products.csv'

# -------------------------------
# CONEXIÓN
# -------------------------------
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
    autocommit=False
)
cursor = conn.cursor()

# -------------------------------
# LEER DATOS BASE
# -------------------------------
# Leemos los productos y los ingredientes ya existentes en SQL
platos = pd.read_sql("SELECT Nombre, Categoria FROM dbo.Platos", conn)
ingredientes = pd.read_sql("SELECT Nombre, Unidad FROM dbo.Ingredientes", conn)

# -------------------------------
# DEFINIR RECETAS EN PYTHON
# -------------------------------
recetas_data = []

def add_receta(plato, ingrediente, cantidad):
    """Agrega una fila de receta si la cantidad no es None"""
    if cantidad is not None:
        unidad = ingredientes.loc[ingredientes["Nombre"] == ingrediente, "Unidad"].values
        if len(unidad) > 0:
            recetas_data.append({
                "Plato": plato,
                "Ingrediente": ingrediente,
                "Cantidad": cantidad,
                "Unidad": unidad[0]
            })

# Ejemplo: cafés
for plato in ['Espresso', 'Long Black', 'Flat White', 'Cappuccino', 'Latte', 'Iced Latte', 'Iced Coffee', 'Mocha']:
    add_receta(plato, 'Café en grano', 0.030 if plato == 'Iced Coffee' else 0.020)

# Leche
leches = {
    'Flat White': 0.160,
    'Cappuccino': 0.120,
    'Latte': 0.180,
    'Iced Latte': 0.200,
    'Mocha': 0.150
}
for plato, cant in leches.items():
    add_receta(plato, 'Leche entera', cant)

# Hielo
for plato in ['Iced Latte', 'Iced Coffee']:
    add_receta(plato, 'Hielo', 0.150)

# Chocolate para Mocha
add_receta('Mocha', 'Chocolate en polvo', 0.015)

# Hot Chocolate
for ingr, cant in {'Leche entera': 0.250, 'Chocolate en polvo': 0.025, 'Azúcar blanca': 0.010}.items():
    add_receta('Hot Chocolate', ingr, cant)

# Chai Latte
for ingr, cant in {'Leche entera': 0.200, 'Especias Chai': 0.005, 'Azúcar blanca': 0.010}.items():
    add_receta('Chai Latte', ingr, cant)

# Croissant
for ingr, cant in {
    'Harina de trigo': 0.100, 'Mantequilla': 0.060, 'Huevos': 0.5,
    'Azúcar blanca': 0.010, 'Sal': 0.003, 'Levadura': 0.008
}.items():
    add_receta('Croissant', ingr, cant)

# Almond Croissant
for ingr, cant in {
    'Harina de trigo': 0.100,
    'Mantequilla': 0.060,
    'Huevos': 0.5,
    'Azúcar blanca': 0.010,
    'Sal': 0.003,
    'Levadura': 0.008,
    'Almendras': 0.030
}.items():
    add_receta('Almond Croissant', ingr, cant)

# Pain au Chocolat
for ingr, cant in {
    'Harina de trigo': 0.100,
    'Mantequilla': 0.060,
    'Huevos': 0.5,
    'Azúcar blanca': 0.010,
    'Sal': 0.003,
    'Levadura': 0.008,
    'Chocolate amargo': 0.040
}.items():
    add_receta('Pain au Chocolat', ingr, cant)

# Muffin Blueberry
for ingr, cant in {
    'Harina de trigo': 0.120,
    'Azúcar blanca': 0.060,
    'Aceite vegetal': 0.040,
    'Huevos': 1.0,
    'Arándanos': 0.080,
    'Sal': 0.003,
    'Levadura': 0.008
}.items():
    add_receta('Muffin Blueberry', ingr, cant)

# Muffin Choc Chip
for ingr, cant in {
    'Harina de trigo': 0.120,
    'Azúcar blanca': 0.060,
    'Aceite vegetal': 0.040,
    'Huevos': 1.0,
    'Chocolate amargo': 0.050,
    'Sal': 0.003,
    'Levadura': 0.008
}.items():
    add_receta('Muffin Choc Chip', ingr, cant)

# Banana Bread
for ingr, cant in {
    'Harina de trigo': 0.150,
    'Plátanos': 0.200,
    'Azúcar blanca': 0.080,
    'Aceite vegetal': 0.060,
    'Huevos': 2.0,
    'Sal': 0.005,
    'Levadura': 0.010
}.items():
    add_receta('Banana Bread', ingr, cant)

# Avocado Toast
for ingr, cant in {
    'Pan de molde': 2.0,
    'Aguacate': 0.150,
    'Aceite de oliva': 0.010,
    'Sal': 0.002
}.items():
    add_receta('Avocado Toast', ingr, cant)

# Bacon & Egg Roll
for ingr, cant in {
    'Pan de molde': 1.0,
    'Huevos frescos': 2.0,
    'Tocino': 0.080
}.items():
    add_receta('Bacon & Egg Roll', ingr, cant)

# Ham & Cheese Toastie
for ingr, cant in {
    'Pan de molde': 2.0,
    'Jamón cocido': 0.100,
    'Queso cheddar': 0.080
}.items():
    add_receta('Ham & Cheese Toastie', ingr, cant)

# Vegetarian Wrap
for ingr, cant in {
    'Tortilla de harina': 1.0,
    'Vegetales mixtos': 0.150,
    'Lechuga': 0.050,
    'Tomate': 0.060,
    'Aceite de oliva': 0.010
}.items():
    add_receta('Vegetarian Wrap', ingr, cant)

# Caesar Salad
for ingr, cant in {
    'Lechuga': 0.150,
    'Aderezo César': 0.030,
    'Queso cheddar': 0.040
}.items():
    add_receta('Caesar Salad', ingr, cant)

# Greek Salad
for ingr, cant in {
    'Lechuga': 0.100,
    'Tomate': 0.150,
    'Cebolla': 0.050,
    'Aceitunas': 0.040,
    'Queso feta': 0.080,
    'Aceite de oliva': 0.020,
    'Vinagre balsámico': 0.010
}.items():
    add_receta('Greek Salad', ingr, cant)

# Chicken Sandwich
for ingr, cant in {
    'Pan de molde': 2.0,
    'Pechuga de pollo': 0.150,
    'Lechuga': 0.040,
    'Tomate': 0.050,
    'Aceite de oliva': 0.010
}.items():
    add_receta('Chicken Sandwich', ingr, cant)

# BLT Sandwich
for ingr, cant in {
    'Pan de molde': 2.0,
    'Tocino': 0.100,
    'Lechuga': 0.050,
    'Tomate': 0.080
}.items():
    add_receta('BLT Sandwich', ingr, cant)

# Orange Juice
add_receta('Orange Juice', 'Jugo de naranja', 0.250)

# -------------------------------
# CREAR DATAFRAME FINAL
# -------------------------------
df_recetas = pd.DataFrame(recetas_data)
print(df_recetas.head())
print(f"→ Total recetas: {len(df_recetas)} filas")

# -------------------------------
# CARGAR TODO EL DATAFRAME A SQL
# -------------------------------
values = ", ".join(
    f"('{row['Plato']}', '{row['Ingrediente']}', {row['Cantidad']}, '{row['Unidad']}')"
    for _, row in df_recetas.iterrows()
)

sql = f"""
INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
VALUES {values};
"""

cursor.execute(sql)
conn.commit()

print("✓ Recetas insertadas correctamente en bloque.")

cursor.close()
conn.close()
