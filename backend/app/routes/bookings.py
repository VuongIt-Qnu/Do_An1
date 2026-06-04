"""
Bookings Routes — /api/bookings
========================================
POST   /                     Tạo booking mới (public hoặc đã đăng nhập)
GET    /                     Danh sách tất cả booking  [ADMIN | OWNER]
GET    /my                   Booking của tôi  [USER]
GET    /:id                  Chi tiết booking
PATCH  /:id/confirm          Xác nhận booking  [ADMIN | OWNER]
PATCH  /:id/complete         Hoàn tất (check-out)  [ADMIN | OWNER]
PATCH  /:id/cancel           Huỷ booking (có tính penalty)
POST   /:id/review           Đăng review (USER, booking đã COMPLETED)
GET    /:id/reviews          Danh sách review của booking
"""
import sqlalchemy as sa
from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.booking import Booking
from ..models.room import Room
from ..models.hotel import Hotel
from ..models.payment import Payment
from ..models.review import Review
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..utils.validators import validate_date_range, sanitize_string
from ..middleware.auth_middleware import role_required, get_current_user, optional_jwt, safe_get_jwt_identity
from ..services.logging_service import log_audit

bookings_bp = Blueprint("bookings", __name__)


# ── POST /api/bookings/ ─────────────────────────────────────────────────────
@bookings_bp.route("/", methods=["POST"])
@jwt_required()
def create_booking():
    """
    Tạo booking mới.
    - Người đã đăng nhập: thông tin khách hàng có thể lấy từ profile.
    - Khách vãng lai: phải cung cấp customer_name + customer_email.
    Body: {
        room_id, check_in, check_out,
        guests?,
        customer_name, customer_email, customer_phone?,
        payment_method?,   # CASH | BANK_TRANSFER | MOMO | QR_CODE
        notes?
    }
    """
    from ..services.booking_service import check_room_availability, calculate_total_price
    from ..services.email_service import send_booking_confirmation

    data = request.get_json(silent=True) or {}

    # --- Validate ngày ---
    try:
        check_in, check_out = validate_date_range(
            data.get("check_in", ""),
            data.get("check_out", "")
        )
    except ValueError as e:
        return error_response(str(e), 400)

    room_id        = data.get("room_id")
    guests         = max(1, int(data.get("guests", 1) or 1))
    customer_name  = sanitize_string(data.get("customer_name", ""), 100)
    customer_email = sanitize_string(data.get("customer_email", ""), 100).lower().strip()
    customer_phone = sanitize_string(data.get("customer_phone", ""), 20)
    notes          = sanitize_string(data.get("notes", ""), 500)
    payment_method = (data.get("payment_method") or "BANK_TRANSFER").upper()

    # --- Validate bắt buộc ---
    errors = {}
    if not room_id:
        errors["room_id"] = "room_id là bắt buộc"
    if not customer_name:
        errors["customer_name"] = "Tên khách hàng là bắt buộc"
    if not customer_email:
        errors["customer_email"] = "Email khách hàng là bắt buộc"
    if errors:
        return error_response("Dữ liệu không hợp lệ", 422, errors)

    if payment_method not in ("CASH", "BANK_TRANSFER", "MOMO", "QR_CODE"):
        payment_method = "BANK_TRANSFER"

    # --- Kiểm tra phòng ---
    room = db.session.get(Room, int(room_id))
    if not room:
        return error_response("Phòng không tồn tại", 404)
    if room.status != "AVAILABLE":
        return error_response("Phòng hiện không khả dụng", 409)
    if guests > room.capacity:
        return error_response(
            f"Phòng chỉ chứa tối đa {room.capacity} khách", 400
        )

    # --- Kiểm tra ngày trống ---
    if not check_room_availability(room.id, check_in, check_out):
        return error_response(
            "Phòng đã được đặt trong khoảng thời gian này", 409
        )

    # --- Tính giá ---
    total_price = calculate_total_price(room.id, check_in, check_out)

    # --- Lấy user_id (luôn có vì @jwt_required) ---
    user_id = int(get_jwt_identity())

    # --- Tạo booking ---
    booking = Booking(
        user_id=user_id,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        hotel_id=room.hotel_id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        total_price=total_price,
        status="PENDING",
        notes=notes,
    )
    db.session.add(booking)
    db.session.flush()  # Lấy booking.id trước khi commit

    # --- Sinh payment_note qua service ---
    from datetime import datetime as dt
    from ..services.payment_service import build_payment_note, get_payment_instructions, CASH_PAYMENT_STATUS
    booking_now  = dt.utcnow()
    payment_note = build_payment_note(customer_name, room.id, booking_now, payment_method)

    # Cash dùng trạng thái riêng để phân biệt "chờ TT quầy" vs "chờ chuyển khoản"
    initial_status = CASH_PAYMENT_STATUS if payment_method == "CASH" else "PENDING"

    # --- Tạo payment record ---
    payment = Payment(
        booking_id=booking.id,
        amount=total_price,
        method=payment_method,
        status=initial_status,
        payment_note=payment_note,
    )
    db.session.add(payment)
    db.session.commit()

    # --- Lấy thông tin TT của owner ---
    hotel = db.session.get(Hotel, room.hotel_id)
    # Trả về structured payment instructions thay vì raw info
    payment_instructions = get_payment_instructions(booking, payment, hotel)

    # --- Gửi email xác nhận (fire-and-forget) ---
    try:
        send_booking_confirmation(
            customer_name,
            customer_email,
            booking.to_dict()
        )
    except Exception:
        pass

    log_audit("BOOKING_CREATED", user_id=user_id,
              target_type="booking", target_id=booking.id,
              details={"room_id": room.id, "total_price": float(total_price)})

    return success_response(
        data={
            "booking": booking.to_dict(),
            "payment": payment.to_dict(),
            # Structured per-method payment instructions (new format)
            "payment_instructions": payment_instructions,
            # Legacy field kept for backward compat
            "owner_payment_info": hotel.payment_info_dict() if hotel else {},
        },
        message="Đặt phòng thành công. Vui lòng hoàn tất thanh toán.",
        status_code=201,
    )


