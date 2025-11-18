import pyodbc
from pathlib import Path

# Config
SERVER = 'LAPTOP-MTPJVFI5\\SQLEXPRESS'
DATABASE = 'Cafe_Bar'

# Conexión
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;',
    autocommit=True
)
cursor = conn.cursor()

# --- FUNCIONES AUXILIARES ---

def agregar_nuevo_ingrediente(cursor):
    """Crea un nuevo ingrediente, lo inserta en SQL y devuelve (nombre, unidad)."""
    nombre_ingrediente = input('Ingrese nombre del nuevo ingrediente: ').capitalize()

    # Costo
    while True:
        try:
            costo = float(input('Ingrese costo: '))
            break
        except ValueError:
            print('Ingrese un número válido.')

    # Cantidad
    while True:
        try:
            cantidad = float(input('Ingrese cantidad disponible: '))
            break
        except ValueError:
            print('Ingrese un número válido.')

    unidad = input('Ingrese unidad (ej: kg, litro, etc.): ').lower()

    # Gluten free
    while True:
        gluten_input = input('¿Es Gluten Free? (SI/NO): ').strip().upper()
        if gluten_input in ['SI', 'NO']:
            gluten_free = 1 if gluten_input == 'SI' else 0
            break

    # Dairy free
    while True:
        dairy_input = input('¿Es Dairy Free? (SI/NO): ').strip().upper()
        if dairy_input in ['SI', 'NO']:
            dairy_free = 1 if dairy_input == 'SI' else 0
            break

    # Insertar en la base
    cursor.execute("""
        INSERT INTO dbo.Ingredientes (Nombre, Costo, Cantidad, Unidad, Gluten_free, Dairy_free)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre_ingrediente, costo, cantidad, unidad, gluten_free, dairy_free))
    conn.commit()

    print(f"Ingrediente '{nombre_ingrediente}' agregado a la base de datos.")
    return nombre_ingrediente, unidad


def agregar_nuevo_plato(cursor):
    cursor.execute("SELECT Nombre FROM Platos ")
    platos = [column[0] for column in cursor]
    # Crear plato nuevo
    while True:
        plato_nombre = input('Nombre del Plato: ').capitalize()
        if plato_nombre.lower() in platos:
            print('Ese plato ya existe.')
        else:
            print('Nombre aceptado.')
            break

    categoria = input('Categoría: ').capitalize()

    # Traer ingredientes existentes
    cursor.execute("SELECT LOWER(Nombre), Unidad FROM Ingredientes")
    ingredientes_existentes = [[row[0], row[1]] for row in cursor]

    receta = {'Plato': [], 'Ingrediente': [], 'Cantidad': [], 'Unidad': []}

    otro_ingrediente = True
    while otro_ingrediente:
        ingrediente = input('Inserte ingrediente: ').capitalize()

        if ingrediente.lower() in [i[0] for i in ingredientes_existentes]:
            if ingrediente.lower() in [x.lower() for x in receta['Ingrediente']]:
                print('Ingrediente ya agregado.')
                continue

            # Buscar unidad
            index = [i[0] for i in ingredientes_existentes].index(ingrediente.lower())
            unidad = ingredientes_existentes[index][1]

        else:
            print("El ingrediente no existe en la base.")
            ingrediente, unidad = agregar_nuevo_ingrediente(cursor)
            ingredientes_existentes.append([ingrediente.lower(), unidad])

        # Pedir cantidad
        while True:
            try:
                cantidad = float(input(f'Ingrese cantidad (unidad: {unidad}): '))
                break
            except ValueError:
                print('Ingrese un número válido.')

        # Agregar al diccionario receta
        receta['Plato'].append(plato_nombre)
        receta['Ingrediente'].append(ingrediente)
        receta['Cantidad'].append(cantidad)
        receta['Unidad'].append(unidad)

        # Preguntar si agregar otro
        while True:
            agregar_otro = input('¿Desea agregar otro ingrediente? (SI/NO): ').strip().upper()
            if agregar_otro in ['SI', 'NO']:
                otro_ingrediente = (agregar_otro == 'SI')
                break
    # Defino precio de plato (opcional) e inserto a la base de datos
    while True:
            try:
                precio = input('Ingrese precio del plato(o "standard"): ')
                if precio=='standard':
                    cursor.execute("""
                        INSERT INTO dbo.Platos (Nombre, Categoria)
                        VALUES (?, ?)
                    """, (plato_nombre, categoria))
                    conn.commit()
                    break
                else:
                    float(precio)
                    cursor.execute("""
                        INSERT INTO dbo.Platos (Nombre, Categoria,Precio)
                        VALUES (?, ?, ?)
                    """, (plato_nombre, categoria, precio))
                    conn.commit()
                    break
            except ValueError:
                print('Ingrese un precio válido.')

    data = list(zip(
        receta['Plato'],
        receta['Ingrediente'],
        receta['Cantidad'],
        receta['Unidad']
    ))

    cursor.executemany("""
        INSERT INTO dbo.Receta (Plato, Ingrediente, Cantidad, Unidad)
        VALUES (?, ?, ?, ?)
    """, data)
    conn.commit()

    # Mostrar receta final
    print(f"\nReceta creada: {plato_nombre}")
    for i in range(len(receta['Plato'])):
        print(f"{receta['Ingrediente'][i]} - {receta['Cantidad'][i]} {receta['Unidad'][i]}")

def borrar_plato(Nombre,cursor):
    conn.commit()
    return Nombre

def modificar_plato(Nombre,cursor):
    cambiar_nombre= input('Desea cambiar el nombre (SI/NO)?: ')
    if cambiar_nombre=='SI':
        nuevo_nombre=input('Ingrese nuevo nombre: ')
        cursor.execute(f"UPDATE Platos Set Nombre='{nuevo_nombre}' where Nombre='{Nombre}'")
        conn.commit()
        Nombre=nuevo_nombre
    cambiar_precio=input('Desea cambiar el precio (SI/NO)?: ')
    if cambiar_precio=='SI':
        while True:
            precio=input('ingrese nuevo precio: ')
            try:
                precio=float(precio)
                break
            except:
                print('ingrese valor válido')
        cursor.execute(f"UPDATE Platos Set Precio='{precio}' where Nombre='{Nombre}'")
        conn.commit()
    cambiar_categoria=input('Desea cambiar la categoría (SI/NO)?: ')
    if cambiar_categoria=='SI':
        categoria=input('Ingrese nueva categoría: ')
        cursor.execute(f"UPDATE Platos Set Categoria='{categoria}' where Nombre='{Nombre}'")
        conn.commit()

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


#modificar_ingrediente(cursor)
#modificar_receta('Avocado Toast',cursor)
#modificar_plato('Cortado',cursor)
#borrar_plato('Flat Whiteni',cursor)