import { API_BASE } from '../config.js';
import { getAuthHeaders } from '../state/session.js';

function buildUrl(path, query) {
    const url = new URL(`${API_BASE}${path}`);
    if (query) {
        Object.entries(query).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                url.searchParams.append(key, value);
            }
        });
    }
    return url.toString();
}

async function parseError(res, fallback) {
    try {
        const data = await res.json();
        if (typeof data?.detail === 'string') return data.detail;
        if (data?.detail) return JSON.stringify(data.detail);
        return fallback;
    } catch {
        return fallback;
    }
}

export async function request(path, options = {}) {
    const {
        method = 'GET',
        body,
        query,
        token = true,
        json = false,
        headers = {},
        responseType = 'json',
        errorMessage = 'Error en la solicitud'
    } = options;

    const finalHeaders = {
        ...(token ? getAuthHeaders() : {}),
        ...headers
    };

    const isFormData = body instanceof FormData;
    if (json && !isFormData) {
        finalHeaders['Content-Type'] = 'application/json';
    }

    const response = await fetch(buildUrl(path, query), {
        method,
        headers: finalHeaders,
        body: body === undefined ? undefined : (json && !isFormData ? JSON.stringify(body) : body)
    });

    if (!response.ok) {
        throw new Error(await parseError(response, errorMessage));
    }

    if (responseType === 'blob') return response.blob();
    if (responseType === 'text') return response.text();
    if (responseType === 'none') return null;
    return response.json();
}
