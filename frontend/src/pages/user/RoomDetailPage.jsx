/**
 * RoomDetailPage
 * Route: /rooms/:id
 * Shows full room info, amenities, availability checker, and reviews.
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { roomService } from '../../services/roomService';
import LoadingSpinner from '../../components/LoadingSpinner';

const VND = (v) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(v ?? 0);

const AMENITY_ICONS = {
  'Wifi':        'bi-wifi',
  'TV':          'bi-tv',
  'AC':          'bi-thermometer-snow',
  'Minibar':     'bi-cup-straw',
  'Jacuzzi':     'bi-droplet',
  'Balcony':     'bi-grid-1x2',
  'Kitchen':     'bi-fire',
  'Safe':        'bi-shield-lock',
  'Parking':     'bi-car-front',
  'Pool':        'bi-water',
  'Gym':         'bi-trophy',
  'Spa':         'bi-flower1',
  'Breakfast':   'bi-egg-fried',
  'Laundry':     'bi-bag',
  'Bathtub':     'bi-droplet-half',
  'Hairdryer':   'bi-wind',
  'Coffee':      'bi-cup-hot',
};

function StarRating({ value, max = 5, size = '' }) {
  return (
    <span>
      {Array.from({ length: max }, (_, i) => (
        <i key={i}
          className={`bi ${i < Math.floor(value) ? 'bi-star-fill' :
            i < value ? 'bi-star-half' : 'bi-star'} text-warning ${size}`} />
      ))}
    </span>
  );
}

function ReviewCard({ review }) {
  const date = review.created_at
    ? new Date(review.created_at).toLocaleDateString('vi-VN')
    : '';
  return (
    <div className="border-bottom pb-3 mb-3">
      <div className="d-flex justify-content-between align-items-start mb-1">
        <div className="fw-semibold small">{review.user_name || 'Ẩn danh'}</div>
        <div className="text-muted" style={{ fontSize: '0.72rem' }}>{date}</div>
      </div>
      <StarRating value={review.rating} />
      {review.comment && (
        <p className="text-muted small mt-1 mb-0">{review.comment}</p>
      )}
    </div>
  );
}

export default function RoomDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [room, setRoom]       = useState(null);
  const [loading, setLoading] = useState(true);

  // Availability checker
  const today    = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
  const [checkIn,  setCheckIn]  = useState(today);
  const [checkOut, setCheckOut] = useState(tomorrow);
  const [guests,   setGuests]   = useState(1);
  const [avail,    setAvail]    = useState(null);   // null | true | false
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    roomService.getRoomById(id)
      .then(data => setRoom(data))
      .catch(() => { toast.error('Không tìm thấy phòng'); navigate('/rooms'); })
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const nights = checkIn && checkOut
    ? Math.max(0, Math.ceil((new Date(checkOut) - new Date(checkIn)) / 86400000))
    : 0;

  const handleCheckAvailability = async () => {
    if (!checkIn || !checkOut || checkOut <= checkIn) {
      toast.warning('Chọn ngày hợp lệ');
      return;
    }
    setChecking(true);
    try {
      const result = await roomService.checkAvailability(id, checkIn, checkOut);
      setAvail(result?.available ?? result?.data?.available ?? false);
    } catch {
      toast.error('Không thể kiểm tra phòng');
    } finally {
      setChecking(false);
    }
  };

  const handleBook = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/rooms/${id}/book` } } });
      return;
    }
    const params = new URLSearchParams({ check_in: checkIn, check_out: checkOut, guests });
    navigate(`/rooms/${id}/book?${params}`);
  };

  if (loading) return <LoadingSpinner fullPage />;
  if (!room)   return null;

  const amenities  = Array.isArray(room.amenities) ? room.amenities : [];
  const reviews    = room.reviews || [];
  const isAvailable = room.status === 'AVAILABLE';

  return (
    <div className="py-4 bg-light">
      <div className="container">

        {/* Breadcrumb */}
        <nav className="mb-3">
          <ol className="breadcrumb mb-0 small">
            <li className="breadcrumb-item"><Link to="/" className="text-decoration-none">Trang chủ</Link></li>
            <li className="breadcrumb-item"><Link to="/rooms" className="text-decoration-none">Phòng</Link></li>
            <li className="breadcrumb-item active">{room.name}</li>
          </ol>
        </nav>

        <div className="row g-4">

          {/* ── LEFT COLUMN ───────────────────────────────────────────────── */}
          <div className="col-lg-8">

            {/* Room Images */}
            <div className="card border-0 shadow-sm overflow-hidden mb-4">
              <img
                src={room.main_image_url || `https://picsum.photos/seed/${room.id}/900/450`}
                alt={room.name}
                className="w-100"
                style={{ height: 380, objectFit: 'cover' }}
              />
            </div>

            {/* Title & Meta */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <div className="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-2">
                  <div>
                    <h2 className="fw-bold mb-1">{room.name}</h2>
                    <div className="text-muted small">
                      <i className="bi bi-building me-1"></i>{room.hotel_name}
                    </div>
                  </div>
                  <span className={`badge fs-6 px-3 py-2 ${isAvailable ? 'bg-success' : 'bg-secondary'}`}>
                    {isAvailable ? 'Còn phòng' : room.status === 'OCCUPIED' ? 'Đã đặt' : 'Bảo trì'}
                  </span>
                </div>

                {/* Quick stats */}
                <div className="d-flex flex-wrap gap-3 mt-3">
                  {[
                    { icon: 'bi-tag',        text: room.room_type },
                    { icon: 'bi-people',     text: `Tối đa ${room.capacity} khách` },
                    room.area && { icon: 'bi-aspect-ratio', text: `${room.area} m²` },
                    { icon: 'bi-star-fill',  text: `${room.rating?.toFixed(1)} / 5.0`, cls: 'text-warning' },
                    { icon: 'bi-chat-text',  text: `${room.review_count ?? reviews.length} đánh giá` },
                  ].filter(Boolean).map((item, i) => (
                    <div key={i} className="d-flex align-items-center gap-1 text-muted small">
                      <i className={`bi ${item.icon} ${item.cls || ''}`}></i>
                      <span>{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Description */}
            {room.description && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-body p-4">
                  <h5 className="fw-bold mb-3">
                    <i className="bi bi-card-text text-primary me-2"></i>Mô tả phòng
                  </h5>
                  <p className="text-muted mb-0" style={{ lineHeight: 1.8 }}>{room.description}</p>
                </div>
              </div>
            )}

            {/* Amenities */}
            {amenities.length > 0 && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-body p-4">
                  <h5 className="fw-bold mb-3">
                    <i className="bi bi-grid text-primary me-2"></i>Tiện nghi phòng
                  </h5>
                  <div className="row g-2">
                    {amenities.map(a => (
                      <div key={a} className="col-6 col-md-4 col-lg-3">
                        <div className="d-flex align-items-center gap-2 p-2 rounded bg-light">
                          <i className={`bi ${AMENITY_ICONS[a] || 'bi-check2'} text-primary`}></i>
                          <span className="small">{a}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Reviews */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <div className="d-flex align-items-center justify-content-between mb-4">
                  <h5 className="fw-bold mb-0">
                    <i className="bi bi-star text-warning me-2"></i>
                    Đánh giá ({room.review_count ?? reviews.length})
                  </h5>
                  {room.rating && (
                    <div className="d-flex align-items-center gap-2">
                      <span className="fs-4 fw-bold text-warning">{room.rating.toFixed(1)}</span>
                      <StarRating value={room.rating} />
                    </div>
                  )}
                </div>

                {reviews.length === 0 ? (
                  <p className="text-muted text-center py-3">
                    <i className="bi bi-chat-square d-block fs-2 mb-2"></i>
                    Chưa có đánh giá nào. Hãy là người đầu tiên!
                  </p>
                ) : (
                  reviews.map(r => <ReviewCard key={r.id} review={r} />)
                )}
              </div>
            </div>

          </div>

          {/* ── RIGHT COLUMN — Booking Widget ─────────────────────────────── */}
          <div className="col-lg-4">
            <div className="sticky-top" style={{ top: '1rem' }}>

              {/* Price & Book */}
              <div className="card border-0 shadow-sm mb-3">
                <div className="card-body p-4">
                  <div className="mb-3">
                    <span className="fs-3 fw-bold text-primary">{VND(room.price_per_night)}</span>
                    <span className="text-muted"> / đêm</span>
                  </div>

                  {/* Dates */}
                  <div className="row g-2 mb-3">
                    <div className="col-6">
                      <label className="form-label small fw-semibold mb-1">Nhận phòng</label>
                      <input type="date" className="form-control form-control-sm"
                        min={today} value={checkIn}
                        onChange={e => { setCheckIn(e.target.value); setAvail(null); }} />
                    </div>
                    <div className="col-6">
                      <label className="form-label small fw-semibold mb-1">Trả phòng</label>
                      <input type="date" className="form-control form-control-sm"
                        min={checkIn || today} value={checkOut}
                        onChange={e => { setCheckOut(e.target.value); setAvail(null); }} />
                    </div>
                  </div>

                  {/* Guests */}
                  <div className="mb-3">
                    <label className="form-label small fw-semibold mb-1">
                      Số khách (tối đa {room.capacity})
                    </label>
                    <select className="form-select form-select-sm"
                      value={guests} onChange={e => setGuests(Number(e.target.value))}>
                      {Array.from({ length: room.capacity }, (_, i) => i + 1).map(n => (
                        <option key={n} value={n}>{n} khách</option>
                      ))}
                    </select>
                  </div>

                  {/* Price breakdown */}
                  {nights > 0 && (
                    <div className="bg-light rounded p-3 mb-3 small">
                      <div className="d-flex justify-content-between text-muted mb-1">
                        <span>{VND(room.price_per_night)} × {nights} đêm</span>
                        <span>{VND(room.price_per_night * nights)}</span>
                      </div>
                      <div className="d-flex justify-content-between fw-bold border-top pt-2 mt-1">
                        <span>Tổng cộng</span>
                        <span className="text-primary">{VND(room.price_per_night * nights)}</span>
                      </div>
                    </div>
                  )}

                  {/* Availability result */}
                  {avail === true && (
                    <div className="alert alert-success py-2 small mb-3">
                      <i className="bi bi-check-circle me-1"></i>Phòng còn trống trong thời gian này!
                    </div>
                  )}
                  {avail === false && (
                    <div className="alert alert-danger py-2 small mb-3">
                      <i className="bi bi-x-circle me-1"></i>Phòng đã được đặt trong thời gian này.
                    </div>
                  )}

                  {/* Action buttons */}
                  {isAvailable ? (
                    <div className="d-grid gap-2">
                      <button className="btn btn-primary py-2 fw-semibold" onClick={handleBook}>
                        <i className="bi bi-calendar-check me-2"></i>Đặt phòng ngay
                      </button>
                      <button className="btn btn-outline-secondary btn-sm" onClick={handleCheckAvailability}
                        disabled={checking}>
                        {checking
                          ? <><span className="spinner-border spinner-border-sm me-1"></span>Đang kiểm tra...</>
                          : <><i className="bi bi-search me-1"></i>Kiểm tra khả dụng</>}
                      </button>
                    </div>
                  ) : (
                    <div className="alert alert-secondary text-center mb-0 py-2">
                      <i className="bi bi-lock me-1"></i>
                      {room.status === 'OCCUPIED' ? 'Phòng đang được sử dụng' : 'Phòng đang bảo trì'}
                    </div>
                  )}
                </div>
              </div>

              {/* Policy */}
              <div className="card border-0 bg-info bg-opacity-10">
                <div className="card-body p-3 small text-muted">
                  <div className="fw-semibold mb-2">
                    <i className="bi bi-shield-check me-1 text-info"></i>Chính sách
                  </div>
                  <ul className="mb-0 ps-3">
                    <li>Nhận phòng từ <strong>14:00</strong></li>
                    <li>Trả phòng trước <strong>12:00</strong></li>
                    <li>Hủy miễn phí trước <strong>24h</strong> check-in</li>
                    <li>Phí hủy muộn: <strong>50%</strong> tổng tiền</li>
                  </ul>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
