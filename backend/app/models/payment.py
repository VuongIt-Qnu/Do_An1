"""
Payment Model
Tracks payment for each Booking.
Status: PENDING → PAID | FAILED | REFUNDED
"""
from datetime import datetime
from ..extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    booking_id = db.Column(db.BigInteger, db.ForeignKey("bookings.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # Method: CASH | BANK_TRANSFER | MOMO | QR_CODE
    method = db.Column(db.String(50), default="BANK_TRANSFER")

    # Status: PENDING | PAID | REFUNDED | FAILED
    status = db.Column(db.String(20), nullable=False, default="PENDING")

    # External reference from payment gateway (simulated)
    transaction_ref = db.Column(db.String(100))

    # Nội dung chuyển khoản: "<customer_name> | ROOM-<id> | <datetime>"
    payment_note = db.Column(db.String(500))

    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": float(self.amount) if self.amount else 0,
            "method": self.method,
            "status": self.status,
            "payment_note": self.payment_note,
            "transaction_ref": self.transaction_ref,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Payment #{self.id} — {self.amount} [{self.status}]>"
