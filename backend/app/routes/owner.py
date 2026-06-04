"""
Owner Routes — /api/owner
========================================
Tất cả endpoint yêu cầu role OWNER.
Quản lý khách sạn, phòng, booking và doanh thu của chính owner đó.

GET    /dashboard              Thống kê tổng quan
GET    /hotels                 Danh sách khách sạn của owner
GET    /hotel/:id/stats        Thống kê chi tiết một khách sạn
GET    /bookings               Danh sách booking (theo hotel của owner)
GET    /rooms                  Danh sách phòng
GET    /revenue                Thống kê doanh thu
"""
import sqlalchemy as sa
from datetime import date
from flask import Blueprint, request

from ..extensions import db
from ..models.hotel import Hotel
from ..models.room import Room
from ..models.booking import Booking
from ..models.payment import Payment
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..middleware.auth_middleware import role_required, get_current_user

owner_bp = Blueprint("owner", __name__)


def _get_owner_hotel_ids(user_id: int) -> list[int]:
    """Helper: danh sách hotel_id thuộc owner này (chỉ enabled)."""
    return [h.id for h in Hotel.query.filter_by(owner_id=user_id, enabled=True).all()]


# ── GET /api/owner/dashboard ─────────────────────────────────────────────────
@owner_bp.route("/dashboard", methods=["GET"])
@role_required("OWNER")
def dashboard():
    """Thống kê tổng quan cho owner."""
    user      = get_current_user()
    hotel_ids = _get_owner_hotel_ids(user.id)
    today          = date.today()
    first_of_month = today.replace(day=1)

    total_hotels = len(hotel_ids)
    total_rooms  = (
        Room.query.filter(Room.hotel_id.in_(hotel_ids)).count()
        if hotel_ids else 0
    )
    available_rooms = (
        Room.query.filter(Room.hotel_id.in_(hotel_ids), Room.status == "AVAILABLE").count()
        if hotel_ids else 0
    )
    occupied_rooms = (
        Room.query.filter(Room.hotel_id.in_(hotel_ids), Room.status == "OCCUPIED").count()
        if hotel_ids else 0
    )

    total_bookings = (
        Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).count()
        if hotel_ids else 0
    )
    pending_bookings = (
        Booking.query.filter(
            Booking.hotel_id.in_(hotel_ids),
            Booking.status == "PENDING",
        ).count()
        if hotel_ids else 0
    )
    bookings_this_month = (
        Booking.query.filter(
            Booking.hotel_id.in_(hotel_ids),
            Booking.created_at >= first_of_month,
        ).count()
        if hotel_ids else 0
    )

    revenue_this_month = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.hotel_id.in_(hotel_ids),
            Booking.status.in_(["CONFIRMED", "COMPLETED"]),
            Booking.created_at >= first_of_month,
        ).scalar() or 0
    ) if hotel_ids else 0.0

    occupancy_rate = round(occupied_rooms / total_rooms * 100, 2) if total_rooms else 0

    return success_response(data={
        "total_hotels":        total_hotels,
        "total_rooms":         total_rooms,
        "available_rooms":     available_rooms,
        "occupied_rooms":      occupied_rooms,
        "occupancy_rate":      occupancy_rate,
        "total_bookings":      total_bookings,
        "pending_bookings":    pending_bookings,
        "bookings_this_month": bookings_this_month,
        "revenue_this_month":  revenue_this_month,
    })


# ── GET /api/owner/hotels ─────────────────────────────────────────────────────
@owner_bp.route("/hotels", methods=["GET"])
@role_required("OWNER")
def get_my_hotels():
    """Danh sách khách sạn do owner này sở hữu."""
    user   = get_current_user()
    hotels = (
        Hotel.query.filter_by(owner_id=user.id)
        .order_by(Hotel.created_at.desc())
        .all()
    )
    return success_response(data={
        "hotels": [h.to_dict(include_stats=True) for h in hotels],
        "total":  len(hotels),
    })


