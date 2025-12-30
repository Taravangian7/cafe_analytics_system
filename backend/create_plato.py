#from numba import List
import pyodbc
from pathlib import Path
'''
# Config
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Conexión
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
    autocommit=True
)
cursor = conn.cursor()
'''
#  NUEVA FUNCIÓN: validación general para Streamlit y para funciones
# -------------------------------------------------------------------

def validar_valor(valor, tipo=float, nombre="valor"):
    """
    Valida que el valor no sea None, no sea string vacío y pueda convertirse
    al tipo indicado (por defecto float).
    """
    if valor is None:
        raise ValueError(f"El campo '{nombre}' no puede ser vacío")

    if tipo == float:
        try:
            return float(valor)
        except:
            raise ValueError(f"El campo '{nombre}' debe ser un número válido")

    if tipo == str:
        if not str(valor).strip():
            raise ValueError(f"El campo '{nombre}' no puede estar vacío")
        return str(valor).strip()

    return valor
# --- FUNCIONES AUXILIARES ---

def agregar_nuevo_ingrediente(conn, nombre, costo, cantidad, unidad, gluten_free, dairy_free,elaborado=0):
    """
    Inserta un ingrediente en SQL.
    Recibe datos validados desde Streamlit, pero aplica validaciones mínimas de seguridad.
    """
    try:
        # Validaciones de tipo
        nombre = validar_valor(nombre, str, "nombre").capitalize()
        unidad = validar_valor(unidad, str, "unidad").capitalize()
        costo = validar_valor(costo, float, "costo")
        cantidad = validar_valor(cantidad, float, "cantidad")

        # Validaciones adicionales
        if costo < 0:
            raise ValueError("El costo no puede ser negativo")

        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")

        if gluten_free not in [0, 1, True, False]:
            raise ValueError("gluten_free debe ser True/False")

        if dairy_free not in [0, 1, True, False]:
            raise ValueError("dairy_free debe ser True/False")

        gluten_free = int(bool(gluten_free))
        dairy_free = int(bool(dairy_free))
        elaborado= int(bool(elaborado))
        cursor=conn.cursor()
        cursor.execute("SELECT Nombre FROM Ingredientes")
        nombres_existentes=cursor.fetchall()
        cursor.close()
        if nombre in nombres_existentes:
            return False,"Ingrediente ya existe",'error','error'
        cursor=conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, Gluten_free, Dairy_free,Elaborado)
            VALUES (?, ?, ?, ?, ?, ?,?)
        """, (nombre, costo, cantidad, unidad, gluten_free, dairy_free,elaborado))
        conn.commit()
        message='Ingrediente agregado correctamente'

        return True, message, nombre, unidad
    except Exception as e:
        return False, f"Error SQL: {e}", 'error', 'error'


def agregar_nuevo_plato(conn, nombre, categoria, precio, lista_ingredientes):
    """
    lista_ingredientes = [
        {"nombre": "Harina", "cantidad": 0.2},
        {"nombre": "Huevo", "cantidad": 1},
        {"nombre": "Sal", "cantidad": 0.01}
    ]
    Las unidades se obtienen automáticamente desde la tabla Ingredientes.
    """
    try:
        cursor = conn.cursor()

        # Validar duplicado
        cursor.execute("SELECT LOWER(Nombre) FROM Platos")
        existentes = [row[0] for row in cursor]
        if nombre.lower() in existentes:
            return False, "El plato ya existe"

        # Insertar plato
        if precio == "standard":
            cursor.execute("""
                INSERT INTO Platos (Nombre, Categoria)
                VALUES (?, ?)
            """, (nombre.capitalize(), categoria.capitalize()))
        else:
            cursor.execute("""
                INSERT INTO Platos (Nombre, Categoria, Precio)
                VALUES (?, ?, ?)
            """, (nombre.capitalize(), categoria.capitalize(), float(precio)))

        conn.commit()

        # ----- Insertar Receta -----

        # Cargar ingredientes existentes con unidades
        if lista_ingredientes:
            cursor.execute("SELECT Nombre, Unidad FROM Ingredientes")
            unidad_por_ing = {row[0].lower(): row[1] for row in cursor}

            receta_rows = []

            for ing in lista_ingredientes:
                nombre_ing = ing["nombre"].capitalize()
                cantidad = float(ing["cantidad"])

                # Obtener unidad según la BD
                unidad = unidad_por_ing[nombre_ing.lower()]

                receta_rows.append((nombre.capitalize(), nombre_ing, cantidad, unidad))

            cursor.executemany("""
                INSERT INTO Receta (Plato, Ingrediente, Cantidad, Unidad)
                VALUES (?, ?, ?, ?)
            """, receta_rows)

        conn.commit()

        return True, f"Plato '{nombre}' creado correctamente."
    except:
        return False, 'Error al intentar crear plato'

def borrar_plato(conn,Nombre):
    try:
        cursor=conn.cursor()
        cursor.execute(f"DELETE FROM Platos WHERE Nombre='{Nombre}'")
        conn.commit()
        return True, 'Plato eliminado'
    except:
        return False,'Error al eliminar'

def modificar_plato(conn,Nombre,nuevo_nombre,precio,categoria,cambios_receta):
    '''
    cambios_receta={"ingrediente_a":{"cantidad":0,"nuevo":True,"unidad":ingredientes_total[nuevo_ingrediente]},
                    "ingrediente_b":{"cantidad":0,"nuevo":True,"unidad":ingredientes_total[nuevo_ingrediente]}
                    }
    '''
    try:
        cursor=conn.cursor()
        cambiar_nombre= validar_valor(nuevo_nombre,str,'nombre')
        cambiar_precio= validar_valor(precio,float,'precio')
        cambiar_categoria= validar_valor(categoria,str,'categoría')
        cursor.execute("""
            UPDATE Platos
            SET Nombre = ?, Precio = ?, Categoria = ?
            WHERE Nombre = ?
        """, (cambiar_nombre, cambiar_precio, cambiar_categoria, Nombre))

        if cambios_receta:
            
            for ing in cambios_receta:

                if cambios_receta[ing]["cantidad"]==0:
                    cursor.execute(f"DELETE FROM Receta WHERE Ingrediente='{ing}' and Plato='{cambiar_nombre}'")
                else:
                    if cambios_receta[ing]["nuevo"]:
                        cursor.execute("""
                                INSERT INTO Receta (Plato, Ingrediente, Cantidad, Unidad)
                                VALUES (?, ?, ?, ?)
                            """, (cambiar_nombre,ing,cambios_receta[ing]["cantidad"],cambios_receta[ing]["unidad"]))
                    else:
                        # Modificar cantidad existente
                        cursor.execute("""
                        UPDATE Receta 
                        SET Cantidad = ? 
                        WHERE Ingrediente = ? AND Plato = ?
                        """, (cambios_receta[ing]["cantidad"], ing, cambiar_nombre))
        cursor.commit()
        cursor.close()
                
        return True,'Cambio realizado correctamente'
    except Exception as e:
        return False, f'Error al modificar: {str(e)}'


def modificar_ingrediente(conn, ing_seleccionado,nombre_ing, costo_ing, cantidad_ing, unidad_ing, gluten_free_ing, dairy_free_ing):
    try:
        cursor=conn.cursor()
        cursor.execute("SELECT Nombre from Ingredientes")
        ingredientes=[ing[0].lower() for ing in cursor]
        nombre_ing=validar_valor(nombre_ing,str,'nombre').capitalize()
        costo_ing=validar_valor(costo_ing,float,'costo')
        cantidad_ing=validar_valor(cantidad_ing,float,'cantidad')
        unidad_ing=validar_valor(unidad_ing,str,'unidad')
        gluten_free_ing=validar_valor(gluten_free_ing,int,'gluten_free')
        dairy_free_ing=validar_valor(dairy_free_ing,int,'dairy_free')
        if ing_seleccionado!=nombre_ing and nombre_ing.lower() in ingredientes:
            return False,'El nombre del ingrediente ya existe'
        else:
            cursor.execute(f"""UPDATE Ingredientes set Nombre=?,Costo=?,Unidad=?,Cantidad=?,Dairy_free=?,Gluten_free=? WHERE Nombre=?
                """,(nombre_ing,costo_ing,unidad_ing,cantidad_ing,dairy_free_ing,gluten_free_ing,ing_seleccionado))
            conn.commit()
            return True,'Ingrediente modificado correctamente'
    except Exception as e:
        return False, f'Error al modificar: {str(e)}'

def obtener_campos(conn,campos:list,tabla,where=None,where_valor=0,formato="lista"):
    #TE DEVUELVE EN FORMATO LISTA O DICT UN SELECT DE SQL, podes poner condiciones where
    try:
        cursor=conn.cursor()
        campo=", ".join(campos)
        total_campos=len(campos)
        try:
            where_valor=float(where_valor)
        except:
            pass
        if where:
            if isinstance(where_valor, float):
                cursor.execute(f"SELECT DISTINCT {campo} FROM {tabla} WHERE {where}={where_valor}")
            else:
                cursor.execute(f"SELECT DISTINCT {campo} FROM {tabla} WHERE {where}='{where_valor}'")
        else:
            cursor.execute(f"SELECT DISTINCT {campo} FROM {tabla}")
        rows=cursor.fetchall()
        cursor.close()
        if formato=="lista":
            if total_campos==1:
                objeto=[i[0] for i in rows]
            elif total_campos==2:
                objeto=[{i[0]:i[1]} for i in rows]
            elif total_campos>2:
                objeto=[{i[0]:{campos[j]:i[j] for j in range(1,total_campos)}} for i in rows]
        if formato=="dict":
            if total_campos==1:
                objeto={i[0] for i in rows}
            elif total_campos==2:
                objeto={i[0]:i[1] for i in rows}
            elif total_campos>2:
                objeto={i[0]:{campos[j]:i[j] for j in range(1,total_campos)} for i in rows}

        
        return objeto
    except Exception as e:
        print(e)
        return []

#validar_valor('elton',float,'keta')
#modificar_ingrediente(cursor)
#modificar_receta('Avocado Toast',cursor)
#modificar_plato('Cortado',cursor)
#borrar_plato('Flat Whiteni',cursor)