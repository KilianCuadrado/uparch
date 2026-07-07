import sqlite3
from typing import Optional

from fastapi import HTTPException, status

from app.repositories.folders import (
    count_files_in_folder,
    count_subfolders,
    create_folder,
    delete_folder,
    folder_exists_for_user,
    get_folder_by_id,
    list_folders,
    rename_folder,
)


def create_user_folder(name: str, parent_id: Optional[int], user: dict):
    if not name or name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de la carpeta no puede estar vacío",
        )

    if parent_id and not folder_exists_for_user(parent_id, user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta padre no encontrada",
        )

    try:
        folder_id = create_folder(user["id"], name.strip(), parent_id)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una carpeta con ese nombre en esta ubicación",
        )

    return {
        "message": "Carpeta creada exitosamente",
        "folder_id": folder_id,
        "name": name,
    }


def list_user_folders(parent_id: Optional[int], user: dict):
    rows = list_folders(user["id"], parent_id)
    folders = []
    for row in rows:
        folder_id = row["id"]
        folders.append(
            {
                "id": folder_id,
                "name": row["name"],
                "parent_id": row["parent_id"],
                "created_at": row["created_at"],
                "file_count": count_files_in_folder(folder_id, user["id"]),
            }
        )
    return {"folders": folders, "total": len(folders)}


def delete_user_folder(folder_id: int, user: dict):
    folder = get_folder_by_id(folder_id, user["id"])
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada",
        )

    file_count = count_files_in_folder(folder_id, user["id"])
    if file_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La carpeta contiene {file_count} archivo(s). Muévelos o elimínalos primero.",
        )

    subfolder_count = count_subfolders(folder_id)
    if subfolder_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La carpeta contiene {subfolder_count} subcarpeta(s). Elimínalas primero.",
        )

    delete_folder(folder_id)
    return {
        "message": "Carpeta eliminada exitosamente",
        "folder_id": folder_id,
        "name": folder["name"],
    }


def rename_user_folder(folder_id: int, new_name: str, user: dict):
    if not new_name or new_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nuevo nombre no puede estar vacío",
        )

    if not get_folder_by_id(folder_id, user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada",
        )

    try:
        rename_folder(folder_id, new_name.strip())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una carpeta con ese nombre",
        )

    return {
        "message": "Carpeta renombrada exitosamente",
        "folder_id": folder_id,
        "new_name": new_name,
    }
