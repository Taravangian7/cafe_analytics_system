import pyodbc

SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

def create_users_table():
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'Trusted_Connection=yes;',
        autocommit=True
    )

    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables WHERE name = 'Users'
        )
        BEGIN
            CREATE TABLE Users (
                id INT IDENTITY PRIMARY KEY,
                username NVARCHAR(50) UNIQUE NOT NULL,
                password_hash NVARCHAR(255) NOT NULL,
                email NVARCHAR(100),
                db_name NVARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
        END
    """)

    cursor.close()
    conn.close()

    print("✓ Tabla Users creada (o ya existía)")


if __name__ == "__main__":
    create_users_table()