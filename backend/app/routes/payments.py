"""
Payments Routes — /api/payments
========================================
GET    /booking/:booking_id      Lấy thông tin thanh toán theo booking
GET    /:id                      Chi tiết một payment
POST   /process                  Xử lý thanh toán (giả lập gateway)
POST   /refund/:id               Hoàn tiền [ADMIN]
GET    /list                     Danh sách thanh toán [ADMIN | OWNER]
GET    /stats                    Thống kê thanh toán [ADMIN | OWNER]
"""
import uuid
from datetime import datetime
import sqlalchemy as sa
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.payment import Payment
from ..models.booking import Booking
from ..models.hotel import Hotel
from ..utils.response_helpers import success_response, error_response, paginated_response, get_page_args
from ..middleware.auth_middleware import role_required, get_current_user, optional_jwt
from ..services.logging_service import log_audit

payments_bp = Blueprint("payments", __name__)

ALLOWED_METHODS = {"BANK_TRANSFER", "MOMO", "QR_CODE", "CASH"}


# ── GET /api/payments/info/:booking_id ──────────────────────────────────────
@payments_bp.route("/info/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_payment_info(booking_id):
    """
    Trả về thông tin thanh toán chuẩn hoá theo phương thức cho một booking.
    Gồm: payment_note, thông tin ngân hàng / MoMo / QR của owner, status.
    """
    from ..models.hotel import Hotel
    from ..services.payment_service import get_payment_instructions
    from flask_jwt_extended import get_jwt_identity

    user_id = int(get_jwt_identity())
    user    = get_current_user()

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    # Kiểm tra quyền: chủ booking, ADMIN, hoặc OWNER của khách sạn
    if user.role == "USER" and booking.user_id != user_id:
        return error_response("Bạn không có quyền xem thông tin này", 403)
    if user.role == "OWNER":
        hotel_check = db.session.get(Hotel, booking.hotel_id) if booking.hotel_id else None
        if not hotel_check or hotel_check.owner_id != user_id:
            return error_response("Bạn không quản lý khách sạn này", 403)

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    hotel   = db.session.get(Hotel, booking.hotel_id) if booking.hotel_id else None

    instructions = get_payment_instructions(booking, payment, hotel)

    return success_response(data=instructions)


# ── GET /api/payments/booking/:booking_id ────────────────────────────────────
@payments_bp.route("/booking/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_payment_by_booking(booking_id):
    """
    Lấy thông tin thanh toán theo booking_id.
    User: chỉ xem booking của mình.
    ADMIN/OWNER: xem tất cả.
    """
    user = get_current_user()

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    # Kiểm tra quyền truy cập
    if user.role == "USER" and booking.user_id != user.id:
        return error_response("Bạn không có quyền xem thanh toán này", 403)

    if user.role == "OWNER":
        hotel = db.session.get(Hotel, booking.hotel_id)
        if not hotel or hotel.owner_id != user.id:
            return error_response("Bạn không có quyền xem thanh toán này", 403)

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        return error_response("Chưa có thông tin thanh toán cho booking này", 404)

    return success_response(data={"payment": payment.to_dict()})


# ── GET /api/payments/:id ────────────────────────────────────────────────────
@payments_bp.route("/<int:payment_id>", methods=["GET"])
@role_required("ADMIN", "OWNER")
def get_payment(payment_id):
    """Chi tiết một payment [ADMIN | OWNER]"""
    user = get_current_user()
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment không tồn tại", 404)

    # OWNER: chỉ xem payment thuộc hotel của mình
    if user.role == "OWNER":
        booking = db.session.get(Booking, payment.booking_id)
        hotel = db.session.get(Hotel, booking.hotel_id) if booking else None
        if not hotel or hotel.owner_id != user.id:
            return error_response("Bạn không có quyền xem payment này", 403)

    return success_response(data={"payment": payment.to_dict()})


# ── POST /api/payments/process ───────────────────────────────────────────────
@payments_bp.route("/process", methods=["POST"])
@jwt_required()
def process_payment():
    """
    Xử lý thanh toán cho một booking.
    Body: { booking_id, method }
    method: BANK_TRANSFER | MOMO | QR_CODE | CASH

    Mô phỏng gateway thanh toán: luôn thành công (production: tích hợp VNPay/MoMo).
    Khi thành công: payment.status = PAID, booking.status = CONFIRMED.
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    booking_id = data.get("booking_id")
    method = (data.get("method") or "BANK_TRANSFER").upper()

    if not booking_id:
        return error_response("booking_id là bắt buộc", 400)
    if method not in ALLOWED_METHODS:
        return error_response(
            f"Phương thức thanh toán không hợp lệ. Cho phép: {sorted(ALLOWED_METHODS)}", 400
        )

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking không tồn tại", 404)

    # Kiểm tra quyền: chỉ chủ booking mới được thanh toán (hoặc ADMIN)
    # booking.user_id == None → anonymous booking: allow owner by email match
    if user.role == "USER":
        if booking.user_id is not None and booking.user_id != user.id:
            return error_response("Bạn không có quyền thanh toán cho booking này", 403)
        if booking.user_id is None and booking.customer_email != user.email:
            return error_response("Bạn không có quyền thanh toán cho booking này", 403)

    if booking.status == "CANCELLED":
        return error_response("Booking đã bị huỷ, không thể thanh toán", 400)
    if booking.status == "COMPLETED":
        return error_response("Booking đã hoàn thành, không thể thanh toán", 400)

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        return error_response("Không tìm thấy thông tin thanh toán cho booking này", 404)
    if payment.status == "PAID":
        return error_response("Booking này đã được thanh toán rồi", 400)

    # ── Xử lý thanh toán (giả lập — 100% thành công) ──────────────────────
    # Production: gọi VNPay/MoMo API, nhận callback để xác nhận
    payment.status          = "PAID"
    payment.method          = method
    payment.paid_at         = datetime.utcnow()
    payment.transaction_ref = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    booking.status = "CONFIRMED"

    # ── Chuyển phòng sang OCCUPIED ──────────────────────────────────────────
    if booking.room:
        booking.room.status = "OCCUPIED"

    db.session.commit()

    # Gửi email xác nhận đặt phòng
    try:
        from ..services.email_service import send_booking_confirmation
        send_booking_confirmation(
            booking.customer_name,
            booking.customer_email,
            booking.to_dict()
        )
    except Exception:
        pass  # Email thất bại không ảnh hưởng kết quả thanh toán

    log_audit(
        "PAYMENT_PROCESSED",
        user_id=user.id,
        target_type="payment",
        target_id=payment.id,
        details={"booking_id": booking_id, "method": method, "amount": float(payment.amount)},
    )

    return success_response(
        data={"payment": payment.to_dict(), "booking": booking.to_dict()},
        message="Thanh toán thành công. Booking đã được xác nhận.",
    )


# ── POST /api/payments/refund/:id ────────────────────────────────────────────
@payments_bp.route("/refund/<int:payment_id>", methods=["POST"])
@role_required("ADMIN")
def refund_payment(payment_id):
    """
    Hoàn tiền cho một payment [ADMIN only].
    Giả lập — production: gọi API hoàn tiền của cổng thanh toán.
    Body (tuỳ chọn): { reason }
    """
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment không tồn tại", 404)

    if payment.status != "PAID":
        return error_response(
            f"Chỉ có thể hoàn tiền cho payment đã thanh toán. "
            f"Trạng thái hiện tại: {payment.status}", 400
        )

    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Hoàn tiền theo yêu cầu")

    payment.status          = "REFUNDED"
    payment.transaction_ref = f"REFUND-{uuid.uuid4().hex[:12].upper()}"
    db.session.commit()

    admin = get_current_user()
    log_audit(
        "PAYMENT_REFUNDED",
        user_id=admin.id,
        target_type="payment",
        target_id=payment_id,
        details={"reason": reason, "amount": float(payment.amount)},
    )

    return success_response(
        data={"payment": payment.to_dict()},
        message="Hoàn tiền thành công",
    )


# ── GET /api/payments/list ───────────────────────────────────────────────────
@payments_bp.route("/list", methods=["GET"])
@role_required("ADMIN", "OWNER")
def list_payments():
    """
    Danh sách thanh toán với filter.
    Query params: status, method, booking_id, page, per_page
    ADMIN: toàn hệ thống. OWNER: chỉ hotel của mình.
    """
    user          = get_current_user()
    status_filter = request.args.get("status", "").upper()
    method_filter = request.args.get("method", "").upper()
    booking_id    = request.args.get("booking_id", type=int)
    page, per_page = get_page_args()

    query = db.session.query(Payment).join(Booking, Payment.booking_id == Booking.id)

    # OWNER: lọc theo hotel của mình
    if user.role == "OWNER":
        owner_hotel_ids = [
            h.id for h in Hotel.query.filter_by(owner_id=user.id, enabled=True).all()
        ]
        if not owner_hotel_ids:
            return paginated_response(items=[], total=0, page=page, per_page=per_page)
        query = query.filter(Booking.hotel_id.in_(owner_hotel_ids))

    if status_filter:
        query = query.filter(Payment.status == status_filter)
    if method_filter:
        query = query.filter(Payment.method == method_filter)
    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)

    total    = query.count()
    payments = (
        query.order_by(Payment.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    return paginated_response(
        items=[p.to_dict() for p in payments],
        total=total, page=page, per_page=per_page
    )


# ── GET /api/payments/stats ──────────────────────────────────────────────────
@payments_bp.route("/stats", methods=["GET"])
@role_required("ADMIN", "OWNER")
def payment_stats():
    """
    Thống kê tổng hợp thanh toán.
    ADMIN: toàn hệ thống. OWNER: chỉ hotel của mình.
    """
    user = get_current_user()

    owner_hotel_ids = (
        [h.id for h in Hotel.query.filter_by(owner_id=user.id, enabled=True).all()]
        if user.role == "OWNER" else None
    )

    def _sum(status_val):
        q = (
            db.session.query(sa.func.sum(Payment.amount))
            .join(Booking, Payment.booking_id == Booking.id)
            .filter(Payment.status == status_val)
        )
        if owner_hotel_ids is not None:
            q = q.filter(Booking.hotel_id.in_(owner_hotel_ids))
        return float(q.scalar() or 0)

    def _count_by(col_filter):
        """Count on a fresh subquery of base to avoid filter accumulation."""
        q = (
            db.session.query(sa.func.count(Payment.id))
            .join(Booking, Payment.booking_id == Booking.id)
        )
        if owner_hotel_ids is not None:
            q = q.filter(Booking.hotel_id.in_(owner_hotel_ids))
        return int(q.filter(col_filter).scalar() or 0)

    total_paid     = _sum("PAID")
    total_refunded = _sum("REFUNDED")

    stats = {
        "total_payments":        _count_by(sa.true()),
        "paid":                  _count_by(Payment.status == "PAID"),
        "pending":               _count_by(Payment.status == "PENDING"),
        "failed":                _count_by(Payment.status == "FAILED"),
        "refunded":              _count_by(Payment.status == "REFUNDED"),
        "total_paid_amount":     total_paid,
        "total_refunded_amount": total_refunded,
        "net_revenue":           total_paid - total_refunded,
        "by_method": {
            "bank_transfer": _count_by(Payment.method == "BANK_TRANSFER"),
            "momo":          _count_by(Payment.method == "MOMO"),
            "qr_code":       _count_by(Payment.method == "QR_CODE"),
            "cash":          _count_by(Payment.method == "CASH"),
        },
    }

    return success_response(data=stats)
