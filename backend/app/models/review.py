"""
Review Model
Guests can review a room ONLY after their booking is COMPLETED.
One review per booking (enforced by unique constraint on booking_id).
"""
from datetime import datetime
from ..extensions import db


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        # One review per booking
        db.UniqueConstraint("booking_id", name="uq_review_booking"),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    booking_id = db.Column(db.BigInteger, db.ForeignKey("bookings.id", ondelete="CASCADE"),
                           nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"),
                        nullable=True, index=True)
    room_id = db.Column(db.BigInteger, db.ForeignKey("rooms.id", ondelete="CASCADE"),
                        nullable=False, index=True)

    # Relationships — back_populates pairs với User.reviews
    user = db.relationship("User", foreign_keys=[user_id], back_populates="reviews", lazy="joined")

    # Rating 1–5
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "Anonymous",
            "room_id": self.room_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Review Booking#{self.booking_id} — {self.rating}★>"
