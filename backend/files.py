# ==========================
# === IMPORTS NECESARIOS ===
# ==========================

# - APIRouter: Es como un "mini FastAPI" que te permite agrupar rutas.
# En vez de tener todas las rutas en main.py, las separas por archivos
# (files.py, auth.py, etc.). Es como tener un app.get() pero organizado.

# - UploadFile: Es un tipo especial que FastAPI usa cuando recibes un archivo subido.
# El navegador manda el archivo, y FastAPI lo pone en una variable de tipo UploadFile.
# Tiene propiedades como .filename (nombre del archivo) y .file (el contenido).

# - File: Es un "decorador" que le dice a FastAPI "esto viene de un archivo subido".
# Se usa así: archivo: UploadFile = File(...).

# - HTTPException: Es un error que, cuando lo lanzas, FastAPI lo convierte en
# una respuesta HTTP con código de error (404, 400, 401, etc.).
# Por ejemplo: raise HTTPException(status_code=404, detail="Archivo no encontrado").

# - Depends: Sirve para "inyectar" dependencias. Por ejemplo,
# para decir "esta ruta necesita que el token sea válido", usas Depends(verify_token).
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

# - HTTPBearer: Es un esquema de seguridad que espera un token en el header
# Authorization: Bearer <tu-token>. Es el estándar para JWT.

# - HTTPAuthorizationCredentials: Son las credenciales que extrae (el token).
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Es una clase de FastAPI que envía un archivo como respuesta HTTP. El navegador lo descarga automáticamente.
from fastapi.responses import FileResponse

# - os: Sirve para manejar rutas de carpetas, crear directorios, etc.
import os

# - shutil: Es como copy pero en Python. Sirve para copiar archivos de un lugar a otro.
# Se usará para guardar el archivo subido en la carpeta uploads/.
import shutil

# Importación de funciones de otros archivos
from .database import get_connection
from .auth import getCurrentUser


# ==========================
# === VARIABLES GLOBALES ===
# ==========================

# Crear el router para las rutas de archivos
router = APIRouter()

# Carpeta donde se guardarán los archivos
UPLOAD_DIR = "uploads"

# Asegurar que la carpeta existe
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =================
# === FUNCIONES ===
# =================

# ===== Funcion para subir un archivo a la carpeta del usuario. =====
@router.post("/upload")
async def subir_archivo(
    archivo: UploadFile = File(...),
    usuario: dict = Depends(getCurrentUser)
    # Sube un archivo al servidor.
    # Requiere autenticación con token JWT.
):

    # 1. Validar que se ha subido un archivo
    if not archivo or not archivo.filename:
        raise HTTPException(status_code=400, detail="No se ha proporcionado ningún archivo")

    # 2. Obtener el username del usuario
    username = usuario["username"]

    # 3. Crear carpeta del usuario (evitar sobrescribir archivos de otros usuarios)
    user_dir = os.path.join(UPLOAD_DIR, username)
    os.makedirs(user_dir, exist_ok=True)

    # 4. Guardar el archivo en la carpeta del usuario
    ruta_completa = os.path.join(user_dir, archivo.filename)

    with open(ruta_completa, "wb") as archivo_destino:
        shutil.copyfileobj(archivo.file, archivo_destino)

    # 5. Obtener el tamany del archivo (después de guardarlo)
    tamany = os.path.getsize(ruta_completa)

    # 6. Guardar metadatos en la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO files (user_id, filename, original_filename, size)
        VALUES (?, ?, ?, ?)
        """,
        (usuario["id"], archivo.filename, archivo.filename, tamany)
    )
    conn.commit()
    conn.close()

    # 7. Devolver información del archivo subido
    return {
        "mensaje": "Archivo subido",
        "filename": archivo.filename,
        "size": tamany
    }

# ===== Funcion para listar los archivos de el usuario autenticado. =====
# NOTA: @router.get("/files") NO es una carpeta real del sistema de archivos.
# Es una "ruta de API" (endpoint) que FastAPI escucha.
# Cuando el navegador hace GET a /files, se ejecuta esta función.
# No tiene relación con la carpeta uploads/, es una URL virtual.
@router.get("/files")
async def listar_archivos(usuario: dict = Depends(getCurrentUser)):

    # Lista todos los archivos del usuario autenticado.
    # Devuelve solo los archivos del usuario logueado (no los de otros).

    # 1. Obtener el user_id del usuario
    user_id = usuario["id"]

    # 2. Consultar la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    # SELECT * FROM files WHERE user_id = ? - Solo archivos de este usuario
    # ORDER BY upload_time DESC - Los más recientes primero
    cursor.execute(
        "SELECT * FROM files WHERE user_id = ? ORDER BY upload_time DESC",
        (user_id,)
    )

    archivos = cursor.fetchall()  # fetchall() devuelve todos los resultados
    conn.close()

    # 3. Convertir a lista de diccionarios (más fácil para el frontend)
    resultado = []
    for archivo in archivos:
        resultado.append({
            "id": archivo["id"],
            "filename": archivo["filename"],
            "original_filename": archivo["original_filename"],
            "size": archivo["size"],
            "upload_time": archivo["upload_time"]
        })

    return {"archivos": resultado}

# ===== Funcion para descargar un archivo específico por su ID. =====
@router.get("/files/{id}")
async def descargar_archivo(
        id: int,
        usuario: dict = Depends(getCurrentUser)
):

    # Descarga un archivo específico por su ID.
    # Solo permite descargar archivos del usuario logueado.
    # 1. Obtener el user_id del usuario
    user_id = usuario["id"]

    # 2. Buscar el archivo en la DB
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM files WHERE id = ? AND user_id = ?",
        (id, user_id)
        # Importante: verificar que es del usuario
    )

    # Limita la salida a un solo archivo
    archivo = cursor.fetchone()
    conn.close()

    # 3. Si no existe o no es del usuario, error 404
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # 4. Construir la ruta al archivo
    ruta_archivo = os.path.join(UPLOAD_DIR, usuario["username"], archivo["filename"])

    # 5. Verificar que el archivo existe físicamente
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail="El archivo no existe en el servidor")

        # 6. Devolver el archivo como descarga
    return FileResponse(
        path=ruta_archivo,
        filename=archivo["original_filename"],
        media_type="application/octet-stream"
        # Fuerza la descarga
    )


@router.delete("/files/{id}")
async def eliminar_archivo(
        id: int,
        usuario: dict = Depends(getCurrentUser)
        # Elimina un archivo por su ID.
        # Solo permite eliminar archivos del usuario logueado.
):

    user_id = usuario["id"]

    # 1. Buscar el archivo en la DB
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM files WHERE id = ? AND user_id = ?",
        (id, user_id)
    )

    archivo = cursor.fetchone()

    if not archivo:
        conn.close()
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # 2. Construir ruta y eliminar el archivo físico
    ruta_archivo = os.path.join(UPLOAD_DIR, usuario["username"], archivo["filename"])

    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)

    # 3. Eliminar registro de la base de datos
    cursor.execute("DELETE FROM files WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {"mensaje": "Archivo eliminado"}

