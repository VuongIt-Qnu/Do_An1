"""
Booking Model
Represents a room reservation made by a User or Guest.
Status flow: PENDING → CONFIRMED → COMPLETED | CANCELLED
"""
from datetime import datetime, date
from ..extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Authenticated user (nullable — guest bookings allowed)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"),
                        nullable=True, index=True)

    # Guest info (always filled, even for logged-in users)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))

    # Hotel & Room
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="SET NULL"),
                         nullable=True, index=True)
    room_id = db.Column(db.BigInteger, db.ForeignKey("rooms.id", ondelete="SET NULL"),
                        nullable=True, index=True)

    # Dates
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False, default=1)

    # Pricing
    total_price = db.Column(db.Numeric(12, 2))

    # Status: PENDING | CONFIRMED | COMPLETED | CANCELLED
    status = db.Column(db.String(20), nullable=False, default="PENDING", index=True)
    cancel_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)

    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    payments = db.relationship("Payment", backref="booking", lazy="dynamic",
                               cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="booking", lazy="dynamic")

    @property
    def nights(self) -> int:
        """Calculate number of nights between check-in and check-out"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel.name if self.hotel else None,
            "room_id": self.room_id,
            "room_name": self.room.name if self.room else None,
            "room_type": self.room.room_type if self.room else None,
            "check_in": self.check_in.isoformat() if self.check_in else None,
            "check_out": self.check_out.isoformat() if self.check_out else None,
            "nights": self.nights,
            "guests": self.guests,
            "total_price": float(self.total_price) if self.total_price else 0,
            "status": self.status,
            "cancel_reason": self.cancel_reason,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "notes": self.notes,
            "reviewed": self.reviews.count() > 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Booking #{self.id} — {self.customer_name} [{self.status}]>"
