/**
 * AuthContext
 * Global authentication state management.
 * Stores JWT token, current user data, and provides
 * login/logout/register actions to the entire app.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import { setAuthToken, clearAuthToken } from '../services/api';

// ── Context Creation ──────────────────────────────────────────────────────────
const AuthContext = createContext(null);

// ── AuthProvider Component ───────────────────────────────────────────────────
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── Helpers — declared first so useEffects below can reference them ────────

  /** Clear all session data and reset user state */
  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    clearAuthToken();
    setUser(null);
  }, []);

  /** Persist token to localStorage and update Axios default header */
  const persistSession = useCallback(({ user: u, access_token, refresh_token }) => {
    localStorage.setItem('access_token', access_token);
    if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
    setAuthToken(access_token);
    setUser(u);
  }, []);

  // ── Listen for session-expired from api.js interceptor ───────────────────
  // Only fires for non-auth/me endpoints → safe from the getProfile race condition.
  useEffect(() => {
    window.addEventListener('auth:session-expired', clearSession);
    return () => window.removeEventListener('auth:session-expired', clearSession);
  }, [clearSession]);

  // ── On mount: restore session from localStorage ────────────────────────────
  // Uses `cancelled` flag to ignore stale getProfile() responses that could
  // arrive AFTER a fresh login and incorrectly wipe the new session.
  useEffect(() => {
    let cancelled = false;
    const token = localStorage.getItem('access_token');
    if (token && token !== 'null' && token !== 'undefined') {
      setAuthToken(token);
      authService.getProfile()
        .then(({ user: u }) => { if (!cancelled) setUser(u); })
        .catch(() => { if (!cancelled) clearSession(); })
        .finally(() => { if (!cancelled) setLoading(false); });
    } else {
      setLoading(false);
    }
    return () => { cancelled = true; };
  }, [clearSession]);

  // ── Actions ───────────────────────────────────────────────────────────────

  const register = useCallback(async (formData) => {
    setError(null);
    try {
      const data = await authService.register(formData);
      persistSession(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      throw err;
    }
  }, [persistSession]);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const data = await authService.login(email, password);
      persistSession(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
      throw err;
    }
  }, [persistSession]);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // ignore server-side logout errors
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser);
  }, []);

  // ── Derived State ──────────────────────────────────────────────────────────
  const isAuthenticated = !!user;
  const isAdmin = user?.role === 'ADMIN';
  const isOwner = user?.role === 'OWNER';
  const isUser  = user?.role === 'USER';

  const value = {
    user, loading, error,
    isAuthenticated, isAdmin, isOwner, isUser,
    login, logout, register, updateUser, setError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Custom Hook ───────────────────────────────────────────────────────────────
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}

export default AuthContext;
