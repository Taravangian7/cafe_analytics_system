from backend.db import get_master_connection

def create_tenant_db(username: str) -> str:
    db_name = f"cafe_{username.lower()}"

    conn = get_master_connection()
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE [{db_name}]")

    cursor.close()
    conn.close()

    return db_name