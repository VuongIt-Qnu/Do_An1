/**
 * HomePage
 * Landing page with hero section, featured rooms, and search.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';
import { roomService } from '../../services/roomService';
import RoomCard from '../../components/RoomCard';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function HomePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [featuredRooms, setFeaturedRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Load featured rooms on mount
  useEffect(() => {
    roomService.getRooms({ featured: true, per_page: 6, status: 'AVAILABLE' })
      .then(data => setFeaturedRooms(data.items || []))
      .catch(() => toast.error('Không thể tải danh sách phòng'))
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/rooms?search=${encodeURIComponent(searchQuery)}`);
  };

  return (
    <div>
      {/* ── HERO SECTION ──────────────────────────────────────────── */}
      <section
        className="hero-section d-flex align-items-center text-white"
        style={{
          minHeight: '85vh',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background decoration */}
        <div
          style={{
            position: 'absolute', inset: 0, opacity: 0.05,
            backgroundImage: 'url("https://picsum.photos/seed/hotel/1920/1080")',
            backgroundSize: 'cover', backgroundPosition: 'center',
          }}
        />

        <div className="container position-relative z-1 py-5">
          <div className="row align-items-center">
            <div className="col-lg-7">
              {/* Headline */}
              <span className="badge bg-warning text-dark mb-3 px-3 py-2">
                <i className="bi bi-star-fill me-1"></i> CNPM2 — Hotel Management v2.0
              </span>
              <h1 className="display-4 fw-bold mb-3 lh-sm">
                {t('home.heroTitle')}
                <br />
                <span className="text-warning">Hotel Management</span>
              </h1>
              <p className="lead text-light opacity-75 mb-4">
                {t('home.heroSubtitle')}
              </p>

              {/* Search Bar */}
              <form onSubmit={handleSearch} className="d-flex gap-2">
                <div className="input-group input-group-lg shadow">
                  <span className="input-group-text bg-white border-0">
                    <i className="bi bi-search text-muted"></i>
                  </span>
                  <input
                    type="text"
                    className="form-control border-0 fs-6"
                    placeholder={t('home.searchPlaceholder')}
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                  <button type="submit" className="btn btn-warning btn-lg px-4 fw-semibold">
                    {t('common.search')}
                  </button>
                </div>
              </form>

              {/* Quick Stats */}
              <div className="d-flex gap-4 mt-4 text-light opacity-75">
                <div className="text-center">
                  <div className="h4 fw-bold text-warning mb-0">500+</div>
                  <small>Phòng khách sạn</small>
                </div>
                <div className="text-center">
                  <div className="h4 fw-bold text-warning mb-0">50+</div>
                  <small>Khách sạn</small>
                </div>
                <div className="text-center">
                  <div className="h4 fw-bold text-warning mb-0">4.8★</div>
                  <small>Đánh giá TB</small>
                </div>
              </div>
            </div>

            {/* Right side illustration */}
            <div className="col-lg-5 d-none d-lg-flex justify-content-center">
              <div className="position-relative">
                <div
                  className="rounded-4 shadow-lg overflow-hidden"
                  style={{ width: '360px', height: '400px' }}
                >
                  <img
                    src="https://picsum.photos/seed/hotelroom/360/400"
                    alt="Hotel"
                    className="w-100 h-100"
                    style={{ objectFit: 'cover' }}
                  />
                </div>
                {/* Floating card */}
                <div
                  className="card position-absolute shadow-lg border-0 p-2"
                  style={{ bottom: '-20px', left: '-30px', width: '180px' }}
                >
                  <div className="d-flex align-items-center gap-2">
                    <div className="bg-success rounded-circle p-2">
                      <i className="bi bi-check-lg text-white"></i>
                    </div>
                    <div>
                      <div className="fw-bold small">Đặt phòng OK</div>
                      <div className="text-muted" style={{ fontSize: '0.7rem' }}>Xác nhận ngay lập tức</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FEATURED ROOMS ────────────────────────────────────────── */}
      <section className="py-5 bg-light">
        <div className="container">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="fw-bold mb-1">{t('home.featuredRooms')}</h2>
              <p className="text-muted mb-0">Những phòng được khách hàng yêu thích nhất</p>
            </div>
            <a href="/rooms" className="btn btn-outline-primary">
              {t('home.viewAll')} <i className="bi bi-arrow-right ms-1"></i>
            </a>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : featuredRooms.length === 0 ? (
            <div className="text-center py-5 text-muted">
              <i className="bi bi-building fs-1 d-block mb-3"></i>
              <p>Chưa có phòng nổi bật</p>
            </div>
          ) : (
            <div className="row g-4">
              {featuredRooms.map(room => (
                <div key={room.id} className="col-md-6 col-lg-4">
                  <RoomCard room={room} />
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── WHY CHOOSE US ─────────────────────────────────────────── */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center fw-bold mb-5">Tại sao chọn chúng tôi?</h2>
          <div className="row g-4 text-center">
            {[
              { icon: 'bi-shield-check', color: 'text-primary', title: 'Bảo mật cao', desc: 'Xác thực JWT, mã hóa dữ liệu end-to-end' },
              { icon: 'bi-clock-history', color: 'text-success', title: 'Đặt phòng nhanh', desc: 'Xác nhận tức thì, hỗ trợ 24/7' },
              { icon: 'bi-credit-card', color: 'text-warning', title: 'Thanh toán đa dạng', desc: 'Bank Transfer, MoMo, QR Code' },
              { icon: 'bi-star-fill', color: 'text-danger', title: 'Đánh giá minh bạch', desc: 'Review từ khách hàng đã lưu trú thực tế' },
            ].map((item, i) => (
              <div key={i} className="col-sm-6 col-lg-3">
                <div className="card border-0 shadow-sm h-100 p-4">
                  <i className={`bi ${item.icon} ${item.color} fs-1 mb-3`}></i>
                  <h5 className="fw-bold">{item.title}</h5>
                  <p className="text-muted small mb-0">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
