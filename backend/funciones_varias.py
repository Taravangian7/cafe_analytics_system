from crud_platos_ingredientes import obtener_campos


def precio_real_vs_database(conn,plato):
    precio_database=obtener_campos(conn,"Precio","Platos",where="Nombre",where_valor=plato,formato="lista")[0]
    