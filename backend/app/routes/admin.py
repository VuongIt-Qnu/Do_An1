"""
Admin Routes — /api/admin
========================================
Tất cả endpoint yêu cầu role ADMIN.

GET    /dashboard              Thống kê tổng quan hệ thống
GET    /users                  Danh sách user (filter + phân trang)
GET    /users/:id              Chi tiết user
PUT    /users/:id              Cập nhật user (role, enabled, full_name)
PATCH  /users/:id/toggle       Khoá / mở khoá tài khoản
DELETE /users/:id              Xoá user (soft — đặt enabled=False)
GET    /hotels                 Danh sách khách sạn (kể cả chưa được duyệt)
PATCH  /hotels/:id/approve     Duyệt / từ chối khách sạn
GET    /bookings               Danh sách booking toàn hệ thống
GET    /logs                   Audit logs từ MongoDB
"""
import sqlalchemy as sa
from datetime import date
from flask import Blueprint, request

from ..extensions import db, mongo
from ..models.user import User
from ..models.hotel import Hotel
from ..models.booking import Booking
from ..models.room import Room
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..utils.validators import sanitize_string
from ..middleware.auth_middleware import role_required, get_current_user
from ..services.logging_service import log_audit

admin_bp = Blueprint("admin", __name__)


# ── GET /api/admin/dashboard ────────────────────────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@role_required("ADMIN")
def dashboard():
    """
    Thống kê tổng quan hệ thống.
    """
    today          = date.today()
    first_of_month = today.replace(day=1)

    total_users    = User.query.filter_by(role="USER").count()
    total_owners   = User.query.filter_by(role="OWNER").count()
    locked_users   = User.query.filter_by(enabled=False).count()

    total_hotels   = Hotel.query.filter_by(enabled=True).count()
    approved_hotels = Hotel.query.filter_by(enabled=True, approved=True).count()
    pending_hotels  = Hotel.query.filter_by(enabled=True, approved=False).count()

    total_rooms    = Room.query.count()
    occupied_rooms = Room.query.filter_by(status="OCCUPIED").count()

    total_bookings   = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status="PENDING").count()
    confirmed_bookings = Booking.query.filter_by(status="CONFIRMED").count()
    completed_bookings = Booking.query.filter_by(status="COMPLETED").count()
    cancelled_bookings = Booking.query.filter_by(status="CANCELLED").count()

    bookings_today = Booking.query.filter(
        sa.cast(Booking.created_at, sa.Date) == today
    ).count()

    bookings_this_month = Booking.query.filter(
        Booking.created_at >= first_of_month
    ).count()

    total_revenue = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(Booking.status.in_(["CONFIRMED", "COMPLETED"]))
        .scalar() or 0
    )

    revenue_this_month = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.status.in_(["CONFIRMED", "COMPLETED"]),
            Booking.created_at >= first_of_month,
        ).scalar() or 0
    )

    occupancy_rate = round(occupied_rooms / total_rooms * 100, 2) if total_rooms else 0

    return success_response(data={
        "users": {
            "total_users":   total_users,
            "total_owners":  total_owners,
            "locked_users":  locked_users,
        },
        "hotels": {
            "total_hotels":   total_hotels,
            "approved":       approved_hotels,
            "pending_approval": pending_hotels,
        },
        "rooms": {
            "total_rooms":    total_rooms,
            "occupied_rooms": occupied_rooms,
            "occupancy_rate": occupancy_rate,
        },
        "bookings": {
            "total":     total_bookings,
            "pending":   pending_bookings,
            "confirmed": confirmed_bookings,
            "completed": completed_bookings,
            "cancelled": cancelled_bookings,
            "today":     bookings_today,
            "this_month": bookings_this_month,
        },
        "revenue": {
            "total":      total_revenue,
            "this_month": revenue_this_month,
        },
    })


