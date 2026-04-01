/**
 * UpArch - Vanilla JS Frontend Logic
 */

const API_BASE = 'http://localhost:8000'; // Conexion al backend
const MAX_FILE_SIZE_MB = 50;

// ==========================================
// 1. Utilities (Toasts, Formatting, etc)
// ==========================================

function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconClass = 'ph-info';
    if (type === 'success') iconClass = 'ph-check-circle';
    if (type === 'error') iconClass = 'ph-warning-circle';

    toast.innerHTML = `
        <i class="ph ${iconClass} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.classList.add('hiding'); setTimeout(() => this.parentElement.remove(), 300)">&times;</button>
    `;

    container.appendChild(toast);

    // Auto remove after 5s
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function getFileIconClass(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'];
    const videoExts = ['mp4', 'mkv', 'avi', 'mov'];
    const docExts = ['pdf', 'doc', 'docx', 'txt', 'md'];
    const codeExts = ['js', 'py', 'html', 'css', 'json'];

    if (imageExts.includes(ext)) return 'ph-image';
    if (videoExts.includes(ext)) return 'ph-video-camera';
    if (docExts.includes(ext)) return 'ph-file-text';
    if (codeExts.includes(ext)) return 'ph-file-code';
    if (['zip', 'rar', 'tar', 'gz'].includes(ext)) return 'ph-file-archive';
    
    return 'ph-file';
}

// ==========================================
// 2. Auth Service
// ==========================================

const Auth = {
    getToken() {
        return localStorage.getItem('uparch_token');
    },
    
    setToken(token) {
        localStorage.setItem('uparch_token', token);
    },
    
    logout() {
        localStorage.removeItem('uparch_token');
        window.location.href = 'index.html';
    },

    async checkAuth() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const res = await fetch(`${API_BASE}/verify`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Token inv\u00e1lido');
            const data = await res.json();
            return data; // Backend /verify returns {"mensaje": "...", "username": "...", "user_id": ...} directly
        } catch (error) {
            this.logout();
            return null;
        }
    },

    async login(username, password) {
        // FastAPI endpoint uses a Pydantic BaseModel (LoginRequest), so it expects JSON
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) throw new Error('Credenciales incorrectas');
        
        const data = await res.json();
        this.setToken(data.token); // Backend models LoginResponse with 'token', not 'access_token'
        return data;
    }
};

// ==========================================
// 3. File Service
// ==========================================

