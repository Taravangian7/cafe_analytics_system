import pandas as pd
from datetime import datetime, timedelta,time

# ============================================
# 1. REVENUE TOTAL POR DÍA/SEMANA/MES
# ============================================
def rango_fechas(conn,anio=None,mes=None,fecha_inicial=None):
    
    if not fecha_inicial:
        cursor=conn.cursor()
        cursor.execute("SELECT MIN(Order_date) AS fecha_inicio From Orders")
        min_date=cursor.fetchone()[0] #fecha_inicio es un string
        cursor.close()
        # Convertir string a datetime.date
        if isinstance(min_date, str):
            min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
    else:
        min_date=fecha_inicial
    max_date= datetime.now().date()
    dias = (max_date - min_date).days + 1   # para incluir ambos extremos

    lista_fechas = [min_date + timedelta(days=i) for i in range(dias)]
    year= list(dict.fromkeys([fecha.year for fecha in lista_fechas]))
    if anio and not mes:
        meses= sorted(list(dict.fromkeys([f.month for f in lista_fechas if f.year == anio])))
        return meses
    if anio and mes:
        dias= sorted(list(dict.fromkeys([f.day for f in lista_fechas if f.month == mes and f.year == anio])))
        return dias

    return lista_fechas, year

def true_if_data(conn, fecha_inicial, fecha_final):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM Orders WHERE Order_date BETWEEN ? AND ?",
        (str(fecha_inicial), str(fecha_final))
    )
    data = cursor.fetchone()
    cursor.close()
    return data is not None


def get_revenue_por_periodo(conn, periodo='dia', fecha_inicio=None, fecha_fin=None):
    """
    Devuelve revenue agrupado por periodo.
    
    Args:
        conn: conexión pyodbc
        periodo: 'dia', 'semana', 'mes'
        fecha_inicio: str 'YYYY-MM-DD' o None (últimos 30 días por defecto)
        fecha_fin: str 'YYYY-MM-DD' o None (hoy por defecto)
    
    Returns:
        DataFrame con columnas: [periodo, revenue]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    if periodo == 'dia':
        group_by = "Order_date"
    elif periodo == 'semana':
        group_by = "DATEPART(WEEK, Order_date), DATEPART(YEAR, Order_date)"
    elif periodo == 'mes':
        group_by = "MONTH(Order_date), YEAR(Order_date)"
    else:
        raise ValueError("Periodo debe ser 'dia', 'semana' o 'mes'")
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min)  
    query = f"""
        SELECT 
            {group_by} AS periodo,
            SUM(Total_cost) AS revenue
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY {group_by}
        ORDER BY periodo
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df


# ============================================
# 2. TICKET PROMEDIO
# ============================================

def get_ticket_promedio(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve el ticket promedio.
    
    Returns:
        float: ticket promedio
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min)  
    query = """
        SELECT AVG(Total_cost) AS ticket_promedio
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
    """
    
    result = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return float(result['ticket_promedio'].fillna(0).iloc[0]) #iloc[0] es para obtener el primer valor de la columna (primer registro)


# ============================================
# 3. VENTAS POR DÍA DE LA SEMANA
# ============================================

def get_ventas_por_dia_semana(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve revenue por día de la semana.
    
    Returns:
        DataFrame: [dia_semana, revenue_promedio, num_ordenes_promedio]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT 
            Day_of_week AS dia_semana,
            SUM(Total_cost) AS revenue,
            COUNT(*) AS num_ordenes
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY Day_of_week
        ORDER BY 
            CASE Day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
    """
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min)  
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    # Genero lista real de días del rango
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin)
    dias = fechas.day_name()
    # Conteo POR DÍA
    repeticiones = dias.value_counts()
    # Agrego columna de repeticiones
    df['repeticiones'] = df['dia_semana'].map(repeticiones)
    # Revenue ajustado por repeticiones
    df['revenue_promedio'] = df['revenue'] / df['repeticiones']
    # Num_orders ajustado por repeticiones
    df['num_ordenes_promedio'] = df['num_ordenes'] / df['repeticiones']
    #Ordeno por días
    orden_dias = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=orden_dias, ordered=True) #Categorical es para definir un nuevo orden explicito
    df = df.sort_values('dia_semana')
    return df[['dia_semana', 'revenue_promedio','num_ordenes_promedio']]


# ============================================
# 4. VENTAS POR HORARIO (AM/PM)
# ============================================

def get_ventas_por_franja_horaria(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve revenue por franja horaria.
    
    Returns:
        DataFrame: [franja_horaria, revenue, num_ordenes]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT 
            CASE 
                WHEN DATEPART(HOUR, Order_time) < 12 THEN 'Morning (6-12)'
                WHEN DATEPART(HOUR, Order_time) < 18 THEN 'Afternoon (12-18)'
                ELSE 'Evening (18-22)'
            END AS franja_horaria,
            SUM(Total_cost) AS revenue,
            COUNT(*) AS num_ordenes
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY 
            CASE 
                WHEN DATEPART(HOUR, Order_time) < 12 THEN 'Morning (6-12)'
                WHEN DATEPART(HOUR, Order_time) < 18 THEN 'Afternoon (12-18)'
                ELSE 'Evening (18-22)'
            END
        ORDER BY franja_horaria
    """
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min) 
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df

