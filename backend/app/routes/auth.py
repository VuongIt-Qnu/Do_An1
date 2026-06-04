"""
Auth Routes — /api/auth
========================================
POST   /register          Đăng ký tài khoản mới
POST   /login             Đăng nhập → JWT access + refresh token
POST   /refresh           Làm mới access token
POST   /logout            Đăng xuất (blacklist token)
POST   /forgot-password   Gửi email link đặt lại mật khẩu
POST   /reset-password    Đặt lại mật khẩu qua token
GET    /me                Lấy thông tin cá nhân
PUT    /me                Cập nhật thông tin cá nhân
PUT    /me/change-password Đổi mật khẩu (cần mật khẩu cũ)
"""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt, decode_token
)

from ..extensions import db, token_blacklist
from ..models.user import User
from ..utils.response_helpers import success_response, error_response
from ..utils.validators import is_valid_email, sanitize_string
from ..middleware.auth_middleware import get_current_user
from ..services.logging_service import log_audit

auth_bp = Blueprint("auth", __name__)


# ── POST /api/auth/register ─────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Đăng ký tài khoản USER mới.
    Body: { full_name, email, password, phone_number? }
    Returns: { user, access_token, refresh_token }
    """
    data = request.get_json(silent=True) or {}

    full_name    = sanitize_string(data.get("full_name", ""), 100)
    email        = sanitize_string(data.get("email", ""), 100).lower().strip()
    phone_number = sanitize_string(data.get("phone_number", ""), 20)
    password     = data.get("password", "")

    # Validation
    errors = {}
    if not full_name:
        errors["full_name"] = "Họ tên không được để trống"
    if not email:
        errors["email"] = "Email không được để trống"
    elif not is_valid_email(email):
        errors["email"] = "Email không hợp lệ"
    if not password:
        errors["password"] = "Mật khẩu không được để trống"
    elif len(password) < 6:
        errors["password"] = "Mật khẩu phải ít nhất 6 ký tự"

    if errors:
        return error_response("Dữ liệu không hợp lệ", 422, errors)

    # Kiểm tra email trùng
    if User.query.filter_by(email=email).first():
        return error_response("Email đã được đăng ký", 409)

    user = User(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        role="USER",
        enabled=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Phát token ngay sau đăng ký (auto-login)
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    log_audit("USER_REGISTERED", user_id=user.id,
              target_type="user", target_id=user.id,
              details={"email": email})

    return success_response(
        data={
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Đăng ký thành công",
        status_code=201,
    )


# ── POST /api/auth/login ────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Đăng nhập — xác thực email/password, trả về JWT.
    Body: { email, password }
    Returns: { user, access_token, refresh_token }
    """
    data     = request.get_json(silent=True) or {}
    email    = sanitize_string(data.get("email", ""), 100).lower().strip()
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email và mật khẩu không được để trống", 400)

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return error_response("Email hoặc mật khẩu không đúng", 401)

    if not user.enabled:
        return error_response("Tài khoản đã bị khoá. Vui lòng liên hệ hỗ trợ.", 403)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    log_audit("USER_LOGIN", user_id=user.id,
              target_type="user", target_id=user.id)

    return success_response(data={
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, message="Đăng nhập thành công")


# ── POST /api/auth/refresh ──────────────────────────────────────────────────
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Làm mới access token bằng refresh token.
    Header: Authorization: Bearer <refresh_token>
    Returns: { access_token }
    """
    user_id = int(get_jwt_identity())

    # Kiểm tra user vẫn tồn tại và chưa bị khoá
    user = db.session.get(User, user_id)
    if not user or not user.enabled:
        return error_response("Tài khoản không hợp lệ", 401)

    new_access_token = create_access_token(identity=str(user_id))
    return success_response(data={"access_token": new_access_token})


# ── POST /api/auth/logout ───────────────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Đăng xuất hoàn toàn:
    1. Blacklist access token hiện tại (từ Authorization header).
    2. Blacklist refresh token (nếu gửi kèm trong body { refresh_token }).
    Body (optional): { "refresh_token": "<refresh_jwt>" }
    """
    # 1. Blacklist access token
    access_jti = get_jwt()["jti"]
    token_blacklist.add(access_jti)

    # 2. Blacklist refresh token nếu client gửi kèm
    data = request.get_json(silent=True) or {}
    refresh_token_str = data.get("refresh_token", "")
    if refresh_token_str:
        try:
            decoded = decode_token(refresh_token_str)
            refresh_jti = decoded.get("jti")
            if refresh_jti:
                token_blacklist.add(refresh_jti)
        except Exception:
            pass  # token không hợp lệ → bỏ qua, vẫn logout thành công

    user = get_current_user()
    if user:
        log_audit("USER_LOGOUT", user_id=user.id,
                  target_type="user", target_id=user.id)

    return success_response(message="Đăng xuất thành công")


# ── POST /api/auth/forgot-password ─────────────────────────────────────────
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Tạo token đặt lại mật khẩu và gửi email.
    Body: { email }
    Luôn trả 200 để tránh email enumeration.
    """
    data  = request.get_json(silent=True) or {}
    email = sanitize_string(data.get("email", ""), 100).lower().strip()

    if not email:
        return error_response("Email không được để trống", 400)

    user = User.query.filter_by(email=email, enabled=True).first()

    if user:
        token = str(uuid.uuid4())
        user.reset_token        = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=2)
        db.session.commit()

        try:
            from ..services.email_service import send_reset_password_email
            from flask import current_app
            reset_link = (
                f"{current_app.config['FRONTEND_URL']}"
                f"/reset-password?token={token}"
            )
            send_reset_password_email(user, reset_link)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Reset email failed: {e}")

    return success_response(
        message="Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn trong vài phút."
    )


# ── POST /api/auth/reset-password ──────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Đặt lại mật khẩu qua token.
    Body: { token, new_password }
    """
    data         = request.get_json(silent=True) or {}
    token        = (data.get("token") or "").strip()
    new_password = data.get("new_password", "")

    if not token:
        return error_response("Token không được để trống", 400)
    if not new_password or len(new_password) < 6:
        return error_response("Mật khẩu mới phải ít nhất 6 ký tự", 400)

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return error_response("Token không hợp lệ hoặc đã hết hạn", 400)
    if not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return error_response("Token đã hết hạn. Vui lòng yêu cầu lại.", 400)

    user.set_password(new_password)
    user.reset_token        = None
    user.reset_token_expiry = None
    db.session.commit()

    log_audit("PASSWORD_RESET", user_id=user.id,
              target_type="user", target_id=user.id)

    return success_response(message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập.")


# ── GET /api/auth/me ────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Lấy thông tin tài khoản hiện tại."""
    user = get_current_user()
    if not user:
        return error_response("Người dùng không tồn tại", 404)
    return success_response(data={"user": user.to_dict()})


# ── PUT /api/auth/me ────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Cập nhật thông tin cá nhân (không thay đổi được role/email).
    Body: { full_name?, phone_number?, passport?, nationality?, address? }
    """
    user = get_current_user()
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    data = request.get_json(silent=True) or {}

    updatable = {
        "full_name":    100,
        "phone_number": 20,
        "passport":     50,
        "nationality":  50,
        "address":      500,
    }
    for field, max_len in updatable.items():
        if field in data:
            setattr(user, field, sanitize_string(str(data[field]), max_len))

    db.session.commit()
    return success_response(data={"user": user.to_dict()},
                            message="Cập nhật thông tin thành công")


# ── PUT /api/auth/me/change-password ───────────────────────────────────────
@auth_bp.route("/me/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    Đổi mật khẩu (yêu cầu mật khẩu hiện tại để xác nhận).
    Body: { current_password, new_password }
    """
    user = get_current_user()
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    data             = request.get_json(silent=True) or {}
    current_password = data.get("current_password", "")
    new_password     = data.get("new_password", "")

    if not current_password:
        return error_response("Mật khẩu hiện tại không được để trống", 400)
    if not new_password or len(new_password) < 6:
        return error_response("Mật khẩu mới phải ít nhất 6 ký tự", 400)
    if current_password == new_password:
        return error_response("Mật khẩu mới phải khác mật khẩu hiện tại", 400)

    if not user.check_password(current_password):
        return error_response("Mật khẩu hiện tại không đúng", 401)

    user.set_password(new_password)
    db.session.commit()

    log_audit("PASSWORD_CHANGED", user_id=user.id,
              target_type="user", target_id=user.id)

    return success_response(message="Đổi mật khẩu thành công")
