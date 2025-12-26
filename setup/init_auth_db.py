import pyodbc

SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'

def create_auth_database():
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER};'
        f'DATABASE=master;'
        f'Trusted_Connection=yes;',
        autocommit=True
    )

    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (
            SELECT name FROM sys.databases WHERE name = 'Cafe_Bar'
        )
        CREATE DATABASE Cafe_Bar
    """)

    cursor.close()
    conn.close()

    print("✓ Base Cafe_Bar creada (o ya existía)")

#Ejecutá esta función solo si este archivo es el que estoy corriendo directamente, no si alguien lo importa
if __name__ == "__main__":
    create_auth_database()