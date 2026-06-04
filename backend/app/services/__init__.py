"""
Services Module
Core business logic for bookings, payments, emails, logging, etc.
"""
from .booking_service import (
    check_room_availability,
    calculate_total_price,
    get_room_availability_calendar,
    cancel_booking,
)
from .email_service import (
    send_email,
    send_booking_confirmation,
    send_booking_cancelled,
    send_reset_password_email,
    send_payment_receipt,
)
from .logging_service import (
    log_audit,
    log_request,
    log_user_activity,
    get_audit_logs,
)
from .payment_service import (
    create_payment,
    simulate_payment,
    process_bank_transfer,
    process_momo_payment,
    process_qr_payment,
    refund_payment,
    get_payment_statistics,
)

__all__ = [
    # Booking
    "check_room_availability",
    "calculate_total_price",
    "get_room_availability_calendar",
    "cancel_booking",
    # Email
    "send_email",
    "send_booking_confirmation",
    "send_booking_cancelled",
    "send_reset_password_email",
    "send_payment_receipt",
    # Logging
    "log_audit",
    "log_request",
    "log_user_activity",
    "get_audit_logs",
    # Payment
    "create_payment",
    "simulate_payment",
    "process_bank_transfer",
    "process_momo_payment",
    "process_qr_payment",
    "refund_payment",
    "get_payment_statistics",
]
