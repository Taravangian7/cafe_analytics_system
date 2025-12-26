import pyodbc
import pandas as pd
from pathlib import Path

def create_database_tables(database:str):
    # Config
    SERVER = 'LAPTOP-MTPJVFI5\SQLEXPRESS'
    DATABASE = database
    # Rutas
    BASE_DIR = Path(__file__).parent
    SCHEMA_SQL = BASE_DIR / 'schema.sql'
    #Conectar a la database
    conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
            autocommit=True
        )
    #Ejecutar schema.sql (dividir por GO)
    with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
            sql = f.read()
        
    for batch in sql.split('GO'):
            batch = batch.strip()
            if batch:
                conn.execute(batch)
        
    print("✓ Tablas creadas")
