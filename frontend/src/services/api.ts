import axios, { type AxiosRequestConfig } from 'axios';

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Pequena interface para tratar requests que usamos para retry
interface RetryableRequest extends AxiosRequestConfig {
  _retry?: boolean;
}

// Request interceptor seguro (prevenção de headers undefined)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    // Garantir que headers exista
    config.headers = config.headers ?? {};
    if (token) {
      (config.headers as any).Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor com tipagem/casts seguros para originalRequest
api.interceptors.response.use(
  (response) => response,
  async (error: any) => {
    const originalRequest = error?.config as RetryableRequest | undefined;

    if (error?.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const resp = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const access = resp?.data?.access;
        if (!access) throw new Error('No access token in refresh response');

        localStorage.setItem('access_token', access);

        originalRequest.headers = originalRequest.headers ?? {};
        (originalRequest.headers as any).Authorization = `Bearer ${access}`;

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        // redirecionar para login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Normalize API error payloads for easier handling in UI
api.interceptors.response.use(undefined, (error) => {
  if (error.response && error.response.data) {
    const data = error.response.data;
    // Backend uses { errors: ... } for validation errors
    if (data.errors) {
      error.apiErrors = data.errors;
    } else if (data.detail) {
      // DRF detail messages
      error.apiErrors = { detail: data.detail };
    }
  }
  return Promise.reject(error);
});

export default api;
