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

def agregar_nuevo_ingrediente(conn, nombre, costo, cantidad, unidad, gluten_free, dairy_free):
    """
    Inserta un ingrediente en SQL.
    Recibe datos validados desde Streamlit, pero aplica validaciones mínimas de seguridad.
    """
    try:
        # Validaciones de tipo
        nombre = validar_valor(nombre, str, "nombre")
        unidad = validar_valor(unidad, str, "unidad")
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
        cursor=conn.cursor()

        cursor.execute("""
            INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, Gluten_free, Dairy_free)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, costo, cantidad, unidad, gluten_free, dairy_free))
        conn.commit()
        message='Ingrediente agregado correctamente'

        return True, message, nombre, unidad
    except:
        message='Error al intentar crear ingrediente'
        return False,message,'error','error'


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
            """, (nombre, categoria))
        else:
            cursor.execute("""
                INSERT INTO Platos (Nombre, Categoria, Precio)
                VALUES (?, ?, ?)
            """, (nombre, categoria, float(precio)))

        conn.commit()

        # ----- Insertar Receta -----

        # Cargar ingredientes existentes con unidades
        cursor.execute("SELECT Nombre, Unidad FROM Ingredientes")
        unidad_por_ing = {row[0].lower(): row[1] for row in cursor}

        receta_rows = []

        for ing in lista_ingredientes:
            nombre_ing = ing["nombre"]
            cantidad = float(ing["cantidad"])

            # Obtener unidad según la BD
            unidad = unidad_por_ing[nombre_ing.lower()]

            receta_rows.append((nombre, nombre_ing, cantidad, unidad))

        cursor.executemany("""
            INSERT INTO Receta (Plato, Ingrediente, Cantidad, Unidad)
            VALUES (?, ?, ?, ?)
        """, receta_rows)

        conn.commit()

        return True, f"Plato '{nombre}' creado correctamente."
    except:
        return False, 'Error al intentar crear plato'

def borrar_plato(conn,Nombre):
    cursor=conn.cursor()
    cursor.execute(f"DELETE FROM Platos WHERE Nombre='{Nombre}'")
    conn.commit()
    return Nombre

def modificar_plato(conn,Nombre,nuevo_nombre,precio,categoria):
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
        conn.commit()
        return True,'Cambio realizado correctamente'
    except:
        return False, 'Error al modificar'

def modifcar_cantidad(ing,plato,unidad,cursor):
    while True:
        cantidad=input(f'Ingrese nueva cantidad ({unidad}): ')
        try:
            cantidad=float(cantidad)
            break
        except:
            print('Ingrese número válido')
    cursor.execute(f"UPDATE Receta Set Cantidad='{cantidad}' WHERE Ingrediente='{ing}' and Plato='{plato}'")
    conn.commit()

def eliminar_ing_receta(ing,plato,cursor):
    cursor.execute(f"DELETE from Receta WHERE Plato='{plato}' and Ingrediente='{ing}'")
    conn.commit()

def modificar_receta(Nombre,cursor):
    cursor.execute(f"select Plato,Ingrediente,Cantidad,Unidad from Receta where Plato='{Nombre}'")
    receta = [(plato, ing, float(cant), unidad) for plato, ing, cant, unidad in cursor]
    print('La receta actual es:')
    for ing in receta:
        print(f'{ing[1]}: {ing[2]} {ing[3]}')
    ingredientes=[ing[1].lower() for ing in receta]
    while True:
        ingrediente=input('Ingrese ingrediente a modificar: ').lower()
        if ingrediente in ingredientes:
            index=ingredientes.index(ingrediente)
            break
        print('Ingrese ingrediente válido')
    while True:
        action= input('Desea MODIFICAR o ELIMINAR: ')
        action=action.lower()
        if action in ['modificar','eliminar']:
            break
    if action=='modificar':
        modifcar_cantidad(ingrediente,Nombre,receta[index][3],cursor)
    elif action=='eliminar':
        eliminar_ing_receta(ingrediente,Nombre,cursor)

def modificar_ingrediente(cursor):
    cursor.execute("SELECT Nombre from Ingredientes")
    ingredientes=[ing[0].lower() for ing in cursor]
    while True:
        ingrediente=input('Ingrese ingrediente a modificar: ').lower()
        if ingrediente in ingredientes:
            break    
    cursor.execute(f"select Nombre,Costo,Unidad,Cantidad,Dairy_free,Gluten_free from Ingredientes where Nombre='{ingrediente}'")
    receta = [(Nombre,float(Costo),Unidad,float(Cantidad),Dairy_free,Gluten_free) for Nombre,Costo,Unidad,Cantidad,Dairy_free,Gluten_free in cursor]
    nombre=input(f'Ingrese nombre (actual:{receta[0][0]}): ')
    while True:
        costo=input(f'Ingrese costo (actual:{receta[0][1]}): ')
        try:
            costo=float(costo)
            break
        except:
            print('ingrese número válido')
    unidad=input(f'Ingrese unidad (actual:{receta[0][2]}): ')
    while True:
        cantidad=input(f'Ingrese cantidad (actual:{receta[0][3]}): ')
        try:
            cantidad=float(cantidad)
            break
        except:
            print('Ingrese número válido')
    while True:
        dairy_free=input('Dairy free (SI/NO)?: ').lower()
        if dairy_free=='si':
            dairy_free=1
            break
        elif dairy_free=='no':
            dairy_free=0
            break
    while True:
        gluten_free=input('Gluten free (SI/NO)?: ').lower()
        if gluten_free=='si':
            gluten_free=1
            break
        elif gluten_free=='no':
            gluten_free=0
            break
    cursor.execute(f"""UPDATE Ingredientes set Nombre=?,Costo=?,Unidad=?,Cantidad=?,Dairy_free=?,Gluten_free=? WHERE Nombre=?
        """,(nombre,costo,unidad,cantidad,dairy_free,gluten_free,ingrediente))
    conn.commit()

#validar_valor('elton',float,'keta')
#modificar_ingrediente(cursor)
#modificar_receta('Avocado Toast',cursor)
#modificar_plato('Cortado',cursor)
#borrar_plato('Flat Whiteni',cursor)