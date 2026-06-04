/**
 * OwnerDashboard
 * Routes: /owner, /owner/hotels, /owner/rooms, /owner/bookings, /owner/revenue
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import api from '../../services/api';
import { bookingService } from '../../services/bookingService';
import { roomService } from '../../services/roomService';
import LoadingSpinner from '../../components/LoadingSpinner';

const VND = (v) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(v ?? 0);
const STATUS_COLOR = { PENDING: 'warning', CONFIRMED: 'success', CANCELLED: 'danger', COMPLETED: 'secondary' };

// ── Sidebar ───────────────────────────────────────────────────────────────────
function OwnerSidebar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const links = [
    { to: '/owner',          label: t('owner.dashboard'),    icon: 'bi-grid-1x2',      end: true },
    { to: '/owner/hotels',   label: t('owner.myHotels'),     icon: 'bi-building' },
    { to: '/owner/rooms',    label: t('owner.manageRooms'),  icon: 'bi-door-open' },
    { to: '/owner/bookings', label: t('owner.viewBookings'), icon: 'bi-calendar-check' },
    { to: '/owner/revenue',  label: t('owner.revenue'),      icon: 'bi-graph-up-arrow' },
  ];

  return (
    <div className="bg-dark text-white d-flex flex-column" style={{ width: '230px', minHeight: '100vh' }}>
      <div className="p-3 border-bottom border-secondary">
        <span className="fw-bold">
          <i className="bi bi-building-gear text-info me-2"></i>Owner Panel
        </span>
      </div>
      <nav className="flex-grow-1 py-2">
        {links.map(link => (
          <NavLink key={link.to} to={link.to} end={link.end}
            className={({ isActive }) =>
              `d-flex align-items-center gap-2 px-3 py-2 text-decoration-none small fw-semibold
               ${isActive ? 'bg-info text-dark' : 'text-light opacity-75'}`}>
            <i className={`bi ${link.icon}`}></i>{link.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-top border-secondary">
        <button className="btn btn-outline-secondary btn-sm w-100" onClick={() => navigate('/')}>
          <i className="bi bi-arrow-left me-1"></i>Về trang chủ
        </button>
      </div>
    </div>
  );
}

// ── Overview ──────────────────────────────────────────────────────────────────
function OwnerOverview() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/owner/dashboard'),
      api.get('/api/owner/bookings', { params: { per_page: 5 } }),
    ]).then(([statsRes, bookingsRes]) => {
      setStats(statsRes.data);
      setRecentBookings(bookingsRes.items || []);
    }).catch(() => toast.error('Không thể tải dữ liệu'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const cards = [
    { label: 'Khách sạn',          value: stats?.total_hotels ?? 0,          icon: 'bi-building',          color: 'info' },
    { label: 'Tổng phòng',         value: stats?.total_rooms ?? 0,           icon: 'bi-door-open',         color: 'primary' },
    { label: 'Booking tháng này',  value: stats?.bookings_this_month ?? 0,   icon: 'bi-calendar-check',    color: 'success' },
    { label: 'Doanh thu tháng',    value: VND(stats?.revenue_this_month),    icon: 'bi-cash-coin',         color: 'warning' },
  ];

  return (
    <div>
      <h4 className="fw-bold mb-4">Tổng quan khách sạn của tôi</h4>
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
        <div className="card-header bg-white border-0 py-3 d-flex justify-content-between">
          <h6 className="fw-bold mb-0">Đặt phòng gần đây</h6>
          <NavLink to="/owner/bookings" className="btn btn-sm btn-outline-info">Xem tất cả</NavLink>
        </div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th className="ps-3">Khách hàng</th><th>Phòng</th>
                  <th>Check-in</th><th>Tổng tiền</th><th>Trạng thái</th><th></th>
                </tr>
              </thead>
              <tbody>
                {recentBookings.map(b => (
                  <tr key={b.id}>
                    <td className="ps-3">
                      <div className="fw-semibold small">{b.customer_name}</div>
                      <div className="text-muted" style={{ fontSize: '0.72rem' }}>{b.customer_email}</div>
                    </td>
                    <td className="small">{b.room_name || '-'}</td>
                    <td className="small">{b.check_in}</td>
                    <td className="small fw-semibold">{VND(b.total_price)}</td>
                    <td>
                      <span className={`badge bg-${STATUS_COLOR[b.status]} text-dark`}>{b.status}</span>
                    </td>
                    <td>
                      {b.status === 'PENDING' && (
                        <button className="btn btn-success btn-sm"
                          onClick={async () => {
                            try { await bookingService.confirmBooking(b.id); toast.success('Đã duyệt'); }
                            catch { toast.error('Lỗi duyệt booking'); }
                          }}>Duyệt</button>
                      )}
                    </td>
                  </tr>
                ))}
                {recentBookings.length === 0 && (
                  <tr><td colSpan={6} className="text-center text-muted py-3">Chưa có booking</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Hotel Management ──────────────────────────────────────────────────────────
function HotelManagement() {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editHotel, setEditHotel] = useState(null);
  const EMPTY_FORM = { name: '', address: '', city: '', phone: '', email: '', description: '', star_rating: 3 };
  const [form, setForm] = useState(EMPTY_FORM);

  const fetchHotels = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/owner/hotels');
      setHotels(res.data?.hotels || []);
    } catch { toast.error('Lỗi tải danh sách khách sạn'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchHotels(); }, []);

  const openCreate = () => { setEditHotel(null); setForm(EMPTY_FORM); setShowForm(true); };
  const openEdit = (h) => {
    setEditHotel(h);
    setForm({ name: h.name, address: h.address || '', city: h.city || '', phone: h.phone || '', email: h.email || '', description: h.description || '', star_rating: h.star_rating || 3 });
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editHotel) {
        await api.put(`/api/hotels/${editHotel.id}`, form);
        toast.success('Đã cập nhật khách sạn');
      } else {
        await api.post('/api/hotels/', form);
        toast.success('Đã thêm khách sạn — chờ Admin duyệt');
      }
      setShowForm(false);
      setForm(EMPTY_FORM);
      setEditHotel(null);
      fetchHotels();
    } catch { toast.error(editHotel ? 'Lỗi cập nhật khách sạn' : 'Lỗi tạo khách sạn'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Xoá khách sạn này?')) return;
    try {
      await api.delete(`/api/hotels/${id}`);
      toast.success('Đã xoá khách sạn');
      fetchHotels();
    } catch { toast.error('Lỗi xoá khách sạn'); }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Khách sạn của tôi</h4>
        <button className="btn btn-info btn-sm text-white" onClick={openCreate}>
          <i className="bi bi-plus-lg me-1"></i>Thêm khách sạn
        </button>
      </div>

      {showForm && (
        <div className="card border-0 shadow-sm mb-4">
          <div className="card-body">
            <h6 className="fw-bold mb-3">{editHotel ? 'Chỉnh sửa khách sạn' : 'Thêm khách sạn mới'}</h6>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-md-6">
                  <input className="form-control" placeholder="Tên khách sạn *" required
                    value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
                </div>
                <div className="col-md-3">
                  <input className="form-control" placeholder="Thành phố"
                    value={form.city} onChange={e => setForm(p => ({ ...p, city: e.target.value }))} />
                </div>
                <div className="col-md-3">
                  <select className="form-select" value={form.star_rating}
                    onChange={e => setForm(p => ({ ...p, star_rating: Number(e.target.value) }))}>
                    {[1,2,3,4,5].map(s => <option key={s} value={s}>{s} sao</option>)}
                  </select>
                </div>
                <div className="col-12">
                  <input className="form-control" placeholder="Địa chỉ"
                    value={form.address} onChange={e => setForm(p => ({ ...p, address: e.target.value }))} />
                </div>
                <div className="col-md-6">
                  <input className="form-control" placeholder="Số điện thoại"
                    value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} />
                </div>
                <div className="col-md-6">
                  <input type="email" className="form-control" placeholder="Email khách sạn"
                    value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} />
                </div>
                <div className="col-12">
                  <textarea className="form-control" rows={2} placeholder="Mô tả"
                    value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="mt-3 d-flex gap-2">
                <button type="submit" className="btn btn-info btn-sm text-white">
                  {editHotel ? 'Lưu thay đổi' : 'Thêm khách sạn'}
                </button>
                <button type="button" className="btn btn-outline-secondary btn-sm"
                  onClick={() => { setShowForm(false); setEditHotel(null); }}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {hotels.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-building fs-1 d-block mb-3"></i>
          <p>Chưa có khách sạn nào. Hãy thêm khách sạn đầu tiên!</p>
        </div>
      ) : (
        <div className="row g-3">
          {hotels.map(h => (
            <div key={h.id} className="col-md-6">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 className="fw-bold">{h.name}</h6>
                      <small className="text-muted">
                        <i className="bi bi-geo-alt me-1"></i>{h.city} — {h.address}
                      </small>
                      <div className="mt-1 text-warning small">{'★'.repeat(h.star_rating || 0)}</div>
                    </div>
                    <span className={`badge ${h.approved ? 'bg-success' : 'bg-warning text-dark'}`}>
                      {h.approved ? 'Đã duyệt' : 'Chờ duyệt'}
                    </span>
                  </div>
                  <div className="mt-3 d-flex gap-2">
                    <button className="btn btn-outline-primary btn-sm" onClick={() => openEdit(h)}>
                      <i className="bi bi-pencil me-1"></i>Sửa
                    </button>
                    <button className="btn btn-outline-danger btn-sm" onClick={() => handleDelete(h.id)}>
                      <i className="bi bi-trash me-1"></i>Xoá
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Room Management ───────────────────────────────────────────────────────────
function RoomManagement() {
  const [rooms, setRooms] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editRoom, setEditRoom] = useState(null);
  const [hotelFilter, setHotelFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({});
  const EMPTY_FORM = { hotel_id: '', name: '', room_type: 'Standard', capacity: 2, price_per_night: '', area: '', amenities: '', description: '', status: 'AVAILABLE' };
  const [form, setForm] = useState(EMPTY_FORM);

  const fetchRooms = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 12 };
      if (hotelFilter) params.hotel_id = hotelFilter;
      const res = await api.get('/api/owner/rooms', { params });
      setRooms(res.items || []);
      setMeta(res.meta || {});
    } catch { toast.error('Lỗi tải danh sách phòng'); }
    finally { setLoading(false); }
  }, [page, hotelFilter]);

  useEffect(() => {
    fetchRooms();
    api.get('/api/owner/hotels').then(res => setHotels(res.data?.hotels || [])).catch(() => {});
  }, [fetchRooms]);

  const openCreate = () => {
    setEditRoom(null);
    setForm({ ...EMPTY_FORM, hotel_id: hotels[0]?.id || '' });
    setShowForm(true);
  };
  const openEdit = (r) => {
    setEditRoom(r);
    setForm({
      hotel_id: r.hotel_id, name: r.name, room_type: r.room_type,
      capacity: r.capacity, price_per_night: r.price_per_night,
      area: r.area || '', amenities: (r.amenities || []).join(', '),
      description: r.description || '', status: r.status,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      hotel_id: Number(form.hotel_id),
      capacity: Number(form.capacity),
      price_per_night: Number(form.price_per_night),
      area: form.area ? Number(form.area) : null,
    };
    try {
      if (editRoom) {
        await roomService.updateRoom(editRoom.id, payload);
        toast.success('Đã cập nhật phòng');
      } else {
        await roomService.createRoom(payload);
        toast.success('Đã thêm phòng mới');
      }
      setShowForm(false); setEditRoom(null); setForm(EMPTY_FORM);
      fetchRooms();
    } catch { toast.error(editRoom ? 'Lỗi cập nhật phòng' : 'Lỗi thêm phòng'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Xoá phòng này?')) return;
    try {
      await roomService.deleteRoom(id);
      toast.success('Đã xoá phòng');
      fetchRooms();
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Lỗi xoá phòng');
    }
  };

  const ROOM_TYPES = ['Standard', 'Deluxe', 'Suite', 'Family', 'Presidential'];

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Quản lý Phòng</h4>
        <button className="btn btn-info btn-sm text-white" onClick={openCreate} disabled={hotels.length === 0}>
          <i className="bi bi-plus-lg me-1"></i>Thêm phòng
        </button>
      </div>

      {hotels.length === 0 && (
        <div className="alert alert-warning">
          <i className="bi bi-exclamation-triangle me-2"></i>
          Bạn cần tạo khách sạn trước khi thêm phòng.
        </div>
      )}

      {/* Filter */}
      <div className="mb-3">
        <select className="form-select form-select-sm w-auto" value={hotelFilter}
          onChange={e => { setHotelFilter(e.target.value); setPage(1); }}>
          <option value="">Tất cả khách sạn</option>
          {hotels.map(h => <option key={h.id} value={h.id}>{h.name}</option>)}
        </select>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card border-0 shadow-sm mb-4">
          <div className="card-body">
            <h6 className="fw-bold mb-3">{editRoom ? 'Sửa thông tin phòng' : 'Thêm phòng mới'}</h6>
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label small">Khách sạn *</label>
                  <select className="form-select" required value={form.hotel_id}
                    onChange={e => setForm(p => ({ ...p, hotel_id: e.target.value }))}>
                    <option value="">-- Chọn khách sạn --</option>
                    {hotels.map(h => <option key={h.id} value={h.id}>{h.name}</option>)}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Tên phòng *</label>
                  <input className="form-control" placeholder="VD: Deluxe Ocean View" required
                    value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
                </div>
                <div className="col-md-4">
                  <label className="form-label small">Loại phòng</label>
                  <select className="form-select" value={form.room_type}
                    onChange={e => setForm(p => ({ ...p, room_type: e.target.value }))}>
                    {ROOM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label small">Sức chứa (người)</label>
                  <input type="number" className="form-control" min={1} max={20}
                    value={form.capacity} onChange={e => setForm(p => ({ ...p, capacity: e.target.value }))} />
                </div>
                <div className="col-md-4">
                  <label className="form-label small">Giá / đêm (VND) *</label>
                  <input type="number" className="form-control" min={0} required
                    value={form.price_per_night} onChange={e => setForm(p => ({ ...p, price_per_night: e.target.value }))} />
                </div>
                <div className="col-md-4">
                  <label className="form-label small">Diện tích (m²)</label>
                  <input type="number" className="form-control" min={0}
                    value={form.area} onChange={e => setForm(p => ({ ...p, area: e.target.value }))} />
                </div>
                <div className="col-md-4">
                  <label className="form-label small">Trạng thái</label>
                  <select className="form-select" value={form.status}
                    onChange={e => setForm(p => ({ ...p, status: e.target.value }))}>
                    <option value="AVAILABLE">Trống</option>
                    <option value="OCCUPIED">Đang ở</option>
                    <option value="MAINTENANCE">Bảo trì</option>
                  </select>
                </div>
                <div className="col-md-8">
                  <label className="form-label small">Tiện nghi (cách nhau bằng dấu phẩy)</label>
                  <input className="form-control" placeholder="WiFi, AC, TV, Minibar..."
                    value={form.amenities} onChange={e => setForm(p => ({ ...p, amenities: e.target.value }))} />
                </div>
                <div className="col-12">
                  <label className="form-label small">Mô tả</label>
                  <textarea className="form-control" rows={2}
                    value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="mt-3 d-flex gap-2">
                <button type="submit" className="btn btn-info btn-sm text-white">
                  {editRoom ? 'Lưu thay đổi' : 'Thêm phòng'}
                </button>
                <button type="button" className="btn btn-outline-secondary btn-sm"
                  onClick={() => { setShowForm(false); setEditRoom(null); }}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? <LoadingSpinner /> : (
        <>
          <div className="row g-3">
            {rooms.map(r => (
              <div key={r.id} className="col-md-6 col-xl-4">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <h6 className="fw-bold mb-0">{r.name}</h6>
                        <small className="text-muted">{r.hotel_name}</small>
                      </div>
                      <span className={`badge ${r.status === 'AVAILABLE' ? 'bg-success' : r.status === 'OCCUPIED' ? 'bg-danger' : 'bg-secondary'}`}>
                        {r.status}
                      </span>
                    </div>
                    <div className="small text-muted mb-2">
                      <span className="badge bg-light text-dark me-1">{r.room_type}</span>
                      <i className="bi bi-people me-1"></i>{r.capacity} người •
                      <i className="bi bi-cash ms-2 me-1"></i>{VND(r.price_per_night)}/đêm
                    </div>
                    <div className="d-flex gap-2 mt-2">
                      <button className="btn btn-outline-primary btn-sm" onClick={() => openEdit(r)}>
                        <i className="bi bi-pencil me-1"></i>Sửa
                      </button>
                      <button className="btn btn-outline-danger btn-sm" onClick={() => handleDelete(r.id)}>
                        <i className="bi bi-trash me-1"></i>Xoá
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {rooms.length === 0 && (
              <div className="col-12 text-center py-5 text-muted">
                <i className="bi bi-door-open fs-1 d-block mb-3"></i>
                <p>Chưa có phòng nào.</p>
              </div>
            )}
          </div>
          <div className="d-flex justify-content-between align-items-center mt-3">
            <span className="text-muted small">Tổng: {meta.total || 0} phòng</span>
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

// ── Booking Management (Owner) ────────────────────────────────────────────────
function OwnerBookingManagement() {
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
      const res = await api.get('/api/owner/bookings', { params });
      setBookings(res.items || []);
      setMeta(res.meta || {});
    } catch { toast.error('Lỗi tải danh sách booking'); }
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
      toast.success('Đã hoàn tất check-out');
      fetchBookings();
    } catch { toast.error('Lỗi cập nhật'); }
  };

  const handleCancel = async (id) => {
    if (!window.confirm('Huỷ booking này?')) return;
    try {
      await bookingService.cancelBooking(id, 'Owner huỷ');
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
                    <th className="ps-3">ID</th><th>Khách hàng</th><th>Phòng</th>
                    <th>Check-in → Check-out</th><th>Tổng</th><th>Trạng thái</th><th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td className="ps-3 text-muted small">#{b.id}</td>
                      <td>
                        <div className="fw-semibold small">{b.customer_name}</div>
                        <div className="text-muted" style={{ fontSize: '0.72rem' }}>{b.customer_phone}</div>
                      </td>
                      <td className="small">{b.room_name || b.hotel_name}</td>
                      <td className="small">{b.check_in} → {b.check_out}
                        <div className="text-muted" style={{ fontSize: '0.7rem' }}>{b.nights} đêm · {b.guests} khách</div>
                      </td>
                      <td className="small fw-semibold">{VND(b.total_price)}</td>
                      <td>
                        <span className={`badge bg-${STATUS_COLOR[b.status]} text-dark`}>{b.status}</span>
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          {b.status === 'PENDING' && (
                            <button className="btn btn-success btn-sm" onClick={() => handleConfirm(b.id)}
                              title="Xác nhận">
                              <i className="bi bi-check"></i>
                            </button>
                          )}
                          {b.status === 'CONFIRMED' && (
                            <button className="btn btn-primary btn-sm" onClick={() => handleComplete(b.id)}
                              title="Hoàn tất check-out">
                              <i className="bi bi-check-all"></i>
                            </button>
                          )}
                          {['PENDING','CONFIRMED'].includes(b.status) && (
                            <button className="btn btn-outline-danger btn-sm" onClick={() => handleCancel(b.id)}
                              title="Huỷ booking">
                              <i className="bi bi-x"></i>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {bookings.length === 0 && (
                    <tr><td colSpan={7} className="text-center text-muted py-4">Không có booking nào</td></tr>
                  )}
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

// ── Revenue ───────────────────────────────────────────────────────────────────
function Revenue() {
  const [data, setData] = useState(null);
  const [hotels, setHotels] = useState([]);
  const [hotelFilter, setHotelFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchRevenue = useCallback(async () => {
    setLoading(true);
    try {
      const params = hotelFilter ? { hotel_id: hotelFilter } : {};
      const res = await api.get('/api/owner/revenue', { params });
      setData(res.data);
    } catch { toast.error('Lỗi tải dữ liệu doanh thu'); }
    finally { setLoading(false); }
  }, [hotelFilter]);

  useEffect(() => {
    fetchRevenue();
    api.get('/api/owner/hotels').then(res => setHotels(res.data?.hotels || [])).catch(() => {});
  }, [fetchRevenue]);

  const handleExport = async (type) => {
    try {
      const res = await api.get(`/api/reports/export/${type}`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res]));
      const a = document.createElement('a');
      a.href = url; a.download = `revenue-report.${type === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click(); URL.revokeObjectURL(url);
    } catch { toast.error('Lỗi xuất file'); }
  };

  const cards = data ? [
    { label: 'Tổng doanh thu',       value: VND(data.total_revenue),      icon: 'bi-cash-stack',     color: 'success' },
    { label: 'Doanh thu hôm nay',    value: VND(data.revenue_today),      icon: 'bi-sun',            color: 'warning' },
    { label: 'Doanh thu tháng này',  value: VND(data.revenue_this_month), icon: 'bi-calendar-month', color: 'info' },
    { label: 'Booking hoàn thành',   value: data.completed_bookings ?? 0, icon: 'bi-check-circle',   color: 'primary' },
    { label: 'Thanh toán chờ xử lý', value: data.pending_payments ?? 0,   icon: 'bi-hourglass-split', color: 'danger' },
  ] : [];

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Báo cáo Doanh thu</h4>
        <div className="d-flex gap-2">
          <select className="form-select form-select-sm w-auto" value={hotelFilter}
            onChange={e => setHotelFilter(e.target.value)}>
            <option value="">Tất cả khách sạn</option>
            {hotels.map(h => <option key={h.id} value={h.id}>{h.name}</option>)}
          </select>
          <button className="btn btn-outline-success btn-sm" onClick={() => handleExport('excel')}>
            <i className="bi bi-file-earmark-excel me-1"></i>Excel
          </button>
          <button className="btn btn-outline-danger btn-sm" onClick={() => handleExport('pdf')}>
            <i className="bi bi-file-earmark-pdf me-1"></i>PDF
          </button>
        </div>
      </div>

      {loading ? <LoadingSpinner /> : (
        <div className="row g-3">
          {cards.map((c, i) => (
            <div key={i} className="col-sm-6 col-xl-4">
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
      )}
    </div>
  );
}

// ── Main OwnerDashboard ────────────────────────────────────────────────────────
export default function OwnerDashboard() {
  return (
    <div className="d-flex" style={{ minHeight: 'calc(100vh - 56px)' }}>
      <OwnerSidebar />
      <main className="flex-grow-1 bg-light p-4 overflow-auto">
        <Routes>
          <Route index    element={<OwnerOverview />} />
          <Route path="hotels"   element={<HotelManagement />} />
          <Route path="rooms"    element={<RoomManagement />} />
          <Route path="bookings" element={<OwnerBookingManagement />} />
          <Route path="revenue"  element={<Revenue />} />
        </Routes>
      </main>
    </div>
  );
}
