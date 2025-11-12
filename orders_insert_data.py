import pyodbc
import pandas as pd
from pathlib import Path


# Config
SERVER = 'LAPTOP-MTPJVFI5\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Rutas
BASE_DIR = Path(__file__).parent
SCHEMA_SQL = BASE_DIR / 'schema.sql'
PRODUCTS_CSV = BASE_DIR / 'csv_generator' / 'orders.csv'

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
df = pd.read_csv('csv_data/orders.csv')
#inserto datos en la tabla de orders. iterrows es para recorrer el dataframe fila por fila
for index, row in df.iterrows():
    cursor.execute(
        "INSERT INTO Orders (Order_id,Order_date,Order_time,Day_of_week,Payment_method,Order_type) VALUES (?,?,?,?,?,?)",
        row['order_id'], row['order_date'], row['order_time'], row['day_of_week'], row['payment_method'], row['order_type']
    )
#commit de la transacción
conn.commit() 

#leo el archivo csv y convierte en dataframe (tabla en memoria)
df = pd.read_csv('csv_data/order_items.csv')
#inserto datos en la tabla de order_items. iterrows es para recorrer el dataframe fila por fila
for index, row in df.iterrows():
    cursor.execute(
        "INSERT INTO Order_items (Item_id,Order_id,Product_name,Quantity) VALUES (?,?,?,?)",
        row['item_id'], row['order_id'], row['product_name'], row['quantity']
    )
#commit de la transacción
conn.commit() 

#cerrar la conexión
cursor.close()
conn.close()