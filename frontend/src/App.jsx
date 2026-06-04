/**
 * App.jsx — Root Component
 * Defines routing structure with role-based route guards.
 *
 * Route Structure:
 * /                     → HomePage (public)
 * /rooms                → RoomsPage (public)
 * /rooms/:id            → RoomDetailPage (public)
 * /rooms/:id/book       → BookingPage (requires auth)
 * /my-bookings          → MyBookingsPage (requires auth)
 * /profile              → ProfilePage (requires auth)
 * /login                → LoginPage (public, redirect if logged in)
 * /register             → RegisterPage (public, redirect if logged in)
 * /forgot-password      → ForgotPasswordPage (public)
 * /reset-password       → ResetPasswordPage (public)
 * /admin/*              → AdminDashboard (requires ADMIN role)
 * /owner/*              → OwnerDashboard (requires OWNER role)
 */
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';

import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LoadingSpinner from './components/LoadingSpinner';

// ── Lazy-loaded Pages (code splitting for performance) ────────────────────────
const HomePage       = lazy(() => import('./pages/user/HomePage'));
const RoomsPage      = lazy(() => import('./pages/user/RoomsPage'));
const RoomDetailPage = lazy(() => import('./pages/user/RoomDetailPage'));
const BookingPage    = lazy(() => import('./pages/user/BookingPage'));
const MyBookingsPage    = lazy(() => import('./pages/user/MyBookingsPage'));
const BookingDetailPage = lazy(() => import('./pages/user/BookingDetailPage'));
const ProfilePage    = lazy(() => import('./pages/user/ProfilePage'));

const LoginPage          = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage       = lazy(() => import('./pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('./pages/auth/ForgotPasswordPage'));
const ResetPasswordPage  = lazy(() => import('./pages/auth/ResetPasswordPage'));

const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const OwnerDashboard = lazy(() => import('./pages/owner/OwnerDashboard'));

const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// ── Route Guards ──────────────────────────────────────────────────────────────

/** Redirect to login if not authenticated */
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

/** Redirect to home if already authenticated */
function PublicOnlyRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return children;
}

/** Require specific role */
function RoleRoute({ role, children }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to="/" replace />;
  return children;
}

// ── App Component ─────────────────────────────────────────────────────────────
function AppRoutes() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />

      <main className="flex-grow-1">
        <Suspense fallback={<LoadingSpinner fullPage />}>
          <Routes>
            {/* ── Public Routes ── */}
            <Route path="/" element={<HomePage />} />
            <Route path="/rooms" element={<RoomsPage />} />
            <Route path="/rooms/:id" element={<RoomDetailPage />} />

            {/* ── Auth Routes (redirect if already logged in) ── */}
            <Route path="/login" element={
              <PublicOnlyRoute><LoginPage /></PublicOnlyRoute>
            } />
            <Route path="/register" element={
              <PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>
            } />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />

            {/* ── Protected Routes (any authenticated user) ── */}
            <Route path="/rooms/:id/book" element={
              <ProtectedRoute><BookingPage /></ProtectedRoute>
            } />
            <Route path="/my-bookings" element={
              <ProtectedRoute><MyBookingsPage /></ProtectedRoute>
            } />
            <Route path="/my-bookings/:id" element={
              <ProtectedRoute><BookingDetailPage /></ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute><ProfilePage /></ProtectedRoute>
            } />

            {/* ── Admin Routes ── */}
            <Route path="/admin/*" element={
              <RoleRoute role="ADMIN"><AdminDashboard /></RoleRoute>
            } />

            {/* ── Owner Routes ── */}
            <Route path="/owner/*" element={
              <RoleRoute role="OWNER"><OwnerDashboard /></RoleRoute>
            } />

            {/* ── 404 ── */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </main>

      <Footer />

      {/* Global toast notifications */}
      <ToastContainer
        position="top-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnHover
        draggable
      />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,       // Tắt warning React Router v7
        v7_relativeSplatPath: true,     // Tắt warning splat route v7
      }}
    >
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
