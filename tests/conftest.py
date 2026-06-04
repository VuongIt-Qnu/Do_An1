"""
pytest tests/conftest.py
Shared fixtures for all tests
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.hotel import Hotel
from app.models.room import Room
from datetime import datetime, timedelta


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Push application context"""
    with app.app_context():
        yield app


# ==================== Users ====================

@pytest.fixture
def admin_user(app):
    """Create admin user"""
    user = User(
        full_name="Admin User",
        email="admin@test.com",
        phone_number="+84901234567",  # FIX: User model uses phone_number not phone
        role="ADMIN"
    )
    user.set_password("Admin123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def owner_user(app):
    """Create owner user"""
    user = User(
        full_name="Hotel Owner",
        email="owner@test.com",
        phone_number="+84901234568",
        role="OWNER"
    )
    user.set_password("Owner123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(app):
    """Create regular user"""
    user = User(
        full_name="Guest User",
        email="guest@test.com",
        phone_number="+84901234569",
        role="USER"
    )
    user.set_password("Guest123!")
    db.session.add(user)
    db.session.commit()
    return user


# ==================== Tokens ====================

@pytest.fixture
def admin_token(client, admin_user):
    """Get admin access token"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'Admin123!'
    })
    return response.json['data']['access_token']


@pytest.fixture
def owner_token(client, owner_user):
    """Get owner access token"""
    response = client.post('/api/auth/login', json={
        'email': 'owner@test.com',
        'password': 'Owner123!'
    })
    return response.json['data']['access_token']


@pytest.fixture
def user_token(client, regular_user):
    """Get regular user access token"""
    response = client.post('/api/auth/login', json={
        'email': 'guest@test.com',
        'password': 'Guest123!'
    })
    return response.json['data']['access_token']


# ==================== Hotels ====================

@pytest.fixture
def sample_hotel(app, owner_user):
    """Create sample hotel"""
    hotel = Hotel(
        name="Test Hotel",
        city="Hanoi",
        description="This is a test hotel",
        star_rating=4,
        address="123 Main Street, Hanoi",
        phone="+84912345678",
        owner_id=owner_user.id
    )
    db.session.add(hotel)
    db.session.commit()
    return hotel


@pytest.fixture
def multiple_hotels(app, owner_user):
    """Create multiple hotels"""
    hotels = []
    cities = [("Hanoi", 5), ("Ho Chi Minh", 4), ("Da Nang", 3)]
    
    for i, (city, stars) in enumerate(cities):
        hotel = Hotel(
            name=f"Test Hotel {i+1}",
            city=city,
            description=f"Test hotel in {city}",
            star_rating=stars,
            address=f"{100+i} Street, {city}",
            phone=f"+8491234567{i}",
            owner_id=owner_user.id
        )
        db.session.add(hotel)
        hotels.append(hotel)
    
    db.session.commit()
    return hotels


# ==================== Rooms ====================

@pytest.fixture
def sample_room(app, sample_hotel):
    """Create sample room"""
    room = Room(
        hotel_id=sample_hotel.id,
        room_number="101",
        room_type="DELUXE",
        price_per_night=150.00,
        capacity=2,
        amenities="WiFi, Air Conditioning, TV, Mini Bar",
        description="Cozy deluxe room with city view"
    )
    db.session.add(room)
    db.session.commit()
    return room


@pytest.fixture
def multiple_rooms(app, sample_hotel):
    """Create multiple different room types"""
    rooms = []
    room_data = [
        ("STANDARD", "201", 100.00, 1, "WiFi, AC"),
        ("DELUXE", "202", 150.00, 2, "WiFi, AC, Mini Bar"),
        ("SUITE", "301", 250.00, 4, "WiFi, AC, Mini Bar, Jacuzzi"),
    ]
    
    for room_type, room_num, price, capacity, amenities in room_data:
        room = Room(
            hotel_id=sample_hotel.id,
            room_number=room_num,
            room_type=room_type,
            price_per_night=price,
            capacity=capacity,
            amenities=amenities,
            description=f"{room_type} room"
        )
        db.session.add(room)
        rooms.append(room)
    
    db.session.commit()
    return rooms


# ==================== Test Data ====================

@pytest.fixture
def valid_user_data():
    """Valid user registration data"""
    return {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "phone": "+84901234567"
    }


@pytest.fixture
def valid_hotel_data():
    """Valid hotel creation data"""
    return {
        "name": "Luxury Hotel",
        "city": "Hanoi",
        "description": "5-star luxury hotel",
        "star_rating": 5,
        "address": "789 Luxury Lane",
        "phone": "+84987654321",
        "image_url": "https://example.com/hotel.jpg"
    }


@pytest.fixture
def valid_room_data():
    """Valid room creation data"""
    return {
        "room_number": "999",
        "room_type": "PENTHOUSE",
        "price_per_night": 500.00,
        "capacity": 6,
        "amenities": "WiFi, AC, Jacuzzi, Sauna",
        "description": "Luxury penthouse suite"
    }


@pytest.fixture
def valid_booking_data():
    """Valid booking creation data"""
    check_in = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    check_out = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
    
    return {
        "check_in": check_in,
        "check_out": check_out,
        "guest_name": "Jane Doe",
        "guest_email": "jane@example.com",
        "guest_phone": "+84901234567",
        "number_of_guests": 2,
        "special_requests": "High floor preferred"
    }


@pytest.fixture
def invalid_booking_data():
    """Invalid booking data (dates in past)"""
    check_in = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    check_out = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    return {
        "check_in": check_in,
        "check_out": check_out,
        "guest_name": "Invalid",
        "guest_email": "invalid@example.com",
        "guest_phone": "+84901234567",
        "number_of_guests": 1
    }


@pytest.fixture
def helpers():
    """Helper functions for tests"""
    class Helpers:
        @staticmethod
        def get_auth_header(token):
            return {'Authorization': f'Bearer {token}'}
        
        @staticmethod
        def assert_success_response(data, required_keys=None):
            """Verify response has success envelope"""
            assert 'success' in data
            assert 'data' in data
            assert 'message' in data or 'errors' in data
            
            if required_keys and data.get('success'):
                for key in required_keys:
                    assert key in data['data'], f"Missing key: {key}"
    
    return Helpers()
