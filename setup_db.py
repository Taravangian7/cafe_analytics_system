import os
import csv
import pyodbc
from pathlib import Path

# Configuration (override via environment variables if needed)
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
DATABASE_NAME = os.getenv('SQL_DATABASE', 'Restaurante')
ODBC_DRIVER = os.getenv('ODBC_DRIVER', 'ODBC Driver 17 for SQL Server')
TRUSTED_CONNECTION = os.getenv('SQL_TRUSTED', 'yes').lower() in ('1', 'true', 'yes')
USERNAME = os.getenv('SQL_USERNAME')
PASSWORD = os.getenv('SQL_PASSWORD')

WORKSPACE_DIR = Path(__file__).resolve().parent
SCHEMA_SQL = WORKSPACE_DIR / 'schema.sql'
BASE_DATA_SQL = WORKSPACE_DIR / 'insert_base_data.sql'
PRODUCTS_CSV = WORKSPACE_DIR / 'csv_generator' / 'products.csv'


def get_connection(database: str = 'master') -> pyodbc.Connection:
	if TRUSTED_CONNECTION:
		conn_str = f'DRIVER={{{ODBC_DRIVER}}};SERVER={SQL_SERVER};DATABASE={database};Trusted_Connection=yes;'
	else:
		if not USERNAME or not PASSWORD:
			raise RuntimeError('SQL_USERNAME and SQL_PASSWORD must be set when not using Trusted_Connection')
		conn_str = f'DRIVER={{{ODBC_DRIVER}}};SERVER={SQL_SERVER};DATABASE={database};UID={USERNAME};PWD={PASSWORD};'
	return pyodbc.connect(conn_str, autocommit=True)


def database_exists() -> bool:
	with get_connection('master') as conn:
		cur = conn.cursor()
		cur.execute("SELECT 1 FROM sys.databases WHERE name = ?", DATABASE_NAME)
		return cur.fetchone() is not None


def execute_sql_file(conn: pyodbc.Connection, sql_path: Path) -> None:
	# Split batches by GO on its own line, case-insensitive
	batch = []
	with open(sql_path, 'r', encoding='utf-8') as f:
		for line in f:
			if line.strip().upper() == 'GO':
				_sql = ''.join(batch).strip()
				if _sql:
					conn.execute(_sql)
				batch = []
			else:
				batch.append(line)
		# last batch
		_sql = ''.join(batch).strip()
		if _sql:
			conn.execute(_sql)


def ensure_schema() -> None:
	with get_connection('master') as conn:
		if not database_exists():
			# Create DB shell
			conn.execute(f"CREATE DATABASE [{DATABASE_NAME}]")
	# Run schema in DB context (idempotent)
	with get_connection(DATABASE_NAME) as conn_db:
		execute_sql_file(conn_db, SCHEMA_SQL)


def load_products_into_platos() -> None:
	if not PRODUCTS_CSV.exists():
		raise FileNotFoundError(f"CSV not found: {PRODUCTS_CSV}")
	with get_connection(DATABASE_NAME) as conn:
		cursor = conn.cursor()
		with open(PRODUCTS_CSV, newline='', encoding='utf-8') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				name = row['product_name'].strip()
				category = row['category'].strip()
				# Insert if not exists by unique name
				cursor.execute(
					"""
					IF NOT EXISTS (SELECT 1 FROM dbo.Platos WHERE Nombre = ?)
						INSERT INTO dbo.Platos (Nombre, Categoria) VALUES (?, ?);
					""",
					name, name, category
				)
			conn.commit()


def load_base_data() -> None:
	with get_connection(DATABASE_NAME) as conn:
		execute_sql_file(conn, BASE_DATA_SQL)


def main() -> None:
	if database_exists():
		print(f"Database '{DATABASE_NAME}' already exists. Nothing to do.")
		return
	print(f"Creating and initializing database '{DATABASE_NAME}' on server '{SQL_SERVER}'...")
	ensure_schema()
	print('Loading Platos from products.csv...')
	load_products_into_platos()
	print('Inserting base ingredients and recipes...')
	load_base_data()
	print('Done.')


if __name__ == '__main__':
	main()

