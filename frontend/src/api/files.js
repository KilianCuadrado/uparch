import { request } from './http.js';

export async function listFiles(folderId = null) {
    const data = await request('/api/files', {
        query: { folder_id: folderId },
        errorMessage: 'Error al listar archivos'
    });
    return data.archivos || [];
}

export async function uploadFile(file, folderId = null, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    if (folderId !== null) {
        formData.append('folder_id', String(folderId));
    }

    if (onProgress) onProgress(10);

    const result = await request('/api/upload', {
        method: 'POST',
        body: formData,
        errorMessage: 'Error al subir archivo'
    });

    if (onProgress) onProgress(100);
    return result;
}

export async function deleteFile(fileId) {
    return request(`/api/files/${fileId}`, {
        method: 'DELETE',
        errorMessage: 'Error al eliminar archivo'
    });
}

export async function downloadFileBlob(fileId) {
    return request(`/api/files/${fileId}`, {
        responseType: 'blob',
        errorMessage: 'Error al descargar'
    });
}
