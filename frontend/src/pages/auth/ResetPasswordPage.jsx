/**
 * ResetPasswordPage
 * Placeholder page for reset password flow.
 */
import React from 'react';
import { Link } from 'react-router-dom';

export default function ResetPasswordPage() {
  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-sm-10 col-md-7 col-lg-5">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-5 text-center">
                <h3 className="mb-3">Đặt lại mật khẩu</h3>
                <p className="text-muted mb-4">
                  Tính năng này đang được phát triển. Vui lòng quay lại trang đăng nhập hoặc liên hệ quản trị viên.
                </p>
                <Link to="/login" className="btn btn-primary">
                  Quay lại Đăng nhập
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
