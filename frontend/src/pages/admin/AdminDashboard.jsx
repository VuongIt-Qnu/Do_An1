/**
 * AdminDashboard
 * Routes: /admin, /admin/bookings, /admin/users, /admin/hotels, /admin/reports
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import api from '../../services/api';
import { bookingService } from '../../services/bookingService';
import LoadingSpinner from '../../components/LoadingSpinner';

const VND = (v) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(v ?? 0);
const STATUS_COLOR = { PENDING: 'warning', CONFIRMED: 'success', CANCELLED: 'danger', COMPLETED: 'secondary' };

// ── Sidebar ───────────────────────────────────────────────────────────────────
function AdminSidebar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const links = [
    { to: '/admin',          label: t('admin.dashboard'),      icon: 'bi-grid-1x2-fill',     end: true },
    { to: '/admin/bookings', label: t('admin.manageBookings'), icon: 'bi-calendar-check-fill' },
    { to: '/admin/users',    label: t('admin.manageUsers'),    icon: 'bi-people-fill' },
    { to: '/admin/hotels',   label: t('admin.manageHotels'),   icon: 'bi-building-fill' },
    { to: '/admin/reports',  label: t('admin.reports'),        icon: 'bi-bar-chart-fill' },
  ];

  return (
    <div className="bg-dark text-white d-flex flex-column" style={{ width: '240px', minHeight: '100vh' }}>
      <div className="p-3 border-bottom border-secondary">
        <span className="fw-bold">
          <i className="bi bi-shield-fill-check text-warning me-2"></i>Admin Panel
        </span>
      </div>
      <nav className="flex-grow-1 py-2">
        {links.map(link => (
          <NavLink key={link.to} to={link.to} end={link.end}
            className={({ isActive }) =>
              `d-flex align-items-center gap-2 px-3 py-2 text-decoration-none small fw-semibold
               ${isActive ? 'bg-primary text-white' : 'text-light opacity-75'}`}>
            <i className={`bi ${link.icon}`}></i>{link.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-top border-secondary">
        <button className="btn btn-outline-danger btn-sm w-100" onClick={() => navigate('/')}>
          <i className="bi bi-arrow-left me-1"></i>Về trang chủ
        </button>
      </div>
    </div>
  );
}

// ── Overview ──────────────────────────────────────────────────────────────────
function AdminOverview() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/admin/dashboard'),
      bookingService.getAllBookings({ per_page: 8 }),
    ]).then(([statsRes, bookingsRes]) => {
      setStats(statsRes.data);
      setRecentBookings(bookingsRes.items || []);
    }).catch(() => toast.error('Không thể tải dữ liệu'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const cards = [
    { label: t('admin.totalBookings'), value: stats?.total_bookings ?? 0,   icon: 'bi-calendar-check', color: 'primary' },
    { label: t('admin.totalRevenue'),  value: VND(stats?.total_revenue),     icon: 'bi-currency-dollar', color: 'success' },
    { label: t('admin.totalUsers'),    value: stats?.total_users ?? 0,       icon: 'bi-people',          color: 'info' },
    { label: t('admin.totalRooms'),    value: stats?.total_rooms ?? 0,       icon: 'bi-door-open',       color: 'warning' },
  ];

  return (
    <div>
      <h4 className="fw-bold mb-4">{t('admin.dashboard')}</h4>
      <div className="row g-3 mb-4">
        {cards.map((c, i) => (
          <div key={i} className="col-sm-6 col-xl-3">
            <div className="card border-0 shadow-sm">
              <div className="card-body d-flex align-items-center gap-3">
                <div className={`bg-${c.color} bg-opacity-15 rounded-3 p-3`}>
                  <i className={`bi ${c.icon} fs-4 text-${c.color}`}></i>
                </div>
                <div>
                  <div className="text-muted small">{c.label}</div>
                  <div className="fw-bold fs-5">{c.value}</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card border-0 shadow-sm">
        <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
          <h6 className="fw-bold mb-0">{t('admin.recentBookings')}</h6>
          <NavLink to="/admin/bookings" className="btn btn-sm btn-outline-primary">Xem tất cả</NavLink>
        </div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th className="ps-3">Mã</th><th>Khách hàng</th><th>Phòng</th>
                  <th>Check-in</th><th>Tổng tiền</th><th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {recentBookings.map(b => (
                  <tr key={b.id}>
                    <td className="ps-3 text-muted small">#{b.id}</td>
                    <td><div className="fw-semibold small">{b.customer_name}</div>
                      <div className="text-muted" style={{ fontSize: '0.72rem' }}>{b.customer_email}</div></td>
                    <td className="small">{b.room_name || b.hotel_name}</td>
                    <td className="small">{b.check_in}</td>
                    <td className="small fw-semibold">{VND(b.total_price)}</td>
                    <td><span className={`badge bg-${STATUS_COLOR[b.status] || 'light'} text-dark`}>{b.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Booking Management ────────────────────────────────────────────────────────
function BookingManagement() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({});

  const fetchBookings = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 15 };
      if (statusFilter) params.status = statusFilter;
      const data = await bookingService.getAllBookings(params);
      setBookings(data.items || []);
      setMeta(data.meta || {});
    } catch { toast.error('Lỗi tải dữ liệu'); }
    finally { setLoading(false); }
  }, [page, statusFilter]);

  useEffect(() => { fetchBookings(); }, [fetchBookings]);

  const handleConfirm = async (id) => {
    try {
      await bookingService.confirmBooking(id);
      toast.success('Đã xác nhận booking');
      fetchBookings();
    } catch { toast.error('Lỗi xác nhận'); }
  };

  const handleComplete = async (id) => {
    try {
      await bookingService.completeBooking(id);
      toast.success('Đã hoàn tất booking');
      fetchBookings();
    } catch { toast.error('Lỗi cập nhật'); }
  };

  const handleCancel = async (id) => {
    if (!window.confirm('Huỷ booking này?')) return;
    try {
      await bookingService.cancelBooking(id, 'Admin huỷ');
      toast.success('Đã huỷ booking');
      fetchBookings();
    } catch { toast.error('Lỗi huỷ booking'); }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Quản lý Đặt phòng</h4>
        <select className="form-select form-select-sm w-auto" value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">Tất cả trạng thái</option>
          {['PENDING','CONFIRMED','COMPLETED','CANCELLED'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {loading ? <LoadingSpinner /> : (
        <>
          <div className="card border-0 shadow-sm">
            <div className="table-responsive">
              <table className="table table-hover mb-0 align-middle">
                <thead className="table-light">
                  <tr>
                    <th className="ps-3">ID</th><th>Khách hàng</th><th>Phòng / Khách sạn</th>
                    <th>Check-in → Check-out</th><th>Tổng</th><th>Trạng thái</th><th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td className="ps-3 text-muted small">#{b.id}</td>
                      <td><div className="fw-semibold small">{b.customer_name}</div>
                        <div className="text-muted" style={{ fontSize: '0.72rem' }}>{b.customer_email}</div></td>
                      <td className="small">{b.room_name || b.hotel_name}</td>
                      <td className="small">{b.check_in} → {b.check_out}
                        <div className="text-muted" style={{ fontSize: '0.7rem' }}>{b.nights} đêm</div></td>
                      <td className="small fw-semibold">{VND(b.total_price)}</td>
                      <td><span className={`badge bg-${STATUS_COLOR[b.status] || 'light'} text-dark`}>{b.status}</span></td>
                      <td>
                        <div className="d-flex gap-1">
                          {b.status === 'PENDING' && (
                            <button className="btn btn-success btn-sm" onClick={() => handleConfirm(b.id)}>
                              <i className="bi bi-check"></i>
                            </button>
                          )}
                          {b.status === 'CONFIRMED' && (
                            <button className="btn btn-primary btn-sm" onClick={() => handleComplete(b.id)}>
                              <i className="bi bi-check-all"></i>
                            </button>
                          )}
                          {['PENDING','CONFIRMED'].includes(b.status) && (
                            <button className="btn btn-outline-danger btn-sm" onClick={() => handleCancel(b.id)}>
                              <i className="bi bi-x"></i>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="d-flex justify-content-between align-items-center mt-3">
            <span className="text-muted small">Tổng: {meta.total || 0} booking</span>
            <div className="d-flex gap-1">
              <button className="btn btn-sm btn-outline-secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>‹</button>
              <span className="btn btn-sm btn-light disabled">{page} / {meta.total_pages || 1}</span>
              <button className="btn btn-sm btn-outline-secondary" disabled={page >= (meta.total_pages || 1)} onClick={() => setPage(p => p + 1)}>›</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── User Management ───────────────────────────────────────────────────────────
function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({});

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 15 };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      const res = await api.get('/api/admin/users', { params });
      setUsers(res.items || []);
      setMeta(res.meta || {});
    } catch { toast.error('Lỗi tải danh sách người dùng'); }
    finally { setLoading(false); }
  }, [page, roleFilter, search]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleToggle = async (userId) => {
    try {
      await api.patch(`/api/admin/users/${userId}/toggle`);
      toast.success('Đã cập nhật trạng thái tài khoản');
      fetchUsers();
    } catch { toast.error('Lỗi cập nhật tài khoản'); }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.put(`/api/admin/users/${userId}`, { role: newRole });
      toast.success('Đã đổi vai trò');
      fetchUsers();
    } catch { toast.error('Lỗi đổi vai trò'); }
  };

  const ROLE_COLOR = { ADMIN: 'danger', OWNER: 'info', USER: 'secondary' };

  return (
    <div>
      <h4 className="fw-bold mb-4">Quản lý Người dùng</h4>

      {/* Filters */}
      <div className="d-flex gap-2 mb-3 flex-wrap">
        <input className="form-control form-control-sm" style={{ maxWidth: 260 }}
          placeholder="Tìm tên / email..." value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && fetchUsers()} />
        <select className="form-select form-select-sm w-auto" value={roleFilter}
          onChange={e => { setRoleFilter(e.target.value); setPage(1); }}>
          <option value="">Tất cả vai trò</option>
          <option value="USER">USER</option>
          <option value="OWNER">OWNER</option>
          <option value="ADMIN">ADMIN</option>
        </select>
        <button className="btn btn-primary btn-sm" onClick={() => { setPage(1); fetchUsers(); }}>
          <i className="bi bi-search me-1"></i>Tìm
        </button>
      </div>

      {loading ? <LoadingSpinner /> : (
        <>
          <div className="card border-0 shadow-sm">
            <div className="table-responsive">
              <table className="table table-hover mb-0 align-middle">
                <thead className="table-light">
                  <tr>
                    <th className="ps-3">ID</th><th>Họ tên</th><th>Email</th>
                    <th>Vai trò</th><th>Trạng thái</th><th>Ngày tạo</th><th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td className="ps-3 text-muted small">{u.id}</td>
                      <td className="fw-semibold small">{u.full_name}</td>
                      <td className="small text-muted">{u.email}</td>
                      <td>
                        <select className={`form-select form-select-sm w-auto border-0 bg-${ROLE_COLOR[u.role]}-subtle`}
                          value={u.role}
                          onChange={e => handleRoleChange(u.id, e.target.value)}>
                          <option value="USER">USER</option>
                          <option value="OWNER">OWNER</option>
                          <option value="ADMIN">ADMIN</option>
                        </select>
                      </td>
                      <td>
                        <span className={`badge ${u.enabled ? 'bg-success' : 'bg-danger'}`}>
                          {u.enabled ? 'Hoạt động' : 'Bị khoá'}
                        </span>
                      </td>
                      <td className="small text-muted">{u.created_at?.slice(0, 10)}</td>
                      <td>
                        <button
                          className={`btn btn-sm ${u.enabled ? 'btn-outline-danger' : 'btn-outline-success'}`}
                          onClick={() => handleToggle(u.id)}>
                          <i className={`bi bi-${u.enabled ? 'lock' : 'unlock'}`}></i>
                          {u.enabled ? ' Khoá' : ' Mở'}
                        </button>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && (
                    <tr><td colSpan={7} className="text-center text-muted py-4">Không tìm thấy người dùng</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          <div className="d-flex justify-content-between align-items-center mt-3">
            <span className="text-muted small">Tổng: {meta.total || 0} người dùng</span>
            <div className="d-flex gap-1">
              <button className="btn btn-sm btn-outline-secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>‹</button>
              <span className="btn btn-sm btn-light disabled">{page} / {meta.total_pages || 1}</span>
              <button className="btn btn-sm btn-outline-secondary" disabled={page >= (meta.total_pages || 1)} onClick={() => setPage(p => p + 1)}>›</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── Hotel Management (Admin) ──────────────────────────────────────────────────
function HotelManagement() {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [approvedFilter, setApprovedFilter] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({});

  const fetchHotels = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 15 };
      if (search) params.search = search;
      if (approvedFilter !== '') params.approved = approvedFilter;
      const res = await api.get('/api/admin/hotels', { params });
      setHotels(res.items || []);
      setMeta(res.meta || {});
    } catch { toast.error('Lỗi tải danh sách khách sạn'); }
    finally { setLoading(false); }
  }, [page, approvedFilter, search]);

  useEffect(() => { fetchHotels(); }, [fetchHotels]);

  const handleApprove = async (hotelId, approved) => {
    try {
      await api.patch(`/api/admin/hotels/${hotelId}/approve`, { approved });
      toast.success(approved ? 'Đã duyệt khách sạn' : 'Đã từ chối khách sạn');
      fetchHotels();
    } catch { toast.error('Lỗi cập nhật'); }
  };

  const handleToggleEnabled = async (hotelId, currentEnabled) => {
    try {
      await api.put(`/api/admin/hotels/${hotelId}`, { enabled: !currentEnabled });
      toast.success(currentEnabled ? 'Đã vô hiệu hoá khách sạn' : 'Đã kích hoạt khách sạn');
      fetchHotels();
    } catch { toast.error('Lỗi cập nhật'); }
  };

  return (
    <div>
      <h4 className="fw-bold mb-4">Quản lý Khách sạn</h4>

      <div className="d-flex gap-2 mb-3 flex-wrap">
        <input className="form-control form-control-sm" style={{ maxWidth: 260 }}
          placeholder="Tìm tên / thành phố..." value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && fetchHotels()} />
        <select className="form-select form-select-sm w-auto" value={approvedFilter}
          onChange={e => { setApprovedFilter(e.target.value); setPage(1); }}>
          <option value="">Tất cả trạng thái</option>
          <option value="false">Chờ duyệt</option>
          <option value="true">Đã duyệt</option>
        </select>
        <button className="btn btn-primary btn-sm" onClick={() => { setPage(1); fetchHotels(); }}>
          <i className="bi bi-search me-1"></i>Tìm
        </button>
      </div>

      {loading ? <LoadingSpinner /> : (
        <>
          <div className="card border-0 shadow-sm">
            <div className="table-responsive">
              <table className="table table-hover mb-0 align-middle">
                <thead className="table-light">
                  <tr>
                    <th className="ps-3">ID</th><th>Tên khách sạn</th><th>Thành phố</th>
                    <th>Sao</th><th>Duyệt</th><th>Hoạt động</th><th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {hotels.map(h => (
                    <tr key={h.id}>
                      <td className="ps-3 text-muted small">{h.id}</td>
                      <td className="fw-semibold small">{h.name}</td>
                      <td className="small text-muted">{h.city}</td>
                      <td className="small">{'★'.repeat(h.star_rating || 0)}</td>
                      <td>
                        <span className={`badge ${h.approved ? 'bg-success' : 'bg-warning text-dark'}`}>
                          {h.approved ? 'Đã duyệt' : 'Chờ duyệt'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${h.enabled ? 'bg-success' : 'bg-secondary'}`}>
                          {h.enabled ? 'Bật' : 'Tắt'}
                        </span>
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          {!h.approved && (
                            <button className="btn btn-success btn-sm" onClick={() => handleApprove(h.id, true)}>
                              <i className="bi bi-check me-1"></i>Duyệt
                            </button>
                          )}
                          {h.approved && (
                            <button className="btn btn-outline-warning btn-sm" onClick={() => handleApprove(h.id, false)}>
                              <i className="bi bi-x me-1"></i>Thu hồi
                            </button>
                          )}
                          <button
                            className={`btn btn-sm ${h.enabled ? 'btn-outline-secondary' : 'btn-outline-success'}`}
                            onClick={() => handleToggleEnabled(h.id, h.enabled)}>
                            {h.enabled ? 'Ẩn' : 'Hiện'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {hotels.length === 0 && (
                    <tr><td colSpan={7} className="text-center text-muted py-4">Không tìm thấy khách sạn</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          <div className="d-flex justify-content-between align-items-center mt-3">
            <span className="text-muted small">Tổng: {meta.total || 0} khách sạn</span>
            <div className="d-flex gap-1">
              <button className="btn btn-sm btn-outline-secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>‹</button>
              <span className="btn btn-sm btn-light disabled">{page} / {meta.total_pages || 1}</span>
              <button className="btn btn-sm btn-outline-secondary" disabled={page >= (meta.total_pages || 1)} onClick={() => setPage(p => p + 1)}>›</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── Reports ───────────────────────────────────────────────────────────────────
function Reports() {
  const [stats, setStats] = useState(null);
  const [payStats, setPayStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/admin/dashboard'),
      api.get('/api/payments/stats'),
    ]).then(([dashRes, payRes]) => {
      setStats(dashRes.data);
      setPayStats(payRes.data || payRes);
    }).catch(() => toast.error('Lỗi tải báo cáo'))
      .finally(() => setLoading(false));
  }, []);

  const handleExport = async (type) => {
    try {
      const res = await api.get(`/api/reports/export/${type}`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res]));
      const a = document.createElement('a');
      a.href = url; a.download = `report.${type === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click(); URL.revokeObjectURL(url);
    } catch { toast.error('Lỗi xuất file'); }
  };

  if (loading) return <LoadingSpinner />;

  const rows = [
    { label: 'Tổng booking',        value: stats?.total_bookings ?? 0 },
    { label: 'Booking hoàn thành',  value: stats?.completed_bookings ?? 0 },
    { label: 'Booking đang chờ',    value: stats?.pending_bookings ?? 0 },
    { label: 'Booking đã huỷ',      value: stats?.cancelled_bookings ?? 0 },
    { label: 'Tổng người dùng',     value: stats?.total_users ?? 0 },
    { label: 'Tổng khách sạn',      value: stats?.total_hotels ?? 0 },
    { label: 'Tổng phòng',          value: stats?.total_rooms ?? 0 },
    { label: 'Doanh thu đã thu',    value: VND(payStats?.total_paid_amount) },
    { label: 'Đã hoàn tiền',        value: VND(payStats?.total_refunded_amount) },
    { label: 'Doanh thu thuần',     value: VND(payStats?.net_revenue) },
  ];

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Báo cáo Doanh thu</h4>
        <div className="d-flex gap-2">
          <button className="btn btn-outline-success btn-sm" onClick={() => handleExport('excel')}>
            <i className="bi bi-file-earmark-excel me-1"></i>Xuất Excel
          </button>
          <button className="btn btn-outline-danger btn-sm" onClick={() => handleExport('pdf')}>
            <i className="bi bi-file-earmark-pdf me-1"></i>Xuất PDF
          </button>
        </div>
      </div>

      <div className="row g-3">
        {rows.map((r, i) => (
          <div key={i} className="col-md-6 col-xl-4">
            <div className="card border-0 shadow-sm">
              <div className="card-body">
                <div className="text-muted small mb-1">{r.label}</div>
                <div className="fw-bold fs-5">{r.value}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {payStats?.by_method && (
        <div className="card border-0 shadow-sm mt-4">
          <div className="card-header bg-white border-0 py-3">
            <h6 className="fw-bold mb-0">Phương thức thanh toán</h6>
          </div>
          <div className="card-body">
            <div className="row g-3">
              {Object.entries(payStats.by_method).map(([method, count]) => (
                <div key={method} className="col-sm-3 text-center">
                  <div className="fw-bold fs-4">{count}</div>
                  <div className="text-muted small text-uppercase">{method.replace('_', ' ')}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main AdminDashboard ───────────────────────────────────────────────────────
export default function AdminDashboard() {
  return (
    <div className="d-flex" style={{ minHeight: 'calc(100vh - 56px)' }}>
      <AdminSidebar />
      <main className="flex-grow-1 bg-light p-4 overflow-auto">
        <Routes>
          <Route index element={<AdminOverview />} />
          <Route path="bookings" element={<BookingManagement />} />
          <Route path="users"    element={<UserManagement />} />
          <Route path="hotels"   element={<HotelManagement />} />
          <Route path="reports"  element={<Reports />} />
        </Routes>
      </main>
    </div>
  );
}
