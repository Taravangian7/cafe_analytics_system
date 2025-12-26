import pyodbc
from backend.db import get_master_connection

AUTH_DATABASE = "Cafe_Bar"


def get_auth_connection():
    """
    Conexión a la base central de autenticación
    """
    return pyodbc.connect(
        f'DRIVER={{SQL Server}};'
        f'SERVER=LAPTOP-MTPJVFI5\\SQLEXPRESS;'
        f'DATABASE={AUTH_DATABASE};'
        f'Trusted_Connection=yes;',
        autocommit=True
    )


def get_user_by_username(username: str):
    """
    Devuelve un usuario por username o None
    """
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password_hash, email, db_name
        FROM Users
        WHERE username = ?
    """, username)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id": row.id,
        "username": row.username,
        "password_hash": row.password_hash,
        "email": row.email,
        "db_name": row.db_name
    }


def create_user(username: str, password_hash: str, email: str, db_name: str):
    """
    Inserta un nuevo usuario en la DB central
    """
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Users (username, password_hash, email, db_name)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, email, db_name))

    cursor.close()
    conn.close()