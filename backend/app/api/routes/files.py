from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.core.dependencies import get_current_user
from app.services.files_service import (
    delete_user_file,
    get_download_info,
    list_user_files,
    move_user_file,
    upload_file_for_user,
)

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    folder_id: Optional[int] = Form(None),
    user: dict = Depends(get_current_user),
):
    return upload_file_for_user(file, folder_id, user)


@router.get("/files")
async def list_files(folder_id: Optional[int] = None, user: dict = Depends(get_current_user)):
    return list_user_files(user, folder_id)


@router.get("/files/{file_id}")
async def download_file(file_id: int, user: dict = Depends(get_current_user)):
    file_path, original_filename = get_download_info(file_id, user)
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type="application/octet-stream",
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: int, user: dict = Depends(get_current_user)):
    return delete_user_file(file_id, user)


@router.put("/files/{file_id}/move")
async def move_file_to_folder(
    file_id: int,
    folder_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    return move_user_file(file_id, folder_id, current_user)
