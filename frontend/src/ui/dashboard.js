import { formatBytes, getFileIconClass } from '../utils/index.js';

export function createDashboardUI() {
    const elements = {
        breadcrumbs: document.getElementById('breadcrumbs'),
        filesGrid: document.getElementById('filesGrid'),
        emptyState: document.getElementById('emptyState'),
        fileCountText: document.getElementById('fileCountText'),
        displayUsername: document.getElementById('displayUsername'),
        userAvatar: document.getElementById('userAvatar'),
        logoutBtn: document.getElementById('logoutBtn'),
        btnCreateFolder: document.getElementById('btnCreateFolder'),
        uploadZone: document.getElementById('uploadZone'),
        btnUploadHeader: document.getElementById('btnUploadHeader'),
        btnUploadZone: document.getElementById('btnUploadZone'),
        fileInput: document.getElementById('fileInput'),
        uploadProgressContainer: document.getElementById('uploadProgressContainer'),
        uploadProgressFill: document.getElementById('uploadProgressFill'),
        uploadProgressText: document.getElementById('uploadProgressText')
    };

    return {
        setUser(user) {
            elements.displayUsername.textContent = user.username;
            elements.userAvatar.textContent = user.username.charAt(0).toUpperCase();
        },

        bindLogout(handler) {
            elements.logoutBtn.addEventListener('click', handler);
        },

        bindCreateFolder(handler) {
            elements.btnCreateFolder?.addEventListener('click', handler);
        },

        bindUpload(handler) {
            const preventDefaults = (event) => {
                event.preventDefault();
                event.stopPropagation();
            };

            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
                elements.uploadZone.addEventListener(eventName, preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach((eventName) => {
                elements.uploadZone.addEventListener(eventName, () => elements.uploadZone.classList.add('drag-active'), false);
            });

            ['dragleave', 'drop'].forEach((eventName) => {
                elements.uploadZone.addEventListener(eventName, () => elements.uploadZone.classList.remove('drag-active'), false);
            });

            elements.uploadZone.addEventListener('drop', (event) => {
                const files = event.dataTransfer?.files;
                if (files?.length) handler(files[0]);
            });

            elements.fileInput.addEventListener('change', (event) => {
                const files = event.target.files;
                if (files?.length) {
                    handler(files[0]);
                    elements.fileInput.value = '';
                }
            });

            elements.btnUploadHeader?.addEventListener('click', () => elements.fileInput.click());
            elements.btnUploadZone?.addEventListener('click', () => elements.fileInput.click());
        },

        renderBreadcrumbs(path, onNavigate) {
            elements.breadcrumbs.innerHTML = '';

            path.forEach((step, index) => {
                const link = document.createElement('a');
                link.className = 'breadcrumb-link';
                link.href = '#';
                link.textContent = step.name;
                link.addEventListener('click', (event) => {
                    event.preventDefault();
                    onNavigate(index);
                });

                elements.breadcrumbs.appendChild(link);

                if (index < path.length - 1) {
                    const separator = document.createElement('span');
                    separator.textContent = ' > ';
                    separator.className = 'breadcrumb-separator';
                    elements.breadcrumbs.appendChild(separator);
                }
            });
        },

        renderItems({ folders, files, onOpenFolder, onDeleteFolder, onDownloadFile, onDeleteFile }) {
            Array.from(elements.filesGrid.children).forEach((child) => {
                if (child.id !== 'emptyState') child.remove();
            });

            const totalItems = folders.length + files.length;
            elements.fileCountText.textContent = `${totalItems} elemento(s)`;

            if (totalItems === 0) {
                elements.emptyState.style.display = 'flex';
                return;
            }

            elements.emptyState.style.display = 'none';

            folders.forEach((folder) => {
                const card = document.createElement('div');
                card.className = 'file-card folder-card';
                card.innerHTML = `
                    <i class="ph ph-folder file-icon text-warning"></i>
                    <div class="file-info">
                        <div class="file-name" title="${folder.name}">${folder.name}</div>
                        <div class="file-meta">
                            <span>Carpeta</span>
                            <span>${new Date(folder.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-ghost open-btn" title="Abrir"><i class="ph ph-folder-open"></i></button>
                        <button class="btn btn-danger delete-btn" title="Eliminar"><i class="ph ph-trash"></i></button>
                    </div>
                `;

                card.querySelector('.open-btn').addEventListener('click', (event) => {
                    event.stopPropagation();
                    onOpenFolder(folder);
                });

                card.addEventListener('dblclick', () => onOpenFolder(folder));

                card.querySelector('.delete-btn').addEventListener('click', async (event) => {
                    event.stopPropagation();
                    await onDeleteFolder(folder);
                });

                elements.filesGrid.appendChild(card);
            });

            files.forEach((file) => {
                const card = document.createElement('div');
                card.className = 'file-card';
                card.innerHTML = `
                    <i class="ph ${getFileIconClass(file.original_filename)} file-icon"></i>
                    <div class="file-info">
                        <div class="file-name" title="${file.original_filename}">${file.original_filename}</div>
                        <div class="file-meta">
                            <span>${formatBytes(file.size)}</span>
                            <span>${new Date(file.upload_time).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-ghost download-btn" title="Descargar"><i class="ph ph-download-simple"></i></button>
                        <button class="btn btn-danger delete-btn" title="Eliminar"><i class="ph ph-trash"></i></button>
                    </div>
                `;

                card.querySelector('.download-btn').addEventListener('click', () => onDownloadFile(file));
                card.querySelector('.delete-btn').addEventListener('click', () => onDeleteFile(file));

                elements.filesGrid.appendChild(card);
            });
        },

        startUploadProgress(filename) {
            elements.uploadProgressContainer.style.display = 'block';
            elements.uploadProgressFill.style.width = '0%';
            elements.uploadProgressText.textContent = `Subiendo... ${filename}`;
        },

        setUploadProgress(percent) {
            elements.uploadProgressFill.style.width = `${percent}%`;
        },

        stopUploadProgress() {
            setTimeout(() => {
                elements.uploadProgressContainer.style.display = 'none';
                elements.uploadProgressFill.style.width = '0%';
            }, 1000);
        }
    };
}
