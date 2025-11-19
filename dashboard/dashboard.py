import streamlit as st
import pyodbc
import pandas as pd

# Configuración
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

@st.cache_resource
def get_connection():
    return pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    )

conn = get_connection()

# Título
st.title("☕ Café Analytics Dashboard")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["📊 Ventas", "🍽️ Productos", "📦 Ingredientes"])

with tab1:
    st.header("Análisis de Ventas")
    st.write("Aquí irán las métricas de ventas")

with tab2:
    st.header("Gestión de Productos")
    df_platos = pd.read_sql("SELECT * FROM Platos", conn)
    st.dataframe(df_platos)

with tab3:
    st.header("Gestión de Ingredientes")
    df_ingredientes = pd.read_sql("SELECT * FROM Ingredientes", conn)
    st.dataframe(df_ingredientes)
