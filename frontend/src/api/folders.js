import { request } from './http.js';

export async function listFolders(parentId = null) {
    return request('/api/folders/list', {
        query: { parent_id: parentId },
        errorMessage: 'Error al listar carpetas'
    });
}

export async function createFolder(name, parentId = null) {
    return request('/api/folders/create', {
        method: 'POST',
        json: true,
        body: { name, parent_id: parentId },
        errorMessage: 'Error al crear carpeta'
    });
}

export async function deleteFolder(folderId) {
    return request(`/api/folders/delete/${folderId}`, {
        method: 'DELETE',
        errorMessage: 'Error al eliminar carpeta'
    });
}
