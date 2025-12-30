import pandas as pd
import pyodbc
from io import BytesIO
from backend.create_plato import agregar_nuevo_plato
# FUNCIONES PARA CORROBORAR SI YA SE CARGARON LOS ARCHIVOS

def datos_iniciales(conn) -> bool:

    cursor = conn.cursor()

    tablas = ["Platos", "Ingredientes", "Receta"]

    for tabla in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        if count == 0:
            return False , f"la tabla {tabla} no tiene datos"

    return True, "las tablas estan cargadas"

# ============================================
# FUNCIONES DE CARGA - INGREDIENTES
# ============================================

def cargar_ingredientes_desde_csv(conn, archivo_csv):
    """
    Carga ingredientes desde un archivo CSV.
    
    CSV esperado con columnas:
    - Nombre
    - Costo
    - Cantidad
    - Unidad
    - Gluten_free (1/0 o True/False)
    - Dairy_free (1/0 o True/False)
    - Elaborado (opcional, 1/0 o True/False)
    
    Returns:
        tuple: (success: bool, message: str, insertados: int)
    """
    try:
        # Leer CSV
        df = pd.read_csv(archivo_csv)
        
        # Validar columnas requeridas
        required_cols = ['Nombre', 'Costo', 'Cantidad', 'Unidad', 'Gluten_free', 'Dairy_free']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return False, f"Faltan columnas: {', '.join(missing)}", 0
        
        # Agregar columna Elaborado si no existe
        if 'Elaborado' not in df.columns:
            df['Elaborado'] = 0
        
        # Convertir booleanos
        df['Gluten_free'] = df['Gluten_free'].astype(int)
        df['Dairy_free'] = df['Dairy_free'].astype(int)
        df['Elaborado'] = df['Elaborado'].astype(int)
        
        df['Unidad']=df['Unidad'].str.capitalize()
        cursor = conn.cursor()
        insertados = 0
        errores = []
        
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO Ingredientes (Nombre, Costo, Cantidad, Unidad, Gluten_free, Dairy_free, Elaborado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['Nombre'],
                    float(row['Costo']),
                    float(row['Cantidad']),
                    row['Unidad'],
                    int(row['Gluten_free']),
                    int(row['Dairy_free']),
                    int(row['Elaborado'])
                ))
                insertados += 1
            except Exception as e:
                errores.append(f"{row['Nombre']}: {str(e)}")
        
        conn.commit()
        cursor.close()
        
        msg = f"✓ {insertados} ingredientes cargados"
        if errores:
            msg += f". {len(errores)} errores: {'; '.join(errores[:3])}"
        
        return True, msg, insertados
        
    except Exception as e:
        return False, f"Error al procesar CSV: {str(e)}", 0


def cargar_ingredientes_desde_excel(conn, archivo_excel, sheet_name=0):
    """
    Carga ingredientes desde un archivo Excel.
    Mismo formato que CSV.
    """
    try:
        df = pd.read_excel(archivo_excel, sheet_name=sheet_name)
        
        # Guardar temporalmente como CSV y usar la función anterior
        temp_csv = BytesIO()
        df.to_csv(temp_csv, index=False)
        temp_csv.seek(0)
        
        return cargar_ingredientes_desde_csv(conn, temp_csv)
        
    except Exception as e:
        return False, f"Error al procesar Excel: {str(e)}", 0


# ============================================
# FUNCIONES DE CARGA - PLATOS
# ============================================

