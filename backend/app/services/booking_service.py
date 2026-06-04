"""
Service: Booking Operations
Handles room availability checking, price calculation, booking creation logic.
"""
from datetime import date, timedelta
from decimal import Decimal
from ..extensions import db
from ..models.booking import Booking
from ..models.room import Room


def check_room_availability(room_id: int, check_in: date, check_out: date) -> bool:
    """
    Check if a room is available for the given date range.
    Returns True if available, False otherwise.
    """
    if check_in >= check_out:
        raise ValueError("check_out must be after check_in")

    # Find any overlapping bookings
    conflict = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(["PENDING", "CONFIRMED"]),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    ).first()

    return conflict is None


def calculate_total_price(room_id: int, check_in: date, check_out: date) -> Decimal:
    """
    Calculate total price for a booking.
    Total = nightly_rate × number_of_nights
    """
    room = db.session.get(Room, room_id)  # FIX: query.get() deprecated in SQLAlchemy 2.0
    if not room:
        raise ValueError(f"Room {room_id} not found")

    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValueError("Invalid date range")

    return Decimal(str(float(room.price_per_night) * nights)).quantize(Decimal('0.01'))


def get_room_availability_calendar(room_id: int, start_date: date, end_date: date) -> dict:
    """
    Get available dates for a room within a date range.
    Returns dict: { "available_dates": [...], "booked_dates": [...] }
    """
    room = db.session.get(Room, room_id)  # FIX: query.get() deprecated in SQLAlchemy 2.0
    if not room:
        raise ValueError(f"Room {room_id} not found")

    available_dates = []
    booked_dates = []

    current = start_date
    while current < end_date:
        # Check if this day is available
        conflict = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(["CONFIRMED", "PENDING"]),
            Booking.check_in <= current,
            Booking.check_out > current,
        ).first()

        if conflict:
            booked_dates.append(current.isoformat())
        else:
            available_dates.append(current.isoformat())

        current += timedelta(days=1)

    return {
        "room_id": room_id,
        "available_dates": available_dates,
        "booked_dates": booked_dates,
    }


def cancel_booking(booking: Booking, reason: str) -> None:
    """
    Cancel a booking and update status.
    Reason should be provided for audit purposes.
    """
    from datetime import datetime
    
    booking.status = "CANCELLED"
    booking.cancel_reason = reason
    booking.cancelled_at = datetime.utcnow()
    db.session.commit()


def calculate_cancellation_penalty(booking: Booking) -> dict:
    """
    Calculate cancellation penalty based on hotel's cancellation policy.
    Returns: {
        "can_cancel": bool,
        "penalty_percent": float,
        "penalty_amount": Decimal,
        "refund_amount": Decimal
    }
    """
    from datetime import datetime, timedelta
    from decimal import Decimal

    now = datetime.utcnow().date()
    check_in = booking.check_in
    total_amount = booking.total_price or Decimal('0')

    # Default policy: free cancellation up to 24 hours before check-in
    hours_until_checkin = (check_in - now).days * 24
    if hours_until_checkin >= 24:
        return {
            "can_cancel": True,
            "penalty_percent": 0.0,
            "penalty_amount": Decimal('0'),
            "refund_amount": total_amount,
        }
    # Late cancellation: 50% penalty
    elif hours_until_checkin >= 0:
        penalty_percent = 50.0
        penalty_amount = total_amount * Decimal(str(penalty_percent / 100))
        refund_amount = total_amount - penalty_amount
        return {
            "can_cancel": True,
            "penalty_percent": penalty_percent,
            "penalty_amount": penalty_amount,
            "refund_amount": refund_amount,
        }
    # Already checked in: cannot cancel
    else:
        return {
            "can_cancel": False,
            "penalty_percent": 100.0,
            "penalty_amount": total_amount,
            "refund_amount": Decimal('0'),
        }
