from backend.db import get_master_connection,get_tenant_connection
from pathlib import Path

def create_tenant_db(username: str) -> str:
    db_name = f"cafe_{username.lower()}"

    conn = get_master_connection()
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE [{db_name}]")

    cursor.close()
    conn.close()

    return db_name

def create_tenant_tables(database: str):
    conn=get_tenant_connection(database)
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    SCHEMA_SQL = BASE_DIR / 'schema.sql'
    #Ejecutar schema.sql (dividir por GO)
    with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
            sql = f.read()
        
    for batch in sql.split('GO'):
            batch = batch.strip()
            if batch:
                conn.execute(batch)
        
    print("✓ Tablas creadas")