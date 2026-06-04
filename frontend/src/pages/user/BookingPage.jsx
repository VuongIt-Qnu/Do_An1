/**
 * BookingPage
 * Booking form for a specific room.
 * Requires authentication. Loads room data from route param.
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { roomService } from '../../services/roomService';
import { bookingService } from '../../services/bookingService';
import LoadingSpinner from '../../components/LoadingSpinner';
import PaymentInstructions from '../../components/PaymentInstructions';

const PAYMENT_METHODS = [
  { value: 'BANK_TRANSFER', label: 'Chuyển khoản ngân hàng', icon: 'bi-bank' },
  { value: 'MOMO',          label: 'Ví MoMo',                icon: 'bi-phone' },
  { value: 'CASH',          label: 'Tiền mặt tại quầy',      icon: 'bi-cash-stack' },
  { value: 'QR_CODE',       label: 'Thanh toán QR',          icon: 'bi-qr-code' },
];

function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(amount);
}

export default function BookingPage() {
  const { id: roomId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  const { user } = useAuth();

  const [room, setRoom] = useState(null);
  const [roomLoading, setRoomLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [createdBooking, setCreatedBooking] = useState(null); // { booking, payment }
  const [paying, setPaying] = useState(false);

  // Pre-fill dates from RoomDetailPage query params
  const [form, setForm] = useState({
    customer_name: user?.full_name || '',
    customer_email: user?.email || '',
    customer_phone: user?.phone_number || '',
    check_in: searchParams.get('check_in') || '',
    check_out: searchParams.get('check_out') || '',
    guests: Number(searchParams.get('guests')) || 1,
    payment_method: 'BANK_TRANSFER',
    notes: '',
  });
  const [errors, setErrors] = useState({});

  // Load room on mount
  useEffect(() => {
    roomService.getRoomById(roomId)
      .then(setRoom)
      .catch(() => { toast.error('Không tìm thấy phòng'); navigate('/rooms'); })
      .finally(() => setRoomLoading(false));
  }, [roomId, navigate]);

  // Pre-fill user info when user changes
  useEffect(() => {
    if (user) {
      setForm(prev => ({
        ...prev,
        customer_name: user.full_name || prev.customer_name,
        customer_email: user.email || prev.customer_email,
        customer_phone: user.phone_number || prev.customer_phone,
      }));
    }
  }, [user]);

  // Calculate total price
  const nights = form.check_in && form.check_out
    ? Math.max(0, Math.ceil(
        (new Date(form.check_out) - new Date(form.check_in)) / (1000 * 60 * 60 * 24)
      ))
    : 0;
  const totalPrice = nights * (room?.price_per_night || 0);

  // ── Validation ───────────────────────────────────────────────────
  const validate = () => {
    const errs = {};
    if (!form.customer_name.trim()) errs.customer_name = 'Họ tên là bắt buộc';
    if (!form.customer_email.trim() || !/\S+@\S+\.\S+/.test(form.customer_email))
      errs.customer_email = 'Email không hợp lệ';
    if (!form.customer_phone.trim()) errs.customer_phone = 'Số điện thoại là bắt buộc';
    if (!form.check_in) errs.check_in = 'Chọn ngày nhận phòng';
    if (!form.check_out) errs.check_out = 'Chọn ngày trả phòng';
    if (form.check_in && form.check_out && form.check_out <= form.check_in)
      errs.check_out = 'Ngày trả phòng phải sau ngày nhận phòng';
    if (form.guests < 1 || form.guests > (room?.capacity || 99))
      errs.guests = `Số khách từ 1 đến ${room?.capacity}`;
    return errs;
  };

  // ── Submit ───────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setSubmitting(true);
    try {
      const result = await bookingService.createBooking({ ...form, room_id: roomId });
      setCreatedBooking(result);
      setSuccess(true);
      toast.success(t('booking.success'));
    } catch (err) {
      const msg = err.response?.data?.message || 'Đặt phòng thất bại';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  // ── Render ───────────────────────────────────────────────────────
  if (roomLoading) return <LoadingSpinner fullPage />;

  const handlePayNow = async () => {
    if (!createdBooking?.booking?.id) return;
    setPaying(true);
    try {
      await bookingService.processPayment(createdBooking.booking.id, form.payment_method);
      toast.success('Thanh toán thành công! Booking đã được xác nhận.');
      navigate(`/my-bookings/${createdBooking.booking.id}`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Thanh toán thất bại');
    } finally {
      setPaying(false);
    }
  };

  if (success) {
    const bookingId           = createdBooking?.booking?.id;
    const paymentData         = createdBooking?.payment;
    const paymentInstructions = createdBooking?.payment_instructions;
    const ownerInfo           = createdBooking?.owner_payment_info;

    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-7">

            {/* Header card */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4 text-center">
                <div className="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: 72, height: 72 }}>
                  <i className="bi bi-check-lg fs-1"></i>
                </div>
                <h3 className="fw-bold mb-1">Đặt phòng thành công!</h3>
                {bookingId && (
                  <p className="text-muted mb-1">
                    Mã đặt phòng: <strong className="text-primary">#{bookingId}</strong>
                  </p>
                )}
                <p className="text-muted small mb-0">
                  Email xác nhận đã gửi đến <strong>{form.customer_email}</strong>
                </p>
              </div>
            </div>

            {/* Payment instructions */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-header bg-white border-0 pt-4 pb-0 px-4">
                <h5 className="fw-bold mb-0">
                  <i className="bi bi-credit-card text-primary me-2"></i>
                  Hướng dẫn thanh toán
                </h5>
              </div>
              <div className="card-body p-4">
                {paymentInstructions?.instructions ? (
                  <PaymentInstructions paymentInstructions={paymentInstructions} />
                ) : (
                  <PaymentInstructions payment={paymentData} ownerPaymentInfo={ownerInfo} />
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="d-flex gap-2 justify-content-center flex-wrap">
              {bookingId && (
                <button className="btn btn-primary"
                  onClick={() => navigate(`/my-bookings/${bookingId}`)}>
                  <i className="bi bi-eye me-1"></i>Xem chi tiết booking
                </button>
              )}
              <button className="btn btn-outline-secondary"
                onClick={() => navigate('/my-bookings')}>
                <i className="bi bi-calendar-check me-1"></i>Đặt phòng của tôi
              </button>
              <button className="btn btn-outline-secondary"
                onClick={() => navigate('/rooms')}>
                <i className="bi bi-arrow-left me-1"></i>Danh sách phòng
              </button>
            </div>

          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="py-4">
      <div className="container">
        <button className="btn btn-link text-muted p-0 mb-3" onClick={() => navigate(-1)}>
          <i className="bi bi-arrow-left me-1"></i>{t('common.back')}
        </button>

        <h2 className="fw-bold mb-4">{t('booking.title')}</h2>

        <div className="row g-4">
          {/* ── LEFT: Booking Form ─────────────────────────────────── */}
          <div className="col-lg-7">
            <form onSubmit={handleSubmit}>
              {/* Guest Info */}
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-body">
                  <h5 className="card-title fw-bold mb-3">
                    <i className="bi bi-person me-2 text-primary"></i>
                    {t('booking.customerInfo')}
                  </h5>
                  <div className="row g-3">
                    <div className="col-12">
                      <label className="form-label">{t('booking.fullName')} *</label>
                      <input
                        type="text" className={`form-control ${errors.customer_name ? 'is-invalid' : ''}`}
                        value={form.customer_name}
                        onChange={e => handleChange('customer_name', e.target.value)}
                      />
                      {errors.customer_name && <div className="invalid-feedback">{errors.customer_name}</div>}
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">{t('booking.email')} *</label>
                      <input
                        type="email" className={`form-control ${errors.customer_email ? 'is-invalid' : ''}`}
                        value={form.customer_email}
                        onChange={e => handleChange('customer_email', e.target.value)}
                      />
                      {errors.customer_email && <div className="invalid-feedback">{errors.customer_email}</div>}
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">{t('booking.phone')} *</label>
                      <input
                        type="tel" className={`form-control ${errors.customer_phone ? 'is-invalid' : ''}`}
                        value={form.customer_phone}
                        onChange={e => handleChange('customer_phone', e.target.value)}
                      />
                      {errors.customer_phone && <div className="invalid-feedback">{errors.customer_phone}</div>}
                    </div>
                  </div>
                </div>
              </div>

              {/* Dates & Guests */}
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-body">
                  <h5 className="card-title fw-bold mb-3">
                    <i className="bi bi-calendar me-2 text-primary"></i>
                    Thời gian lưu trú
                  </h5>
                  <div className="row g-3">
                    <div className="col-md-4">
                      <label className="form-label">{t('booking.checkIn')} *</label>
                      <input
                        type="date" className={`form-control ${errors.check_in ? 'is-invalid' : ''}`}
                        min={new Date().toISOString().split('T')[0]}
                        value={form.check_in}
                        onChange={e => handleChange('check_in', e.target.value)}
                      />
                      {errors.check_in && <div className="invalid-feedback">{errors.check_in}</div>}
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">{t('booking.checkOut')} *</label>
                      <input
                        type="date" className={`form-control ${errors.check_out ? 'is-invalid' : ''}`}
                        min={form.check_in || new Date().toISOString().split('T')[0]}
                        value={form.check_out}
                        onChange={e => handleChange('check_out', e.target.value)}
                      />
                      {errors.check_out && <div className="invalid-feedback">{errors.check_out}</div>}
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">{t('booking.guests')} *</label>
                      <input
                        type="number" className={`form-control ${errors.guests ? 'is-invalid' : ''}`}
                        min="1" max={room?.capacity || 10}
                        value={form.guests}
                        onChange={e => handleChange('guests', parseInt(e.target.value))}
                      />
                      {errors.guests && <div className="invalid-feedback">{errors.guests}</div>}
                      <div className="form-text">Tối đa {room?.capacity} khách</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Payment Method */}
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-body">
                  <h5 className="card-title fw-bold mb-3">
                    <i className="bi bi-credit-card me-2 text-primary"></i>
                    {t('booking.paymentMethod')}
                  </h5>
                  <div className="row g-2">
                    {PAYMENT_METHODS.map(method => (
                      <div key={method.value} className="col-md-6">
                        <div
                          className={`card border-2 cursor-pointer ${form.payment_method === method.value ? 'border-primary bg-primary bg-opacity-10' : 'border-light'}`}
                          onClick={() => handleChange('payment_method', method.value)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="card-body py-2 px-3 d-flex align-items-center gap-2">
                            <i className={`bi ${method.icon} fs-5 ${form.payment_method === method.value ? 'text-primary' : 'text-muted'}`}></i>
                            <span className="small fw-semibold">{method.label}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Special Requests */}
              <div className="mb-4">
                <label className="form-label">{t('booking.notes')}</label>
                <textarea
                  className="form-control" rows={3}
                  placeholder="Ví dụ: Phòng tầng cao, tránh hướng Tây..."
                  value={form.notes}
                  onChange={e => handleChange('notes', e.target.value)}
                />
              </div>

              {/* Submit */}
              <button
                type="submit" className="btn btn-primary btn-lg w-100 py-3"
                disabled={submitting}
              >
                {submitting ? (
                  <><span className="spinner-border spinner-border-sm me-2"></span>Đang xử lý...</>
                ) : (
                  <><i className="bi bi-calendar-check me-2"></i>{t('booking.confirm')}</>
                )}
              </button>
            </form>
          </div>

          {/* ── RIGHT: Order Summary ────────────────────────────────── */}
          <div className="col-lg-5">
            <div className="card border-0 shadow-sm sticky-top" style={{ top: '1rem' }}>
              <div className="card-body">
                <h5 className="card-title fw-bold mb-3">Tóm tắt đặt phòng</h5>

                {/* Room Preview */}
                <div className="d-flex gap-3 mb-3 pb-3 border-bottom">
                  <img
                    src={room?.main_image_url || `https://picsum.photos/seed/${roomId}/100/80`}
                    alt={room?.name}
                    className="rounded" width="90" height="70"
                    style={{ objectFit: 'cover' }}
                  />
                  <div>
                    <div className="fw-bold">{room?.name}</div>
                    <div className="text-muted small">{room?.room_type}</div>
                    <div className="text-muted small">
                      <i className="bi bi-people me-1"></i>{room?.capacity} khách
                    </div>
                  </div>
                </div>

                {/* Price Breakdown */}
                <div className="mb-3">
                  <div className="d-flex justify-content-between text-muted small mb-1">
                    <span>{formatVND(room?.price_per_night || 0)} × {nights} đêm</span>
                    <span>{formatVND(totalPrice)}</span>
                  </div>
                  {nights > 3 && (
                    <div className="d-flex justify-content-between text-success small mb-1">
                      <span>Ưu đãi (lưu trú dài)</span>
                      <span>-0%</span>
                    </div>
                  )}
                </div>

                <div className="d-flex justify-content-between fw-bold fs-5 pt-2 border-top">
                  <span>{t('booking.totalPrice')}</span>
                  <span className="text-primary">{formatVND(totalPrice)}</span>
                </div>

                {nights > 0 && (
                  <div className="text-muted small mt-1 text-end">
                    {nights} {t('booking.nights')}
                  </div>
                )}

                {/* Policy Note */}
                <div className="alert alert-info border-0 small mt-3 mb-0 py-2">
                  <i className="bi bi-info-circle me-1"></i>
                  Hủy miễn phí trước 24 giờ check-in. Sau thời gian này, phí hủy là 50%.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