# ── GET /api/bookings/ ──────────────────────────────────────────────────────
@bookings_bp.route("/", methods=["GET"])
@role_required("ADMIN", "OWNER")
def list_bookings():
    """
    Danh sách tất cả booking.
    ADMIN: xem tất cả.
    OWNER: chỉ xem booking của khách sạn mình.
    Query params: status, hotel_id, check_in_from, check_in_to, page, per_page
    """
    from ..models.hotel import Hotel
    user = get_current_user()

    status_filter    = request.args.get("status", "").upper()
    hotel_id_filter  = request.args.get("hotel_id", type=int)
    check_in_from    = request.args.get("check_in_from")
    check_in_to      = request.args.get("check_in_to")
    search           = request.args.get("search", "").strip()
    page, per_page   = get_page_args()

    query = Booking.query

    # OWNER chỉ xem booking của khách sạn mình
    if user.role == "OWNER":
        owner_hotel_ids = [
            h.id for h in Hotel.query.filter_by(owner_id=user.id).all()
        ]
        if not owner_hotel_ids:
            return paginated_response(items=[], total=0, page=1, per_page=per_page)
        query = query.filter(Booking.hotel_id.in_(owner_hotel_ids))

    if hotel_id_filter:
        query = query.filter(Booking.hotel_id == hotel_id_filter)
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if check_in_from:
        try:
            from datetime import date
            query = query.filter(Booking.check_in >= date.fromisoformat(check_in_from))
        except ValueError:
            pass
    if check_in_to:
        try:
            from datetime import date
            query = query.filter(Booking.check_in <= date.fromisoformat(check_in_to))
        except ValueError:
            pass
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


# ── GET /api/bookings/my ────────────────────────────────────────────────────
@bookings_bp.route("/my", methods=["GET"])
@jwt_required()
def get_my_bookings():
    """
    Danh sách booking của người dùng hiện tại.
    Query params: status, page, per_page
    """
    user          = get_current_user()
    status_filter = request.args.get("status", "").upper()
    page, per_page = get_page_args(default_per_page=10, max_per_page=50)

    query = Booking.query.filter_by(user_id=user.id)
    if status_filter:
        query = query.filter(Booking.status == status_filter)

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


