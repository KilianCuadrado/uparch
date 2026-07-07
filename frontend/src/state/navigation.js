const ROOT_STEP = { id: null, name: 'Raíz' };

let currentFolderId = ROOT_STEP.id;
let folderPath = [ROOT_STEP];

export function getCurrentFolderId() {
    return currentFolderId;
}

export function getFolderPath() {
    return [...folderPath];
}

export function openFolder(folder) {
    folderPath = [...folderPath, { id: folder.id, name: folder.name }];
    currentFolderId = folder.id;
}

export function navigateToPathIndex(index) {
    folderPath = folderPath.slice(0, index + 1);
    currentFolderId = folderPath[folderPath.length - 1]?.id ?? null;
}

export function resetNavigation() {
    currentFolderId = ROOT_STEP.id;
    folderPath = [ROOT_STEP];
}