# ── GET /api/owner/hotel/:id/stats ────────────────────────────────────────────
@owner_bp.route("/hotel/<int:hotel_id>/stats", methods=["GET"])
@role_required("OWNER")
def get_hotel_stats(hotel_id):
    """Thống kê chi tiết cho một khách sạn cụ thể."""
    user  = get_current_user()
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        return error_response("Khách sạn không tồn tại", 404)
    if hotel.owner_id != user.id:
        return error_response("Bạn không sở hữu khách sạn này", 403)

    today          = date.today()
    first_of_month = today.replace(day=1)

    total_rooms     = Room.query.filter_by(hotel_id=hotel_id).count()
    occupied_rooms  = Room.query.filter_by(hotel_id=hotel_id, status="OCCUPIED").count()
    available_rooms = Room.query.filter_by(hotel_id=hotel_id, status="AVAILABLE").count()

    total_bookings     = Booking.query.filter_by(hotel_id=hotel_id).count()
    pending_bookings   = Booking.query.filter_by(hotel_id=hotel_id, status="PENDING").count()
    confirmed_bookings = Booking.query.filter_by(hotel_id=hotel_id, status="CONFIRMED").count()
    completed_bookings = Booking.query.filter_by(hotel_id=hotel_id, status="COMPLETED").count()

    total_revenue = float(
        db.session.query(sa.func.sum(Booking.total_price))
        .filter(
            Booking.hotel_id == hotel_id,
            Booking.status.in_(["CONFIRMED", "COMPLETED"]),
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

    avg_rating = float(
        db.session.query(sa.func.avg(Room.rating))
        .filter(Room.hotel_id == hotel_id)
        .scalar() or 0
    )

    occupancy_rate = round(occupied_rooms / total_rooms * 100, 2) if total_rooms else 0

    return success_response(data={
        "hotel_id":            hotel_id,
        "hotel_name":          hotel.name,
        "total_rooms":         total_rooms,
        "occupied_rooms":      occupied_rooms,
        "available_rooms":     available_rooms,
        "occupancy_rate":      occupancy_rate,
        "total_bookings":      total_bookings,
        "pending_bookings":    pending_bookings,
        "confirmed_bookings":  confirmed_bookings,
        "completed_bookings":  completed_bookings,
        "total_revenue":       total_revenue,
        "revenue_this_month":  revenue_this_month,
        "average_room_rating": round(avg_rating, 2),
    })


# ── GET /api/owner/bookings ───────────────────────────────────────────────────
@owner_bp.route("/bookings", methods=["GET"])
@role_required("OWNER")
def get_hotel_bookings():
    """
    Danh sách booking thuộc các khách sạn của owner.
    Query params: status, hotel_id, search, page, per_page
    """
    user      = get_current_user()
    hotel_ids = _get_owner_hotel_ids(user.id)

    if not hotel_ids:
        return paginated_response(items=[], total=0, page=1, per_page=20)

    status_filter   = request.args.get("status", "").upper()
    hotel_id_filter = request.args.get("hotel_id", type=int)
    search          = request.args.get("search", "").strip()
    page, per_page  = get_page_args()

    query = Booking.query.filter(Booking.hotel_id.in_(hotel_ids))

    if status_filter in ("PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"):
        query = query.filter(Booking.status == status_filter)
    if hotel_id_filter and hotel_id_filter in hotel_ids:
        query = query.filter(Booking.hotel_id == hotel_id_filter)
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


# ── GET /api/owner/rooms ──────────────────────────────────────────────────────
@owner_bp.route("/rooms", methods=["GET"])
@role_required("OWNER")
def get_my_rooms():
    """
    Danh sách phòng thuộc các khách sạn của owner.
    Query params: hotel_id, room_type, status, min_price, max_price, page, per_page
    """
    user      = get_current_user()
    hotel_ids = _get_owner_hotel_ids(user.id)

    if not hotel_ids:
        return paginated_response(items=[], total=0, page=1, per_page=20)

    hotel_id_filter = request.args.get("hotel_id", type=int)
    room_type       = request.args.get("room_type", "").strip()
    status_filter   = request.args.get("status", "").upper()
    min_price       = request.args.get("min_price", type=float)
    max_price       = request.args.get("max_price", type=float)
    page, per_page  = get_page_args()

    query = Room.query.filter(Room.hotel_id.in_(hotel_ids))

    if hotel_id_filter and hotel_id_filter in hotel_ids:
        query = query.filter(Room.hotel_id == hotel_id_filter)
    if room_type:
        query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
    if status_filter in ("AVAILABLE", "OCCUPIED", "MAINTENANCE"):
        query = query.filter(Room.status == status_filter)
    if min_price is not None:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Room.price_per_night <= max_price)

    total = query.count()
    rooms = (
        query.order_by(Room.hotel_id.asc(), Room.price_per_night.asc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[r.to_dict() for r in rooms],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/owner/revenue ────────────────────────────────────────────────────
@owner_bp.route("/revenue", methods=["GET"])
@role_required("OWNER")
def get_revenue():
    """
    Thống kê doanh thu tổng hợp cho owner.
    Query params: hotel_id (lọc theo khách sạn cụ thể)
    """
    user      = get_current_user()
    hotel_ids = _get_owner_hotel_ids(user.id)
    today          = date.today()
    first_of_month = today.replace(day=1)

    hotel_id_filter = request.args.get("hotel_id", type=int)
    if hotel_id_filter:
        if hotel_id_filter not in hotel_ids:
            return error_response("Bạn không sở hữu khách sạn này", 403)
        hotel_ids = [hotel_id_filter]

    if not hotel_ids:
        return success_response(data={
            "total_revenue":       0.0,
            "revenue_today":       0.0,
            "revenue_this_month":  0.0,
            "completed_bookings":  0,
            "pending_payments":    0,
        })

    def _revenue(extra_filters):
        return float(
            db.session.query(sa.func.sum(Booking.total_price))
            .filter(
                Booking.hotel_id.in_(hotel_ids),
                Booking.status.in_(["CONFIRMED", "COMPLETED"]),
                *extra_filters,
            ).scalar() or 0
        )

    total_revenue      = _revenue([])
    revenue_today      = _revenue([sa.cast(Booking.created_at, sa.Date) == today])
    revenue_this_month = _revenue([Booking.created_at >= first_of_month])

    completed_bookings = Booking.query.filter(
        Booking.hotel_id.in_(hotel_ids),
        Booking.status == "COMPLETED",
    ).count()

    pending_payments = db.session.query(sa.func.count(Payment.id)).join(
        Booking, Payment.booking_id == Booking.id
    ).filter(
        Booking.hotel_id.in_(hotel_ids),
        Payment.status == "PENDING",
    ).scalar() or 0

    return success_response(data={
        "total_revenue":      total_revenue,
        "revenue_today":      revenue_today,
        "revenue_this_month": revenue_this_month,
        "completed_bookings": completed_bookings,
        "pending_payments":   pending_payments,
    })


# ── GET /api/owner/payment-info ──────────────────────────────────────────────
@owner_bp.route("/payment-info", methods=["GET"])
@role_required("OWNER")
def get_payment_info():
    """Lấy thông tin TT của hotel đầu tiên (hoặc theo ?hotel_id=)"""
    user      = get_current_user()
    hotel_id  = request.args.get("hotel_id", type=int)

    query = Hotel.query.filter_by(owner_id=user.id, enabled=True)
    hotel = query.filter_by(id=hotel_id).first() if hotel_id else query.first()

    if not hotel:
        return error_response("Không tìm thấy khách sạn", 404)

    return success_response(data={"hotel_id": hotel.id, **hotel.payment_info_dict()})


# ── PUT /api/owner/payment-info ───────────────────────────────────────────────
@owner_bp.route("/payment-info", methods=["PUT"])
@role_required("OWNER")
def update_payment_info():
    """Cập nhật thông tin TT của một hotel."""
    user     = get_current_user()
    data     = request.get_json(silent=True) or {}
    hotel_id = data.get("hotel_id")

    if not hotel_id:
        return error_response("hotel_id là bắt buộc", 400)

    hotel = Hotel.query.filter_by(id=hotel_id, owner_id=user.id, enabled=True).first()
    if not hotel:
        return error_response("Không tìm thấy khách sạn hoặc bạn không sở hữu khách sạn này", 404)

    FIELDS = ["bank_name", "account_number", "account_holder", "bank_branch",
              "momo_number", "momo_qr", "qr_code_url"]
    for f in FIELDS:
        if f in data:
            setattr(hotel, f, data[f])

    db.session.commit()
    return success_response(data={"hotel_id": hotel.id, **hotel.payment_info_dict()},
                            message="Cập nhật thông tin thanh toán thành công")
