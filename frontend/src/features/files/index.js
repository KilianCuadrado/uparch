import { MAX_FILE_SIZE_MB } from '../../config.js';
import { deleteFile, downloadFileBlob, uploadFile } from '../../api/files.js';
import { showToast } from '../../utils/index.js';

export async function handleDownloadFile(file) {
    try {
        showToast('Descargando...', `Iniciando descarga de ${file.original_filename}`, 'info');
        const blob = await downloadFileBlob(file.id);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.style.display = 'none';
        link.href = url;
        link.download = file.original_filename;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        link.remove();
    } catch {
        showToast('Error', 'No se pudo descargar el archivo', 'error');
    }
}

export async function handleDeleteFile(file, onSuccess) {
    if (!confirm(`¿Estás seguro de eliminar "${file.original_filename}"?`)) {
        return;
    }

    try {
        await deleteFile(file.id);
        showToast('Eliminado', 'Archivo eliminado con éxito', 'success');
        await onSuccess();
    } catch {
        showToast('Error', 'No se pudo eliminar el archivo', 'error');
    }
}

export async function handleUploadFile(file, currentFolderId, ui, onSuccess) {
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_FILE_SIZE_MB) {
        showToast('Error', `El archivo excede el límite de ${MAX_FILE_SIZE_MB}MB`, 'error');
        return;
    }

    ui.startUploadProgress(file.name);

    try {
        await uploadFile(file, currentFolderId, (progress) => ui.setUploadProgress(progress));
        showToast('¡Éxito!', 'Archivo subido correctamente', 'success');
        await onSuccess();
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        ui.stopUploadProgress();
    }
}
