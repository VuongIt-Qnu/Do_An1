"""
Rooms Routes — /api/rooms
========================================
GET    /                     Danh sách phòng (filter + phân trang)
GET    /:id                  Chi tiết phòng + reviews
POST   /                     Tạo phòng mới  [ADMIN | OWNER]
PUT    /:id                  Cập nhật phòng [ADMIN | OWNER]
DELETE /:id                  Vô hiệu hoá phòng [ADMIN | OWNER]
GET    /:id/availability     Kiểm tra phòng trống theo ngày
GET    /:id/reviews          Danh sách review của phòng
"""
import sqlalchemy as sa
from datetime import timedelta
from flask import Blueprint, request

from ..extensions import db
from ..models.room import Room
from ..models.hotel import Hotel
from ..models.booking import Booking
from ..models.review import Review
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..utils.validators import sanitize_string, validate_date_range
from ..middleware.auth_middleware import role_required, get_current_user, optional_jwt

rooms_bp = Blueprint("rooms", __name__)


# ── GET /api/rooms/ ─────────────────────────────────────────────────────────
@rooms_bp.route("/", methods=["GET"])
@optional_jwt
def list_rooms():
    """
    Danh sách phòng có thể lọc theo nhiều tiêu chí.
    Query params:
        hotel_id    — lọc theo khách sạn
        room_type   — Standard | Deluxe | Suite | Family | Presidential
        min_price   — giá tối thiểu (VND)
        max_price   — giá tối đa (VND)
        capacity    — số khách tối thiểu
        status      — AVAILABLE | OCCUPIED | MAINTENANCE (mặc định AVAILABLE)
        featured    — true | false
        search      — tìm theo tên phòng
        page        — trang (mặc định 1)
        per_page    — số item mỗi trang (mặc định 12, tối đa 100)
    """
    hotel_id  = request.args.get("hotel_id", type=int)
    room_type = request.args.get("room_type", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    capacity  = request.args.get("capacity", type=int)
    status    = request.args.get("status", "AVAILABLE").upper()
    search    = request.args.get("search", "").strip()
    page, per_page = get_page_args(default_per_page=12)

    # Lọc featured — chấp nhận "true"/"false" hoặc "1"/"0"
    featured_str = request.args.get("featured")
    featured = None
    if featured_str is not None:
        featured = featured_str.lower() in ("true", "1", "yes")

    query = Room.query

    if hotel_id:
        query = query.filter(Room.hotel_id == hotel_id)
    if room_type:
        query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
    if min_price is not None:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Room.price_per_night <= max_price)
    if capacity:
        query = query.filter(Room.capacity >= capacity)
    if status:
        query = query.filter(Room.status == status)
    if featured is not None:
        query = query.filter(Room.featured == featured)
    if search:
        query = query.filter(
            sa.or_(
                Room.name.ilike(f"%{search}%"),
                Room.description.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    rooms = (
        query.order_by(Room.featured.desc(), Room.rating.desc(), Room.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[r.to_dict() for r in rooms],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/rooms/:id ──────────────────────────────────────────────────────
@rooms_bp.route("/<int:room_id>", methods=["GET"])
def get_room(room_id):
    """
    Chi tiết một phòng, kèm 10 review gần nhất.
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Phòng không tồn tại", 404)

    data = room.to_dict()
    data["reviews"] = [
        r.to_dict()
        for r in room.reviews.order_by(Review.created_at.desc()).limit(10).all()
    ]
    data["review_count"] = room.reviews.count()
    return success_response(data={"room": data})


# ── POST /api/rooms/ ─────────────────────────────────────────────────────────
@rooms_bp.route("/", methods=["POST"])
@role_required("ADMIN", "OWNER")
def create_room():
    """
    Tạo phòng mới.
    OWNER: chỉ tạo được cho khách sạn của mình.
    Body: { hotel_id, name, room_type, capacity, price_per_night,
            area?, amenities?, description?, main_image_url?, featured?, status? }
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    # --- Validate bắt buộc ---
    errors = {}
    hotel_id        = data.get("hotel_id")
    name            = sanitize_string(data.get("name", ""), 100)
    room_type       = sanitize_string(data.get("room_type", ""), 50)
    capacity        = data.get("capacity")
    price_per_night = data.get("price_per_night")

    if not hotel_id:
        errors["hotel_id"] = "hotel_id là bắt buộc"
    if not name:
        errors["name"] = "Tên phòng là bắt buộc"
    if not room_type:
        errors["room_type"] = "Loại phòng là bắt buộc"
    if capacity is None or int(capacity) < 1:
        errors["capacity"] = "Sức chứa phải >= 1"
    if price_per_night is None or float(price_per_night) < 0:
        errors["price_per_night"] = "Giá phòng không hợp lệ"

    if errors:
        return error_response("Dữ liệu không hợp lệ", 422, errors)

    # --- Kiểm tra khách sạn ---
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel or not hotel.enabled:
        return error_response("Khách sạn không tồn tại", 404)

    # OWNER chỉ được tạo phòng cho khách sạn của mình
    if user.role == "OWNER" and hotel.owner_id != user.id:
        return error_response("Bạn không sở hữu khách sạn này", 403)

    # --- Tạo phòng ---
    status = (data.get("status") or "AVAILABLE").upper()
    if status not in ("AVAILABLE", "OCCUPIED", "MAINTENANCE"):
        status = "AVAILABLE"

    room = Room(
        hotel_id=int(hotel_id),
        name=name,
        room_type=room_type,
        capacity=int(capacity),
        price_per_night=float(price_per_night),
        area=float(data["area"]) if data.get("area") else None,
        amenities=sanitize_string(data.get("amenities", ""), 500),
        description=sanitize_string(data.get("description", ""), 2000),
        main_image_url=sanitize_string(data.get("main_image_url", ""), 500),
        featured=bool(data.get("featured", False)),
        status=status,
    )
    db.session.add(room)
    db.session.commit()

    return success_response(
        data={"room": room.to_dict()},
        message="Tạo phòng thành công",
        status_code=201,
    )


# ── PUT /api/rooms/:id ──────────────────────────────────────────────────────
@rooms_bp.route("/<int:room_id>", methods=["PUT"])
@role_required("ADMIN", "OWNER")
def update_room(room_id):
    """
    Cập nhật thông tin phòng.
    OWNER: chỉ cập nhật phòng thuộc khách sạn của mình.
    """
    user = get_current_user()
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Phòng không tồn tại", 404)

    if user.role == "OWNER" and room.hotel.owner_id != user.id:
        return error_response("Bạn không có quyền chỉnh sửa phòng này", 403)

    data = request.get_json(silent=True) or {}

    # Cập nhật từng trường nếu được cung cấp
    if "name" in data:
        room.name = sanitize_string(data["name"], 100)
    if "room_type" in data:
        room.room_type = sanitize_string(data["room_type"], 50)
    if "capacity" in data:
        val = int(data["capacity"])
        if val < 1:
            return error_response("Sức chứa phải >= 1", 400)
        # Ensure no active booking exceeds the new capacity
        overbooked = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(["PENDING", "CONFIRMED"]),
            Booking.guests > val,
        ).first()
        if overbooked:
            return error_response(
                f"Không thể giảm sức chứa xuống {val}: "
                f"có booking đang hoạt động với {overbooked.guests} khách.", 409
            )
        room.capacity = val
    if "price_per_night" in data:
        val = float(data["price_per_night"])
        if val < 0:
            return error_response("Giá không được âm", 400)
        room.price_per_night = val
    if "area" in data:
        room.area = float(data["area"]) if data["area"] else None
    if "amenities" in data:
        room.amenities = sanitize_string(str(data["amenities"]), 500)
    if "description" in data:
        room.description = sanitize_string(data["description"], 2000)
    if "main_image_url" in data:
        room.main_image_url = sanitize_string(data["main_image_url"], 500)
    if "featured" in data:
        room.featured = bool(data["featured"])
    if "status" in data:
        new_status = str(data["status"]).upper()
        if new_status in ("AVAILABLE", "OCCUPIED", "MAINTENANCE"):
            room.status = new_status

    db.session.commit()
    return success_response(data={"room": room.to_dict()},
                            message="Cập nhật phòng thành công")


# ── DELETE /api/rooms/:id ───────────────────────────────────────────────────
@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
@role_required("ADMIN", "OWNER")
def delete_room(room_id):
    """
    Vô hiệu hoá phòng (soft-delete → status = MAINTENANCE).
    Không xoá cứng để giữ lịch sử booking.
    """
    user = get_current_user()
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Phòng không tồn tại", 404)

    if user.role == "OWNER" and room.hotel.owner_id != user.id:
        return error_response("Bạn không có quyền xoá phòng này", 403)

    # Kiểm tra có booking đang active không
    active_booking = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(["PENDING", "CONFIRMED"])
    ).first()
    if active_booking:
        return error_response(
            "Không thể xoá phòng đang có booking chờ xử lý. "
            "Vui lòng huỷ hoặc hoàn tất booking trước.", 409
        )

    room.status = "MAINTENANCE"
    db.session.commit()
    return success_response(message="Phòng đã được vô hiệu hoá")


# ── GET /api/rooms/:id/availability ────────────────────────────────────────
@rooms_bp.route("/<int:room_id>/availability", methods=["GET"])
def check_availability(room_id):
    """
    Kiểm tra phòng có trống trong khoảng ngày không.
    Query params: check_in (YYYY-MM-DD), check_out (YYYY-MM-DD)
    Returns: { available, booked_dates: [date...] }
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Phòng không tồn tại", 404)

    check_in_str  = request.args.get("check_in")
    check_out_str = request.args.get("check_out")

    if not check_in_str or not check_out_str:
        return error_response("check_in và check_out là bắt buộc (YYYY-MM-DD)", 400)

    try:
        check_in, check_out = validate_date_range(check_in_str, check_out_str)
    except ValueError as e:
        return error_response(str(e), 400)

    # Booking chồng lấp trong khoảng ngày yêu cầu
    conflict_count = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(["PENDING", "CONFIRMED"]),
        Booking.check_in  < check_out,
        Booking.check_out > check_in,
    ).count()

    # Tất cả ngày đã bị đặt trong khoảng yêu cầu (cho calendar UI)
    booked = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(["PENDING", "CONFIRMED"]),
    ).all()

    booked_dates = set()
    for b in booked:
        cur = b.check_in
        while cur < b.check_out:
            booked_dates.add(cur.isoformat())
            cur += timedelta(days=1)

    return success_response(data={
        "room_id":     room_id,
        "room_name":   room.name,
        "available":   conflict_count == 0,
        "booked_dates": sorted(booked_dates),
    })


# ── GET /api/rooms/:id/reviews ─────────────────────────────────────────────
@rooms_bp.route("/<int:room_id>/reviews", methods=["GET"])
def get_room_reviews(room_id):
    """
    Danh sách review của phòng, phân trang.
    Query params: page, per_page
    """
    room = db.session.get(Room, room_id)
    if not room:
        return error_response("Phòng không tồn tại", 404)

    page, per_page = get_page_args(default_per_page=10, max_per_page=50)

    total   = room.reviews.count()
    reviews = (
        room.reviews
        .order_by(Review.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # Tính điểm trung bình
    avg = db.session.query(
        sa.func.avg(Review.rating)
    ).filter(Review.room_id == room_id).scalar()

    return success_response(data={
        "room_id":        room_id,
        "average_rating": round(float(avg), 2) if avg else 0,
        "total_reviews":  total,
        "reviews":        [r.to_dict() for r in reviews],
    })
