import { listFiles } from './api/files.js';
import { listFolders } from './api/folders.js';
import { initLoginPage, requireDashboardUser } from './features/auth/index.js';
import { handleCreateFolder, handleDeleteFolder } from './features/folders/index.js';
import { handleDeleteFile, handleDownloadFile, handleUploadFile } from './features/files/index.js';
import { getCurrentFolderId, getFolderPath, navigateToPathIndex, openFolder, resetNavigation } from './state/navigation.js';
import { logout } from './state/session.js';
import { showToast } from './utils/index.js';
import { createDashboardUI } from './ui/dashboard.js';

async function initDashboardPage() {
    const user = await requireDashboardUser();
    if (!user) return;

    resetNavigation();

    const ui = createDashboardUI();
    ui.setUser(user);
    ui.bindLogout(logout);

    const refreshDashboard = async () => {
        try {
            const currentFolderId = getCurrentFolderId();
            const [foldersResponse, files] = await Promise.all([
                listFolders(currentFolderId),
                listFiles(currentFolderId)
            ]);

            const folders = foldersResponse.folders || [];

            ui.renderBreadcrumbs(getFolderPath(), async (index) => {
                navigateToPathIndex(index);
                await refreshDashboard();
            });

            ui.renderItems({
                folders,
                files,
                onOpenFolder: async (folder) => {
                    openFolder(folder);
                    await refreshDashboard();
                },
                onDeleteFolder: async (folder) => {
                    await handleDeleteFolder(folder, refreshDashboard);
                },
                onDownloadFile: handleDownloadFile,
                onDeleteFile: async (file) => {
                    await handleDeleteFile(file, refreshDashboard);
                }
            });
        } catch {
            showToast('Error', 'No se pudieron cargar los archivos o carpetas', 'error');
        }
    };

    ui.bindCreateFolder(async () => {
        await handleCreateFolder(getCurrentFolderId(), refreshDashboard);
    });

    ui.bindUpload(async (file) => {
        await handleUploadFile(file, getCurrentFolderId(), ui, refreshDashboard);
    });

    await refreshDashboard();
}

document.addEventListener('DOMContentLoaded', async () => {
    const isLoginScreen = document.getElementById('loginForm') !== null;
    const isDashboard = document.getElementById('filesGrid') !== null;

    if (isLoginScreen) {
        initLoginPage();
        return;
    }

    if (isDashboard) {
        await initDashboardPage();
    }
});
