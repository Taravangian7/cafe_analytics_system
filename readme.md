# ☕ Café Analytics System

Sistema completo de gestión y análisis para cafeterías y restaurantes pequeños.

## 🎯 Características

- **Multitenant**: Cada usuario tiene su propia base de datos aislada
- **Autenticación**: Sistema de registro y login seguro
- **Gestión completa**: CRUD de productos, ingredientes y recetas
- **Análisis avanzado**: 20+ métricas de negocio
- **Carga masiva**: Importación desde CSV/Excel
- **Cálculo de costos**: Sistema de recetas con costos automáticos

## 🚀 Instalación

### Requisitos previos

- Python 3.10+
- SQL Server 2019+ (Express es suficiente)
- ODBC Driver for SQL Server

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/Taravangian7/cafe-analytics-system.git
cd cafe-analytics-system
```

### Paso 2: Crear entorno virtual (ver .env.example)
```bash
python -m venv venv

DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost
DB_TRUSTED_CONNECTION=yes

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar la conexión a SQL Server
```bash
# Copiar el template de configuración
cp config.example.py config.py

# Editar config.py con tus credenciales
# En Windows con SQL Server local, generalmente solo necesitás cambiar:
# SQL_SERVER = 'localhost\\SQLEXPRESS'
```
### Paso 5: Ejecutar el setup
```bash
python -m setup.init_auth_db.py
python -m setup.init_users_table.py
```
### Paso 6: Ejecutar el dashboard
```bash
streamlit run frontend/dashboard.py
```

El sistema estará disponible en `http://localhost:8501`

## 📚 Uso

1. **Registro**: Crear una cuenta (esto crea automáticamente tu base de datos)
2. **Carga de datos**: Subir CSVs de ingredientes, platos y recetas
3. **Análisis**: Explorar las métricas de ventas y rentabilidad

### Formato de CSVs

Ver ejemplos en `data/templates/`

## 🏗️ Arquitectura

- **Backend**: Python con pyodbc
- **Frontend**: Streamlit
- **Base de datos**: SQL Server (una DB por usuario)
- **Autenticación**: Hash SHA256 + salt

## 📊 Métricas disponibles

- Revenue por período
- Top productos vendidos
- Análisis de rentabilidad
- Márgenes de ganancia
- Comparativas semanales/mensuales
- y más...

## 🤝 Contribuciones

Pull requests son bienvenidos. Para cambios mayores, abrir un issue primero.

## 📝 Licencia

MIT

## 👤 Autor

**Pablo Hergenreder**
- GitHub: [@Taravangian7](https://github.com/Taravangian7)