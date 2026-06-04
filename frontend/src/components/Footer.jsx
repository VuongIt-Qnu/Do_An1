/**
 * Footer Component
 */
import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-light mt-auto py-4">
      <div className="container">
        <div className="row g-4">
          {/* Brand */}
          <div className="col-md-4">
            <h5 className="fw-bold mb-3">
              <i className="bi bi-building me-2 text-warning"></i>
              <span className="text-warning">Hotel</span>MS
            </h5>
            <p className="text-muted small">
              Hệ thống quản lý khách sạn hiện đại, kết nối khách hàng với
              những trải nghiệm lưu trú tuyệt vời.
            </p>
          </div>

          {/* Quick Links */}
          <div className="col-md-2">
            <h6 className="fw-semibold mb-3">Liên kết</h6>
            <ul className="list-unstyled">
              <li><Link to="/" className="text-muted text-decoration-none small">Trang chủ</Link></li>
              <li><Link to="/rooms" className="text-muted text-decoration-none small">Danh sách phòng</Link></li>
              <li><Link to="/login" className="text-muted text-decoration-none small">Đăng nhập</Link></li>
              <li><Link to="/register" className="text-muted text-decoration-none small">Đăng ký</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div className="col-md-3">
            <h6 className="fw-semibold mb-3">Hỗ trợ</h6>
            <ul className="list-unstyled">
              <li className="text-muted small">
                <i className="bi bi-envelope me-2"></i>vuong19092004@gmail.com
              </li>
              <li className="text-muted small">
                <i className="bi bi-telephone me-2"></i>0383468103
              </li>
              <li className="text-muted small">
                <i className="bi bi-clock me-2"></i>24/7 Hỗ trợ
              </li>
            </ul>
          </div>

          {/* Tech Stack */}
          <div className="col-md-3">
            <h6 className="fw-semibold mb-3">Công nghệ</h6>
            <div className="d-flex flex-wrap gap-1">
              {['ReactJS', 'Flask', 'PostgreSQL', 'MongoDB', 'Docker'].map(tech => (
                <span key={tech} className="badge bg-secondary small">{tech}</span>
              ))}
            </div>
            <p className="text-muted small mt-2">CNPM2 — v2.0.0</p>
          </div>
        </div>

        <hr className="border-secondary" />
        <div className="text-center text-muted small">
          © {currentYear} HotelMS — Đồ án Công nghệ Phần mềm 2
        </div>
      </div>
    </footer>
  );
}
