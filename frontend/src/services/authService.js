/**
 * Auth Service
 * API calls for authentication endpoints
 */
import api from './api';

export const authService = {
  /**
   * Register new user
   * POST /api/auth/register
   */
  register: async (formData) => {
    const res = await api.post('/api/auth/register', formData);
    return res.data; // { user, access_token, refresh_token }
  },

  /**
   * Login with email + password
   * POST /api/auth/login
   */
  login: async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    return res.data; // { user, access_token, refresh_token }
  },

  /**
   * Logout — revoke access token + refresh token on server
   * POST /api/auth/logout  { refresh_token }
   */
  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    return api.post('/api/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
  },

  /**
   * Get current user's profile
   * GET /api/auth/me
   */
  getProfile: async () => {
    const res = await api.get('/api/auth/me');
    return res.data; // { user }
  },

  /**
   * Update current user's profile
   * PUT /api/auth/me
   */
  updateProfile: async (profileData) => {
    const res = await api.put('/api/auth/me', profileData);
    return res.data; // { user }
  },

  /**
   * Request password reset email
   * POST /api/auth/forgot-password
   */
  forgotPassword: async (email) => {
    return api.post('/api/auth/forgot-password', { email });
  },

  /**
   * Reset password using token from email
   * POST /api/auth/reset-password
   */
  resetPassword: async (token, newPassword) => {
    return api.post('/api/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  },

  /**
   * Change password (authenticated)
   * PUT /api/auth/me/change-password
   */
  changePassword: async (oldPassword, newPassword) => {
    return api.put('/api/auth/me/change-password', {
      current_password: oldPassword,
      new_password: newPassword,
    });
  },
};
