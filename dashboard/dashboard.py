import streamlit as st
import pyodbc
import pandas as pd
import sys
from pathlib import Path

# Agregar carpeta padre al path (para encontrar create_plato)
sys.path.append(str(Path(__file__).parent.parent))
from create_plato import agregar_nuevo_ingrediente, agregar_nuevo_plato, borrar_plato, modificar_plato

# Configuración
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

@st.cache_resource #Decorador que va asociado a una función (la que va debajo), lo que hace es guardar el return de la función para no volverle a ejecutar cada vez que refresca
def get_connection():
    return pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    )
conn = get_connection() #Con en el cache que puse arriba, si vuelvo a definir otra conn voy a usar la misma conexión, no ejecuta una nueva.


# Título
st.title("☕ Café Analytics Dashboard")

# Crear tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Ventas", "🍽️ Productos", "📦 Ingredientes","Platos","Modificaciones"])

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
    st.header("Agregar nuevo ingrediente")
    nombre = st.text_input("Nombre del ingrediente")
    costo = st.number_input("Costo", min_value=0.0, step=0.01)
    cantidad = st.number_input("Cantidad por Paquete", min_value=0.01, step=0.01)
    unidad = st.selectbox("Unidad", ["gr","kg","cm3","litro", "unidades"])
    gluten_free = st.checkbox("Gluten Free")
    dairy_free = st.checkbox("Dairy Free")

    if st.button("Agregar Ingrediente"): #Devuelve True solo cuando el usuario hace click en el botón
        success, message, nombre, unidad = agregar_nuevo_ingrediente(
            conn, nombre, costo, cantidad, unidad, gluten_free, dairy_free
        )
        if success:
            st.success(message)
        else:
            st.error(message)
    
    # --- DATOS DEL PLATO ---
    st.header("Agregar nuevo plato")
    cursor=conn.cursor()
    nombre_plato = st.text_input("Nombre del plato")

    cursor.execute("SELECT DISTINCT categoria FROM Platos")
    categorias_existentes= [i[0] for i in cursor.fetchall()]
    cursor.close()
    categoria_plato = st.selectbox("Elegir categoría",categorias_existentes+["Agregar categoria"])
    if categoria_plato == "Agregar categoria":
        categoria_plato= st.text_input("Nueva categoría")

    st.subheader("Precio del plato")
    opcion_precio = st.selectbox(
        "¿Cómo querés definir el precio?",
        ["Standard (precio automático)", "Ingresar precio manualmente"]
    )
    precio_plato = None  # default
    if opcion_precio == "Ingresar precio manualmente":
        precio_plato = st.number_input(
            "Precio",
            min_value=0.0,
            step=0.1,
            format="%.2f"
        )
    else:
        precio_plato = "standard"
    
    # Obtener ingredientes existentes de SQL
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre, Unidad FROM Ingredientes")
    ingredientes_bd = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()   # dict Nombre -> Unidad

    # --- INGREDIENTES TEMPORALES ---
    if "ingredientes_temp" not in st.session_state: #session_state es un diccionario. lo que hace es guardar valores entre recargas (cada vez que hago click la pagina se recarga)
        st.session_state.ingredientes_temp = [] #La primera vez que se carga la página se crea esta lista, y luego permite guardar los valores hasta el commit

    st.subheader("Agregar ingredientes al plato")
    # Selectbox con ingredientes existentes
    ing_nombre = st.selectbox("Ingrediente", list(ingredientes_bd.keys()))
    # Mostrar la unidad automáticamente
    st.caption(f"Unidad: **{ingredientes_bd[ing_nombre]}**")
    # Cantidad
    ing_cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1)

    if st.button("Agregar ingrediente a la receta"): #Agregar al diccionario temporal el ingrediente (se refresca y se mantiene)
        ingredientes_existentes= [ing['nombre'].lower() for ing in st.session_state.ingredientes_temp]
        if ing_nombre.lower() in ingredientes_existentes:
            st.error("Ese ingrediente ya fue agregado.")
        else:
            st.session_state.ingredientes_temp.append({
                "nombre": ing_nombre,
                "cantidad": ing_cantidad,
                "unidad": ingredientes_bd[ing_nombre]  # guardo unidad también
            })
            st.success(f"{ing_nombre} agregado")

    st.write("Ingredientes agregados:")


    for index, item in enumerate(st.session_state.ingredientes_temp):
        col1, col2, col3, col4 = st.columns([5, 3, 3, 1], gap='small') #Los números son formato de columna

        with col1:
            st.markdown(f"**{item['nombre']}**") #el doble ** muestra en negrita

        with col2:
            st.markdown(f"{item['cantidad']}")

        with col3:
            st.markdown(f"_{item['unidad']}_")

        with col4:
            if st.button("❌", key=f"delete_{index}"):
                st.session_state.ingredientes_temp.pop(index)
                st.rerun()

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
with tab5:
    st.header("Modificar Plato")
    # --- 1. Traer platos existentes ---
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre, Categoria, Precio FROM Platos")
    platos_bd = cursor.fetchall()  # Lista de tuplas: (Nombre, Categoria, Precio)
    cursor.close()

    # Crear diccionarios para precargar
    platos_nombres = [p[0] for p in platos_bd]
    platos_info = {p[0]: {"categoria": p[1], "precio": p[2]} for p in platos_bd}

    # --- 2. Selección del plato ---
    plato_seleccionado = st.selectbox("Seleccione el plato a modificar", platos_nombres)

    if plato_seleccionado:
        info_actual = platos_info[plato_seleccionado]

        # --- 3. Campos de modificación con valores por defecto ---
        nuevo_nombre = st.text_input("Nuevo nombre", value=plato_seleccionado)
        nuevo_precio = st.number_input(
            "Nuevo precio", 
            min_value=0.0, 
            step=0.1, 
            value= float(info_actual["precio"]) if info_actual["precio"] is not None else 0.0
        )

        index_actual = categorias_existentes.index(info_actual["categoria"]) if info_actual["categoria"] in categorias_existentes else 0
        nueva_categoria= st.selectbox(
            "Elegir categoría",
            categorias_existentes + ["Agregar categoria"],
            key="selectbox_categoria_1",
            index=index_actual  # <-- índice numérico
        )

        if nueva_categoria == "Agregar categoria":
            nueva_categoria= st.text_input("Nueva categoría",key="selectbox_categoria_2")
        # --- MODIFICAR RECETA ---
        st.subheader("Receta actual")

        # Traer receta desde SQL
        if "cambios_receta" not in st.session_state:
            st.session_state.cambios_receta = {}
        if "plato_actual" not in st.session_state:
            st.session_state.plato_actual = plato_seleccionado
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Ingrediente, Cantidad, Unidad 
                FROM Receta 
                WHERE Plato = ?
            """, plato_seleccionado)  # plato_seleccionado = el que elegiste en el selectbox
            st.session_state.receta_visual = [
                {"ingrediente": r[0], "cantidad": float(r[1]), "unidad": r[2]}
                for r in cursor.fetchall()
            ]
            cursor.close()
        if st.session_state.plato_actual != plato_seleccionado:
            # plato cambiado → reset receta
            st.session_state.receta_visual = []
            st.session_state.cambios_receta = {}
            st.session_state.plato_actual = plato_seleccionado
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Ingrediente, Cantidad, Unidad 
                FROM Receta 
                WHERE Plato = ?
            """, plato_seleccionado)  # plato_seleccionado = el que elegiste en el selectbox
            st.session_state.receta_visual = [
                {"ingrediente": r[0], "cantidad": float(r[1]), "unidad": r[2]}
                for r in cursor.fetchall()
            ]
            cursor.close()

        for index, ing in enumerate(st.session_state.receta_visual):
            col1, col2, col3, col4 = st.columns([5, 3, 3, 1], gap='small')
            
            with col1:
                st.markdown(f"**{ing['ingrediente']}**")
            
            with col2:
                # Campo editable para cantidad
                nueva_cantidad = st.number_input(
                    "cant",
                    value=float(ing["cantidad"]),
                    min_value=0.001,
                    step=0.1,
                    key=f"cant_{plato_seleccionado}_{ing['ingrediente']}",
                    label_visibility="collapsed"
                )
                # Guardar si cambió
                if nueva_cantidad != float(ing["cantidad"]):
                    st.session_state.cambios_receta[ing["ingrediente"]] = nueva_cantidad
            
            with col3:
                st.markdown(f"_{ing['unidad']}_")
            
            with col4:
                if st.button("❌", key=f"delete_{plato_seleccionado}_{ing['ingrediente']}"):
                    st.session_state.receta_visual.pop(index)
                    st.session_state.cambios_receta[ing["ingrediente"]] = 0
                    st.success(f"{ing['ingrediente']} eliminado")
                    st.rerun()
        # --- 4. Botón para confirmar cambios ---
        cambios_receta=st.session_state.cambios_receta
        if st.button("Modificar plato"):
            ok, msg = modificar_plato(conn, plato_seleccionado, nuevo_nombre, nuevo_precio, nueva_categoria,cambios_receta)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


    st.header("Eliminar Plato")
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre FROM Platos")
    platos_bd = cursor.fetchall()  # Lista de tuplas: (Nombre, Categoria, Precio)
    cursor.close()
    # Crear diccionarios para precargar
    platos_nombres = [p[0] for p in platos_bd]

    # --- 2. Selección del plato ---
    plato_seleccionado = st.selectbox("Seleccione el plato a eliminar", platos_nombres)
    if st.button("Eliminar plato"):
            ok, msg = borrar_plato(conn, plato_seleccionado)
            if ok:
                st.success(msg)
            else:
                st.error(msg)