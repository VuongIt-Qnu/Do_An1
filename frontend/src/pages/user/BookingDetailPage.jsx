/**
 * BookingDetailPage
 * Route: /my-bookings/:id
 * Shows full booking info, payment status, timeline, and actions.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { bookingService } from '../../services/bookingService';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import PaymentInstructions from '../../components/PaymentInstructions';

const VND = (v) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(v ?? 0);

const STATUS_META = {
  PENDING:   { color: 'warning',   icon: 'bi-clock',           label: 'Chờ xác nhận' },
  CONFIRMED: { color: 'success',   icon: 'bi-check-circle',    label: 'Đã xác nhận'  },
  COMPLETED: { color: 'secondary', icon: 'bi-check-all',       label: 'Hoàn thành'   },
  CANCELLED: { color: 'danger',    icon: 'bi-x-circle',        label: 'Đã hủy'       },
};

const PAYMENT_STATUS_META = {
  PENDING:  { color: 'warning',   label: 'Chờ thanh toán' },
  PAID:     { color: 'success',   label: 'Đã thanh toán'  },
  REFUNDED: { color: 'info',      label: 'Đã hoàn tiền'   },
  FAILED:   { color: 'danger',    label: 'Thất bại'       },
};

const METHOD_LABEL = {
  BANK_TRANSFER: 'Chuyển khoản ngân hàng',
  MOMO:          'Ví MoMo',
  CASH:          'Tiền mặt tại quầy',
  QR_CODE:       'Thanh toán QR',
};

const TIMELINE_STEPS = ['PENDING', 'CONFIRMED', 'COMPLETED'];

function fmt(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function fmtDatetime(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function BookingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ownerPaymentInfo, setOwnerPaymentInfo] = useState(null);

  // Cancel modal
  const [showCancel, setShowCancel] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelling, setCancelling] = useState(false);

  // Review modal
  const [showReview, setShowReview] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [reviewing, setReviewing] = useState(false);

  // Payment
  const [paying, setPaying] = useState(false);

  const fetchBooking = useCallback(async () => {
    setLoading(true);
    try {
      const data = await bookingService.getBookingById(id);
      setBooking(data);
      // Fetch structured payment instructions
      bookingService.getPaymentInfo(id)
        .then(info => setOwnerPaymentInfo(info))
        .catch(() => {}); // non-critical
    } catch (err) {
      const status = err.response?.status;
      if (status === 404) toast.error('Không tìm thấy booking');
      else if (status === 403) toast.error('Bạn không có quyền xem booking này');
      else toast.error('Lỗi tải dữ liệu');
      navigate('/my-bookings');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { fetchBooking(); }, [fetchBooking]);

  // ── Actions ─────────────────────────────────────────────────────────────────
  const handlePayNow = async () => {
    setPaying(true);
    try {
      await bookingService.processPayment(booking.id, payment?.method || 'BANK_TRANSFER');
      toast.success('Thanh toán thành công! Booking đã được xác nhận.');
      fetchBooking();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Thanh toán thất bại');
    } finally {
      setPaying(false);
    }
  };

  const handleCancel = async () => {
    setCancelling(true);
    try {
      const result = await bookingService.cancelBooking(id, cancelReason);
      const penalty = result?.penalty_info;
      if (penalty?.penalty_amount > 0) {
        toast.warning(`Đã hủy. Phí hủy: ${VND(penalty.penalty_amount)} (${penalty.penalty_percent}%)`);
      } else {
        toast.success('Hủy booking thành công');
      }
      setShowCancel(false);
      fetchBooking();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi hủy booking');
    } finally {
      setCancelling(false);
    }
  };

  const handleReview = async () => {
    setReviewing(true);
    try {
      await bookingService.createReview(id, {
        room_id: booking.room_id,
        rating: reviewForm.rating,
        comment: reviewForm.comment,
      });
      toast.success('Đánh giá đã được gửi!');
      setShowReview(false);
      fetchBooking();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi gửi đánh giá');
    } finally {
      setReviewing(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────
  if (loading) return <LoadingSpinner fullPage />;
  if (!booking) return null;

  const statusMeta  = STATUS_META[booking.status]  || STATUS_META.PENDING;
  const payment     = booking.payment;
  const payMeta     = payment ? (PAYMENT_STATUS_META[payment.status] || {}) : null;
  const canCancel   = ['PENDING', 'CONFIRMED'].includes(booking.status);
  const canReview   = booking.status === 'COMPLETED' && !booking.reviewed;
  const isCancelled = booking.status === 'CANCELLED';

  // Timeline: which step index is current (CANCELLED shows as failed at step 0)
  const stepIndex = isCancelled ? -1 : TIMELINE_STEPS.indexOf(booking.status);

  return (
    <div className="py-4 bg-light min-vh-100">
      <div className="container" style={{ maxWidth: 860 }}>

        {/* ── Breadcrumb ─────────────────────────────────────────────── */}
        <nav className="mb-3">
          <ol className="breadcrumb mb-0 small">
            <li className="breadcrumb-item"><Link to="/" className="text-decoration-none">Trang chủ</Link></li>
            <li className="breadcrumb-item"><Link to="/my-bookings" className="text-decoration-none">Đặt phòng của tôi</Link></li>
            <li className="breadcrumb-item active">Chi tiết #{booking.id}</li>
          </ol>
        </nav>

        {/* ── Header Card ────────────────────────────────────────────── */}
        <div className="card border-0 shadow-sm mb-4">
          <div className="card-body p-4">
            <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
              <div>
                <h4 className="fw-bold mb-1">Booking #{booking.id}</h4>
                <p className="text-muted mb-0 small">
                  <i className="bi bi-clock me-1"></i>
                  Đặt lúc {fmtDatetime(booking.created_at)}
                </p>
              </div>
              <span className={`badge bg-${statusMeta.color} fs-6 px-3 py-2`}>
                <i className={`bi ${statusMeta.icon} me-2`}></i>{statusMeta.label}
              </span>
            </div>

            {/* ── Status Timeline ─────────────────────────────────────── */}
            {!isCancelled ? (
              <div className="mt-4">
                <div className="d-flex align-items-center">
                  {TIMELINE_STEPS.map((step, i) => {
                    const done    = i <= stepIndex;
                    const current = i === stepIndex;
                    return (
                      <React.Fragment key={step}>
                        <div className="d-flex flex-column align-items-center" style={{ flex: '0 0 auto' }}>
                          <div className={`rounded-circle d-flex align-items-center justify-content-center fw-bold
                            ${done ? `bg-${STATUS_META[step].color} text-white` : 'bg-light text-muted border'}`}
                            style={{ width: 36, height: 36, fontSize: 14 }}>
                            {done ? <i className="bi bi-check-lg"></i> : i + 1}
                          </div>
                          <div className={`small mt-1 text-center ${current ? 'fw-bold' : 'text-muted'}`}
                               style={{ width: 80, fontSize: '0.72rem' }}>
                            {STATUS_META[step].label}
                          </div>
                        </div>
                        {i < TIMELINE_STEPS.length - 1 && (
                          <div className={`flex-grow-1 border-top border-2 mx-1 mb-4
                            ${i < stepIndex ? `border-${STATUS_META[TIMELINE_STEPS[i + 1]].color}` : 'border-light'}`} />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="alert alert-danger border-0 mt-3 mb-0 py-2 small">
                <i className="bi bi-x-circle me-2"></i>
                <strong>Đã hủy</strong>
                {booking.cancelled_at && ` lúc ${fmtDatetime(booking.cancelled_at)}`}
                {booking.cancel_reason && ` — Lý do: ${booking.cancel_reason}`}
              </div>
            )}
          </div>
        </div>

        <div className="row g-4">

          {/* ── LEFT COLUMN ──────────────────────────────────────────── */}
          <div className="col-lg-7">

            {/* Room / Hotel */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-door-open text-primary me-2"></i>Thông tin phòng
                </h6>
                <div className="d-flex gap-3">
                  <img
                    src={`https://picsum.photos/seed/${booking.room_id || booking.id}/100/80`}
                    alt={booking.room_name}
                    className="rounded"
                    width="100" height="80"
                    style={{ objectFit: 'cover', flexShrink: 0 }}
                  />
                  <div>
                    <div className="fw-bold">{booking.room_name || '—'}</div>
                    <div className="text-muted small">{booking.room_type || ''}</div>
                    <div className="text-muted small mt-1">
                      <i className="bi bi-building me-1"></i>{booking.hotel_name || '—'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Stay details */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-calendar3 text-primary me-2"></i>Thời gian lưu trú
                </h6>
                <div className="row g-3">
                  <div className="col-6">
                    <div className="text-muted small mb-1">Nhận phòng</div>
                    <div className="fw-semibold">{fmt(booking.check_in)}</div>
                    <div className="text-muted" style={{ fontSize: '0.72rem' }}>Từ 14:00</div>
                  </div>
                  <div className="col-6">
                    <div className="text-muted small mb-1">Trả phòng</div>
                    <div className="fw-semibold">{fmt(booking.check_out)}</div>
                    <div className="text-muted" style={{ fontSize: '0.72rem' }}>Trước 12:00</div>
                  </div>
                  <div className="col-6">
                    <div className="text-muted small mb-1">Số đêm</div>
                    <div className="fw-semibold">{booking.nights} đêm</div>
                  </div>
                  <div className="col-6">
                    <div className="text-muted small mb-1">Số khách</div>
                    <div className="fw-semibold">
                      <i className="bi bi-people me-1 text-muted"></i>{booking.guests} khách
                    </div>
                  </div>
                </div>
                {booking.notes && (
                  <div className="mt-3 pt-3 border-top">
                    <div className="text-muted small mb-1">Ghi chú đặc biệt</div>
                    <div className="small">{booking.notes}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Customer info */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-person text-primary me-2"></i>Thông tin khách hàng
                </h6>
                <div className="row g-2">
                  {[
                    { label: 'Họ tên',        value: booking.customer_name,  icon: 'bi-person' },
                    { label: 'Email',          value: booking.customer_email, icon: 'bi-envelope' },
                    { label: 'Số điện thoại', value: booking.customer_phone || '—', icon: 'bi-telephone' },
                  ].map(item => (
                    <div key={item.label} className="col-12">
                      <div className="d-flex align-items-center gap-2 py-1">
                        <i className={`bi ${item.icon} text-muted`} style={{ width: 18 }}></i>
                        <span className="text-muted small">{item.label}:</span>
                        <span className="small fw-semibold">{item.value}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* ── RIGHT COLUMN ─────────────────────────────────────────── */}
          <div className="col-lg-5">

            {/* Price summary */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-receipt text-primary me-2"></i>Chi tiết thanh toán
                </h6>

                {payment && (
                  <>
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted small">Phương thức</span>
                      <span className="small fw-semibold">
                        {METHOD_LABEL[payment.method] || payment.method}
                      </span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span className="text-muted small">Trạng thái</span>
                      <span className={`badge bg-${payMeta?.color || 'secondary'}`}>
                        {payMeta?.label || payment.status}
                      </span>
                    </div>
                    {payment.paid_at && (
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <span className="text-muted small">Thanh toán lúc</span>
                        <span className="small">{fmtDatetime(payment.paid_at)}</span>
                      </div>
                    )}
                    {payment.transaction_ref && (
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <span className="text-muted small">Mã giao dịch</span>
                        <code className="small">{payment.transaction_ref}</code>
                      </div>
                    )}
                    <hr className="my-2" />
                  </>
                )}

                <div className="d-flex justify-content-between text-muted small mb-1">
                  <span>Tiền phòng ({booking.nights} đêm)</span>
                  <span>{VND(booking.total_price)}</span>
                </div>
                <div className="d-flex justify-content-between fw-bold mt-2 pt-2 border-top">
                  <span>Tổng cộng</span>
                  <span className="text-primary fs-6">{VND(booking.total_price)}</span>
                </div>
              </div>
            </div>

            {/* Payment instructions — show if booking/payment PENDING */}
            {['PENDING', 'AWAITING_PAYMENT'].includes(payment?.status) &&
              booking.status === 'PENDING' && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-header bg-white border-0 pt-3 pb-0 px-4">
                  <h6 className="fw-bold mb-0">
                    <i className="bi bi-credit-card text-primary me-2"></i>
                    Hướng dẫn thanh toán
                  </h6>
                </div>
                <div className="card-body p-4">
                  {/* Use new structured format if available, fallback to legacy */}
                  {ownerPaymentInfo?.instructions ? (
                    <PaymentInstructions paymentInstructions={ownerPaymentInfo} />
                  ) : (
                    <PaymentInstructions payment={payment} ownerPaymentInfo={null} />
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-gear text-primary me-2"></i>Thao tác
                </h6>
                <div className="d-grid gap-2">
                  {/* Pay now — when payment pending */}
                  {payment?.status === 'PENDING' && booking.status === 'PENDING' && (
                    <button className="btn btn-warning fw-semibold" onClick={handlePayNow}
                      disabled={paying}>
                      {paying
                        ? <><span className="spinner-border spinner-border-sm me-2"></span>Đang xử lý...</>
                        : <><i className="bi bi-credit-card me-2"></i>Thanh toán ngay</>
                      }
                    </button>
                  )}
                  {canCancel && (
                    <button className="btn btn-outline-danger" onClick={() => setShowCancel(true)}>
                      <i className="bi bi-x-circle me-2"></i>Hủy đặt phòng
                    </button>
                  )}
                  {canReview && (
                    <button className="btn btn-warning" onClick={() => setShowReview(true)}>
                      <i className="bi bi-star me-2"></i>Viết đánh giá
                    </button>
                  )}
                  {booking.status === 'COMPLETED' && booking.reviewed && (
                    <div className="alert alert-success border-0 py-2 small mb-0 text-center">
                      <i className="bi bi-check-circle me-1"></i>Đã đánh giá
                    </div>
                  )}
                  <Link to="/my-bookings" className="btn btn-outline-secondary">
                    <i className="bi bi-arrow-left me-2"></i>Quay lại danh sách
                  </Link>
                </div>
              </div>
            </div>

            {/* Policy */}
            <div className="card border-0 bg-info bg-opacity-10 mb-4">
              <div className="card-body p-3 small text-muted">
                <div className="fw-semibold mb-1">
                  <i className="bi bi-info-circle me-1 text-info"></i>Chính sách hủy phòng
                </div>
                <ul className="mb-0 ps-3">
                  <li>Hủy trước 24h check-in: <strong className="text-success">Miễn phí</strong></li>
                  <li>Hủy trong 24h: <strong className="text-danger">Phí 50%</strong> tổng tiền</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Cancel Modal ───────────────────────────────────────────────────── */}
      {showCancel && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }} onClick={() => setShowCancel(false)}>
          <div className="modal-dialog modal-dialog-centered" onClick={e => e.stopPropagation()}>
            <div className="modal-content border-0 shadow-lg">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title fw-bold text-danger">
                  <i className="bi bi-exclamation-triangle me-2"></i>Xác nhận hủy booking
                </h5>
                <button className="btn-close" onClick={() => setShowCancel(false)}></button>
              </div>
              <div className="modal-body">
                <div className="alert alert-warning small">
                  <i className="bi bi-info-circle me-1"></i>
                  Hủy trước 24h nhận phòng: miễn phí. Hủy muộn hơn: phí 50% tổng tiền.
                </div>
                <p className="mb-3">
                  Hủy booking <strong>#{booking.id}</strong> — {booking.room_name}
                  <br />
                  <span className="text-muted small">Tổng tiền: {VND(booking.total_price)}</span>
                </p>
                <label className="form-label fw-semibold">Lý do hủy</label>
                <textarea
                  className="form-control" rows={3}
                  placeholder="Nhập lý do hủy (không bắt buộc)..."
                  value={cancelReason}
                  onChange={e => setCancelReason(e.target.value)}
                />
              </div>
              <div className="modal-footer border-0">
                <button className="btn btn-outline-secondary" onClick={() => setShowCancel(false)}>
                  Quay lại
                </button>
                <button className="btn btn-danger" onClick={handleCancel} disabled={cancelling}>
                  {cancelling
                    ? <><span className="spinner-border spinner-border-sm me-2"></span>Đang xử lý...</>
                    : <><i className="bi bi-x-circle me-1"></i>Xác nhận hủy</>
                  }
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Review Modal ───────────────────────────────────────────────────── */}
      {showReview && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }} onClick={() => setShowReview(false)}>
          <div className="modal-dialog modal-dialog-centered" onClick={e => e.stopPropagation()}>
            <div className="modal-content border-0 shadow-lg">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title fw-bold">
                  <i className="bi bi-star-fill text-warning me-2"></i>Đánh giá phòng
                </h5>
                <button className="btn-close" onClick={() => setShowReview(false)}></button>
              </div>
              <div className="modal-body">
                <p className="text-muted small mb-3">
                  Phòng: <strong>{booking.room_name}</strong> — {booking.hotel_name}
                </p>

                {/* Star Rating */}
                <div className="mb-3">
                  <label className="form-label fw-semibold">Điểm đánh giá</label>
                  <div className="d-flex align-items-center gap-1">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        type="button"
                        className="btn p-0 border-0"
                        onClick={() => setReviewForm(p => ({ ...p, rating: star }))}
                      >
                        <i className={`bi bi-star${star <= reviewForm.rating ? '-fill' : ''} fs-3 text-warning`}></i>
                      </button>
                    ))}
                    <span className="ms-2 fw-bold text-warning fs-5">{reviewForm.rating}/5</span>
                  </div>
                  <div className="text-muted small mt-1">
                    {['', 'Rất tệ', 'Tệ', 'Bình thường', 'Tốt', 'Xuất sắc'][reviewForm.rating]}
                  </div>
                </div>

                <div>
                  <label className="form-label fw-semibold">Nhận xét của bạn</label>
                  <textarea
                    className="form-control" rows={4}
                    placeholder="Chia sẻ trải nghiệm lưu trú của bạn..."
                    value={reviewForm.comment}
                    onChange={e => setReviewForm(p => ({ ...p, comment: e.target.value }))}
                  />
                </div>
              </div>
              <div className="modal-footer border-0">
                <button className="btn btn-outline-secondary" onClick={() => setShowReview(false)}>
                  Hủy
                </button>
                <button className="btn btn-warning" onClick={handleReview} disabled={reviewing}>
                  {reviewing
                    ? <><span className="spinner-border spinner-border-sm me-2"></span>Đang gửi...</>
                    : <><i className="bi bi-send me-1"></i>Gửi đánh giá</>
                  }
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
