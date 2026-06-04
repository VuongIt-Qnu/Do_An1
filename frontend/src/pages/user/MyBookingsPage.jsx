/**
 * MyBookingsPage
 * Authenticated user's booking history with cancel and review actions.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { bookingService } from '../../services/bookingService';
import LoadingSpinner from '../../components/LoadingSpinner';

const STATUS_COLORS = {
  PENDING: 'warning', CONFIRMED: 'success', CANCELLED: 'danger', COMPLETED: 'secondary',
};

function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(amount);
}

export default function MyBookingsPage() {
  const { t } = useTranslation();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [cancelModal, setCancelModal] = useState(null); // booking to cancel
  const [cancelReason, setCancelReason] = useState('');
  const [reviewModal, setReviewModal] = useState(null); // booking to review

  const fetchBookings = useCallback(async () => {
    setLoading(true);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const data = await bookingService.getMyBookings(params);
      setBookings(data.items || []);
    } catch { toast.error('Không thể tải danh sách booking'); }
    finally { setLoading(false); }
  }, [statusFilter]);

  useEffect(() => { fetchBookings(); }, [fetchBookings]);

  // ── Cancel Booking ────────────────────────────────────────────────
  const handleCancel = async () => {
    if (!cancelModal) return;
    try {
      const result = await bookingService.cancelBooking(cancelModal.id, cancelReason);
      const penalty = result.penalty_info;
      if (penalty?.penalty_amount > 0) {
        toast.warning(`Đã hủy. Phí hủy: ${formatVND(penalty.penalty_amount)} (${penalty.penalty_percent}%)`);
      } else {
        toast.success('Đã hủy booking thành công');
      }
      setCancelModal(null);
      setCancelReason('');
      fetchBookings();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi hủy booking');
    }
  };

  // ── Post Review ───────────────────────────────────────────────────
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });

  const handleReview = async () => {
    if (!reviewModal) return;
    try {
      await bookingService.createReview(reviewModal.id, {
        room_id: reviewModal.room_id,
        rating: reviewForm.rating,
        comment: reviewForm.comment,
      });
      toast.success('Đánh giá của bạn đã được gửi!');
      setReviewModal(null);
      setReviewForm({ rating: 5, comment: '' });
      fetchBookings();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Lỗi gửi đánh giá');
    }
  };

  return (
    <div className="py-4">
      <div className="container">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 className="fw-bold mb-1">{t('nav.myBookings')}</h2>
            <p className="text-muted mb-0">Lịch sử đặt phòng của bạn</p>
          </div>
          <select
            className="form-select form-select-sm w-auto"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
          >
            <option value="">Tất cả</option>
            {Object.keys(STATUS_COLORS).map(s => (
              <option key={s} value={s}>{t(`booking.status.${s}`)}</option>
            ))}
          </select>
        </div>

        {loading ? <LoadingSpinner /> : bookings.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <i className="bi bi-calendar-x fs-1 d-block mb-3"></i>
            <h5>{t('booking.noBookings')}</h5>
            <a href="/rooms" className="btn btn-primary mt-2">Đặt phòng ngay</a>
          </div>
        ) : (
          <div className="row g-3">
            {bookings.map(booking => (
              <div key={booking.id} className="col-12">
                <div className="card border-0 shadow-sm">
                  <div className="card-body">
                    <div className="row align-items-center g-3">
                      {/* Room Image */}
                      <div className="col-auto">
                        <img
                          src={`https://picsum.photos/seed/${booking.room_id}/90/70`}
                          alt={booking.room_name}
                          className="rounded" width="90" height="70"
                          style={{ objectFit: 'cover' }}
                        />
                      </div>

                      {/* Booking Info */}
                      <div className="col">
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <h6 className="fw-bold mb-0">{booking.room_name || booking.hotel_name}</h6>
                          <span className={`badge bg-${STATUS_COLORS[booking.status]} text-dark`}>
                            {t(`booking.status.${booking.status}`)}
                          </span>
                        </div>
                        <div className="text-muted small">
                          <i className="bi bi-calendar3 me-1"></i>
                          {booking.check_in} → {booking.check_out}
                          <span className="ms-2">({booking.nights} đêm)</span>
                          <span className="ms-3">
                            <i className="bi bi-people me-1"></i>{booking.guests} khách
                          </span>
                        </div>
                        <div className="small text-muted mt-1">
                          Mã đặt phòng: <code>#{booking.id}</code>
                        </div>
                      </div>

                      {/* Price + Actions */}
                      <div className="col-auto text-end">
                        <div className="fw-bold fs-6 text-primary mb-2">
                          {formatVND(booking.total_price)}
                        </div>
                        <div className="d-flex gap-1 justify-content-end flex-wrap">
                          {/* Detail button */}
                          <Link
                            to={`/my-bookings/${booking.id}`}
                            className="btn btn-outline-primary btn-sm"
                          >
                            <i className="bi bi-eye me-1"></i>Chi tiết
                          </Link>

                          {/* Cancel button */}
                          {['PENDING', 'CONFIRMED'].includes(booking.status) && (
                            <button
                              className="btn btn-outline-danger btn-sm"
                              onClick={() => { setCancelModal(booking); setCancelReason(''); }}
                            >
                              <i className="bi bi-x-circle me-1"></i>Hủy
                            </button>
                          )}

                          {/* Review button */}
                          {booking.status === 'COMPLETED' && !booking.reviewed && (
                            <button
                              className="btn btn-outline-warning btn-sm"
                              onClick={() => { setReviewModal(booking); setReviewForm({ rating: 5, comment: '' }); }}
                            >
                              <i className="bi bi-star me-1"></i>Đánh giá
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Cancel Modal ──────────────────────────────────────────── */}
        {cancelModal && (
          <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content border-0 shadow-lg">
                <div className="modal-header border-0">
                  <h5 className="modal-title fw-bold text-danger">
                    <i className="bi bi-exclamation-triangle me-2"></i>Xác nhận hủy booking
                  </h5>
                  <button className="btn-close" onClick={() => setCancelModal(null)}></button>
                </div>
                <div className="modal-body">
                  <div className="alert alert-warning small">
                    <i className="bi bi-info-circle me-1"></i>
                    Hủy trước 24h: miễn phí. Hủy muộn hơn: phí 50% tổng tiền.
                  </div>
                  <p>Bạn có chắc muốn hủy booking <strong>#{cancelModal.id}</strong>?</p>
                  <label className="form-label">{t('booking.cancelReason')}</label>
                  <textarea
                    className="form-control" rows={3}
                    placeholder="Nhập lý do hủy..."
                    value={cancelReason}
                    onChange={e => setCancelReason(e.target.value)}
                  />
                </div>
                <div className="modal-footer border-0">
                  <button className="btn btn-outline-secondary" onClick={() => setCancelModal(null)}>Quay lại</button>
                  <button className="btn btn-danger" onClick={handleCancel}>
                    <i className="bi bi-x-circle me-1"></i>Xác nhận hủy
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Review Modal ──────────────────────────────────────────── */}
        {reviewModal && (
          <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content border-0 shadow-lg">
                <div className="modal-header border-0">
                  <h5 className="modal-title fw-bold">
                    <i className="bi bi-star-fill text-warning me-2"></i>Đánh giá phòng
                  </h5>
                  <button className="btn-close" onClick={() => setReviewModal(null)}></button>
                </div>
                <div className="modal-body">
                  <p className="text-muted">Đánh giá phòng: <strong>{reviewModal.room_name}</strong></p>
                  {/* Star Rating */}
                  <div className="mb-3">
                    <label className="form-label fw-semibold">Điểm đánh giá</label>
                    <div className="d-flex gap-1">
                      {[1, 2, 3, 4, 5].map(star => (
                        <button
                          key={star}
                          type="button"
                          className="btn p-0"
                          onClick={() => setReviewForm(p => ({ ...p, rating: star }))}
                        >
                          <i className={`bi bi-star${star <= reviewForm.rating ? '-fill' : ''} fs-4 text-warning`}></i>
                        </button>
                      ))}
                      <span className="ms-2 fw-bold text-warning">{reviewForm.rating}/5</span>
                    </div>
                  </div>
                  <div>
                    <label className="form-label fw-semibold">Nhận xét</label>
                    <textarea
                      className="form-control" rows={4}
                      placeholder="Chia sẻ trải nghiệm của bạn..."
                      value={reviewForm.comment}
                      onChange={e => setReviewForm(p => ({ ...p, comment: e.target.value }))}
                    />
                  </div>
                </div>
                <div className="modal-footer border-0">
                  <button className="btn btn-outline-secondary" onClick={() => setReviewModal(null)}>Hủy</button>
                  <button className="btn btn-warning" onClick={handleReview}>
                    <i className="bi bi-send me-1"></i>Gửi đánh giá
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