def cargar_platos_y_recetas_desde_csv(conn, archivo_platos_csv,archivo_receta_csv):
    """
    Carga platos y recetas desde dos archivos CSV.
    
    CSV Platos esperado con columnas:
    - Nombre
    - Categoria
    - Precio (opcional:standard)
    
    Returns:
        tuple: (success: bool, message: str, insertados: int)
    """
    try:
        df_platos = pd.read_csv(archivo_platos_csv)
        df_receta = pd.read_csv(archivo_receta_csv)
        df_platos.columns = df_platos.columns.str.lower()
        df_receta.columns = df_receta.columns.str.lower()
        # Validar columnas
        if 'nombre' not in df_platos.columns or 'categoria' not in df_platos.columns:
            return False, "El CSV Platos debe tener columnas 'Nombre' y 'Categoria'", 0
        
        columnas=["plato","ingrediente","cantidad","unidad"]
        for col in columnas:
            if col not in df_receta.columns:
                return False, f"El CSV Receta debe tener la columnas {col}'", 0
        
        # Precio opcional
        if 'precio' not in df_platos.columns:
            df_platos['precio'] = "standard"
        

        insertados = 0
        errores = []
        recetas_grouped = (
            df_receta
            .groupby("plato")
            .apply(
                lambda x: x[["ingrediente", "cantidad"]]
                .rename(columns={"ingrediente": "nombre"})
                .to_dict(orient="records")
            )
        )
        for _, plato in df_platos.iterrows():
            nombre = plato["nombre"]
            categoria = plato["categoria"]
            precio = plato["precio"]

            lista_ingredientes = recetas_grouped.get(nombre, [])
            estado,mensaje=agregar_nuevo_plato(conn, nombre, categoria, precio, lista_ingredientes)
            if estado:
                insertados+=1
            else:
                errores.append(nombre)
        msg = f"✓ {insertados} platos cargados"
        if errores:
            msg += f". {len(errores)} errores: {'; '.join(errores[:3])}"
        
        return True, msg, insertados
        
    except Exception as e:
        return False, f"Error al procesar CSV: {str(e)}", 0


def cargar_platos_desde_excel(conn, archivo_excel, sheet_name=0):
    """Carga platos desde Excel"""
    try:
        df = pd.read_excel(archivo_excel, sheet_name=sheet_name)
        temp_csv = BytesIO()
        df.to_csv(temp_csv, index=False)
        temp_csv.seek(0)
        return cargar_platos_desde_csv(conn, temp_csv)
    except Exception as e:
        return False, f"Error al procesar Excel: {str(e)}", 0





def cargar_recetas_desde_excel(conn, archivo_excel, sheet_name=0):
    """Carga recetas desde Excel"""
    try:
        df = pd.read_excel(archivo_excel, sheet_name=sheet_name)
        temp_csv = BytesIO()
        df.to_csv(temp_csv, index=False)
        temp_csv.seek(0)
        return cargar_recetas_desde_csv(conn, temp_csv)
    except Exception as e:
        return False, f"Error al procesar Excel: {str(e)}", 0


# ============================================
# FUNCIONES DE CARGA - ÓRDENES
# ============================================

def cargar_ordenes_desde_csv(conn, archivo_csv_orders, archivo_csv_items):
    """
    Carga órdenes desde dos CSVs (orders y order_items).
    
    orders.csv:
    - Order_id, Order_date, Order_time, Day_of_week, Payment_method, Order_type
    
    order_items.csv:
    - Item_id, Order_id, Product_name, Quantity, Unit_price
    
    Returns:
        tuple: (success: bool, message: str, ordenes_insertadas: int, items_insertados: int)
    """
    try:
        df_orders = pd.read_csv(archivo_csv_orders)
        df_items = pd.read_csv(archivo_csv_items)
        
        cursor = conn.cursor()
        ordenes_insertadas = 0
        items_insertados = 0
        errores = []
        
        # Insertar orders
        for _, row in df_orders.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO Orders (Order_id, Order_date, Order_time, Day_of_week, Payment_method, Order_type, Total_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['Order_id']),
                    row['Order_date'],
                    row['Order_time'],
                    row['Day_of_week'],
                    row['Payment_method'],
                    row['Order_type'],
                    float(row.get('Total_cost', 0))  # Si no existe, 0 (se calcula con trigger)
                ))
                ordenes_insertadas += 1
            except Exception as e:
                errores.append(f"Order {row['Order_id']}: {str(e)}")
        
        # Insertar order_items
        for _, row in df_items.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO Order_items (Item_id, Order_id, Product_name, Quantity, Unit_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(row['Item_id']),
                    int(row['Order_id']),
                    row['Product_name'],
                    float(row['Quantity']),
                    float(row['Unit_price'])
                ))
                items_insertados += 1
            except Exception as e:
                errores.append(f"Item {row['Item_id']}: {str(e)}")
        
        conn.commit()
        cursor.close()
        
        msg = f"✓ {ordenes_insertadas} órdenes y {items_insertados} items cargados"
        if errores:
            msg += f". {len(errores)} errores"
        
        return True, msg, ordenes_insertadas, items_insertados
        
    except Exception as e:
        return False, f"Error: {str(e)}", 0, 0