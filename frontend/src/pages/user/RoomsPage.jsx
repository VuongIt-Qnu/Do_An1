/**
 * RoomsPage
 * Public room listing with filters, search, and pagination.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { roomService } from '../../services/roomService';
import RoomCard from '../../components/RoomCard';
import LoadingSpinner from '../../components/LoadingSpinner';

const ROOM_TYPES = ['Standard', 'Deluxe', 'Suite', 'Presidential', 'Family'];

export default function RoomsPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  // Filter state
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    room_type: '',
    min_price: '',
    max_price: '',
    capacity: '',
    status: 'AVAILABLE',
  });

  // Data state
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, per_page: 12, total: 0, pages: 1 });

  // ── Fetch rooms ──────────────────────────────────────────────────
  const fetchRooms = useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const params = {
        ...filters,
        page,
        per_page: pagination.per_page,
      };
      // Remove empty params
      Object.keys(params).forEach(k => !params[k] && delete params[k]);

      const data = await roomService.getRooms(params);
      setRooms(data.items || []);
      setPagination(prev => ({
        ...prev,
        page: data.meta?.page ?? prev.page,
        total: data.meta?.total ?? 0,
        pages: data.meta?.total_pages ?? Math.ceil((data.meta?.total ?? 0) / prev.per_page),
      }));
    } catch {
      setRooms([]);
    } finally {
      setLoading(false);
    }
  }, [filters, pagination.per_page]);

  useEffect(() => {
    fetchRooms(1);
  }, [filters]); // Re-fetch when filters change

  // ── Filter Handlers ──────────────────────────────────────────────
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters({
      search: '', room_type: '', min_price: '',
      max_price: '', capacity: '', status: 'AVAILABLE',
    });
    setSearchParams({});
  };

  return (
    <div className="py-4">
      <div className="container">
        <h1 className="fw-bold mb-1">{t('rooms.title')}</h1>
        <p className="text-muted mb-4">
          {loading ? '...' : `${pagination.total} phòng khả dụng`}
        </p>

        <div className="row g-4">
          {/* ── SIDEBAR FILTERS ─────────────────────────────────── */}
          <div className="col-lg-3">
            <div className="card border-0 shadow-sm sticky-top" style={{ top: '1rem' }}>
              <div className="card-body">
                <h6 className="fw-bold mb-3">
                  <i className="bi bi-sliders me-2"></i>{t('rooms.filter')}
                </h6>

                {/* Search */}
                <div className="mb-3">
                  <label className="form-label small fw-semibold">Tìm kiếm</label>
                  <input
                    type="text"
                    className="form-control form-control-sm"
                    placeholder={t('home.searchPlaceholder')}
                    value={filters.search}
                    onChange={e => handleFilterChange('search', e.target.value)}
                  />
                </div>

                {/* Room Type */}
                <div className="mb-3">
                  <label className="form-label small fw-semibold">{t('rooms.roomType')}</label>
                  <select
                    className="form-select form-select-sm"
                    value={filters.room_type}
                    onChange={e => handleFilterChange('room_type', e.target.value)}
                  >
                    <option value="">-- Tất cả --</option>
                    {ROOM_TYPES.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Capacity */}
                <div className="mb-3">
                  <label className="form-label small fw-semibold">{t('rooms.capacity')}</label>
                  <select
                    className="form-select form-select-sm"
                    value={filters.capacity}
                    onChange={e => handleFilterChange('capacity', e.target.value)}
                  >
                    <option value="">-- Tất cả --</option>
                    {[1, 2, 3, 4, 5].map(n => (
                      <option key={n} value={n}>{n}+ khách</option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div className="mb-3">
                  <label className="form-label small fw-semibold">{t('rooms.priceRange')}</label>
                  <div className="d-flex gap-2">
                    <input
                      type="number"
                      className="form-control form-control-sm"
                      placeholder="Min"
                      min="0"
                      value={filters.min_price}
                      onChange={e => handleFilterChange('min_price', e.target.value)}
                    />
                    <input
                      type="number"
                      className="form-control form-control-sm"
                      placeholder="Max"
                      min="0"
                      value={filters.max_price}
                      onChange={e => handleFilterChange('max_price', e.target.value)}
                    />
                  </div>
                </div>

                {/* Reset Button */}
                <button
                  className="btn btn-outline-secondary btn-sm w-100"
                  onClick={handleResetFilters}
                >
                  <i className="bi bi-arrow-counterclockwise me-1"></i>{t('common.reset')}
                </button>
              </div>
            </div>
          </div>

          {/* ── ROOM GRID ─────────────────────────────────────────── */}
          <div className="col-lg-9">
            {loading ? (
              <LoadingSpinner />
            ) : rooms.length === 0 ? (
              <div className="text-center py-5 text-muted">
                <i className="bi bi-search fs-1 d-block mb-3"></i>
                <h5>{t('rooms.noRooms')}</h5>
                <button className="btn btn-link" onClick={handleResetFilters}>
                  Xóa bộ lọc
                </button>
              </div>
            ) : (
              <>
                <div className="row g-3">
                  {rooms.map(room => (
                    <div key={room.id} className="col-md-6 col-xl-4">
                      <RoomCard room={room} />
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {pagination.pages > 1 && (
                  <nav className="mt-4 d-flex justify-content-center">
                    <ul className="pagination">
                      <li className={`page-item ${pagination.page <= 1 ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => fetchRooms(pagination.page - 1)}>
                          <i className="bi bi-chevron-left"></i>
                        </button>
                      </li>
                      {Array.from({ length: pagination.pages }, (_, i) => i + 1)
                        .filter(p => Math.abs(p - pagination.page) <= 2)
                        .map(p => (
                          <li key={p} className={`page-item ${p === pagination.page ? 'active' : ''}`}>
                            <button className="page-link" onClick={() => fetchRooms(p)}>{p}</button>
                          </li>
                        ))}
                      <li className={`page-item ${pagination.page >= pagination.pages ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => fetchRooms(pagination.page + 1)}>
                          <i className="bi bi-chevron-right"></i>
                        </button>
                      </li>
                    </ul>
                  </nav>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
