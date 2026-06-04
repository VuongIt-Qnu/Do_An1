/**
 * RegisterPage — Trang đăng ký tài khoản mới
 */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';

export default function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    full_name: '', email: '', phone_number: '', password: '', confirm_password: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const validate = () => {
    const errs = {};
    if (!form.full_name.trim()) errs.full_name = 'Họ tên là bắt buộc';
    if (!form.email || !/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Email không hợp lệ';
    if (!form.phone_number.trim()) errs.phone_number = 'Số điện thoại là bắt buộc';
    if (!form.password || form.password.length < 6) errs.password = 'Mật khẩu tối thiểu 6 ký tự';
    if (form.password !== form.confirm_password) errs.confirm_password = 'Mật khẩu không khớp';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        phone_number: form.phone_number,
        password: form.password,
      });
      toast.success('Đăng ký thành công! Chào mừng bạn.');
      navigate('/', { replace: true });
    } catch (err) {
      toast.error(err.response?.data?.message || 'Đăng ký thất bại');
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => {
    setForm(p => ({ ...p, [field]: e.target.value }));
    setErrors(p => ({ ...p, [field]: undefined }));
  };

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-sm-10 col-md-8 col-lg-5">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5">
                {/* Logo */}
                <div className="text-center mb-4">
                  <Link to="/" className="text-decoration-none">
                    <h3 className="fw-bold">
                      <i className="bi bi-building me-2 text-warning"></i>
                      <span className="text-warning">Hotel</span>MS
                    </h3>
                  </Link>
                  <h5 className="text-muted fw-normal">{t('auth.registerTitle')}</h5>
                </div>

                <form onSubmit={handleSubmit} noValidate>
                  {/* Full Name */}
                  <div className="mb-3">
                    <label className="form-label fw-semibold">{t('auth.fullName')}</label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-person text-muted"></i>
                      </span>
                      <input
                        type="text"
                        className={`form-control border-start-0 ${errors.full_name ? 'is-invalid' : ''}`}
                        placeholder="Nguyễn Văn A"
                        value={form.full_name}
                        onChange={set('full_name')}
                      />
                      {errors.full_name && <div className="invalid-feedback">{errors.full_name}</div>}
                    </div>
                  </div>

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
                        placeholder="email@example.com"
                        value={form.email}
                        onChange={set('email')}
                      />
                      {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                    </div>
                  </div>

                  {/* Phone */}
                  <div className="mb-3">
                    <label className="form-label fw-semibold">{t('auth.phone')}</label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-telephone text-muted"></i>
                      </span>
                      <input
                        type="tel"
                        className={`form-control border-start-0 ${errors.phone_number ? 'is-invalid' : ''}`}
                        placeholder="0912345678"
                        value={form.phone_number}
                        onChange={set('phone_number')}
                      />
                      {errors.phone_number && <div className="invalid-feedback">{errors.phone_number}</div>}
                    </div>
                  </div>

                  {/* Password */}
                  <div className="mb-3">
                    <label className="form-label fw-semibold">{t('auth.password')}</label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-lock text-muted"></i>
                      </span>
                      <input
                        type={showPass ? 'text' : 'password'}
                        className={`form-control border-start-0 border-end-0 ${errors.password ? 'is-invalid' : ''}`}
                        placeholder="Tối thiểu 6 ký tự"
                        value={form.password}
                        onChange={set('password')}
                      />
                      <button type="button" className="input-group-text bg-light border-start-0"
                        onClick={() => setShowPass(p => !p)}>
                        <i className={`bi ${showPass ? 'bi-eye-slash' : 'bi-eye'} text-muted`}></i>
                      </button>
                      {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div className="mb-4">
                    <label className="form-label fw-semibold">{t('auth.confirmPassword')}</label>
                    <input
                      type="password"
                      className={`form-control ${errors.confirm_password ? 'is-invalid' : ''}`}
                      placeholder="Nhập lại mật khẩu"
                      value={form.confirm_password}
                      onChange={set('confirm_password')}
                    />
                    {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
                  </div>

                  <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold" disabled={loading}>
                    {loading ? (
                      <><span className="spinner-border spinner-border-sm me-2"></span>Đang tạo tài khoản...</>
                    ) : (
                      <><i className="bi bi-person-plus me-2"></i>{t('auth.registerBtn')}</>
                    )}
                  </button>
                </form>

                <p className="text-center text-muted mt-4 mb-0 small">
                  {t('auth.haveAccount')}{' '}
                  <Link to="/login" className="text-primary fw-semibold text-decoration-none">
                    {t('auth.loginBtn')}
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
