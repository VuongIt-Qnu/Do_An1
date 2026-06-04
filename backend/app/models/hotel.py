"""
Hotel Model
Represents a hotel managed by an Owner.
Supports multi-hotel: one Owner → many Hotels.
"""
from datetime import datetime
from ..extensions import db


class Hotel(db.Model):
    __tablename__ = "hotels"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Owner — FK to users (role=OWNER)
    owner_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"),
                         nullable=True, index=True)

    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    star_rating = db.Column(db.Integer, default=3)  # 1–5

    # ── Payment info (owner-specific) ───────────────────────────────────────
    # Bank transfer
    bank_name      = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    account_holder = db.Column(db.String(100))
    bank_branch    = db.Column(db.String(200))

    # MoMo
    momo_number = db.Column(db.String(20))
    momo_qr     = db.Column(db.Text)   # URL hoặc base64 QR image

    # QR code chung
    qr_code_url = db.Column(db.Text)

    # Soft delete / visibility
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    # Admin approval — OWNER submits hotel; ADMIN approves before it's visible
    approved = db.Column(db.Boolean, nullable=False, default=False)  # FIX: was missing, required by schema & frontend

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    rooms = db.relationship("Room", backref="hotel", lazy="dynamic",
                            cascade="all, delete-orphan")
    bookings = db.relationship("Booking", backref="hotel", lazy="dynamic")

    def payment_info_dict(self) -> dict:
        """Thông tin thanh toán của owner — trả về cho khách khi tạo booking."""
        return {
            "bank_transfer": {
                "bank_name":      self.bank_name or "",
                "account_number": self.account_number or "",
                "account_holder": self.account_holder or "",
                "bank_branch":    self.bank_branch or "",
            },
            "momo": {
                "momo_number": self.momo_number or "",
                "momo_qr":     self.momo_qr or "",
            },
            "qr": {
                "qr_code_url": self.qr_code_url or "",
            },
        }

    def to_dict(self, include_stats: bool = False) -> dict:
        data = {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "description": self.description,
            "phone": self.phone,
            "email": self.email,
            "star_rating": self.star_rating,
            "enabled": self.enabled,
            "approved": self.approved,
            # Payment fields (owner sets these in their dashboard)
            "bank_name":      self.bank_name,
            "account_number": self.account_number,
            "account_holder": self.account_holder,
            "bank_branch":    self.bank_branch,
            "momo_number":    self.momo_number,
            "momo_qr":        self.momo_qr,
            "qr_code_url":    self.qr_code_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_stats:
            data["total_rooms"] = self.rooms.count()
        return data

    def __repr__(self):
        return f"<Hotel {self.name} — {self.city}>"