# ── GET /api/bookings/:id ───────────────────────────────────────────────────
@bookings_bp.route("/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):
    """
    Chi tiết booking.
    - ADMIN / OWNER của khách sạn: xem mọi booking.
    - USER: chỉ xem booking của mình.
    - Khách vãng lai: không xem được.
    """
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    user_id = int(get_jwt_identity())
    if user_id:
        user = get_current_user()
        if user:
            is_admin    = user.role == "ADMIN"
            is_hotel_owner = (
                user.role == "OWNER"
                and booking.hotel
                and booking.hotel.owner_id == user.id
            )
            is_own = booking.user_id == user.id
            if not (is_admin or is_hotel_owner or is_own):
                return error_response("Bạn không có quyền xem booking này", 403)
    else:
        return error_response("Cần đăng nhập để xem chi tiết booking", 401)

    data = booking.to_dict()
    # Kèm thông tin payment
    payment = booking.payments.first()
    data["payment"] = payment.to_dict() if payment else None

    return success_response(data={"booking": data})


# ── PATCH /api/bookings/:id/confirm ────────────────────────────────────────
@bookings_bp.route("/<int:booking_id>/confirm", methods=["PATCH"])
@role_required("ADMIN", "OWNER")
def confirm_booking(booking_id):
    """
    Xác nhận booking đang PENDING → CONFIRMED.
    OWNER: chỉ xác nhận booking của khách sạn mình.
    """
    from ..services.email_service import send_booking_confirmed_by_admin
    user    = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    if user.role == "OWNER":
        if not booking.hotel or booking.hotel.owner_id != user.id:
            return error_response("Bạn không quản lý khách sạn này", 403)

    if booking.status != "PENDING":
        return error_response(
            f"Chỉ xác nhận được booking đang PENDING. Trạng thái hiện tại: {booking.status}", 400
        )

    booking.status = "CONFIRMED"

    # ── Chuyển phòng sang OCCUPIED ──────────────────────────────────────────
    if booking.room:
        booking.room.status = "OCCUPIED"

    db.session.commit()

    try:
        send_booking_confirmed_by_admin(booking, booking.customer_email)
    except Exception:
        pass

    log_audit("BOOKING_CONFIRMED", user_id=user.id,
              target_type="booking", target_id=booking.id)

    return success_response(data={"booking": booking.to_dict()},
                            message="Xác nhận booking thành công")


# ── PATCH /api/bookings/:id/complete ───────────────────────────────────────
@bookings_bp.route("/<int:booking_id>/complete", methods=["PATCH"])
@role_required("ADMIN", "OWNER")
def complete_booking(booking_id):
    """
    Đánh dấu booking CONFIRMED → COMPLETED (khách đã check-out).
    Trả phòng về trạng thái AVAILABLE.
    """
    user    = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    if user.role == "OWNER":
        if not booking.hotel or booking.hotel.owner_id != user.id:
            return error_response("Bạn không quản lý khách sạn này", 403)

    if booking.status != "CONFIRMED":
        return error_response(
            f"Chỉ hoàn tất được booking đang CONFIRMED. Trạng thái hiện tại: {booking.status}", 400
        )

    booking.status = "COMPLETED"

    # Trả phòng về AVAILABLE
    if booking.room:
        booking.room.status = "AVAILABLE"

    db.session.commit()

    log_audit("BOOKING_COMPLETED", user_id=user.id,
              target_type="booking", target_id=booking.id)

    return success_response(data={"booking": booking.to_dict()},
                            message="Check-out thành công")


# ── PATCH /api/bookings/:id/cancel ─────────────────────────────────────────
@bookings_bp.route("/<int:booking_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_booking(booking_id):
    """
    Huỷ booking với tính phí phạt nếu có.
    - ADMIN/OWNER: huỷ bất kỳ booking nào.
    - USER: chỉ huỷ booking của mình (phải PENDING hoặc CONFIRMED).
    Chính sách huỷ: miễn phí trước 24h; 50% nếu trong vòng 24h.
    Body: { reason? }
    """
    from ..services.booking_service import calculate_cancellation_penalty
    from ..services.email_service import send_booking_cancelled

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    data   = request.get_json(silent=True) or {}
    reason = sanitize_string(data.get("reason", ""), 500)

    user_id = int(get_jwt_identity())
    actor_id = None

    if user_id:
        user = get_current_user()
        if user:
            actor_id = user.id
            is_admin_or_owner = user.role in ("ADMIN", "OWNER")
            is_own_booking    = booking.user_id == user.id
            if not (is_admin_or_owner or is_own_booking):
                return error_response("Bạn không có quyền huỷ booking này", 403)

    if booking.status in ("CANCELLED", "COMPLETED"):
        return error_response(
            f"Booking đã ở trạng thái {booking.status}, không thể huỷ", 400
        )

    # Tính phí phạt
    penalty_info = calculate_cancellation_penalty(booking)

    booking.status       = "CANCELLED"
    booking.cancel_reason = reason
    booking.cancelled_at = datetime.utcnow()

    # Xử lý hoàn tiền nếu đã thanh toán
    payment = booking.payments.first()
    if payment and payment.status == "PAID" and penalty_info["penalty_amount"] > 0:
        payment.status = "REFUNDED"

    # Trả phòng về AVAILABLE (bất kể trạng thái phòng hiện tại)
    if booking.room:
        booking.room.status = "AVAILABLE"

    db.session.commit()

    # Gửi email thông báo huỷ
    try:
        send_booking_cancelled(
            booking.customer_name,
            booking.customer_email,
            booking.id,
            reason or "Không có lý do"
        )
    except Exception:
        pass

    log_audit("BOOKING_CANCELLED", user_id=actor_id,
              target_type="booking", target_id=booking.id,
              details={"reason": reason, "penalty": str(penalty_info["penalty_amount"])})

    return success_response(
        data={
            "booking": booking.to_dict(),
            "penalty_info": {
                "penalty_percent": penalty_info["penalty_percent"],
                "penalty_amount":  float(penalty_info["penalty_amount"]),
                "refund_amount":   float(penalty_info["refund_amount"]),
            },
        },
        message="Huỷ booking thành công",
    )


# ── POST /api/bookings/:id/review ──────────────────────────────────────────
@bookings_bp.route("/<int:booking_id>/review", methods=["POST"])
@jwt_required()
def create_review(booking_id):
    """
    Đăng review cho booking đã COMPLETED.
    Mỗi booking chỉ được review 1 lần.
    Body: { rating (1-5), comment? }
    """
    user    = get_current_user()
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    if booking.user_id != user.id:
        return error_response("Bạn chỉ có thể review booking của mình", 403)
    if booking.status != "COMPLETED":
        return error_response("Chỉ có thể review sau khi booking hoàn tất", 400)

    # Kiểm tra đã review chưa
    existing = Review.query.filter_by(booking_id=booking_id).first()
    if existing:
        return error_response("Booking này đã được review", 409)

    data    = request.get_json(silent=True) or {}
    rating  = data.get("rating")
    comment = sanitize_string(data.get("comment", ""), 1000)

    if rating is None:
        return error_response("rating là bắt buộc", 400)
    try:
        rating = int(rating)
    except (ValueError, TypeError):
        return error_response("rating phải là số nguyên", 400)
    if not (1 <= rating <= 5):
        return error_response("rating phải từ 1 đến 5", 400)

    room_id = booking.room_id
    review = Review(
        booking_id=booking_id,
        user_id=user.id,
        room_id=room_id,
        rating=rating,
        comment=comment,
    )
    db.session.add(review)

    # Cập nhật điểm trung bình của phòng
    room = db.session.get(Room, room_id)
    if room:
        avg = db.session.query(
            sa.func.avg(Review.rating)
        ).filter(Review.room_id == room_id).scalar()
        if avg:
            room.rating = round(float(avg), 2)

    db.session.commit()

    return success_response(
        data={"review": review.to_dict()},
        message="Cảm ơn bạn đã gửi đánh giá!",
        status_code=201,
    )


# ── GET /api/bookings/:id/reviews ──────────────────────────────────────────
@bookings_bp.route("/<int:booking_id>/reviews", methods=["GET"])
def get_booking_reviews(booking_id):
    """Danh sách review của phòng trong booking."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    if not booking.room_id:
        return success_response(data={"reviews": [], "average_rating": 0})

    reviews = (
        Review.query.filter_by(room_id=booking.room_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    avg = db.session.query(
        sa.func.avg(Review.rating)
    ).filter(Review.room_id == booking.room_id).scalar()

    return success_response(data={
        "reviews":        [r.to_dict() for r in reviews],
        "average_rating": round(float(avg), 2) if avg else 0,
    })
