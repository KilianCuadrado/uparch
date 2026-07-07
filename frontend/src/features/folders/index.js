import { createFolder, deleteFolder } from '../../api/folders.js';
import { showToast } from '../../utils/index.js';

export async function handleCreateFolder(currentFolderId, onSuccess) {
    const name = prompt('Nombre de la nueva carpeta:');
    if (!name || !name.trim()) return;

    try {
        await createFolder(name.trim(), currentFolderId);
        showToast('¡Éxito!', 'Carpeta creada', 'success');
        await onSuccess();
    } catch (error) {
        showToast('Error', error.message, 'error');
    }
}

export async function handleDeleteFolder(folder, onSuccess) {
    if (!confirm(`¿Estás seguro de eliminar la carpeta "${folder.name}"? Debe estar vacía.`)) {
        return;
    }

    try {
        await deleteFolder(folder.id);
        showToast('Eliminada', 'Carpeta eliminada con éxito', 'success');
        await onSuccess();
    } catch (error) {
        showToast('Error', error.message, 'error');
    }
}
