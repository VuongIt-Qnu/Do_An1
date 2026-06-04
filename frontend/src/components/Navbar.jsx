/**
 * Navbar Component
 * React-controlled dropdown (no Bootstrap JS dependency).
 */
import React, { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';

// React-controlled dropdown — không phụ thuộc Bootstrap JS
function UserMenu({ user, isAdmin, isOwner, onLogout }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Đóng menu khi click ra ngoài
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const displayName = user?.full_name?.split(' ').slice(-1)[0] || 'User';

  return (
    <div className="position-relative" ref={ref}>
      <button
        className="btn btn-outline-light btn-sm d-flex align-items-center gap-1"
        onClick={() => setOpen(v => !v)}
      >
        <i className="bi bi-person-circle"></i>
        <span>{displayName}</span>
        {isAdmin && <span className="badge bg-warning text-dark">Admin</span>}
        {isOwner && <span className="badge bg-info text-dark">Owner</span>}
        <i className={`bi bi-chevron-${open ? 'up' : 'down'} ms-1`} style={{ fontSize: '0.65rem' }}></i>
      </button>

      {open && (
        <ul className="dropdown-menu dropdown-menu-end show shadow"
          style={{ position: 'absolute', right: 0, top: '110%', minWidth: 200, zIndex: 9999 }}>
          {/* User info header */}
          <li className="px-3 py-2 border-bottom">
            <div className="fw-semibold small">{user?.full_name}</div>
            <div className="text-muted" style={{ fontSize: '0.72rem' }}>{user?.email}</div>
          </li>

          {/* Profile */}
          <li>
            <Link className="dropdown-item d-flex align-items-center gap-2 py-2"
              to="/profile" onClick={() => setOpen(false)}>
              <i className="bi bi-person text-primary"></i>Hồ sơ cá nhân
            </Link>
          </li>

          {/* My Bookings — USER only */}
          {!isAdmin && !isOwner && (
            <li>
              <Link className="dropdown-item d-flex align-items-center gap-2 py-2"
                to="/my-bookings" onClick={() => setOpen(false)}>
                <i className="bi bi-calendar-check text-success"></i>Đặt phòng của tôi
              </Link>
            </li>
          )}

          {/* Dashboard link */}
          {isAdmin && (
            <li>
              <Link className="dropdown-item d-flex align-items-center gap-2 py-2"
                to="/admin" onClick={() => setOpen(false)}>
                <i className="bi bi-shield-check text-warning"></i>Admin Dashboard
              </Link>
            </li>
          )}
          {isOwner && (
            <li>
              <Link className="dropdown-item d-flex align-items-center gap-2 py-2"
                to="/owner" onClick={() => setOpen(false)}>
                <i className="bi bi-building-gear text-info"></i>Owner Dashboard
              </Link>
            </li>
          )}

          <li><hr className="dropdown-divider my-1" /></li>

          {/* Logout */}
          <li>
            <button
              className="dropdown-item d-flex align-items-center gap-2 py-2 text-danger fw-semibold"
              onClick={() => { setOpen(false); onLogout(); }}
            >
              <i className="bi bi-box-arrow-right"></i>Đăng xuất
            </button>
          </li>
        </ul>
      )}
    </div>
  );
}

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated, isAdmin, isOwner, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Đã đăng xuất thành công');
    navigate('/');
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'vi' ? 'en' : 'vi';
    i18n.changeLanguage(newLang);
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div className="container">
        {/* Brand */}
        <Link className="navbar-brand fw-bold fs-4" to="/">
          <i className="bi bi-building me-2 text-warning"></i>
          <span className="text-warning">Hotel</span>MS
        </Link>

        {/* Mobile Toggle */}
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
          aria-controls="navbarContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Nav Content */}
        <div className="collapse navbar-collapse" id="navbarContent">
          {/* Left Links */}
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <NavLink className="nav-link" to="/">
                <i className="bi bi-house me-1"></i>{t('nav.home')}
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/rooms">
                <i className="bi bi-door-open me-1"></i>{t('nav.rooms')}
              </NavLink>
            </li>
          </ul>

          {/* Right Links */}
          <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center gap-2">

            {/* Language Switch */}
            <li className="nav-item">
              <button
                className="btn btn-sm btn-outline-secondary text-light"
                onClick={toggleLanguage}
                title="Switch Language"
              >
                <i className="bi bi-translate me-1"></i>
                {i18n.language === 'vi' ? 'EN' : 'VI'}
              </button>
            </li>

            {/* Not authenticated */}
            {!isAuthenticated && (
              <>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/login">
                    <i className="bi bi-box-arrow-in-right me-1"></i>{t('nav.login')}
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="btn btn-warning btn-sm" to="/register">
                    {t('nav.register')}
                  </NavLink>
                </li>
              </>
            )}

            {/* Authenticated — dashboard shortcut + user menu */}
            {isAuthenticated && (
              <>
                {/* My Bookings pill (USER only — visible at glance) */}
                {!isAdmin && !isOwner && (
                  <li className="nav-item">
                    <NavLink className="nav-link" to="/my-bookings">
                      <i className="bi bi-calendar-check me-1"></i>{t('nav.myBookings')}
                    </NavLink>
                  </li>
                )}

                {/* Admin Dashboard */}
                {isAdmin && (
                  <li className="nav-item">
                    <NavLink className="nav-link text-warning" to="/admin">
                      <i className="bi bi-shield-check me-1"></i>Quản trị
                    </NavLink>
                  </li>
                )}

                {/* Owner Dashboard */}
                {isOwner && (
                  <li className="nav-item">
                    <NavLink className="nav-link text-info" to="/owner">
                      <i className="bi bi-building-gear me-1"></i>Quản lý
                    </NavLink>
                  </li>
                )}

                {/* User dropdown menu (React-controlled) */}
                <li className="nav-item">
                  <UserMenu
                    user={user}
                    isAdmin={isAdmin}
                    isOwner={isOwner}
                    onLogout={handleLogout}
                  />
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}
