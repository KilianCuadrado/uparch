# ==========================
# === IMPORTS NECESARIOS ===
# ==========================

# FastAPI es el framework principal para crear la API
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# Para manejar el ciclo de vida de la aplicación (startup/shutdown)
from contextlib import asynccontextmanager

# Pydantic se usa para validar los datos que llegan del frontend
# BaseModel es como un "molde" para definir qué campos esperas
from pydantic import BaseModel

# HTTPBearer y HTTPAuthorizationCredentials sirven para extraer el token JWT
# del header "Authorization: Bearer <token>"
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importamos las funciones de autenticación que ya creaste
from .auth import authenticate_user, create_access_token, verify_token

# Importamos el router de files que ya tiene todos los endpoints CRUD de archivos
from .files import router as files_router

# Importamos la función para inicializar la base de datos
from .database import init_db


# ================================
# === EVENTO AL INICIAR LA APP ===
# ================================

# Lifespan event handler - reemplaza al deprecado on_event("startup")
# Se ejecuta cuando el servidor arranca y cuando se apaga.

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Gestiona el ciclo de vida de la aplicación.
    # El código antes del yield se ejecuta al iniciar.
    # El código después del yield se ejecuta al apagar.

    # === STARTUP ===
    print("🚀 Iniciando UpArch API...")
    init_db()
    print("✅ Base de datos inicializada")
    print("📡 Servidor listo en http://0.0.0.0:8000")
    print("📚 Documentación en http://0.0.0.0:8000/docs")

    yield  # Aquí el servidor funciona normalmente

    # === SHUTDOWN (opcional) ===
    print("👋 Cerrando UpArch API...")

# ====================
# === CREAR LA APP ===
# ====================

# Creamos la instancia principal de FastAPI
# Esta es la "aplicación" que escuchará las peticiones HTTP
app = FastAPI(
    title="UpArch API",
    description="API para almacenamiento de archivos en red local",
    version="1.0.0",
    lifespan=lifespan
)

# =======================
# === CONFIGURAR CORS ===
# =======================

# CORS (Cross-Origin Resource Sharing) permite que el frontend (HTML)
# pueda hacer peticiones a la API aunque estén en puertos diferentes.
# Sin esto, el navegador bloquearía las peticiones por seguridad.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia "*" por la IP específica de tu red local
    allow_credentials=True,  # Permite enviar cookies y headers de autenticación
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los headers (incluido Authorization)
)
# Explicación:
# ¿Por qué necesitas CORS?
# Imagina que tu frontend está en http://localhost:5500 (puerto del HTML) y tu backend
# en http://localhost:8000. El navegador ve que son "orígenes diferentes" y bloquea la
# comunicación por seguridad.
# CORS es como decirle al navegador: "Tranquilo, estos dos pueden hablar entre sí".
# - allow_origins=["*"]: Acepta peticiones desde cualquier origen (útil en desarrollo y red local)
# - allow_credentials=True: Permite enviar tokens JWT en los headers
# - allow_methods=["*"]: Permite GET, POST, DELETE, etc.
# - allow_headers=["*"]: Permite el header Authorization (donde va tu token)


# ==========================
# === MODELOS PYDANTIC ===
# ==========================

# Estos "modelos" definen qué datos esperas del frontend.
# Pydantic valida automáticamente que los datos sean correctos.

class LoginRequest(BaseModel):
    username: str
    password: str
    # Ejemplo de uso: {"username": "admin", "password": "1234"}


class LoginResponse(BaseModel):
    token: str
    username: str
    # Ejemplo de respuesta: {"token": "eyJ0eXAiOiJKV1...", "username": "admin"}


# ============================
# === ESQUEMA DE SEGURIDAD ===
# ============================

# HTTPBearer es el esquema que dice "espero un token en el header Authorization"
security = HTTPBearer()


# ====================================
# === FUNCIÓN PARA VERIFICAR TOKEN ===
# ====================================

# Esta función se usa como "dependencia" en las rutas protegidas.
# Extrae el token del header, lo verifica, y devuelve el usuario.
# Si el token no es válido, lanza un error 401 (no autorizado).

def getCurrentUser(credentials: HTTPAuthorizationCredentials = Depends(security)):

    # Extrae y verifica el token JWT del header Authorization.
    # Si es válido, devuelve los datos del usuario.
    # Si no, lanza HTTPException 401.

    # credentials.credentials contiene el token (sin el prefijo "Bearer")
    token = credentials.credentials

    # verify_token devuelve el usuario si el token es válido, o None si no lo es
    user = verify_token(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    return user

    # ==========================
    # === ENDPOINTS (RUTAS) ===
    # ==========================

    # ===== RUTA RAÍZ (para verificar que el servidor funciona) =====
@app.get("/")
async def root():
    """
    Endpoint de prueba. Devuelve un mensaje simple.
    Útil para verificar que el servidor está corriendo.
    """
    return {
        "mensaje": "UpArch API está funcionando",
        "version": "1.0.0"
    }


# ===== ENDPOINT DE LOGIN =====
@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Autentica un usuario y devuelve un token JWT.

    Pasos:
    1. Recibe username y password del frontend
    2. Verifica que el usuario existe y la contraseña es correcta
    3. Si es correcto, genera un token JWT
    4. Devuelve el token al frontend

    El frontend guardará este token y lo usará en todas las peticiones futuras.
    """

    # 1. Intentar autenticar al usuario
    user = authenticate_user(request.username, request.password)

    # 2. Si la autenticación falla, devolver error 401
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )
    # 3. Si es correcto, crear un token JWT
    token = create_access_token(request.username)

    # 4. Devolver el token y el username
    return LoginResponse(
        token=token,
        username=request.username
    )


# ===== ENDPOINT PARA VERIFICAR SI EL TOKEN ES VÁLIDO =====
@app.get("/verify")
async def verify(user: dict = Depends(getCurrentUser)):

    # Verifica si el token del usuario es válido.
    # El frontend puede llamar a esta ruta para comprobar si el usuario sigue logueado.
    # Si el token es válido, devuelve los datos del usuario.
    # Si no, devuelve error 401.

    return {
        "mensaje": "Token válido",
        "username": user["username"],
        "user_id": user["id"]
    }


# ================================
# === INCLUIR ROUTERS EXTERNOS ===
# ================================

# Aquí incluimos el router de files.py, que contiene todos los endpoints
# para subir, listar, descargar y eliminar archivos.

# El prefix="/api" significa que todas las rutas de files_router
# estarán bajo /api/... (ejemplo: /api/upload, /api/files, etc.)

app.include_router(
    files_router,
    prefix="/api",
    tags=["files"]  # Agrupa estos endpoints en la documentación automática
)

# ================================
# === EJECUTAR EL SERVIDOR ===
# ================================

# Esta parte solo se ejecuta si corres este archivo directamente
# con "python main.py" (no con uvicorn).
# En desarrollo usaremos uvicorn, pero esto es útil para pruebas rápidas.

if __name__ == "__main__":
    import uvicorn

    # Inicia el servidor en el puerto 8000, accesible desde toda la red local
    uvicorn.run(
        app,
        host="0.0.0.0",  # 0.0.0.0 = accesible desde cualquier dispositivo en la red local
        port=8000,
        reload=True  # Recarga automáticamente cuando cambies el código
    )