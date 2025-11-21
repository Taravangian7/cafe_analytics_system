import pyodbc

SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Conexión
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
    autocommit=True
)
cursor = conn.cursor()

import pandas as pd

df = pd.read_sql("SELECT Nombre, Unidad FROM Ingredientes", conn)
print((type(df["Nombre"]), df["Unidad"]))
#ingredientes_bd = dict(zip(df["Nombre"], df["Unidad"]))

#print(ingredientes_bd)