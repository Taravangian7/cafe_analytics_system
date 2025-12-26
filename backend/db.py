import pyodbc
#CONEXION AL MASTER DE BASE DE DATOS
# Config existente
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'

def get_master_connection():
    return pyodbc.connect(
        f'DRIVER={{SQL Server}};'
        f'SERVER={SERVER};'
        f'DATABASE=master;'
        f'Trusted_Connection=yes;',
        autocommit=True
    )
