import { request } from './http.js';
import { setToken } from '../state/session.js';

export async function login(username, password) {
    const data = await request('/login', {
        method: 'POST',
        token: false,
        json: true,
        body: { username, password },
        errorMessage: 'Credenciales incorrectas'
    });
    setToken(data.token);
    return data;
}

export async function verifySession() {
    return request('/verify', { errorMessage: 'Token inválido' });
}
