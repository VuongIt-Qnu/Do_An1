import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="text-center">
        <div className="display-1 fw-bold text-primary">404</div>
        <h2 className="fw-bold mt-3">Trang không tìm thấy</h2>
        <p className="text-muted mb-4">Trang bạn tìm kiếm không tồn tại hoặc đã bị xóa.</p>
        <Link to="/" className="btn btn-primary">
          <i className="bi bi-house me-2"></i>Về trang chủ
        </Link>
      </div>
    </div>
  );
}
