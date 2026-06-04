/**
 * Room Service
 * Note: api.js interceptor already returns response.data (the full JSON body).
 * Backend wraps data in: { success, data: {...} } or { success, items, meta }
 */
import api from './api';

export const roomService = {
  /** GET /api/rooms/ → { success, items, meta } */
  getRooms: async (params = {}) => {
    return api.get('/api/rooms/', { params }); // caller uses .items, .meta
  },

  /** GET /api/rooms/:id → { success, data: { room } } */
  getRoomById: async (roomId) => {
    const res = await api.get(`/api/rooms/${roomId}`);
    return res.data?.room || res.data;
  },

  /** GET /api/rooms/:id/availability → { success, data: { available, booked_dates } } */
  checkAvailability: async (roomId, checkIn, checkOut) => {
    const res = await api.get(`/api/rooms/${roomId}/availability`, {
      params: { check_in: checkIn, check_out: checkOut },
    });
    return res.data; // { available, booked_dates }
  },

  /** POST /api/rooms/ → { success, data: { room } } */
  createRoom: async (roomData) => {
    const res = await api.post('/api/rooms/', roomData);
    return res.data?.room || res.data;
  },

  /** PUT /api/rooms/:id → { success, data: { room } } */
  updateRoom: async (roomId, roomData) => {
    const res = await api.put(`/api/rooms/${roomId}`, roomData);
    return res.data?.room || res.data;
  },

  /** DELETE /api/rooms/:id → { success, message } */
  deleteRoom: async (roomId) => {
    return api.delete(`/api/rooms/${roomId}`);
  },
};
