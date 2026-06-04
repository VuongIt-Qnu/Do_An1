"""
User Model
Represents system users: ADMIN, OWNER, USER roles.
"""
import bcrypt
from datetime import datetime
from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)

    # Role: ADMIN | OWNER | USER
    role = db.Column(db.String(20), nullable=False, default="USER")

    # Profile extras
    passport = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)

    # Account state
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    # Password reset
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    hotels = db.relationship("Hotel", backref="owner", lazy="dynamic",
                             foreign_keys="Hotel.owner_id")
    bookings = db.relationship("Booking", backref="user", lazy="dynamic",
                               foreign_keys="Booking.user_id")
    reviews = db.relationship("Review", back_populates="user", lazy="dynamic")

    # ── Password Helpers ─────────────────────────────────────────────

    def set_password(self, plain_password: str) -> None:
        """Hash and store password using bcrypt"""
        self.password_hash = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        """Verify plain password against stored hash"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    # ── Serialization ─────────────────────────────────────────────────

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary. Never expose password_hash."""
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role,
            "passport": self.passport,
            "nationality": self.nationality,
            "address": self.address,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"
