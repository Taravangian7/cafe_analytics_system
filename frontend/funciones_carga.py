from backend.upload_data.upload import cargar_ingredientes_desde_csv,cargar_ingredientes_desde_excel,cargar_platos_y_recetas_desde_csv,cargar_platos_y_recetas_desde_excel,cargar_ordenes_desde_csv,cargar_ordenes_desde_excel
import streamlit as st
from backend.create_plato import agregar_nuevo_ingrediente,obtener_campos,agregar_nuevo_plato



def carga_plato_y_receta_manual(conn,prefix):
    # --- DATOS DEL PLATO ---
        nombre_plato = st.text_input("Nombre del plato",value="",key=f'{prefix}_nombre_plato')
        categorias_existentes= obtener_campos(conn,campos=['categoria'],tabla='Platos')#Lista con todas las categorías
        categoria_plato = st.selectbox("Elegir categoría",categorias_existentes+["Agregar categoria"],key=f'{prefix}_categoria_plato')
        if categoria_plato == "Agregar categoria":
            categoria_plato= st.text_input("Nueva categoría",key=f'{prefix}_nueva_categoria')

        # --- INGREDIENTES TEMPORALES ---
        temp_key = f"{prefix}_ingredientes_temp"
        if temp_key not in st.session_state: #session_state es un diccionario. lo que hace es guardar valores entre recargas (cada vez que hago click la pagina se recarga)
            st.session_state[temp_key] = [] #La primera vez que se carga la página se crea esta lista, y luego permite guardar los valores hasta el commit        
        
        # Obtener ingredientes y elaborados existentes de SQL

        ingredientes_bd= obtener_campos(conn,campos=["Nombre","Unidad"],tabla="Ingredientes",where="Elaborado",where_valor=0,formato="dict")
        elaborados_bd= obtener_campos(conn,campos=["Nombre"],tabla="Ingredientes",where="Elaborado",where_valor=1)

        #Opción de producto elaborado
        producto_elaborado= st.checkbox("Producto elaborado(proveedor)",key=f'{prefix}_producto_elaborado')
        if producto_elaborado:
            st.subheader("Producto elaborado")
            ingredientes_existentes= [ing['nombre'].lower() for ing in st.session_state[temp_key]]
            nombre_elaborado=st.selectbox("Nombre", elaborados_bd+["Agregar Producto"],key=f'{prefix}_nombre_elaborado')
            if nombre_elaborado=="Agregar Producto":
                nombre_elaborado=st.text_input("Nombre",key=f'{prefix}_nombre_elaborado_2')
                precio_elaborado=st.number_input("Precio unitario",min_value=0.0,step=0.1,format="%.2f",key=f'{prefix}_precio_elaborado')
                gluten_free_elaborado = st.checkbox("Gluten Free",key=f'{prefix}_gf_elaborado')
                dairy_free_elaborado = st.checkbox("Dairy Free",key=f'{prefix}_df_elaborado')
            cantidad_elaborado= st.number_input("Unidades que utiliza el plato", min_value=0.0,step=0.1,key=f'{prefix}_cantidad_elaborado')

            if st.button("Agregar producto elaborado",key=f'{prefix}_agregar_elaborado'): #Agregar al diccionario temporal el producto (se refresca y se mantiene)
                if nombre_elaborado.lower() not in ingredientes_existentes:
                    if not nombre_elaborado or nombre_elaborado.strip() == "":
                        st.error("Ingrese un Nombre")
                    else:
                        st.session_state[temp_key].append({
                            "nombre": nombre_elaborado,
                            "cantidad": cantidad_elaborado,
                            "unidad": "unidades"
                        })
                        if nombre_elaborado not in elaborados_bd:
                            success, message, nombre, unidad = agregar_nuevo_ingrediente(
                                conn, nombre_elaborado, precio_elaborado, 1, "unidades", gluten_free_elaborado, dairy_free_elaborado,1
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
        ing_nombre = st.selectbox("Ingrediente", list(ingredientes_bd.keys()),key=f'{prefix}_nombre_ingrediente')
        # Mostrar la unidad automáticamente
        st.caption(f"Unidad: **{ingredientes_bd[ing_nombre]}**")
        # Cantidad
        ing_cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1,key=f'{prefix}_cantidad_ing')

        if st.button("Agregar ingrediente a la receta",key=f'{prefix}_agregar_ing_receta'): #Agregar al diccionario temporal el ingrediente (se refresca y se mantiene)
            ingredientes_existentes= [ing['nombre'].lower() for ing in st.session_state[temp_key]]
            if ing_nombre.lower() in ingredientes_existentes:
                st.error("Ese ingrediente ya fue agregado.")
            else:
                st.session_state[temp_key].append({
                    "nombre": ing_nombre,
                    "cantidad": ing_cantidad,
                    "unidad": ingredientes_bd[ing_nombre]  # guardo unidad también
                })
                st.success(f"{ing_nombre} agregado")

        st.write("Ingredientes agregados:")


        for index, item in enumerate(st.session_state[temp_key]):
            col1, col2, col3, col4 = st.columns([5, 3, 3, 1], gap='small') #Los números son formato de columna

            with col1:
                st.markdown(f"**{item['nombre']}**") #el doble ** muestra en negrita

            with col2:
                st.markdown(f"{item['cantidad']}")

            with col3:
                st.markdown(f"_{item['unidad']}_")

            with col4:
                if st.button("❌", key=f"{prefix}_delete_{index}"):
                    st.session_state[temp_key].pop(index)
                    st.rerun()

        st.subheader("Precio del plato")
        opcion_precio = st.selectbox(
            "¿Cómo querés definir el precio?",
            ["Standard (precio automático)", "Ingresar precio manualmente"],key=f'{prefix}_precio_plato'
        )
        precio_plato = None  # default
        if opcion_precio == "Ingresar precio manualmente":
            precio_plato = st.number_input(
                "Precio",
                min_value=0.0,
                step=0.1,
                format="%.2f",key=f'{prefix}_precio_plato2'
            )
        else:
            precio_plato = "standard"
        # --- CREAR PLATO ---
        if st.button("Crear plato",key=f'{prefix}_crear_plato'):
            if not nombre_plato or nombre_plato.strip() == "":
                st.error("El campo 'Nombre del plato' está vacío")
            else:
                if st.session_state[temp_key]:
                    
                    ok, msg = agregar_nuevo_plato(
                        conn,
                        nombre_plato,
                        categoria_plato,
                        precio_plato,
                        st.session_state[temp_key]
                    )

                    if ok:
                        st.success(msg)
                        st.session_state[temp_key]=[]
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Ingrese al menos 1 ingrediente/elaborado")