# ── GET /api/admin/users ────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@role_required("ADMIN")
def list_users():
    """
    Danh sách user toàn hệ thống.
    Query params: role, enabled (true|false), search, page, per_page
    """
    role_filter    = request.args.get("role", "").upper()
    enabled_filter = request.args.get("enabled")
    search         = request.args.get("search", "").strip()
    page, per_page = get_page_args()

    query = User.query

    if role_filter in ("USER", "OWNER", "ADMIN"):
        query = query.filter(User.role == role_filter)
    if enabled_filter is not None:
        query = query.filter(User.enabled == (enabled_filter.lower() in ("true", "1")))
    if search:
        query = query.filter(
            sa.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[u.to_dict() for u in users],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/admin/users/:id ────────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@role_required("ADMIN")
def get_user(user_id):
    """Chi tiết một user kèm số lượng booking."""
    user = db.session.get(User, user_id)
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    data = user.to_dict()
    data["total_bookings"]     = Booking.query.filter_by(user_id=user_id).count()
    data["completed_bookings"] = Booking.query.filter_by(
        user_id=user_id, status="COMPLETED"
    ).count()

    if user.role == "OWNER":
        data["total_hotels"] = Hotel.query.filter_by(owner_id=user_id, enabled=True).count()

    return success_response(data={"user": data})


# ── PUT /api/admin/users/:id ────────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@role_required("ADMIN")
def update_user(user_id):
    """
    Cập nhật thông tin user.
    Body: { full_name?, role?, enabled? }
    Không được tự đổi role của chính mình.
    """
    admin = get_current_user()
    user  = db.session.get(User, user_id)
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    data = request.get_json(silent=True) or {}

    # Admin không được tự đổi role của chính mình
    if user.id == admin.id and "role" in data:
        return error_response("Không thể thay đổi role của chính mình", 400)
    changes = {}

    if "full_name" in data:
        user.full_name = sanitize_string(str(data["full_name"]), 100)
        changes["full_name"] = user.full_name

    if "role" in data:
        new_role = str(data["role"]).upper()
        if new_role not in ("USER", "OWNER", "ADMIN"):
            return error_response("Role không hợp lệ. Cho phép: USER, OWNER, ADMIN", 400)
        user.role = new_role
        changes["role"] = new_role

    if "enabled" in data:
        user.enabled = bool(data["enabled"])
        changes["enabled"] = user.enabled

    db.session.commit()

    log_audit(
        "ADMIN_USER_UPDATED",
        user_id=admin.id,
        target_type="user",
        target_id=user_id,
        details=changes,
    )

    return success_response(data={"user": user.to_dict()},
                            message="Cập nhật người dùng thành công")


# ── PATCH /api/admin/users/:id/toggle ──────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/toggle", methods=["PATCH"])
@role_required("ADMIN")
def toggle_user(user_id):
    """
    Khoá hoặc mở khoá tài khoản.
    Không thể khoá chính mình.
    """
    admin = get_current_user()
    if admin.id == user_id:
        return error_response("Không thể khoá tài khoản của chính mình", 400)

    user = db.session.get(User, user_id)
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    user.enabled = not user.enabled
    db.session.commit()

    action = "ADMIN_USER_UNLOCKED" if user.enabled else "ADMIN_USER_LOCKED"
    log_audit(action, user_id=admin.id, target_type="user", target_id=user_id)

    msg = f"Tài khoản đã được {'mở khoá' if user.enabled else 'khoá'}"
    return success_response(data={"user": user.to_dict()}, message=msg)


# ── DELETE /api/admin/users/:id ─────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_user(user_id):
    """
    Vô hiệu hoá user (soft-delete → enabled=False).
    Không xoá cứng để giữ lịch sử booking.
    """
    admin = get_current_user()
    if admin.id == user_id:
        return error_response("Không thể xoá tài khoản của chính mình", 400)

    user = db.session.get(User, user_id)
    if not user:
        return error_response("Người dùng không tồn tại", 404)

    user.enabled = False
    db.session.commit()

    log_audit("ADMIN_USER_DELETED", user_id=admin.id, target_type="user", target_id=user_id)
    return success_response(message="Tài khoản người dùng đã bị vô hiệu hoá")


# ── GET /api/admin/hotels ────────────────────────────────────────────────────
@admin_bp.route("/hotels", methods=["GET"])
@role_required("ADMIN")
def list_hotels():
    """
    Danh sách toàn bộ khách sạn (kể cả chưa được duyệt / đã bị vô hiệu hoá).
    Query params: approved (true|false), enabled (true|false), search, page, per_page
    """
    approved_filter = request.args.get("approved")
    enabled_filter  = request.args.get("enabled")
    search          = request.args.get("search", "").strip()
    page, per_page  = get_page_args()

    query = Hotel.query

    if approved_filter is not None:
        query = query.filter(Hotel.approved == (approved_filter.lower() in ("true", "1")))
    if enabled_filter is not None:
        query = query.filter(Hotel.enabled == (enabled_filter.lower() in ("true", "1")))
    if search:
        query = query.filter(
            sa.or_(
                Hotel.name.ilike(f"%{search}%"),
                Hotel.city.ilike(f"%{search}%"),
            )
        )

    total  = query.count()
    hotels = (
        query.order_by(Hotel.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[h.to_dict(include_stats=True) for h in hotels],
        total=total, page=page, per_page=per_page
    )


# ── PATCH /api/admin/hotels/:id/approve ─────────────────────────────────────
@admin_bp.route("/hotels/<int:hotel_id>/approve", methods=["PATCH"])
@role_required("ADMIN")
def approve_hotel(hotel_id):
    """
    Duyệt hoặc từ chối khách sạn.
    Body: { approved: true | false, reason? }
    """
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)

    data     = request.get_json(silent=True) or {}
    approved = bool(data.get("approved", True))
    reason   = data.get("reason", "")

    hotel.approved = approved
    db.session.commit()

    admin = get_current_user()
    log_audit(
        "ADMIN_HOTEL_APPROVED" if approved else "ADMIN_HOTEL_REJECTED",
        user_id=admin.id,
        target_type="hotel",
        target_id=hotel_id,
        details={"reason": reason},
    )

    msg = "Khách sạn đã được duyệt" if approved else "Khách sạn đã bị từ chối"
    return success_response(data={"hotel": hotel.to_dict()}, message=msg)


# ── GET /api/admin/bookings ──────────────────────────────────────────────────
@admin_bp.route("/bookings", methods=["GET"])
@role_required("ADMIN")
def list_bookings():
    """
    Danh sách toàn bộ booking hệ thống.
    Query params: status, hotel_id, user_id, search, page, per_page
    """
    status_filter  = request.args.get("status", "").upper()
    hotel_id_filter = request.args.get("hotel_id", type=int)
    user_id_filter  = request.args.get("user_id", type=int)
    search          = request.args.get("search", "").strip()
    page, per_page  = get_page_args()

    query = Booking.query

    if status_filter in ("PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"):
        query = query.filter(Booking.status == status_filter)
    if hotel_id_filter:
        query = query.filter(Booking.hotel_id == hotel_id_filter)
    if user_id_filter:
        query = query.filter(Booking.user_id == user_id_filter)
    if search:
        query = query.filter(
            sa.or_(
                Booking.customer_name.ilike(f"%{search}%"),
                Booking.customer_email.ilike(f"%{search}%"),
            )
        )

    total    = query.count()
    bookings = (
        query.order_by(Booking.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[b.to_dict() for b in bookings],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/admin/logs ──────────────────────────────────────────────────────
@admin_bp.route("/logs", methods=["GET"])
@role_required("ADMIN")
def get_audit_logs():
    """
    Đọc audit logs từ MongoDB.
    Query params: action, user_id, target_type, page, per_page
    """
    page, per_page  = get_page_args()
    action_filter   = request.args.get("action")
    user_id_filter  = request.args.get("user_id", type=int)
    target_type     = request.args.get("target_type")

    mongo_filter = {}
    if action_filter:
        mongo_filter["action"] = action_filter
    if user_id_filter:
        mongo_filter["user_id"] = user_id_filter
    if target_type:
        mongo_filter["target_type"] = target_type

    try:
        total = mongo.db.audit_logs.count_documents(mongo_filter)
        logs  = list(
            mongo.db.audit_logs.find(mongo_filter)
            .sort("created_at", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        for log in logs:
            log["_id"] = str(log["_id"])
            if "created_at" in log and hasattr(log["created_at"], "isoformat"):
                log["created_at"] = log["created_at"].isoformat()
    except Exception:
        logs  = []
        total = 0

    return paginated_response(items=logs, total=total, page=page, per_page=per_page)
