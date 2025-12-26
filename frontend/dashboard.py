import streamlit as st
import altair as alt
import pyodbc
import pandas as pd
import sys
from pathlib import Path
from datetime import date,datetime,timedelta
import matplotlib.pyplot as plt

# Agregar carpeta padre al path (para encontrar create_plato)
sys.path.append(str(Path(__file__).parent.parent))
from backend.create_plato import agregar_nuevo_ingrediente, agregar_nuevo_plato, borrar_plato, modificar_plato,modificar_ingrediente,obtener_campos
from backend.data_analyst import true_if_data,rango_fechas,get_metodos_pago, get_ventas_por_hora, get_ventas_por_franja_horaria,  get_ventas_por_dia_semana, get_ticket_promedio,get_revenue_por_periodo
from backend.data_analyst import get_top_productos_vendidos,get_productos_menos_vendidos,get_ventas_por_categoria,get_rentabilidad_por_producto,get_margen_por_producto
from backend.data_analyst import get_ganancia_bruta_total,get_margen_promedio_negocio,get_food_cost_percentage,get_productos_especiales_vendidos,get_dine_in_vs_takeaway,get_combos_frecuentes,get_ventas_por_mes,get_ingresos_ultimas_semanas,variacion_semanal_mensual
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
    st.header("Análisis de Datos")
    if true_if_data(conn):
        ultimas_12_semanas= get_ingresos_ultimas_semanas(conn)
        ingreso_semana_actual,variacion_semanal,ingreso_mes_actual,variacion_mensual=variacion_semanal_mensual(ultimas_12_semanas)
        
        col1, col2 = st.columns(2)
        col1.metric(
            label="Ingreso última semana",
            value=f"${ingreso_semana_actual:,.0f}",
            delta=variacion_semanal
        )

        col2.metric(
            label="Ingreso últimas 4 semanas",
            value=f"${ingreso_mes_actual:,.0f}",
            delta=variacion_mensual
        )

        st.subheader("Ingresos últimos 3 meses")
        
        chart = (
            alt.Chart(ultimas_12_semanas)
            .mark_bar()
            .encode(
                x=alt.X(
                    'semana:O',
                    title='Semana (1 = más reciente)',
                    sort='descending'
                ),
                y=alt.Y(
                    'revenue:Q',
                    title='Ingresos'
                ),
                tooltip=[
                    alt.Tooltip('semana:O', title='Semana'),
                    alt.Tooltip('fecha_inicio:T', title='Fecha inicio'),
                    alt.Tooltip('fecha_fin:T', title='Fecha fin'),
                    alt.Tooltip('revenue:Q', title='Ingresos', format='$,.2f'),
                    alt.Tooltip('num_ordenes:Q', title='Cantidad de órdenes'),
                ]
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    st.header("Seleccionar Rango de Fechas")
    fechas= st.selectbox("Rango de fechas",["Última semana","Último mes","Ingrese manualmente"])
    if fechas=="Última semana":
        fecha_fin=datetime.now().date()
        fecha_inicio=fecha_fin-timedelta(weeks=1)
    elif fechas=="Último mes":
        fecha_fin=datetime.now().date()
        fecha_inicio=fecha_fin-timedelta(weeks=4)
    else:
        fechas,anios_in=rango_fechas(conn)
        col1, col2, col3 = st.columns(3)
        with col1:
            anio_inicio = st.selectbox("Año Inicio", anios_in)
        if anio_inicio:
            meses_in = rango_fechas(conn, anio=anio_inicio)
            with col2:
                mes_inicio = st.selectbox("Mes Inicio", meses_in)
        else:
            mes_inicio = None
        if anio_inicio and mes_inicio:
            dias_in = rango_fechas(conn, anio=anio_inicio, mes=mes_inicio)
            with col3:
                dia_inicio = st.selectbox("Día Inicio", dias_in)
        fecha_inicio=date(anio_inicio,mes_inicio,dia_inicio)

        if fecha_inicio:
            fechas_fin,anios_fin=rango_fechas(conn,fecha_inicial=fecha_inicio)
            col1, col2, col3 = st.columns(3)
            with col1:
                anio_fin = st.selectbox("Año Fin", anios_fin)
            if anio_fin:
                meses_fin = rango_fechas(conn, anio=anio_fin,fecha_inicial=fecha_inicio)
                with col2:
                    mes_fin = st.selectbox("Mes Fin", meses_fin)
            else:
                mes_fin = None
            if anio_fin and mes_fin:
                dias_fin = rango_fechas(conn, anio=anio_fin, mes=mes_fin,fecha_inicial=fecha_inicio)
                with col3:
                    dia_fin = st.selectbox("Día Fin", dias_fin)
            fecha_fin=date(anio_fin,mes_fin,dia_fin)
    
    
    fecha_con_datos=true_if_data(conn,fecha_inicio,fecha_fin)
    
    if fecha_con_datos:
        st.header("Análisis de datos")
        ventas_data=st.checkbox(label="Datos de ventas")
        if ventas_data:
            
            # Revenue por día
            st.subheader("Ganancias por día")
            df_revenue = get_revenue_por_periodo(conn, periodo='dia',fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            if not df_revenue.empty:
                st.line_chart(df_revenue.set_index('periodo'),y_label="Ganancias")
            
            # Ticket promedio
            st.subheader("Tickets promedio vendidos")
            ticket = get_ticket_promedio(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            if ticket !=0:
                st.metric("Consumo promedio por orden", f"${ticket:.2f}")
            #Ventas promedio por día de semana
            st.subheader("Ventas promedio por día de semana")
            df_ventas_por_dia=get_ventas_por_dia_semana(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            if not df_ventas_por_dia.empty:
                st.bar_chart(df_ventas_por_dia.set_index('dia_semana')[['revenue_promedio','num_ordenes_promedio']])
            #Ventas por franja horaria
            st.subheader("Ventas por franja horaria")
            df_ventas_franja_horaria=get_ventas_por_franja_horaria(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            if not df_ventas_franja_horaria.empty:
                st.bar_chart(df_ventas_franja_horaria.set_index('franja_horaria')[['revenue','num_ordenes']])
            #Ventas por hora
            st.subheader("Ventas promedio por horario")
            df_ventas_por_hora=get_ventas_por_hora(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            if not df_ventas_por_hora.empty:
                st.line_chart(df_ventas_por_hora.set_index('hora')[['revenue_promedio','num_ordenes_promedio']])
            #Método de pago
            st.subheader("Distribución de Operaciones por Método de Pago")
            df_metodo_pago = get_metodos_pago(conn, fecha_inicio, fecha_fin)
            chart = (
                alt.Chart(df_metodo_pago)
                .mark_arc(innerRadius=50)  # donut, más fachero
                .encode(
                    theta=alt.Theta('revenue:Q', title='Ingresos'),
                    color=alt.Color('metodo_pago:N', title='Método de pago'),
                    tooltip=[
                        alt.Tooltip('metodo_pago:N', title='Tipo'),
                        alt.Tooltip('revenue:Q', title='Ingresos', format="$.2f"),
                        alt.Tooltip('num_ordenes:Q', title='Cantidad de órdenes'),
                        alt.Tooltip('porcentaje:Q', title='Porcentaje', format=".1f")
                    ]
                )
                .properties(height=400)
            )

            st.altair_chart(chart, use_container_width=True)


        productos_data=st.checkbox(label="Datos de productos")
        if productos_data:
            # Productos más vendidos
            st.subheader("Productos más vendidos")
            productos_vendidos_criterio=st.selectbox(label="Seleccione un criterio",options=["cantidad","revenue"])
            df_productos_vendidos=get_top_productos_vendidos(conn,10,productos_vendidos_criterio,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
                alt.Chart(df_productos_vendidos)
                .mark_bar()
                .encode(
                    x=alt.X(productos_vendidos_criterio, title=productos_vendidos_criterio),
                    y=alt.Y('producto:N', sort=None, title='Producto')  # respeta el orden original del DataFrame
                )
                .properties(height=400)
            )

            st.altair_chart(chart, use_container_width=True)
            # Productos menos vendidos
            st.subheader("Productos menos vendidos")
            df_productos_menos_vendidos=get_productos_menos_vendidos(conn,10,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
            alt.Chart(df_productos_menos_vendidos)
            .mark_bar()
            .encode(
                # cantidad va en X (valor numérico) -> :Q
                x=alt.X('cantidad:Q', title='Cantidad'),
                # producto en Y (categoría) -> :N ; sort=None preserva el orden del DataFrame
                y=alt.Y('producto:N', sort=None, title='Producto'),
                # tooltip VA DENTRO de encode
                tooltip=[
                    alt.Tooltip('producto:N', title='Producto'),
                    alt.Tooltip('revenue:Q', title='Ingresos', format="$.2f"),
                    alt.Tooltip('cantidad:Q', title='Cantidad'),
                    alt.Tooltip('ultima_venta:T', title='Última venta')
                ]
            )
            .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            # Ventas por categoría
            st.subheader("Ventas por categorías")
            df_ventas_categoria=get_ventas_por_categoria(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
                alt.Chart(df_ventas_categoria)
                .mark_bar()
                .encode(
                    x=alt.X('revenue:Q', title='Ingresos'),
                    y=alt.Y('categoria:N', sort='-x', title='Categoría'),
                    tooltip=[
                        alt.Tooltip('categoria:N', title='Categoría'),
                        alt.Tooltip('revenue:Q', title='Ingresos', format="$.2f"),
                        alt.Tooltip('cantidad_vendida:Q', title='Cantidad vendida'),
                        alt.Tooltip('num_productos:Q', title='Productos en categoría')
                    ]
                )
            .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            # Rentabilidad por producto
            st.subheader("Rentabilidad por producto")
            df_rentabilidad=get_rentabilidad_por_producto(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
                alt.Chart(df_rentabilidad)
                .mark_bar()
                .encode(
                    x=alt.X('ganancia_bruta:Q', title='Ganancia Bruta'),
                    y=alt.Y('producto:N', sort='-x', title='Producto'),
                    tooltip=[
                        alt.Tooltip('revenue:Q', title='Ingresos', format="$.2f"),
                        alt.Tooltip('cantidad_vendida:Q', title='Cantidad vendida'),
                        alt.Tooltip('margen_porcentaje:Q', title='Margen de ganancia (%)') #Del precio total, este porcentaje es ganancia
                    ]
                )
            .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            # Margen que deja cada producto
            st.subheader("Margen por producto (unitario)")
            df_margen_producto=get_margen_por_producto(conn)
            chart = (
                alt.Chart(df_margen_producto)
                .mark_bar()
                .encode(
                    x=alt.X('margen_porcentaje:Q', title='Margen de ganancia (%)'),
                    y=alt.Y('producto:N', sort='-x', title='Producto'),
                    tooltip=[
                        alt.Tooltip('precio:Q', title='Precio', format="$.2f"),
                        alt.Tooltip('costo:Q', title='Costo', format="$.2f"),
                        alt.Tooltip('margen_porcentaje:Q', title='Margen (%)') #Del precio total, este porcentaje es ganancia
                    ]
                )
            .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
        #RENTABILIDAD GLOBAL
        rentabilidad_data=st.checkbox(label="Datos de rentabilidad global")
        if rentabilidad_data:
            # Ganancia bruta total
            st.subheader("Rentabilidad Global")
            dict_ganancia_bruta= get_ganancia_bruta_total(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            margen_promedio_negocio= get_margen_promedio_negocio(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ingresos Totales", f"${dict_ganancia_bruta['revenue']:,.0f}")
            col2.metric("Costo Total", f"${dict_ganancia_bruta['costo_total']:,.0f}")
            col3.metric("Ganancia Bruta", f"${dict_ganancia_bruta['ganancia_bruta']:,.0f}")
            col4.metric("Margen de Ganancias", f"{margen_promedio_negocio:.1f}%")
        #TENDENCIAS
        tendencias_data=st.checkbox(label="Tendencias")
        if tendencias_data:
            # Ventas por mes
            st.subheader("Ventas mensuales")
            ventas_por_mes= get_ventas_por_mes(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            metrica_tendencia_mes = st.selectbox(label="Métrica",options=["revenue", "cantidad de órdenes"])
            if metrica_tendencia_mes=="cantidad de órdenes":
                metrica_tendencia_mes="num_ordenes"
            titulo_tendencia_mes = "Ingresos" if metrica_tendencia_mes == "revenue" else "Cantidad de órdenes"

            chart = (
                alt.Chart(ventas_por_mes)
                .mark_line(point=True)
                .encode(
                    x=alt.X('periodo:N', title='Período'),
                    y=alt.Y(f'{metrica_tendencia_mes}:Q', title=titulo_tendencia_mes),
                    tooltip=[
                        alt.Tooltip('periodo:N', title='Período'),
                        alt.Tooltip(f'{metrica_tendencia_mes}:Q', title=titulo_tendencia_mes)
                    ]
                )
                .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)

        #OTROS ANÁLISIS
        costos_ingredientes_sobre_total=get_food_cost_percentage(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
        otros_data=st.checkbox(label="Otros")
        if otros_data:
            # Productos especiales vendidos
            st.subheader("Productos especiales vendidos")
            tipo_especial=st.selectbox(label="Especial",options=["Gluten Free","Dairy Free"])
            df_especiales_vendidos=get_productos_especiales_vendidos(conn, tipo=tipo_especial, top_n=5,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
                alt.Chart(df_especiales_vendidos)
                .mark_bar()
                .encode(
                    x=alt.X('revenue:Q', title='Ingresos'),
                    y=alt.Y('producto:N', sort='-x', title='Producto'),
                    tooltip=[
                        alt.Tooltip('revenue:Q', title='Ingreso', format="$.2f"),
                        alt.Tooltip('cantidad_vendida:Q', title='Cantidad vendida'),
                    ]
                )
            .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            # Dine in vs Take away
            st.subheader("Dine in vs Take away")
            df_dine_in_take_away=get_dine_in_vs_takeaway(conn,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            chart = (
                alt.Chart(df_dine_in_take_away)
                .mark_arc(innerRadius=50)  # donut, más fachero
                .encode(
                    theta=alt.Theta('revenue:Q', title='Ingresos'),
                    color=alt.Color('tipo_orden:N', title='Tipo de orden'),
                    tooltip=[
                        alt.Tooltip('tipo_orden:N', title='Tipo'),
                        alt.Tooltip('revenue:Q', title='Ingresos', format="$.2f"),
                        alt.Tooltip('num_ordenes:Q', title='Cantidad de órdenes'),
                        alt.Tooltip('porcentaje:Q', title='Porcentaje', format=".1f")
                    ]
                )
                .properties(height=400)
            )

            st.altair_chart(chart, use_container_width=True)
            # Combos de productos
            st.subheader("Combinaciones de productos")
            df_combinaciones=get_combos_frecuentes(conn, top_n=10, fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)
            df_combinaciones = (
                df_combinaciones.rename(columns={
                    'producto_1': 'Producto A',
                    'producto_2': 'Producto B',
                    'veces_juntos': 'Veces comprados juntos'
                })
                .sort_values('Veces comprados juntos', ascending=False)
            )

            st.dataframe(df_combinaciones, use_container_width=True, hide_index=True)







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
    
    st.header("Modificar ingrediente")
    ing_seleccionado = st.selectbox("Seleccione el plato a modificar", df_ingredientes["Nombre"].tolist(),index=None)
    if ing_seleccionado:
        nombre_ing=st.text_input("Nombre", value=ing_seleccionado)
        costo_ing = st.number_input("Costo", min_value=0.0, step=0.01, value=df_ingredientes[df_ingredientes["Nombre"]==ing_seleccionado]["Costo"].values[0])
        cantidad_ing = st.number_input("Cantidad por Paquete", min_value=0.01, step=0.01, value=df_ingredientes[df_ingredientes["Nombre"]==ing_seleccionado]["Cantidad"].values[0])
        unidad_actual = df_ingredientes[df_ingredientes["Nombre"]==ing_seleccionado]["Unidad"].values[0]
        opciones_unidad = ["gr","kg","cm3","litro", "unidades"]
        # Encontrar el índice de la unidad actual
        index_unidad = opciones_unidad.index(unidad_actual) if unidad_actual in opciones_unidad else 0
        unidad_ing = st.selectbox("Unidad", opciones_unidad, index=index_unidad,key=f"selectbox_unidad_mod_{ing_seleccionado}")

        gluten_free_ing = st.checkbox("Gluten Free", value=df_ingredientes[df_ingredientes["Nombre"]==ing_seleccionado]["Gluten_free"].values[0],key=f"gluten_free_{ing_seleccionado}")
        dairy_free_ing = st.checkbox("Dairy Free", value=df_ingredientes[df_ingredientes["Nombre"]==ing_seleccionado]["Dairy_free"].values[0],key=f"dairy_free_{ing_seleccionado}")
        if st.button("Modificar ingrediente"):
            success, message = modificar_ingrediente(conn, ing_seleccionado,nombre_ing, costo_ing, cantidad_ing, unidad_ing, gluten_free_ing, dairy_free_ing)
            if success:
                st.success(message)
            else:
                st.error(message)
with tab4:    
    # --- DATOS DEL PLATO ---
    st.header("Agregar nuevo plato")
    nombre_plato = st.text_input("Nombre del plato")
    categorias_existentes= obtener_campos(conn,campos=['categoria'],tabla='Platos')#Lista con todas las categorías
    categoria_plato = st.selectbox("Elegir categoría",categorias_existentes+["Agregar categoria"])
    if categoria_plato == "Agregar categoria":
        categoria_plato= st.text_input("Nueva categoría")

    # --- INGREDIENTES TEMPORALES ---
    if "ingredientes_temp" not in st.session_state: #session_state es un diccionario. lo que hace es guardar valores entre recargas (cada vez que hago click la pagina se recarga)
        st.session_state.ingredientes_temp = [] #La primera vez que se carga la página se crea esta lista, y luego permite guardar los valores hasta el commit        
    
    # Obtener ingredientes y elaborados existentes de SQL

    ingredientes_bd= obtener_campos(conn,campos=["Nombre","Unidad"],tabla="Ingredientes",where="Elaborado",where_valor=0,formato="dict")
    elaborados_bd= obtener_campos(conn,campos=["Nombre"],tabla="Ingredientes",where="Elaborado",where_valor=1)

    #Opción de producto elaborado
    producto_elaborado= st.checkbox("Producto elaborado(proveedor)")
    if producto_elaborado:
        st.subheader("Producto elaborado")
        ingredientes_existentes= [ing['nombre'].lower() for ing in st.session_state.ingredientes_temp]
        nombre_elaborado=st.selectbox("Nombre", elaborados_bd+["Agregar Producto"])
        if nombre_elaborado=="Agregar Producto":
            nombre_elaborado=st.text_input("Nombre")
            precio_elaborado=st.number_input("Precio unitario",min_value=0.0,step=0.1,format="%.2f")
            gluten_free_elaborado = st.checkbox("Gluten Free",key="gluten_tab4")
            dairy_free_elaborado = st.checkbox("Dairy Free",key="dairy_tab4")
        cantidad_elaborado= st.number_input("Unidades que utiliza el plato", min_value=0.0,step=0.1)

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
    platos_nombres = obtener_campos(conn,campos=["nombre"],tabla="Platos")
    platos_info= obtener_campos(conn,campos=["nombre","categoria","precio"],tabla="Platos",formato="dict")


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
            nueva_categoria= st.text_input("Nueva categoría",key="selectbox_categoria_2").capitalize()
            if nueva_categoria in categorias_existentes:
                nueva_categoria = "Agregar categoria"
                st.error("Categoría ya existente")

        # --- MODIFICAR RECETA ---
        st.subheader("Receta actual")

        # Traer receta desde SQL

        if "plato_actual" not in st.session_state or st.session_state.plato_actual != plato_seleccionado: #Si se está inicializando o si cambias de plato

            st.session_state.cambios_receta = {}
            st.session_state.plato_actual = plato_seleccionado
            
            #
            st.session_state.receta_visual = obtener_campos(conn,campos=["ingrediente","cantidad","unidad"],tabla="Receta",where="Plato",where_valor=plato_seleccionado,formato="lista")
            
            ingredientes_db_actuales=[list(a.keys())[0] for a in st.session_state.receta_visual]
            st.session_state.ingredientes_db_actuales=ingredientes_db_actuales #Guardo los ingredientes del plato que estan en la BASE DE DATOS (esto no cambia hasta que guarde los cambios)
            st.session_state.nuevo_ingrediente='Elton'

        ingredientes_actuales=[list(a.keys())[0] for a in st.session_state.receta_visual]#Son los ingredientes del plato que se muestran en pantalla (no son necesariamente los mismos que BD)
        
        ingredientes_total= obtener_campos(conn,campos=["nombre","unidad"],tabla="Ingredientes",formato="dict")#Todos los ingredientes de la bd con sus unidades
        ingredientes_total_nombres=obtener_campos(conn,campos=["nombre"],tabla="Ingredientes",formato="lista")#Lista de todos los ing de la bd


        for index, ing in enumerate(st.session_state.receta_visual):
            col1, col2, col3, col4 = st.columns([5, 3, 3, 1], gap='small')
            
            with col1:
                nombre_ingrediente = list(ing.keys())[0] 
                if nombre_ingrediente:
                    st.markdown(f"**{nombre_ingrediente}**")
                else:
                     # Selectbox SIN valor inicial
                    nuevo_ingrediente = st.selectbox(
                        "Elegir ingrediente",
                        [x for x in ingredientes_total_nombres if x not in ingredientes_actuales],
                        index=None,
                        key=f"selectbox_ingredientes_mod_{index}"
                    )
                    st.session_state.nuevo_ingrediente=nuevo_ingrediente#Si no elijo nada, este parámetro se hace None y luego no me permite agregar otro ing
                    # Solo actualizar si el usuario eligió algo real
                    if nuevo_ingrediente:
                        st.session_state.receta_visual[index]={nuevo_ingrediente:{"cantidad": 0.01, "unidad": ingredientes_total[nuevo_ingrediente]}}

                        if nuevo_ingrediente not in st.session_state.ingredientes_db_actuales:
                            st.session_state.cambios_receta[nuevo_ingrediente]={"cantidad":0.01,"nuevo":True,"unidad":ingredientes_total[nuevo_ingrediente]}
                        else:
                            st.session_state.cambios_receta[nuevo_ingrediente]={"cantidad":0.01,"nuevo":False,"unidad":ingredientes_total[nuevo_ingrediente]}
                        
                        st.rerun()
            with col2:
                # Campo editable para cantidad, muestra por defecto la cantidad actual
                cantidad=list(ing.values())[0]['cantidad']
                unidad=list(ing.values())[0]['unidad']
                nueva_cantidad = st.number_input(
                    "cant",
                    value=float(cantidad),
                    min_value=0.001,
                    step=0.01,
                    key=f"cant_{plato_seleccionado}_{nombre_ingrediente}",
                    label_visibility="collapsed"
                )
                # Guardar si cambió
                if nueva_cantidad != float(cantidad):
                    if nombre_ingrediente not in st.session_state.cambios_receta:#Si era un ingrediente ya existente, no iba estar nunca en cambios_receta.
                        st.session_state.cambios_receta[nombre_ingrediente] = {
                            "cantidad": float(nueva_cantidad),
                            "nuevo": False,
                            "unidad": unidad
                        }
                    st.session_state.cambios_receta[nombre_ingrediente]["cantidad"] = nueva_cantidad
            
            with col3:
                st.markdown(f"_{unidad}_")

            with col4:
                if st.button("❌", key=f"delete_{plato_seleccionado}_{nombre_ingrediente}"):
                    st.session_state.receta_visual.pop(index)
                    st.session_state.cambios_receta[nombre_ingrediente]={"cantidad":0} #Puede dar la orden de borrar un ing que ni esté en la base, pero por como es la función a lo sumo no borra nada, no da eror.
                    st.success(f"{nombre_ingrediente} eliminado")
                    st.rerun()
        if st.button("Agregar ingrediente"):
            if st.session_state.nuevo_ingrediente==None:
                st.error("Finalice selección anterior")
            else:
                st.session_state.receta_visual.append({
                    None:{
                    "cantidad": 0.01,
                    "unidad": None}
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
                        if nombre_ingrediente not in st.session_state.ingredientes_db_actuales:
                            st.session_state.ingredientes_db_actuales.append(nombre_ingrediente)
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