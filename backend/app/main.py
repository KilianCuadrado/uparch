from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.files import router as files_router
from app.api.routes.folders import router as folders_router
from app.db.init import init_db

API_PREFIX = "/api"
LEGACY_FILES_PREFIX = "/files"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("🚀 Iniciando UpArch API...")
    init_db()
    print("✅ Base de datos inicializada")
    print("📡 Servidor listo en http://0.0.0.0:8000")
    print("📚 Documentación en http://0.0.0.0:8000/docs")
    yield
    print("👋 Cerrando UpArch API...")


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="UpArch API",
        description="API para almacenamiento de archivos en red local",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "UpArch API está funcionando",
            "mensaje": "UpArch API está funcionando",
            "version": "1.0.0",
        }

    app.include_router(auth_router)
    app.include_router(files_router, prefix=API_PREFIX, tags=["files"])
    # Compatibilidad heredada: mantener /files/* para clientes antiguos.
    # Nuevos clientes deben usar el prefijo canónico /api/*.
    app.include_router(files_router, prefix=LEGACY_FILES_PREFIX, tags=["files-legacy"])
    app.include_router(folders_router)

    return app


app = create_app()

