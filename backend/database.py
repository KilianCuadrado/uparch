# ==========================
# === IMPORTS NECESARIOS ===
# ==========================

import sqlite3
import os


# ==========================
# === VARIABLES GLOBALES ===
# ==========================

# Permite usar una variable de entorno para definir la ruta de la base de datos (muy útil para Docker).
# Por defecto (si no hay variable), asume que la base de datos está un nivel arriba de esta carpeta.
DB_PATH = os.getenv("UPARCH_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "uparch.db"))


# =================
# === FUNCIONES ===
# =================

# conn.row_factory = sqlite3.Row hace que los resultados de las
# consultas se puedan acceder por nombre de columna
# (como row["username"]) en vez de por índice
# (como row[0]). Mucho más cómodo.
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Inicializa la base de datos creando las tablas necesarias si no existen.
def init_db():
    # Abrimos una conexión a la base de datos y obtenemos un cursor para ejecutar consultas.
    conn = get_connection()
    cursor = conn.cursor() # Puntero para ejecutar consultas — es como el bolígrafo con el que escribes y lees dentro.

    # Crear tabla de usuarios en caso de que no exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Crear tabla de archivos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            size INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Verificar si existe algún usuario, si no, crear el administrador por defecto
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    if result["count"] == 0:
        from auth import hash_password
        hashed = hash_password("1234")
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", ("admin", hashed))
        print("👤 Creado usuario administrador por defecto (admin:1234)")

    # Guardar los cambios en la base de datos
    conn.commit()
    # Cerrar la conexión después de inicializar la base de datos
    conn.close()


# if __name__ == "__main__" significa "solo ejecuta esto si estás corriendo este archivo directamente",
# no cuando lo importes desde otro archivo.
if __name__ == "__main__":
    # Inicializamos la base de datos
    init_db()
    print("Database initialized successfully")