def get_ventas_por_hora(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve revenue promedio por hora.
    
    Returns:
        DataFrame: [hora, revenue, num_ordenes]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT 
            DATEPART(HOUR, Order_time) AS hora,
            SUM(Total_cost) AS revenue,
            COUNT(*) AS num_ordenes
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY DATEPART(HOUR, Order_time)
        ORDER BY hora
    """
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min)   
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    # Cantidad de días reales del rango
    dias_rango = (fecha_fin - fecha_inicio).days + 1 #El +1 incluye el primer y el último día
    # Promedio por hora
    df["revenue_promedio"] = df["revenue"] / dias_rango
    df["num_ordenes_promedio"] = df["num_ordenes"] / dias_rango
    return df


# ============================================
# 5. MÉTODO DE PAGO MÁS USADO
# ============================================

def get_metodos_pago(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve distribución de métodos de pago.
    
    Returns:
        DataFrame: [metodo_pago, num_ordenes, revenue, porcentaje]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT 
            Payment_method AS metodo_pago,
            COUNT(*) AS num_ordenes,
            SUM(Total_cost) AS revenue,
            CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS DECIMAL(5,2)) AS porcentaje
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY Payment_method
        ORDER BY num_ordenes DESC
    """
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # pq sino sql tira error
    fecha_fin_dt    = datetime.combine(fecha_fin, time.min)  
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df

    # ============================================
# 6. TOP 10 PRODUCTOS MÁS VENDIDOS
# ============================================

def get_top_productos_vendidos(conn, top_n=10, criterio='cantidad', fecha_inicio=None, fecha_fin=None):
    """
    Devuelve los productos más vendidos.
    
    Args:
        criterio: 'cantidad' o 'revenue'
        top_n: número de productos a mostrar
    
    Returns:
        DataFrame: [producto, cantidad_vendida, revenue]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.min)
    
    order_by = "cantidad" if criterio == 'cantidad' else "revenue"
    
    query = f"""
        SELECT TOP {top_n}
            oi.Product_name AS producto,
            SUM(oi.Quantity) AS cantidad,
            SUM(oi.Total_price) AS revenue
        FROM Order_items oi
        JOIN Orders o ON o.Order_id = oi.Order_id
        WHERE o.Order_date BETWEEN ? AND ?
        GROUP BY oi.Product_name
        ORDER BY {order_by} DESC
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df


# ============================================
# 7. TOP 10 PRODUCTOS MENOS VENDIDOS
# ============================================

def get_productos_menos_vendidos(conn, top_n=10, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve los productos menos vendidos (candidatos a sacar del menú).
    
    Returns:
        DataFrame: [producto, cantidad_vendida, revenue, ultima_venta]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.min)
    
    query = f"""
        SELECT TOP {top_n}
            oi.Product_name AS producto,
            SUM(oi.Quantity) AS cantidad,
            SUM(oi.Total_price) AS revenue,
            MAX(o.Order_date) AS ultima_venta
        FROM Order_items oi
        JOIN Orders o ON o.Order_id = oi.Order_id
        WHERE o.Order_date BETWEEN ? AND ?
        GROUP BY oi.Product_name
        ORDER BY cantidad ASC
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df


# ============================================
# 8. PRODUCTOS POR CATEGORÍA
# ============================================

def get_ventas_por_categoria(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve ventas agrupadas por categoría de producto.
    
    Returns:
        DataFrame: [categoria, cantidad_vendida, revenue, num_productos]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.min)
    
    query = """
        SELECT 
            p.Categoria AS categoria,
            SUM(oi.Quantity) AS cantidad_vendida,
            SUM(oi.Total_price) AS revenue,
            COUNT(DISTINCT oi.Product_name) AS num_productos
        FROM Order_items oi
        JOIN Orders o ON o.Order_id = oi.Order_id
        JOIN Platos p ON p.Nombre = oi.Product_name
        WHERE o.Order_date BETWEEN ? AND ?
        GROUP BY p.Categoria
        ORDER BY revenue DESC
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df


# ============================================
# 9. ANÁLISIS DE RENTABILIDAD POR PRODUCTO
# ============================================

def get_rentabilidad_por_producto(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve análisis de rentabilidad: (precio - costo) × cantidad vendida.
    
    Returns:
        DataFrame: [producto, cantidad_vendida, revenue, costo_total, ganancia_bruta, margen_%]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.min)
    
    query = """
        SELECT 
            oi.Product_name AS producto,
            SUM(oi.Quantity) AS cantidad_vendida,
            SUM(oi.Total_price) AS revenue,
            SUM(oi.Quantity * p.Costo) AS costo_total,
            SUM(oi.Total_price - (oi.Quantity * p.Costo)) AS ganancia_bruta,
            CASE 
                WHEN SUM(oi.Total_price) > 0 
                THEN CAST((SUM(oi.Total_price - (oi.Quantity * p.Costo)) / SUM(oi.Total_price)) * 100 AS DECIMAL(5,2))
                ELSE 0 
            END AS margen_porcentaje
        FROM Order_items oi
        JOIN Orders o ON o.Order_id = oi.Order_id
        JOIN Platos p ON p.Nombre = oi.Product_name
        WHERE o.Order_date BETWEEN ? AND ?
        GROUP BY oi.Product_name
        ORDER BY ganancia_bruta DESC
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return df


# ============================================
# 10. MARGEN DE GANANCIA POR PRODUCTO
# ============================================

def get_margen_por_producto(conn):
    """
    Devuelve el margen teórico de cada producto del menú (sin filtro de ventas).
    Útil para revisar pricing.
    
    Returns:
        DataFrame: [producto, precio, costo, margen_absoluto, margen_%]
    """
    query = """
        SELECT 
            Nombre AS producto,
            Precio AS precio,
            Costo AS costo,
            (Precio - Costo) AS margen_absoluto,
            CASE 
                WHEN Precio > 0 
                THEN CAST((((Precio - Costo) / Precio) * 100) AS DECIMAL(5,2))
                ELSE 0 
            END AS margen_porcentaje
        FROM Platos
        WHERE Precio IS NOT NULL AND Precio > 0
        ORDER BY margen_porcentaje ASC
    """
    
    df = pd.read_sql(query, conn)
    return df

    #RENTABILIDAD
    # 11. GANANCIA BRUTA TOTAL
# ============================================

def get_ganancia_bruta_total(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve ganancia bruta total: Revenue - Costos
    
    Returns:
        dict: {revenue, costo_total, ganancia_bruta}
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.min)
    
    query = """
        SELECT 
            SUM(oi.Total_price) AS revenue,
            SUM(oi.Quantity * p.Costo) AS costo_total,
            SUM(oi.Total_price - (oi.Quantity * p.Costo)) AS ganancia_bruta
        FROM Order_items oi
        JOIN Orders o ON o.Order_id = oi.Order_id
        JOIN Platos p ON p.Nombre = oi.Product_name
        WHERE o.Order_date BETWEEN ? AND ?
    """
    
    result = pd.read_sql(query, conn, params=(fecha_inicio_dt, fecha_fin_dt))
    return {
        'revenue': float(result['revenue'].iloc[0]) if result['revenue'].iloc[0] else 0.0,
        'costo_total': float(result['costo_total'].iloc[0]) if result['costo_total'].iloc[0] else 0.0,
        'ganancia_bruta': float(result['ganancia_bruta'].iloc[0]) if result['ganancia_bruta'].iloc[0] else 0.0
    }


# ============================================
# 12. MARGEN PROMEDIO DEL NEGOCIO
# ============================================

def get_margen_promedio_negocio(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve el margen promedio del negocio: % ganancia sobre ventas
    
    Returns:
        float: margen en porcentaje
    """
    datos = get_ganancia_bruta_total(conn, fecha_inicio, fecha_fin)
    
    if datos['revenue'] > 0:
        margen = (datos['ganancia_bruta'] / datos['revenue']) * 100
        return round(margen, 2)
    return 0.0


# ============================================
# 13. FOOD COST %
# ============================================

def get_food_cost_percentage(conn, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve el food cost %: Costo ingredientes / Revenue
    Ideal: 25-35%
    
    Returns:
        float: food cost en porcentaje
    """
    datos = get_ganancia_bruta_total(conn, fecha_inicio, fecha_fin)
    
    if datos['revenue'] > 0:
        food_cost = (datos['costo_total'] / datos['revenue']) * 100
        return round(food_cost, 2)
    return 0.0