"""
Service: Payment Processing
Handles payment creation, simulation of bank/MoMo/QR transactions, receipt generation.
Uses SQLAlchemy 2.0 style (db.session.get) — compatible with Flask-SQLAlchemy 3.x
"""
from datetime import datetime
from decimal import Decimal
import uuid
import random
from ..extensions import db
from ..models.payment import Payment
from ..models.booking import Booking
import logging

logger = logging.getLogger(__name__)

# Cash payments use a distinct sub-status to clearly separate
# "waiting at counter" from "waiting for transfer confirmation"
CASH_PAYMENT_STATUS = "AWAITING_PAYMENT"


# ── Payment Note Builder ──────────────────────────────────────────────────────

def build_payment_note(payer_name: str, room_id: int,
                       booking_dt: datetime, method: str) -> str:
    """
    Generate transfer note (nội dung chuyển khoản) for a booking.

    Format:
        BANK_TRANSFER / MOMO  → "<name> | ROOM-<id> | <YYYY-MM-DD HH:MM>"
        QR_CODE               → "<name> | ROOM-<id>"
        CASH                  → "" (no transfer note needed)
    """
    if method == "CASH":
        return ""

    room_code  = f"ROOM-{room_id}"
    name_clean = (payer_name or "Khach hang").strip()

    if method == "QR_CODE":
        return f"{name_clean} | {room_code}"

    dt_str = booking_dt.strftime("%Y-%m-%d %H:%M") if booking_dt else ""
    return f"{name_clean} | {room_code} | {dt_str}"


# ── Payment Instruction Builder ───────────────────────────────────────────────

def get_payment_instructions(booking, payment, hotel) -> dict:
    """
    Build a complete, method-specific payment instruction block.

    Returns:
        {
            method, amount, payment_note, status, owner_id,
            instructions: { ... method-specific fields ... }
        }
    """
    method = payment.method if payment else "BANK_TRANSFER"
    amount = float(payment.amount) if payment and payment.amount else 0.0
    note   = payment.payment_note or ""
    status = payment.status if payment else "PENDING"

    instr: dict = {}

    if method == "BANK_TRANSFER":
        instr = {
            "bank_name":      hotel.bank_name      if hotel else "",
            "account_number": hotel.account_number if hotel else "",
            "account_holder": hotel.account_holder if hotel else "",
            "bank_branch":    hotel.bank_branch    if hotel else "",
            "payment_note":   note,
        }

    elif method == "MOMO":
        instr = {
            "momo_number":  hotel.momo_number if hotel else "",
            "momo_qr":      hotel.momo_qr     if hotel else "",
            "payment_note": note,
        }

    elif method == "QR_CODE":
        instr = {
            "qr_code_url":  hotel.qr_code_url if hotel else "",
            "payment_note": note,
        }

    elif method == "CASH":
        instr = {
            "cash_status":          CASH_PAYMENT_STATUS,
            "payment_instructions": (
                "Vui lòng thanh toán tại quầy lễ tân khi check-in. "
                "Hãy mang theo mã đặt phòng."
            ),
        }

    return {
        "method":       method,
        "amount":       amount,
        "payment_note": note,
        "status":       status,
        "owner_id":     hotel.owner_id if hotel else None,
        "instructions": instr,
    }


def create_payment(booking_id: int, amount: Decimal, method: str = "BANK_TRANSFER") -> Payment:
    """Create a payment record for a booking."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")

    payment = Payment(
        booking_id=booking_id,
        amount=amount,
        method=method,
        status="PENDING",
        transaction_ref=None,
    )
    db.session.add(payment)
    db.session.commit()
    return payment


def simulate_payment(payment_id: int, success: bool = True) -> Payment:
    """
    Simulate a payment transaction.
    In production: call VNPay/MoMo/ZaloPay API here.
    """
    payment = db.session.get(Payment, payment_id)
    if not payment:
        raise ValueError(f"Payment {payment_id} not found")

    if success:
        payment.status = "PAID"
        payment.paid_at = datetime.utcnow()
        payment.transaction_ref = f"TXN-{uuid.uuid4().hex[:16].upper()}"
        logger.info(f"Payment {payment_id} marked as PAID")
    else:
        payment.status = "FAILED"
        payment.transaction_ref = f"FAILED-{uuid.uuid4().hex[:16].upper()}"
        logger.warning(f"Payment {payment_id} marked as FAILED")

    db.session.commit()
    return payment


def process_bank_transfer(payment_id: int, account_number: str, bank_code: str) -> dict:
    """Simulate processing a bank transfer payment."""
    logger.info(f"Processing bank transfer for payment {payment_id} to {account_number} ({bank_code})")
    success = random.random() > 0.1  # 90% success

    payment = simulate_payment(payment_id, success)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "transaction_ref": payment.transaction_ref,
        "message": "Bank transfer processed" if success else "Bank transfer failed",
    }


def process_momo_payment(payment_id: int, phone_number: str) -> dict:
    """Simulate processing a MoMo payment."""
    logger.info(f"Processing MoMo payment for payment {payment_id} to {phone_number}")
    success = random.random() > 0.05  # 95% success

    payment = simulate_payment(payment_id, success)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "transaction_ref": payment.transaction_ref,
        "message": "MoMo payment processed" if success else "MoMo payment failed",
    }


def process_qr_payment(payment_id: int, qr_code: str) -> dict:
    """Simulate processing a QR code payment (VietQR)."""
    logger.info(f"Processing QR payment for payment {payment_id}: {qr_code}")
    success = random.random() > 0.02  # 98% success

    payment = simulate_payment(payment_id, success)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "transaction_ref": payment.transaction_ref,
        "message": "QR payment processed" if success else "QR payment failed",
    }


def refund_payment(payment_id: int, reason: str = None) -> Payment:
    """Refund a paid payment."""
    payment = db.session.get(Payment, payment_id)
    if not payment:
        raise ValueError(f"Payment {payment_id} not found")

    if payment.status != "PAID":
        raise ValueError(f"Only PAID payments can be refunded. Current status: {payment.status}")

    payment.status = "REFUNDED"
    payment.transaction_ref = f"REFUND-{uuid.uuid4().hex[:16].upper()}"
    db.session.commit()

    logger.info(f"Payment {payment_id} refunded. Reason: {reason}")
    return payment


def get_payment_statistics(hotel_id: int = None) -> dict:
    """Get payment statistics for a hotel or entire system."""
    import sqlalchemy as sa

    base_query = db.session.query(Payment)

    if hotel_id:
        base_query = base_query.join(Booking, Payment.booking_id == Booking.id).filter(
            Booking.hotel_id == hotel_id
        )

    total_paid = float(
        db.session.query(sa.func.sum(Payment.amount))
        .filter(Payment.status == "PAID")
        .scalar() or 0
    )
    total_refunded = float(
        db.session.query(sa.func.sum(Payment.amount))
        .filter(Payment.status == "REFUNDED")
        .scalar() or 0
    )

    return {
        "total_payments":  base_query.count(),
        "paid_count":      base_query.filter(Payment.status == "PAID").count(),
        "pending_count":   base_query.filter(Payment.status == "PENDING").count(),
        "failed_count":    base_query.filter(Payment.status == "FAILED").count(),
        "refunded_count":  base_query.filter(Payment.status == "REFUNDED").count(),
        "total_amount":    total_paid,
        "net_revenue":     total_paid - total_refunded,
    }
