import streamlit as st
import pyodbc
import pandas as pd
import sys
from pathlib import Path

# Agregar carpeta padre al path
sys.path.append(str(Path(__file__).parent.parent))
from create_plato import agregar_nuevo_ingrediente, agregar_nuevo_plato, borrar_plato, modificar_plato
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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Ventas", "🍽️ Productos", "📦 Ingredientes","Platos"])

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

with tab4:
    st.header("Agregar ingredientes y platos")
    nombre = st.text_input("Nombre del ingrediente")
    costo = st.number_input("Costo", min_value=0.0, step=0.01)
    cantidad = st.number_input("Cantidad", min_value=0.01, step=0.01)
    unidad = st.selectbox("Unidad", ["kg", "litro", "unidad", "gramo"])
    gluten_free = st.checkbox("Gluten Free")
    dairy_free = st.checkbox("Dairy Free")

    if st.button("Agregar Ingrediente"):
        success, message, nombre, unidad = agregar_nuevo_ingrediente(
            conn, nombre, costo, cantidad, unidad, gluten_free, dairy_free
        )
        
        if success:

            st.success(message)
        else:
            st.error(message)
    
    # --- DATOS DEL PLATO ---
    st.header("Crear nuevo plato")

    nombre_plato = st.text_input("Nombre del plato")
    categoria_plato = st.text_input("Categoría")
    precio_plato = st.number_input("Precio", min_value=0.0, step=0.1)
    
    # Obtener ingredientes existentes de SQL
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre, Unidad FROM Ingredientes")
    ingredientes_bd = {row[0]: row[1] for row in cursor}   # dict Nombre -> Unidad

    # --- INGREDIENTES TEMPORALES ---
    if "ingredientes_temp" not in st.session_state:
        st.session_state.ingredientes_temp = []

    st.subheader("Agregar ingredientes al plato")
    # Selectbox con ingredientes existentes
    ing_nombre = st.selectbox("Ingrediente", list(ingredientes_bd.keys()))

    # Mostrar la unidad automáticamente
    st.caption(f"Unidad: **{ingredientes_bd[ing_nombre]}**")
    # Cantidad
    ing_cantidad = st.number_input("Cantidad", min_value=0.0)

    if st.button("Agregar ingrediente a la receta"):
        st.session_state.ingredientes_temp.append({
            "nombre": ing_nombre,
            "cantidad": ing_cantidad,
            "unidad": ingredientes_bd[ing_nombre]  # guardo unidad también
        })
        st.success(f"{ing_nombre} agregado")

    st.write("Ingredientes agregados:")
    st.table(st.session_state.ingredientes_temp)

    # --- CREAR PLATO ---
    if st.button("Crear plato"):
        ok, msg = agregar_nuevo_plato(
            conn,
            nombre_plato,
            categoria_plato,
            precio_plato,
            st.session_state.ingredientes_temp
        )

        if ok:
            st.success(msg)
            st.session_state.ingredientes_temp = []  # reset
        else:
            st.error(msg)