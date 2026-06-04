/**
 * Booking Service
 * Note: api.js interceptor already returns response.data (the full JSON body).
 * Backend wraps data in: { success, data: {...} } or { success, items, meta }
 */
import api from './api';

export const bookingService = {
  /** POST /api/bookings/ → { success, data: { booking, payment } } */
  createBooking: async (bookingData) => {
    const res = await api.post('/api/bookings/', bookingData);
    return res.data; // { booking, payment }
  },

  /** GET /api/bookings/my → { success, items, meta } */
  getMyBookings: async (params = {}) => {
    return api.get('/api/bookings/my', { params }); // caller uses .items, .meta
  },

  /** GET /api/bookings/ (ADMIN|OWNER) → { success, items, meta } */
  getAllBookings: async (params = {}) => {
    return api.get('/api/bookings/', { params }); // caller uses .items, .meta
  },

  /** GET /api/bookings/:id → { success, data: { booking } } */
  getBookingById: async (bookingId) => {
    const res = await api.get(`/api/bookings/${bookingId}`);
    return res.data?.booking || res.data;
  },

  /** PATCH /api/bookings/:id/confirm → { success, data: { booking } } */
  confirmBooking: async (bookingId) => {
    const res = await api.patch(`/api/bookings/${bookingId}/confirm`);
    return res.data?.booking || res.data;
  },

  /** PATCH /api/bookings/:id/complete → { success, data: { booking } } */
  completeBooking: async (bookingId) => {
    const res = await api.patch(`/api/bookings/${bookingId}/complete`);
    return res.data?.booking || res.data;
  },

  /** PATCH /api/bookings/:id/cancel → { success, data: { booking, penalty_info } } */
  cancelBooking: async (bookingId, reason = '') => {
    const res = await api.patch(`/api/bookings/${bookingId}/cancel`, { reason });
    return res.data; // { booking, penalty_info }
  },

  /** POST /api/bookings/:id/review → { success, data: { review } } */
  createReview: async (bookingId, reviewData) => {
    const res = await api.post(`/api/bookings/${bookingId}/review`, reviewData);
    return res.data?.review || res.data;
  },

  /** POST /api/payments/process → { success, data: { payment, booking } } */
  processPayment: async (bookingId, method = 'BANK_TRANSFER') => {
    const res = await api.post('/api/payments/process', { booking_id: bookingId, method });
    return res.data; // { payment, booking }
  },

  /**
   * GET /api/payments/info/:id
   * Returns structured payment instructions for a booking:
   *   { method, amount, payment_note, status, owner_id, instructions: { ... } }
   */
  getPaymentInfo: async (bookingId) => {
    const res = await api.get(`/api/payments/info/${bookingId}`);
    return res.data || res;
  },
};
