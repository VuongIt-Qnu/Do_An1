"""
Hotels Routes — /api/hotels
========================================
GET    /                   Danh sách khách sạn (public, filter + phân trang)
GET    /:id                Chi tiết khách sạn + danh sách phòng trống
POST   /                   Tạo khách sạn  [ADMIN | OWNER]
PUT    /:id                Cập nhật khách sạn [ADMIN | OWNER]
DELETE /:id                Vô hiệu hoá [ADMIN]
PATCH  /:id/approve        Duyệt khách sạn [ADMIN]
GET    /:id/stats          Thống kê khách sạn [ADMIN | OWNER]
"""
import sqlalchemy as sa
from datetime import date
from flask import Blueprint, request

from ..extensions import db
from ..models.hotel import Hotel
from ..models.room import Room
from ..models.booking import Booking
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..utils.validators import sanitize_string
from ..middleware.auth_middleware import role_required, get_current_user, optional_jwt

hotels_bp = Blueprint("hotels", __name__)


# ── GET /api/hotels/ ────────────────────────────────────────────────────────
@hotels_bp.route("/", methods=["GET"])
@optional_jwt
def list_hotels():
    """
    Danh sách khách sạn đã được duyệt và đang hoạt động.
    Query params:
        city        — lọc theo thành phố
        search      — tìm theo tên
        star_rating — lọc theo số sao (1-5)
        page, per_page
    """
    city        = request.args.get("city", "").strip()
    search      = request.args.get("search", "").strip()
    star_rating = request.args.get("star_rating", type=int)
    page, per_page = get_page_args(default_per_page=12)

    query = Hotel.query.filter_by(enabled=True, approved=True)

    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            sa.or_(
                Hotel.name.ilike(f"%{search}%"),
                Hotel.description.ilike(f"%{search}%"),
            )
        )
    if star_rating:
        query = query.filter(Hotel.star_rating == star_rating)

    total  = query.count()
    hotels = (
        query.order_by(Hotel.star_rating.desc(), Hotel.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[h.to_dict(include_stats=True) for h in hotels],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/hotels/:id ─────────────────────────────────────────────────────
@hotels_bp.route("/<int:hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    """
    Chi tiết khách sạn kèm danh sách phòng đang AVAILABLE.
    """
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel or not hotel.enabled:
        return error_response("Khách sạn không tồn tại", 404)

    data = hotel.to_dict(include_stats=True)
    data["rooms"] = [
        r.to_dict()
        for r in hotel.rooms.filter_by(status="AVAILABLE")
                             .order_by(Room.price_per_night.asc())
                             .all()
    ]
    return success_response(data={"hotel": data})


# ── POST /api/hotels/ ───────────────────────────────────────────────────────
@hotels_bp.route("/", methods=["POST"])
@role_required("ADMIN", "OWNER")
def create_hotel():
    """
    Tạo khách sạn mới.
    OWNER tạo cho chính mình (approved=False, chờ ADMIN duyệt).
    ADMIN tạo → tự động approved=True.
    Body: { name, city, address?, description?, phone?, email?, star_rating? }
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    name = sanitize_string(data.get("name", ""), 200)
    city = sanitize_string(data.get("city", ""), 100)

    if not name:
        return error_response("Tên khách sạn là bắt buộc", 400)

    owner_id = user.id if user.role == "OWNER" else (data.get("owner_id") or user.id)
    approved = True if user.role == "ADMIN" else False  # OWNER cần ADMIN duyệt

    hotel = Hotel(
        owner_id=int(owner_id),
        name=name,
        city=city,
        address=sanitize_string(data.get("address", ""), 500),
        description=sanitize_string(data.get("description", ""), 2000),
        phone=sanitize_string(data.get("phone", ""), 20),
        email=sanitize_string(data.get("email", ""), 100),
        star_rating=max(1, min(5, int(data.get("star_rating", 3)))),
        enabled=True,
        approved=approved,
    )
    db.session.add(hotel)
    db.session.commit()

    msg = "Tạo khách sạn thành công" if approved else \
          "Khách sạn đã được tạo và đang chờ admin duyệt"

    return success_response(data={"hotel": hotel.to_dict()},
                            message=msg, status_code=201)


# ── PUT /api/hotels/:id ─────────────────────────────────────────────────────
@hotels_bp.route("/<int:hotel_id>", methods=["PUT"])
@role_required("ADMIN", "OWNER")
def update_hotel(hotel_id):
    """
    Cập nhật thông tin khách sạn.
    OWNER: chỉ cập nhật khách sạn của mình.
    """
    user  = get_current_user()
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)

    if user.role == "OWNER" and hotel.owner_id != user.id:
        return error_response("Bạn không sở hữu khách sạn này", 403)

    data = request.get_json(silent=True) or {}

    fields = {
        "name":        200,
        "city":        100,
        "address":     500,
        "description": 2000,
        "phone":       20,
        "email":       100,
    }
    for field, max_len in fields.items():
        if field in data:
            setattr(hotel, field, sanitize_string(str(data[field]), max_len))

    if "star_rating" in data:
        hotel.star_rating = max(1, min(5, int(data["star_rating"])))

    db.session.commit()
    return success_response(data={"hotel": hotel.to_dict()},
                            message="Cập nhật khách sạn thành công")


# ── DELETE /api/hotels/:id ──────────────────────────────────────────────────
@hotels_bp.route("/<int:hotel_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_hotel(hotel_id):
    """
    Vô hiệu hoá khách sạn (soft-delete, ADMIN only).
    """
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)

    hotel.enabled = False
    db.session.commit()
    return success_response(message="Khách sạn đã bị vô hiệu hoá")


# ── PATCH /api/hotels/:id/approve ──────────────────────────────────────────
@hotels_bp.route("/<int:hotel_id>/approve", methods=["PATCH"])
@role_required("ADMIN")
def approve_hotel(hotel_id):
    """
    Duyệt hoặc từ chối khách sạn (ADMIN only).
    Body: { approved: true | false }
    """
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)

    data     = request.get_json(silent=True) or {}
    approved = bool(data.get("approved", True))

    hotel.approved = approved
    db.session.commit()

    msg = "Khách sạn đã được duyệt" if approved else "Khách sạn đã bị từ chối"
    return success_response(data={"hotel": hotel.to_dict()}, message=msg)


# ── GET /api/hotels/:id/stats ───────────────────────────────────────────────
@hotels_bp.route("/<int:hotel_id>/stats", methods=["GET"])
@role_required("ADMIN", "OWNER")
def hotel_stats(hotel_id):
    """
    Thống kê chi tiết cho một khách sạn.
    OWNER: chỉ xem được khách sạn của mình.
    """
    user  = get_current_user()
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)

    if user.role == "OWNER" and hotel.owner_id != user.id:
        return error_response("Bạn không sở hữu khách sạn này", 403)

    today          = date.today()
    first_of_month = today.replace(day=1)

    total_rooms     = hotel.rooms.count()
    available_rooms = hotel.rooms.filter_by(status="AVAILABLE").count()
    occupied_rooms  = hotel.rooms.filter_by(status="OCCUPIED").count()

    total_bookings     = hotel.bookings.count()
    pending_bookings   = hotel.bookings.filter_by(status="PENDING").count()
    confirmed_bookings = hotel.bookings.filter_by(status="CONFIRMED").count()
    completed_bookings = hotel.bookings.filter_by(status="COMPLETED").count()

    bookings_this_month = hotel.bookings.filter(
        Booking.created_at >= first_of_month
    ).count()

    total_revenue = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.hotel_id == hotel_id,
            Booking.status.in_(["CONFIRMED", "COMPLETED"])
        ).scalar() or 0
    )

    revenue_this_month = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.hotel_id == hotel_id,
            Booking.status.in_(["CONFIRMED", "COMPLETED"]),
            Booking.created_at >= first_of_month,
        ).scalar() or 0
    )

    occupancy_rate = round(occupied_rooms / total_rooms * 100, 2) if total_rooms else 0

    return success_response(data={
        "hotel_id":            hotel_id,
        "hotel_name":          hotel.name,
        "total_rooms":         total_rooms,
        "available_rooms":     available_rooms,
        "occupied_rooms":      occupied_rooms,
        "occupancy_rate":      occupancy_rate,
        "total_bookings":      total_bookings,
        "pending_bookings":    pending_bookings,
        "confirmed_bookings":  confirmed_bookings,
        "completed_bookings":  completed_bookings,
        "bookings_this_month": bookings_this_month,
        "total_revenue":       total_revenue,
        "revenue_this_month":  revenue_this_month,
    })
