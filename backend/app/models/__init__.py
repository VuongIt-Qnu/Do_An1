"""
Models package — import all models so SQLAlchemy registers them.
"""
from .user import User
from .hotel import Hotel
from .room import Room
from .booking import Booking
from .payment import Payment
from .review import Review

__all__ = ["User", "Hotel", "Room", "Booking", "Payment", "Review"]
