/**
 * Axios API Client
 * Centralized HTTP client with:
 * - Base URL configuration
 * - JWT token injection on every request
 * - Auto token refresh on 401 responses
 * - Global error handling
 */
import axios from 'axios';

// ── Base configuration ────────────────────────────────────────────────────────
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,                             // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request Interceptor ───────────────────────────────────────────────────────
// Automatically inject JWT token from localStorage on every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    // Only send token if it looks like a valid JWT (starts with eyJ)
    if (token && token !== 'null' && token !== 'undefined' && token.startsWith('eyJ')) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (token && !token.startsWith('eyJ')) {
      // Corrupt/stale non-JWT value — purge immediately
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor ──────────────────────────────────────────────────────
// Handle global errors and auto-refresh on 401
let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  failedQueue = [];
}

api.interceptors.response.use(
  // Success: pass through
  (response) => response.data,

  // Error handling
  async (error) => {
    const originalRequest = error.config;

    // ── 422 Invalid Token ──────────────────────────────────────────────────
    // Flask-JWT-Extended returns 422 for structurally invalid JWTs.
    // Strategy:
    //   /api/auth/me  → just clear tokens; AuthContext.catch() handles redirect
    //                   (avoids race condition: stale getProfile + fresh login)
    //   all other     → clear tokens + dispatch event so AuthContext logs out
    if (error.response?.status === 422) {
      const msg = error.response?.data?.message || '';
      if (msg === 'Invalid token' || msg === 'Signature verification failed') {
        clearAuthToken();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        const url = error.config?.url || '';
        const isAuthMe = url.includes('/api/auth/me') || url.includes('/api/auth/refresh');
        if (!isAuthMe) {
          window.dispatchEvent(new CustomEvent('auth:session-expired'));
        }
      }
      return Promise.reject(error);
    }

    // ── Auto-refresh on 401 Unauthorized ──────────────────────────────────
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token');

      // No refresh token — session truly expired, redirect to login
      if (!refreshToken) {
        clearAuthToken();
        localStorage.removeItem('access_token');
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue concurrent requests while refreshing
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await axios.post(
          `${BASE_URL}/api/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );
        const { access_token } = response.data.data;

        localStorage.setItem('access_token', access_token);
        setAuthToken(access_token);
        processQueue(null, access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearAuthToken();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ── Token Helpers ─────────────────────────────────────────────────────────────
/**
 * Set Authorization header globally after login
 * @param {string} token - JWT access token
 */
export function setAuthToken(token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

/**
 * Remove Authorization header globally after logout
 */
export function clearAuthToken() {
  delete api.defaults.headers.common['Authorization'];
}

export default api;