def carga_ingredientes_ui(conn):
    tipo = st.selectbox("Tipo de carga",["csv", "excel", "manual"],key="tipo_carga_ing")

    if tipo == "csv":
        archivo = st.file_uploader(
            "Seleccioná un archivo CSV",
            type=["csv"],
            key="csv_ing"
        )
        if st.button("Cargar ingredientes CSV", key="btn_csv_ing"):
            estado, message, ingresados = cargar_ingredientes_desde_csv(conn, archivo)
            st.info(message)

    elif tipo == "excel":
        archivo = st.file_uploader("Seleccioná un archivo Excel",type=["xlsx"],key="excel_ing")
        if st.button("Cargar ingredientes Excel", key="btn_excel_ing"):
            estado, message, ingresados = cargar_ingredientes_desde_excel(conn, archivo)
            st.info(message)

    else:
        with st.form("form_ingrediente"):
            nombre = st.text_input("Nombre del ingrediente")
            costo = st.number_input("Costo", min_value=0.0, step=0.01)
            cantidad = st.number_input("Cantidad por Paquete", min_value=0.01, step=0.01)
            unidad = st.selectbox("Unidad", ["gr","kg","cm3","litro", "unidades"])
            gluten_free = st.checkbox("Gluten Free")
            dairy_free = st.checkbox("Dairy Free")
            elaborado= st.checkbox("Elaborado")

            submitted = st.form_submit_button("Guardar")
            if submitted:
                success, message, nombre, unidad = agregar_nuevo_ingrediente(conn, nombre, costo, cantidad, unidad, gluten_free, dairy_free,elaborado)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def carga_platos_y_recetas_ui(conn,prefix):
    tipo = st.selectbox("Tipo de carga",["csv", "excel", "manual"],key="tipo_carga_plato")

    if tipo == "csv":
        archivo_plato = st.file_uploader(
            "Seleccioná CSV para Platos",
            type=["csv"],
            key="csv_plato"
        )
        archivo_receta = st.file_uploader(
            "Seleccioná CSV para Receta",
            type=["csv"],
            key="csv_receta"
        )

        if st.button("Cargar platos y recetas CSV", key="btn_csv_plato_receta"):
            estado, message, ingresados = cargar_platos_y_recetas_desde_csv(conn, archivo_plato,archivo_receta)
            st.info(message)

    elif tipo == "excel":
        archivo_plato = st.file_uploader("Seleccioná Excel de Platos",type=["xlsx"],key="excel_plato")
        archivo_receta = st.file_uploader("Seleccioná Excel de Recetas",type=["xlsx"],key="excel_receta")
        if st.button("Cargar platos y recetas Excel", key="btn_excel_plato"):
            estado, message, ingresados = cargar_platos_y_recetas_desde_excel(conn, archivo_plato,archivo_receta)
            st.info(message)

    else:
        carga_plato_y_receta_manual(conn,prefix)

def carga_ordenes_ui(conn):
    tipo = st.selectbox("Tipo de carga",["csv", "excel"],key="tipo_carga_ordenes")

    if tipo == "csv":
        archivo_orders = st.file_uploader(
            "Seleccioná CSV para Órdenes",
            type=["csv"],
            key="csv_orders"
        )
        archivo_items = st.file_uploader(
            "Seleccioná CSV para Items",
            type=["csv"],
            key="csv_items"
        )

        if st.button("Cargar ordenes CSV", key="btn_csv_ordenes"):
            estado, message, ordenes_ingresados,items_ingresados = cargar_ordenes_desde_csv(conn, archivo_orders,archivo_items)
            st.info(message)

    elif tipo == "excel":
        archivo_orders = st.file_uploader("Seleccioná Excel de Órdenes",type=["xlsx"],key="excel_orders")
        archivo_items = st.file_uploader("Seleccioná Excel de Items",type=["xlsx"],key="excel_items")
        if st.button("Cargar Órdenes desde Excel", key="btn_excel_orders"):
            estado, message, ordenes_ingresados,items_ingresados = cargar_ordenes_desde_excel(conn, archivo_orders,archivo_items)
            st.info(message)

