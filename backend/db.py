import pyodbc
from config import DB_DRIVER, DB_SERVER, DB_TRUSTED_CONNECTION
#CONEXION AL MASTER DE BASE DE DATOS
# Config existente
SERVER = DB_SERVER

#Base de datos general
def get_master_connection():
    return pyodbc.connect(
        f'DRIVER={{{DB_DRIVER}}};'
        f'SERVER={SERVER};'
        f'DATABASE=master;'
        f'Trusted_Connection={DB_TRUSTED_CONNECTION};',
        autocommit=True
    )

#Base de datos para cada cliente
def get_tenant_connection(database:str):
    return pyodbc.connect(
        f'DRIVER={{{DB_DRIVER}}};'
        f'SERVER={SERVER};'
        f'DATABASE={database};'
        f'Trusted_Connection={DB_TRUSTED_CONNECTION};',
        autocommit=True
    )

#Base de datos donde se registran los usuarios 
AUTH_DATABASE = "Cafe_Bar"
def get_auth_connection():
    """
    Conexión a la base central de autenticación
    """
    return pyodbc.connect(
        f'DRIVER={{{DB_DRIVER}}};'
        f'SERVER={SERVER};'
        f'DATABASE={AUTH_DATABASE};'
        f'Trusted_Connection={DB_TRUSTED_CONNECTION};',
        autocommit=True
    )