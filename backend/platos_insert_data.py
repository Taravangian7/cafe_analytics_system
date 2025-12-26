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

#leo el archivo csv y convierte en dataframe (tabla en memoria)
df = pd.read_csv('csv_data/products.csv')
#inserto datos en la tabla de platos. iterrows es para recorrer el dataframe fila por fila
for index, row in df.iterrows():
    cursor.execute(
        "INSERT INTO Platos (Nombre, Categoria) VALUES (?,?)",
        row[nombre], row[categoria]
    )

#commit de la transacción
conn.commit() 

#cerrar la conexión
cursor.close()
conn.close()
