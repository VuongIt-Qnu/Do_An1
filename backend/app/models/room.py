"""
Room Model
Represents a bookable room within a Hotel.
"""
from datetime import datetime
from ..extensions import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Parent hotel
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="CASCADE"),
                         nullable=False, index=True)

    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)   # Standard/Deluxe/Suite/…
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Numeric(12, 2), nullable=False)
    area = db.Column(db.Numeric(6, 2))                      # m²

    # Amenities stored as comma-separated string: "Wifi,TV,AC,Minibar"
    amenities = db.Column(db.Text)
    description = db.Column(db.Text)
    main_image_url = db.Column(db.Text)

    # Rating averaged from reviews
    rating = db.Column(db.Numeric(3, 2), default=5.0)

    # Featured on homepage
    featured = db.Column(db.Boolean, default=False)

    # Status: AVAILABLE | OCCUPIED | MAINTENANCE
    status = db.Column(db.String(20), nullable=False, default="AVAILABLE", index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bookings = db.relationship("Booking", backref="room", lazy="dynamic")
    reviews = db.relationship("Review", backref="room", lazy="dynamic")

    @property
    def amenities_list(self) -> list:
        """Return amenities as a Python list"""
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel.name if self.hotel else None,
            "name": self.name,
            "room_type": self.room_type,
            "capacity": self.capacity,
            "price_per_night": float(self.price_per_night) if self.price_per_night else 0,
            "area": float(self.area) if self.area else None,
            "amenities": self.amenities_list,
            "description": self.description,
            "main_image_url": self.main_image_url,
            "rating": float(self.rating) if self.rating else 5.0,
            "featured": self.featured,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Room {self.name} [{self.room_type}] — Hotel {self.hotel_id}>"
