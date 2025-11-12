import pyodbc
import pandas as pd
from pathlib import Path


# Config
SERVER = 'LAPTOP-MTPJVFI5\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Rutas
BASE_DIR = Path(__file__).parent
SCHEMA_SQL = BASE_DIR / 'schema.sql'


conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};Trusted_Connection=yes;',
        autocommit=True
    )

# 2. Crear database si no existe
conn.execute(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name='{DATABASE}') CREATE DATABASE {DATABASE}")
conn.close()

# 3. Conectar a la database
conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
        autocommit=True
    )
# 4. Ejecutar schema.sql (dividir por GO)
with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
        sql = f.read()
    
for batch in sql.split('GO'):
        batch = batch.strip()
        if batch:
            conn.execute(batch)
    
print("✓ Tablas creadas")
