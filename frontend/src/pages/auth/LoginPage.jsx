/**
 * LoginPage
 * Email + password login form with validation.
 */
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Redirect to the page user was trying to visit, or home
  const from = location.state?.from?.pathname || '/';

  const validate = () => {
    const errs = {};
    if (!form.email || !/\S+@\S+\.\S+/.test(form.email))
      errs.email = 'Email không hợp lệ';
    if (!form.password || form.password.length < 6)
      errs.password = 'Mật khẩu tối thiểu 6 ký tự';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      const { user } = await login(form.email, form.password);

      toast.success(`Chào mừng, ${user.full_name}!`);

      // Redirect based on role
      if (user.role === 'ADMIN') navigate('/admin', { replace: true });
      else if (user.role === 'OWNER') navigate('/owner', { replace: true });
      else navigate(from, { replace: true });
    } catch (err) {
      const msg = err.response?.data?.message || 'Đăng nhập thất bại';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-sm-10 col-md-7 col-lg-5">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                {/* Logo */}
                <div className="text-center mb-4">
                  <Link to="/" className="text-decoration-none">
                    <h3 className="fw-bold text-dark">
                      <i className="bi bi-building me-2 text-warning"></i>
                      <span className="text-warning">Hotel</span>MS
                    </h3>
                  </Link>
                  <h5 className="text-muted mt-2 fw-normal">{t('auth.loginTitle')}</h5>
                </div>

                <form onSubmit={handleSubmit} noValidate>
                  {/* Email */}
                  <div className="mb-3">
                    <label className="form-label fw-semibold">{t('auth.email')}</label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-envelope text-muted"></i>
                      </span>
                      <input
                        type="email"
                        className={`form-control border-start-0 ${errors.email ? 'is-invalid' : ''}`}
                        placeholder="example@email.com"
                        value={form.email}
                        onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                        autoComplete="email"
                      />
                      {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                    </div>
                  </div>

                  {/* Password */}
                  <div className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <label className="form-label fw-semibold mb-0">{t('auth.password')}</label>
                      <Link to="/forgot-password" className="text-sm text-primary text-decoration-none small">
                        {t('auth.forgotPassword')}
                      </Link>
                    </div>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-lock text-muted"></i>
                      </span>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        className={`form-control border-start-0 border-end-0 ${errors.password ? 'is-invalid' : ''}`}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                        autoComplete="current-password"
                      />
                      <button
                        type="button"
                        className="input-group-text bg-light border-start-0"
                        onClick={() => setShowPassword(p => !p)}
                      >
                        <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'} text-muted`}></i>
                      </button>
                      {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                    </div>
                  </div>

                  {/* Submit */}
                  <button
                    type="submit"
                    className="btn btn-primary w-100 py-2 fw-semibold mt-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <><span className="spinner-border spinner-border-sm me-2"></span>Đang đăng nhập...</>
                    ) : (
                      <><i className="bi bi-box-arrow-in-right me-2"></i>{t('auth.loginBtn')}</>
                    )}
                  </button>
                </form>

                {/* Register Link */}
                <p className="text-center text-muted mt-4 mb-0 small">
                  {t('auth.noAccount')}{' '}
                  <Link to="/register" className="text-primary fw-semibold text-decoration-none">
                    {t('auth.registerBtn')}
                  </Link>
                </p>
              </div>
            </div>

            {/* Demo credentials */}
            <div className="card border-0 bg-info bg-opacity-10 mt-3">
              <div className="card-body py-2 px-3">
                <small className="text-muted fw-semibold d-block mb-1">
                  <i className="bi bi-info-circle me-1"></i>Demo Credentials
                </small>
                <small className="text-muted d-block">Admin: admin@hotel.com / Admin@123</small>
                <small className="text-muted d-block">Owner: owner1@hotel.com / Owner@123</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
