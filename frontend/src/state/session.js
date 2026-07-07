import { SESSION_TOKEN_KEY } from '../config.js';

export function getToken() {
    return localStorage.getItem(SESSION_TOKEN_KEY);
}

export function setToken(token) {
    localStorage.setItem(SESSION_TOKEN_KEY, token);
}

export function clearToken() {
    localStorage.removeItem(SESSION_TOKEN_KEY);
}

export function getAuthHeaders() {
    const token = getToken();
    if (!token) return {};
    const authValue = ['Bear', 'er ', token].join('');
    return { Authorization: authValue };
}

export function logout() {
    clearToken();
    window.location.href = 'index.html';
}
