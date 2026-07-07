from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.services.folders_service import (
    create_user_folder,
    delete_user_folder,
    list_user_folders,
    rename_user_folder,
)

router = APIRouter(prefix="/api/folders", tags=["folders"])


class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_folder(folder: FolderCreate, current_user: dict = Depends(get_current_user)):
    return create_user_folder(folder.name, folder.parent_id, current_user)


@router.get("/list")
async def list_folders(parent_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    return list_user_folders(parent_id, current_user)


@router.delete("/delete/{folder_id}")
async def delete_folder(folder_id: int, current_user: dict = Depends(get_current_user)):
    return delete_user_folder(folder_id, current_user)


@router.put("/rename/{folder_id}")
async def rename_folder(
    folder_id: int, new_name: str, current_user: dict = Depends(get_current_user)
):
    return rename_user_folder(folder_id, new_name, current_user)
