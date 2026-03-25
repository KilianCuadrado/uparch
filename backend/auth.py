# ==========================
# === IMPORTS NECESARIOS ===
# ==========================


# Para manejar fechas y tiempos. Los JWT
# tienen una fecha de expiración,
# con timedelta defines cuánto tiempo dura
# el token (por ejemplo 24 horas).
from datetime import datetime, timedelta, timezone

# De la librería que instalada antes.
# jwt crea y verifica tokens,
# JWTError es el error que lanza
# cuando un token no es válido.
from jose import JWTError, jwt

# Librería bcrypt para hashear contraseñas de forma segura.
# Se encarga de hashear contraseñas
# y verificarlas. Nunca guardaremos
# la contraseña real en la base de
# datos, solo su hash.
import bcrypt

# Para extraer el token del header Authorization
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importa la función de database.py
# para conectarte a la DB.
from .database import get_connection



# ==========================
# === VARIABLES GLOBALES ===
# ==========================


# Clave secreta para firmar los tokens JWT
SECRET_KEY = "dro1oXi-IIMg3mrB8zj7roN12nb4PUwV5D4XGgliS9Y" # Cambiar a secrets.propoerties para no tenerla visiblen en GitHub
ALGORITHM = "HS256"
# Tiempo de expiración del token (en horas)
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Esquema de seguridad HTTPBearer para extraer el token del header
security = HTTPBearer()



# =================
# === FUNCIONES ===
# =================


def hash_password(password: str) -> str:
    # Convierte la contraseña en un hash seguro usando bcrypt directamente
    # encode('utf-8') convierte el string a bytes (bcrypt necesita bytes)
    # gensalt() genera una "sal" aleatoria para mayor seguridad
    # decode('utf-8') convierte el resultado de bytes a string para guardar en la DB
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compara la contraseña con el hash guardado en la DB
    # checkpw devuelve True si coinciden, False si no
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_user(username: str):
    # Buscamos el usuario en la base de datos por su nombre
    conn = get_connection()
    cursor = conn.cursor()

    # El ? es un placeholder, evita inyecciones SQL.
    # Nunca metas variables directamente en una query
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

    user = cursor.fetchone() # Devuelve solo un resultado, ya que el username es único.
    conn.close()
    return user


def authenticate_user(username: str, password: str):
    # Buscamos el usuario en la base de datos
    user = get_user(username)

    # Si no existe o la contraseña es incorrecta devolvemos False
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False

    return user


def create_access_token(username: str) -> str:
    # Definimos el contenido del token y su fecha de expiración
    data = {
        "sub": username, # Es el campo estándar de JWT para identificar al usuario, viene de "subject".

        # Fecha de expiración del token.
        # Después de 24 horas el token deja de ser válido
        # y el usuario tendrá que hacer login de nuevo.
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    # Creamos y devolvemos el token firmado
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM) # Firma el token con tu SECRET_KEY para que nadie pueda manipularlo.


def verify_token(token: str):
    try:
        # Decodificamos el token y extraemos el username
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            return None

        # Buscamos y devolvemos el usuario en la base de datos
        return get_user(username)
    except JWTError:
        # Si el token no es válido o ha expirado devolvemos None
        return None


def getCurrentUser(credentials: HTTPAuthorizationCredentials = Depends(security)):

    # Función de dependencia que extrae y verifica el token JWT automáticamente.
    # Se usa en los endpoints protegidos con Depends(getCurrentUser).
    
    # Esta función:
    # 1. Extrae el token del header "Authorization: Bearer <token>"
    # 2. Verifica que el token sea válido
    # 3. Devuelve el usuario si todo está correcto
    # 4. Lanza error 401 si el token es inválido

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