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
with tab4:    
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

    # --- INGREDIENTES TEMPORALES ---
    if "ingredientes_temp" not in st.session_state: #session_state es un diccionario. lo que hace es guardar valores entre recargas (cada vez que hago click la pagina se recarga)
        st.session_state.ingredientes_temp = [] #La primera vez que se carga la página se crea esta lista, y luego permite guardar los valores hasta el commit        
    
    # Obtener ingredientes y elaborados existentes de SQL
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre, Unidad FROM Ingredientes WHERE Elaborado=0")
    ingredientes_bd = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()   # dict Nombre -> Unidad
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre FROM Ingredientes WHERE Elaborado=1")
    elaborados_bd = [row[0] for row in cursor.fetchall()]
    cursor.close()   

    #Opción de producto elaborado
    producto_elaborado= st.checkbox("Producto elaborado(proveedor)")
    if producto_elaborado:
        st.subheader("Producto elaborado")
        ingredientes_existentes= [ing['nombre'].lower() for ing in st.session_state.ingredientes_temp]
        nombre_elaborado=st.selectbox("Nombre", elaborados_bd+["Agregar Producto"])
        if nombre_elaborado=="Agregar Producto":
            nombre_elaborado=st.text_input("Nombre")
            precio_elaborado=st.number_input("Precio unitario",min_value=0.0,step=0.1,format="%.2f")
            cantidad_elaborado= st.number_input("Unidades que utiliza el plato", min_value=0.0,step=0.1)
            gluten_free_elaborado = st.checkbox("Gluten Free",key="gluten_tab4")
            dairy_free_elaborado = st.checkbox("Dairy Free",key="dairy_tab4")

        if st.button("Agregar producto elaborado"): #Agregar al diccionario temporal el producto (se refresca y se mantiene)
            if nombre_elaborado.lower() not in ingredientes_existentes:
                if not nombre_elaborado or nombre_elaborado.strip() == "":
                    st.error("Ingrese un Nombre")
                else:
                    st.session_state.ingredientes_temp.append({
                        "nombre": nombre_elaborado,
                        "cantidad": cantidad_elaborado,
                        "unidad": "unidad"
                    })
                    if nombre_elaborado not in elaborados_bd:
                        success, message, nombre, unidad = agregar_nuevo_ingrediente(
                            conn, nombre_elaborado, precio_elaborado, 1, "unidad", gluten_free_elaborado, dairy_free_elaborado,1
                        )
                        if success:
                            st.success(message)
          
                        else:
                            st.error(message)
                    
                    st.success(f"{nombre_elaborado} agregado a receta")
                    st.rerun()
            else:
                st.error("El producto ya está ingresado")
     
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
    # --- CREAR PLATO ---
    if st.button("Crear plato"):
        if not nombre_plato or nombre_plato.strip() == "":
            st.error("El campo 'Nombre del plato' está vacío")
        else:
            if st.session_state.ingredientes_temp:
                
                ok, msg = agregar_nuevo_plato(
                    conn,
                    nombre_plato,
                    categoria_plato,
                    precio_plato,
                    st.session_state.ingredientes_temp
                )

                if ok:
                    st.success(msg)
                    st.session_state.ingredientes_temp = [] #reset
                else:
                    st.error(msg)
            else:
                st.error("Ingrese al menos 1 ingrediente/elaborado")
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

        index_actual = categorias_existentes.index(info_actual["categoria"]) if info_actual["categoria"] in categorias_existentes else 0#Busco el índice de la categoria del plato, asi la muestro preseleccionada
        nueva_categoria= st.selectbox(
            "Elegir categoría",
            categorias_existentes + ["Agregar categoria"],
            key="selectbox_categoria_1",
            index=index_actual  # <-- índice numérico
        )

        if nueva_categoria == "Agregar categoria":
            nueva_categoria= st.text_input("Nueva categoría",key="selectbox_categoria_2")
            if nueva_categoria in categorias_existentes:
                nueva_categoria = "Agregar categoria"
                st.error("Categoría ya existente")

        # --- MODIFICAR RECETA ---
        st.subheader("Receta actual")

        # Traer receta desde SQL

        if "plato_actual" not in st.session_state or st.session_state.plato_actual != plato_seleccionado: #Si se está inicializando o si cambias de plato
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
            ingredientes_db_actuales=[a['ingrediente'] for a in st.session_state.receta_visual]
            st.session_state.ingredientes_db_actuales=ingredientes_db_actuales #Guardo los ingredientes del plato que estan en la BASE DE DATOS (esto no cambia hasta que guarde los cambios)
            st.session_state.nuevo_ingrediente='Elton'

        ingredientes_actuales=[a['ingrediente'] for a in st.session_state.receta_visual]#Son los ingredientes del plato que se muestran en pantalla (no son necesariamente los mismos que BD)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Nombre,Unidad 
            FROM Ingredientes 
            """,)
        ingredientes_total={a[0]:a[1] for a in cursor.fetchall()}#Todos los ingredientes con sus unidades
        ingredientes_total_nombres=list(ingredientes_total.keys())#Lista de todos los ingredientes
        cursor.close()

        for index, ing in enumerate(st.session_state.receta_visual):
            col1, col2, col3, col4 = st.columns([5, 3, 3, 1], gap='small')
            
            with col1:
                if ing['ingrediente']:
                    st.markdown(f"**{ing['ingrediente']}**")
                else:
                     # Selectbox SIN valor inicial
                    nuevo_ingrediente = st.selectbox(
                        "Elegir ingrediente",
                        [x for x in ingredientes_total_nombres if x not in ingredientes_actuales],
                        index=None,
                        key=f"selectbox_ingredientes_mod_{index}"
                    )
                    st.session_state.nuevo_ingrediente=nuevo_ingrediente#Si no elijo nada, este parámetro de hace None y luego no me permite agregar otro ing
                    # Solo actualizar si el usuario eligió algo real
                    if nuevo_ingrediente:
                        st.session_state.receta_visual[index]['ingrediente'] = nuevo_ingrediente
                        st.session_state.receta_visual[index]['unidad'] = ingredientes_total[nuevo_ingrediente]
                        if nuevo_ingrediente not in st.session_state.ingredientes_db_actuales:
                            st.session_state.cambios_receta[nuevo_ingrediente]={"cantidad":0.01,"nuevo":True,"unidad":ingredientes_total[nuevo_ingrediente]}
                        else:
                            st.session_state.cambios_receta[nuevo_ingrediente]={"cantidad":0.01,"nuevo":False,"unidad":ingredientes_total[nuevo_ingrediente]}
                        
                        st.rerun()
            with col2:
                # Campo editable para cantidad, muestra por defecto la cantidad actual
                nueva_cantidad = st.number_input(
                    "cant",
                    value=float(ing["cantidad"]),
                    min_value=0.01,
                    step=0.1,
                    key=f"cant_{plato_seleccionado}_{ing['ingrediente']}",
                    label_visibility="collapsed"
                )
                # Guardar si cambió
                if nueva_cantidad != float(ing["cantidad"]):
                    if ing["ingrediente"] not in st.session_state.cambios_receta:#Si era un ingrediente ya existente, no iba estar nunca en cambios_receta.
                        st.session_state.cambios_receta[ing["ingrediente"]] = {
                            "cantidad": float(nueva_cantidad),
                            "nuevo": False,
                            "unidad": ing["unidad"]
                        }
                    st.session_state.cambios_receta[ing["ingrediente"]]["cantidad"] = nueva_cantidad
            
            with col3:
                st.markdown(f"_{ing['unidad']}_")

            with col4:
                if st.button("❌", key=f"delete_{plato_seleccionado}_{ing['ingrediente']}"):
                    st.session_state.receta_visual.pop(index)
                    st.session_state.cambios_receta[ing["ingrediente"]]={"cantidad":0} #Puede dar la orden de borrar un ing que ni esté en la base, pero por como es la función a lo sumo no borra nada, no da eror.
                    st.success(f"{ing['ingrediente']} eliminado")
                    st.rerun()
        if st.button("Agregar ingrediente"):
            if st.session_state.nuevo_ingrediente==None:
                st.error("Finalice selección anterior")
            else:
                st.session_state.receta_visual.append({
                    "ingrediente": None,
                    "cantidad": 0.01,
                    "unidad": None
                })
                st.rerun()
        # --- 4. Botón para confirmar cambios ---
        cambios_receta=st.session_state.cambios_receta
        if st.button("Modificar plato"):
            if st.session_state.receta_visual:#Controlo que el plato tenga al menos 1 ingrediente
                ok, msg = modificar_plato(conn, plato_seleccionado, nuevo_nombre, nuevo_precio, nueva_categoria,cambios_receta)
                if ok:
                    st.success(msg)
                    st.session_state.cambios_receta={}
                    for ing in st.session_state.receta_visual:
                        if ing["ingrediente"] not in st.session_state.ingredientes_db_actuales:
                            st.session_state.ingredientes_db_actuales.append(ing["ingrediente"])
                else:
                    st.error(msg)
            else:
                st.error("El plato debe tener al menos 1 ingrediente")


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