const Files = {
    getHeaders() {
        return { 'Authorization': `Bearer ${Auth.getToken()}` };
    },

    async list() {
        const res = await fetch(`${API_BASE}/api/files`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error('Error al listar archivos');
        const data = await res.json();
        return data.archivos; // Backend returns {"archivos": [...]}
    },

    async upload(fileObj, onProgress) {
        const formData = new FormData();
        // El backend espera el nombre 'archivo' en la petición de form data (def subir_archivo(archivo: UploadFile = File(...)))
        formData.append('archivo', fileObj);

        // Fetch does not natively support upload progress without XMLHttpRequest, 
        // so we fake a tiny progressive bar or just await if it's small, 
        // but since we want premium feel, we simulate a loading state if XHR is too complex.
        // For simplicity and matching vanilla Fetch API:
        
        if (onProgress) onProgress(10);
        
        const res = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: formData
        });

        if (onProgress) onProgress(100);

        if (!res.ok) {
            const err = await res.json();
            // FastAPI devuelve un array de objetos en `detail` cuando hay errores de validación (422)
            let errorMsg = err.detail;
            if (typeof errorMsg === 'object') {
                errorMsg = JSON.stringify(errorMsg); // Prevenir error '[object Object]'
            }
            throw new Error(errorMsg || 'Error al subir archivo');
        }
        return res.json();
    },

    async delete(id) {
        const res = await fetch(`${API_BASE}/api/files/${id}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (!res.ok) throw new Error('Error al eliminar archivo');
        return res.json();
    },

    downloadUrl(id) {
        // Direct download using token usually requires a blob(Binary Large Object) fetch 
        // because we can't easily append Authorization header to an <a> tag href
        return async () => {
            const res = await fetch(`${API_BASE}/api/files/${id}`, { headers: this.getHeaders() });
            if (!res.ok) throw new Error('Error al descargar');
            
            // Reconstruct filename from headers if possible or rely on the blob
            const blob = await res.blob();
            // Since we don't have the filename directly here without an extra call, 
            // the user will pass the filename to the click handler.
            return blob;
        };
    }
};

// ==========================================
// 4. Page Routing / Initialization
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    
    const isLoginScreen = document.getElementById('loginForm') !== null;
    const isDashboard = document.getElementById('filesGrid') !== null;

    if (isLoginScreen) {
        initLoginScreen();
    } else if (isDashboard) {
        await initDashboardScreen();
    }
});

function initLoginScreen() {
    // If already logged in, redirect
    if (Auth.getToken()) {
        window.location.href = 'dashboard.html';
    }

    const form = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const u = document.getElementById('username').value;
        const p = document.getElementById('password').value;
        
        loginBtn.classList.add('loading');
        
        try {
            await Auth.login(u, p);
            showToast('¡Éxito!', 'Inicio de sesión completado', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 600);
        } catch (err) {
            showToast('Error', err.message, 'error');
        } finally {
            loginBtn.classList.remove('loading');
        }
    });
}

async function initDashboardScreen() {
    const user = await Auth.checkAuth();
    if (!user) return; // Will redirect

    // Populate user UI
    document.getElementById('displayUsername').textContent = user.username;
    document.getElementById('userAvatar').textContent = user.username.charAt(0).toUpperCase();

    // Bind Logout
    document.getElementById('logoutBtn').addEventListener('click', () => Auth.logout());

    // Load Files
    await refreshFiles();

    // Setup Drag&Drop and Upload
    setupUploadHandlers();
}

// ==========================================
// 5. Dashboard Specific Logic
// ==========================================

async function refreshFiles() {
    const grid = document.getElementById('filesGrid');
    const emptyState = document.getElementById('emptyState');
    const countText = document.getElementById('fileCountText');
    
    try {
        const files = await Files.list();
        
        // Clear current elements except empty state
        Array.from(grid.children).forEach(child => {
            if (child.id !== 'emptyState') child.remove();
        });

        countText.textContent = `${files.length} archivo(s)`;

        if (files.length === 0) {
            emptyState.style.display = 'flex';
        } else {
            emptyState.style.display = 'none';
            files.forEach(f => {
                const card = document.createElement('div');
                card.className = 'file-card';
                card.innerHTML = `
                    <i class="ph ${getFileIconClass(f.original_filename)} file-icon"></i>
                    <div class="file-info">
                        <div class="file-name" title="${f.original_filename}">${f.original_filename}</div>
                        <div class="file-meta">
                            <span>${formatBytes(f.size)}</span>
                            <span>${new Date(f.upload_time).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-ghost download-btn" title="Descargar"><i class="ph ph-download-simple"></i></button>
                        <button class="btn btn-danger delete-btn" title="Eliminar"><i class="ph ph-trash"></i></button>
                    </div>
                `;

                // Bind actions
                card.querySelector('.download-btn').addEventListener('click', async () => {
                    try {
                        showToast('Descargando...', 'Iniciando descarga de ' + f.original_filename, 'info');
                        const getBlob = Files.downloadUrl(f.id);
                        const blob = await getBlob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = f.original_filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        a.remove();
                    } catch (e) {
                        showToast('Error', 'No se pudo descargar el archivo', 'error');
                    }
                });

                card.querySelector('.delete-btn').addEventListener('click', async () => {
                    if (confirm(`¿Estás seguro de eliminar "${f.original_filename}"?`)) {
                        try {
                            await Files.delete(f.id);
                            showToast('Eliminado', 'Archivo eliminado con éxito', 'success');
                            card.remove();
                            // Update count text slightly hacky but works
                            const currentList = Array.from(grid.children).filter(c => c.id !== 'emptyState');
                            countText.textContent = `${currentList.length} archivo(s)`;
                            if (currentList.length === 0) emptyState.style.display = 'flex';
                        } catch (e) {
                            showToast('Error', 'No se pudo eliminar el archivo', 'error');
                        }
                    }
                });

                grid.appendChild(card);
            });
        }
    } catch (e) {
        showToast('Error', 'No se pudieron cargar los archivos', 'error');
    }
}

function setupUploadHandlers() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.getElementById('uploadProgressContainer');
    const progressFill = document.getElementById('uploadProgressFill');
    const progressText = document.getElementById('uploadProgressText');

    // Drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('drag-active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('drag-active'), false);
    });

    uploadZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    // Bind upload buttons
    const btnUploadHeader = document.getElementById('btnUploadHeader');
    const btnUploadZone = document.getElementById('btnUploadZone');
    if (btnUploadHeader) btnUploadHeader.addEventListener('click', () => fileInput.click());
    if (btnUploadZone) btnUploadZone.addEventListener('click', () => fileInput.click());

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length) {
            uploadFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files && files.length) {
            uploadFile(files[0]);
            fileInput.value = ''; // reset
        }
    }

    async function uploadFile(file) {
        // Validate size
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > MAX_FILE_SIZE_MB) {
            showToast('Error', `El archivo excede el l\u00edmite de ${MAX_FILE_SIZE_MB}MB`, 'error');
            return;
        }

        // Show Progress Bar
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = `Subiendo... ${file.name}`;

        try {
            await Files.upload(file, (perc) => {
                progressFill.style.width = `${perc}%`;
            });
            showToast('¡Éxito!', 'Archivo subido correctamente', 'success');
            await refreshFiles();
        } catch (e) {
            showToast('Error', e.message, 'error');
        } finally {
            setTimeout(() => {
                progressContainer.style.display = 'none';
                progressFill.style.width = '0%';
            }, 1000); // hide after a second
        }
    }
}
