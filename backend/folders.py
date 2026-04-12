
# Módulo para gestionar folders (carpetas) en UpArch.


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_connection
from auth import verify_token, getCurrentUser


# ========
# ROUTER =
# ========

router = APIRouter(
    prefix="/api/folders",
    tags=["folders"]
)


# ==================
# MODELOS PYDANTIC =
# ==================

class FolderCreate(BaseModel):
    # Esquema para crear folder
    name: str
    parent_id: Optional[int] = None  # None = root folder


class FolderResponse(BaseModel):
    """Esquema de respuesta de folder"""
    id: int
    name: str
    parent_id: Optional[int]
    created_at: str
    file_count: int = 0


# ===========
# ENDPOINTS =
# ===========

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder: FolderCreate,
    current_user: dict = Depends(getCurrentUser)
):
    """
    Crear un nuevo folder.
    
    Args:
        name: Nombre del folder
        parent_id: ID del folder padre (None = raíz)
    """
    
    # Validar nombre
    if not folder.name or folder.name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del folder no puede estar vacío"
        )
    
    # Validar que el folder padre existe (si se especificó)
    if folder.parent_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM folders WHERE id = ? AND user_id = ?",
            (folder.parent_id, current_user["id"])
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder padre no encontrado"
            )
        conn.close()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO folders (user_id, name, parent_id)
            VALUES (?, ?, ?)
        """, (current_user["id"], folder.name.strip(), folder.parent_id))
        
        conn.commit()
        folder_id = cursor.lastrowid
        conn.close()
        
        return {
            "message": "Folder creado exitosamente",
            "folder_id": folder_id,
            "name": folder.name
        }
        
    except Exception as e:
        # Error de UNIQUE constraint = folder duplicado
        if "UNIQUE constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un folder con ese nombre en esta ubicación"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear folder: {str(e)}"
        )


@router.get("/list")
async def list_folders(
    parent_id: Optional[int] = None,
    current_user: dict = Depends(getCurrentUser)
):
    """
    Listar folders del usuario.
    
    Args:
        parent_id: Si se especifica, lista subfolders. Si es None, lista root folders.
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Listar folders
        if parent_id is None:
            # Root folders (parent_id IS NULL)
            cursor.execute("""
                SELECT id, name, parent_id, created_at
                FROM folders
                WHERE user_id = ? AND parent_id IS NULL
                ORDER BY name
            """, (current_user["id"],))
        else:
            # Subfolders
            cursor.execute("""
                SELECT id, name, parent_id, created_at
                FROM folders
                WHERE user_id = ? AND parent_id = ?
                ORDER BY name
            """, (current_user["id"], parent_id))
        
        folders = []
        for row in cursor.fetchall():
            folder_id = row["id"]
            
            # Contar archivos en este folder
            cursor.execute(
                "SELECT COUNT(*) as count FROM files WHERE folder_id = ?",
                (folder_id,)
            )
            file_count_row = cursor.fetchone()
            file_count = file_count_row["count"] if file_count_row else 0
            
            folders.append({
                "id": folder_id,
                "name": row["name"],
                "parent_id": row["parent_id"],
                "created_at": row["created_at"],
                "file_count": file_count
            })
        
        conn.close()
        
        return {
            "folders": folders,
            "total": len(folders)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar folders: {str(e)}"
        )


@router.delete("/delete/{folder_id}")
async def delete_folder(
    folder_id: int,
    current_user: dict = Depends(getCurrentUser)
):
    """
    Eliminar un folder.
    Solo se puede eliminar si está vacío (sin archivos ni subfolders).
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que el folder existe y es del usuario
        cursor.execute(
            "SELECT name FROM folders WHERE id = ? AND user_id = ?",
            (folder_id, current_user["id"])
        )
        folder = cursor.fetchone()
        
        if not folder:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder no encontrado"
            )
        
        # Verificar que está vacío (sin archivos)
        cursor.execute(
            "SELECT COUNT(*) as count FROM files WHERE folder_id = ?",
            (folder_id,)
        )
        file_count = cursor.fetchone()["count"]
        
        if file_count > 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El folder contiene {file_count} archivo(s). Muévelos o elimínalos primero."
            )
        
        # Verificar que no tiene subfolders
        cursor.execute(
            "SELECT COUNT(*) as count FROM folders WHERE parent_id = ?",
            (folder_id,)
        )
        subfolder_count = cursor.fetchone()["count"]
        
        if subfolder_count > 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El folder contiene {subfolder_count} subfolder(s). Elimínalos primero."
            )
        
        # Eliminar folder
        cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        conn.commit()
        conn.close()
        
        return {
            "message": "Folder eliminado exitosamente",
            "folder_id": folder_id,
            "name": folder["name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar folder: {str(e)}"
        )


@router.put("/rename/{folder_id}")
async def rename_folder(
    folder_id: int,
    new_name: str,
    current_user: dict = Depends(getCurrentUser)
):
    """Renombrar un folder"""
    
    if not new_name or new_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nuevo nombre no puede estar vacío"
        )
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute(
            "SELECT name FROM folders WHERE id = ? AND user_id = ?",
            (folder_id, current_user["id"])
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder no encontrado"
            )
        
        # Renombrar
        cursor.execute(
            "UPDATE folders SET name = ? WHERE id = ?",
            (new_name.strip(), folder_id)
        )
        conn.commit()
        conn.close()
        
        return {
            "message": "Folder renombrado exitosamente",
            "folder_id": folder_id,
            "new_name": new_name
        }
        
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un folder con ese nombre"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al renombrar: {str(e)}"
        )
