"""
Utility Validators
Reusable validation functions used across routes and services.
"""
import re
from datetime import date, datetime


def validate_date_range(check_in_str: str, check_out_str: str) -> tuple[date, date]:
    """
    Parse and validate check-in / check-out date strings.

    Args:
        check_in_str:  Date string in ISO format (YYYY-MM-DD)
        check_out_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        Tuple (check_in: date, check_out: date)

    Raises:
        ValueError: If format is invalid or dates are logically wrong
    """
    try:
        check_in = date.fromisoformat(check_in_str)
        check_out = date.fromisoformat(check_out_str)
    except (ValueError, TypeError):
        raise ValueError("Dates must be in ISO format: YYYY-MM-DD")

    today = date.today()
    if check_in < today:
        raise ValueError("Check-in date cannot be in the past")
    if check_out <= check_in:
        raise ValueError("Check-out must be after check-in")
    if (check_out - check_in).days > 365:
        raise ValueError("Booking cannot exceed 365 nights")

    return check_in, check_out


def validate_role(role: str) -> str:
    """
    Validate that role is one of the allowed values.

    Raises:
        ValueError: If role is invalid
    """
    allowed = {"ADMIN", "OWNER", "USER"}
    role = role.upper()
    if role not in allowed:
        raise ValueError(f"Invalid role. Allowed: {allowed}")
    return role


def validate_payment_method(method: str) -> str:
    """
    Validate payment method.

    Raises:
        ValueError: If method is invalid
    """
    allowed = {"CASH", "BANK_TRANSFER", "MOMO", "QR_CODE"}  # FIX: QR → QR_CODE (matches schema)
    method = method.upper()
    if method not in allowed:
        raise ValueError(f"Invalid payment method. Allowed: {allowed}")
    return method


def validate_booking_status(status: str) -> str:
    """Validate booking status transition"""
    allowed = {"PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"}
    status = status.upper()
    if status not in allowed:
        raise ValueError(f"Invalid booking status. Allowed: {allowed}")
    return status


def sanitize_string(text: str, max_length: int = 500) -> str:
    """Strip whitespace and enforce maximum length"""
    if not text:
        return ""
    return text.strip()[:max_length]


def is_valid_email(email: str) -> bool:
    """Basic email format validation"""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
