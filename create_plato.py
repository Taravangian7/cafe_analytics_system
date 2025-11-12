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
# Insertar en la base
cursor.execute("""
    INSERT INTO dbo.Platos (Nombre, Categoria)
    VALUES (?, ?)
""", (plato_nombre, categoria))
conn.commit()

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


