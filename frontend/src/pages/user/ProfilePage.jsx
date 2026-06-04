/**
 * ProfilePage — View & edit current user's profile + change password
 */
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';

const INPUT = 'form-control';
const ERR   = 'invalid-feedback';

export default function ProfilePage() {
  const { user, updateUser } = useAuth();

  // ── Profile form ──────────────────────────────────────────────────────────
  const [profile, setProfile] = useState({
    full_name:    user?.full_name    || '',
    phone_number: user?.phone_number || '',
    passport:     user?.passport     || '',
    nationality:  user?.nationality  || '',
    address:      user?.address      || '',
  });
  const [profileSaving, setProfileSaving] = useState(false);

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setProfileSaving(true);
    try {
      const res  = await authService.updateProfile(profile);
      const updated = res?.data?.user || res?.user || res;
      updateUser(updated);
      toast.success('Cập nhật hồ sơ thành công!');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi cập nhật hồ sơ');
    } finally {
      setProfileSaving(false);
    }
  };

  // ── Password form ─────────────────────────────────────────────────────────
  const [pw, setPw] = useState({ current_password: '', new_password: '', confirm: '' });
  const [pwErrors, setPwErrors] = useState({});
  const [pwSaving, setPwSaving] = useState(false);

  const validatePw = () => {
    const errs = {};
    if (!pw.current_password) errs.current_password = 'Nhập mật khẩu hiện tại';
    if (!pw.new_password || pw.new_password.length < 6) errs.new_password = 'Tối thiểu 6 ký tự';
    if (pw.new_password !== pw.confirm) errs.confirm = 'Mật khẩu xác nhận không khớp';
    return errs;
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    const errs = validatePw();
    setPwErrors(errs);
    if (Object.keys(errs).length > 0) return;
    setPwSaving(true);
    try {
      await authService.changePassword(pw.current_password, pw.new_password);
      toast.success('Đổi mật khẩu thành công!');
      setPw({ current_password: '', new_password: '', confirm: '' });
      setPwErrors({});
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi đổi mật khẩu');
    } finally {
      setPwSaving(false);
    }
  };

  const ROLE_LABEL = { ADMIN: 'Quản trị viên', OWNER: 'Chủ khách sạn', USER: 'Khách hàng' };
  const ROLE_COLOR = { ADMIN: 'danger', OWNER: 'info', USER: 'primary' };

  return (
    <div className="py-4 bg-light min-vh-100">
      <div className="container" style={{ maxWidth: 760 }}>
        <h3 className="fw-bold mb-4">Hồ sơ cá nhân</h3>

        <div className="row g-4">
          {/* ── LEFT: Account summary ────────────────────────────────── */}
          <div className="col-md-4">
            <div className="card border-0 shadow-sm text-center p-4">
              <div className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mx-auto mb-3"
                style={{ width: 80, height: 80, fontSize: 32 }}>
                {user?.full_name?.[0]?.toUpperCase() || '?'}
              </div>
              <h5 className="fw-bold mb-1">{user?.full_name}</h5>
              <p className="text-muted small mb-2">{user?.email}</p>
              <span className={`badge bg-${ROLE_COLOR[user?.role] || 'secondary'}`}>
                {ROLE_LABEL[user?.role] || user?.role}
              </span>
              {user?.phone_number && (
                <p className="text-muted small mt-3 mb-0">
                  <i className="bi bi-telephone me-1"></i>{user.phone_number}
                </p>
              )}
            </div>
          </div>

          {/* ── RIGHT: Forms ─────────────────────────────────────────── */}
          <div className="col-md-8">

            {/* Profile form */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-person-gear text-primary me-2"></i>Thông tin cá nhân
                </h6>
                <form onSubmit={handleProfileSave}>
                  <div className="row g-3">
                    <div className="col-12">
                      <label className="form-label small fw-semibold">Họ và tên</label>
                      <input className={INPUT} value={profile.full_name}
                        onChange={e => setProfile(p => ({ ...p, full_name: e.target.value }))} />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small fw-semibold">Email</label>
                      <input className={`${INPUT} bg-light`} value={user?.email || ''} readOnly />
                      <div className="form-text">Email không thể thay đổi</div>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small fw-semibold">Số điện thoại</label>
                      <input className={INPUT} value={profile.phone_number}
                        onChange={e => setProfile(p => ({ ...p, phone_number: e.target.value }))} />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small fw-semibold">Số hộ chiếu</label>
                      <input className={INPUT} value={profile.passport} placeholder="Tùy chọn"
                        onChange={e => setProfile(p => ({ ...p, passport: e.target.value }))} />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small fw-semibold">Quốc tịch</label>
                      <input className={INPUT} value={profile.nationality} placeholder="Tùy chọn"
                        onChange={e => setProfile(p => ({ ...p, nationality: e.target.value }))} />
                    </div>
                    <div className="col-12">
                      <label className="form-label small fw-semibold">Địa chỉ</label>
                      <input className={INPUT} value={profile.address} placeholder="Tùy chọn"
                        onChange={e => setProfile(p => ({ ...p, address: e.target.value }))} />
                    </div>
                    <div className="col-12">
                      <button type="submit" className="btn btn-primary"
                        disabled={profileSaving}>
                        {profileSaving
                          ? <><span className="spinner-border spinner-border-sm me-2"></span>Đang lưu...</>
                          : <><i className="bi bi-check2 me-1"></i>Lưu thay đổi</>}
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>

            {/* Password form */}
            <div className="card border-0 shadow-sm">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-lock text-primary me-2"></i>Đổi mật khẩu
                </h6>
                <form onSubmit={handlePasswordChange}>
                  <div className="row g-3">
                    {[
                      { field: 'current_password', label: 'Mật khẩu hiện tại' },
                      { field: 'new_password',     label: 'Mật khẩu mới (tối thiểu 6 ký tự)' },
                      { field: 'confirm',          label: 'Xác nhận mật khẩu mới' },
                    ].map(({ field, label }) => (
                      <div key={field} className="col-12">
                        <label className="form-label small fw-semibold">{label}</label>
                        <input
                          type="password"
                          className={`${INPUT} ${pwErrors[field] ? 'is-invalid' : ''}`}
                          value={pw[field]}
                          onChange={e => {
                            setPw(p => ({ ...p, [field]: e.target.value }));
                            setPwErrors(p => ({ ...p, [field]: undefined }));
                          }}
                        />
                        {pwErrors[field] && <div className={ERR}>{pwErrors[field]}</div>}
                      </div>
                    ))}
                    <div className="col-12">
                      <button type="submit" className="btn btn-outline-warning"
                        disabled={pwSaving}>
                        {pwSaving
                          ? <><span className="spinner-border spinner-border-sm me-2"></span>Đang xử lý...</>
                          : <><i className="bi bi-key me-1"></i>Đổi mật khẩu</>}
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
