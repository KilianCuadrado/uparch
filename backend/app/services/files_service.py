import os
import shutil
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from app.core.config import UPLOAD_DIR
from app.repositories.files import (
    create_file_record,
    delete_file,
    get_file_by_id,
    list_files,
    move_file,
)
from app.repositories.folders import folder_exists_for_user

os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


def upload_file_for_user(file: UploadFile, folder_id: Optional[int], user: dict):
    current_position = file.file.tell()
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(current_position)

    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413, detail="Archivo demasiado grande. Máximo: 10MB"
        )
    file.file.seek(0)

    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No se ha proporcionado ningún archivo")

    if folder_id is not None and not folder_exists_for_user(folder_id, user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada",
        )

    user_dir = os.path.join(UPLOAD_DIR, user["username"])
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as destination:
        shutil.copyfileobj(file.file, destination)

    size = os.path.getsize(file_path)
    file_id = create_file_record(user["id"], folder_id, file.filename, file.filename, size)

    message = "Archivo subido"
    return {
        "message": message,
        "mensaje": message,  # Compatibilidad heredada: usar "message" en clientes nuevos.
        "file_id": file_id,
        "filename": file.filename,
        "size": size,
        "folder_id": folder_id,
    }


def list_user_files(user: dict, folder_id: Optional[int]):
    rows = list_files(user["id"], folder_id)
    files = [
        {
            "id": row["id"],
            "filename": row["filename"],
            "original_filename": row["original_filename"],
            "size": row["size"],
            "upload_time": row["upload_time"],
            "folder_id": row["folder_id"],
        }
        for row in rows
    ]
    return {
        "files": files,
        "archivos": files,  # Compatibilidad heredada: usar "files" en clientes nuevos.
    }


def get_download_info(file_id: int, user: dict):
    record = get_file_by_id(user["id"], file_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file_path = os.path.join(UPLOAD_DIR, user["username"], record["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="El archivo no existe en el servidor")

    return file_path, record["original_filename"]


def delete_user_file(file_id: int, user: dict):
    record = get_file_by_id(user["id"], file_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file_path = os.path.join(UPLOAD_DIR, user["username"], record["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    delete_file(file_id)
    message = "Archivo eliminado"
    return {
        "message": message,
        "mensaje": message,  # Compatibilidad heredada: usar "message" en clientes nuevos.
    }


def move_user_file(file_id: int, folder_id: Optional[int], user: dict):
    record = get_file_by_id(user["id"], file_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado",
        )

    if folder_id and not folder_exists_for_user(folder_id, user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta de destino no encontrada",
        )

    move_file(file_id, folder_id)
    return {
        "message": "Archivo movido exitosamente",
        "file_id": file_id,
        "filename": record["original_filename"],
        "folder_id": folder_id,
    }
