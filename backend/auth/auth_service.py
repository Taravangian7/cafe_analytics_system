from backend.auth.password import hash_password, verify_password
from backend.auth.user_store import get_user_by_username, create_user
from backend.tenants.tenant_service import create_tenant_db,create_tenant_tables

def register_user(username, password, email=None):
    if len(username) < 3:
        return False, "Usuario muy corto"

    if len(password) < 6:
        return False, "Contraseña muy corta"

    if get_user_by_username(username):
        return False, "Usuario ya existe"

    # 1️⃣ crear DB del negocio
    db_name = create_tenant_db(username)

    #creamos las tablas
    create_tenant_tables(db_name)
    # 2️⃣ crear usuario
    password_hash = hash_password(password)
    create_user(username, password_hash, email, db_name)

    return True, "Usuario creado correctamente"


def login_user(username, password):
    user = get_user_by_username(username)

    if not user:
        return False, None, "Usuario no encontrado"

    if not verify_password(user["password_hash"], password):
        return False, None, "Contraseña incorrecta"

    return True, {
        "user_id": user["id"],
        "username": user["username"],
        "db_name": user["db_name"]
    }, "Login OK"
