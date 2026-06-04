/**
 * RoomCard Component
 * Displays a single room in a Bootstrap card format.
 * Used on HomePage (featured) and RoomsPage (list).
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

/**
 * Format price as Vietnamese Dong
 * @param {number} price
 */
function formatPrice(price) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(price);
}

/**
 * Star rating display
 */
function StarRating({ rating = 5, maxStars = 5 }) {
  return (
    <span className="text-warning">
      {Array.from({ length: maxStars }, (_, i) => (
        <i
          key={i}
          className={`bi ${i < Math.round(rating) ? 'bi-star-fill' : 'bi-star'} me-1`}
          style={{ fontSize: '0.75rem' }}
        />
      ))}
      <small className="text-muted ms-1">({rating?.toFixed(1)})</small>
    </span>
  );
}

export default function RoomCard({ room, compact = false }) {
  const { t } = useTranslation();

  if (!room) return null;

  const amenities = room.amenities
    ? (typeof room.amenities === 'string'
        ? room.amenities.split(',').map(a => a.trim())
        : room.amenities)
    : [];

  const isAvailable = room.status === 'AVAILABLE';

  return (
    <div className="card h-100 shadow-sm border-0 room-card">
      {/* Room Image */}
      <div className="position-relative overflow-hidden" style={{ height: compact ? '160px' : '200px' }}>
        <img
          src={room.main_image_url || `https://picsum.photos/seed/${room.id}/400/300`}
          alt={room.name}
          className="card-img-top w-100 h-100"
          style={{ objectFit: 'cover', transition: 'transform 0.3s ease' }}
          onError={(e) => {
            e.target.src = `https://picsum.photos/seed/${room.id}/400/300`;
          }}
        />
        {/* Status Badge */}
        <span className={`badge position-absolute top-0 end-0 m-2 ${isAvailable ? 'bg-success' : 'bg-danger'}`}>
          {isAvailable ? t('rooms.available') : t('rooms.occupied')}
        </span>
        {/* Featured Badge */}
        {room.featured && (
          <span className="badge bg-warning text-dark position-absolute top-0 start-0 m-2">
            <i className="bi bi-star-fill me-1"></i>Nổi bật
          </span>
        )}
      </div>

      <div className="card-body d-flex flex-column">
        {/* Room Type */}
        <small className="text-muted text-uppercase fw-semibold mb-1">
          {room.room_type || room.room_type_name}
        </small>

        {/* Room Name */}
        <h5 className="card-title fw-bold text-truncate mb-1">{room.name}</h5>

        {/* Hotel Name */}
        {room.hotel_name && (
          <small className="text-muted mb-2">
            <i className="bi bi-geo-alt me-1"></i>{room.hotel_name}
          </small>
        )}

        {/* Rating */}
        <div className="mb-2">
          <StarRating rating={room.rating} />
          {room.review_count > 0 && (
            <small className="text-muted">({room.review_count} đánh giá)</small>
          )}
        </div>

        {/* Room Info */}
        <div className="d-flex gap-3 text-muted small mb-2">
          <span>
            <i className="bi bi-people me-1"></i>
            {room.capacity} {t('rooms.guests')}
          </span>
          {room.area && (
            <span>
              <i className="bi bi-grid me-1"></i>
              {room.area} m²
            </span>
          )}
        </div>

        {/* Amenities (max 3) */}
        {!compact && amenities.length > 0 && (
          <div className="d-flex flex-wrap gap-1 mb-3">
            {amenities.slice(0, 3).map((amenity, i) => (
              <span key={i} className="badge bg-light text-dark border small">
                {amenity}
              </span>
            ))}
            {amenities.length > 3 && (
              <span className="badge bg-light text-muted border small">
                +{amenities.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Price + CTA */}
        <div className="mt-auto">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <span className="fs-5 fw-bold text-primary">
                {formatPrice(room.price_per_night)}
              </span>
              <small className="text-muted"> {t('rooms.perNight')}</small>
            </div>

            <Link
              to={`/rooms/${room.id}`}
              className={`btn btn-sm ${isAvailable ? 'btn-primary' : 'btn-secondary'}`}
            >
              {t('rooms.viewDetail')}
              <i className="bi bi-arrow-right ms-1"></i>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
