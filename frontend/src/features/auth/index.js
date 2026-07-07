import { login, verifySession } from '../../api/auth.js';
import { getToken, logout } from '../../state/session.js';
import { showToast } from '../../utils/index.js';

export function initLoginPage() {
    if (getToken()) {
        window.location.href = 'dashboard.html';
    }

    const form = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        loginBtn.classList.add('loading');

        try {
            await login(username, password);
            showToast('¡Éxito!', 'Inicio de sesión completado', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 600);
        } catch (error) {
            showToast('Error', error.message, 'error');
        } finally {
            loginBtn.classList.remove('loading');
        }
    });
}

export async function requireDashboardUser() {
    if (!getToken()) {
        window.location.href = 'index.html';
        return null;
    }

    try {
        return await verifySession();
    } catch {
        logout();
        return null;
    }
}
