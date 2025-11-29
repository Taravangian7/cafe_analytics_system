def funcion_prueba(conn,*campos,tabla,where=None,where_valor=0,formato="lista"):
    try:
        cursor=conn.cursor()
        campo=", ".join(campos)
        total_campos=len(campos)
        if where:
            cursor.execute(f"SELECT DISTINCT {campo} FROM {tabla} where {where}={where_valor}")
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
        
        return objeto
    except:
        return False

my_dict=[{"azucar":{"cantidad":2, "unidad": "kg"}},{"limon": {"cantidad":1, "unidad": "kg"}}]
lista= [list(a.values())[0]['cantidad'] for a in my_dict]
print(lista)
my_dict={"elton":"keta","trompue":"trompueta"}
print(list(my_dict.keys()))

print(type('elton'))
