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
    #months = [fecha.month for fecha in lista_fechas]
    #days = [fecha.day for fecha in lista_fechas]
    return lista_fechas, year

def true_if_data(conn, fecha_inicial, fecha_final):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM Orders WHERE Order_date BETWEEN ? AND ?",
        (fecha_inicial, fecha_final)
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
        DataFrame: [dia_semana, revenue, num_ordenes]
    """
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT 
            Day_of_week AS dia_semana,
            SUM(Total_cost) AS revenue,
            COUNT(*) AS num_ordenes,
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
    df = pd.read_sql(query, conn, params=(fecha_inicio, fecha_fin))
    # Genero lista real de días del rango
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin)
    dias = fechas.day_name()
    # Conteo POR DÍA
    repeticiones = dias.value_counts()
    # Agrego columna de repeticiones
    df['repeticiones'] = df['dia_semana'].map(repeticiones)
    # Revenue ajustado por repeticiones
    df['revenue_promedio'] = df['revenue'] / df['repeticiones']
    return df


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
    
    df = pd.read_sql(query, conn, params=(fecha_inicio, fecha_fin))
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
            DATEPART(HOUR, Order_time) AS hora
            SUM(Total_cost) AS revenue,
            COUNT(*) AS num_ordenes
        FROM Orders
        WHERE Order_date BETWEEN ? AND ?
        GROUP BY DATEPART(HOUR, Order_time)
        ORDER BY hora
    """
    
    df = pd.read_sql(query, conn, params=(fecha_inicio, fecha_fin))
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
    
    df = pd.read_sql(query, conn, params=(fecha_inicio, fecha_fin))
    return df