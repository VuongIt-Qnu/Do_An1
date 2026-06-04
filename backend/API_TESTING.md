# Hotel Management System - API Testing Guide

Complete guide for testing all 50+ endpoints in the CNPM2 Hotel Management REST API.

---

## 🎯 Testing Overview

| Tool | Use Case | Skill Level |
|------|----------|------------|
| **cURL** | Quick endpoint testing | Beginner |
| **Postman** | API collection, automated testing | Beginner-Intermediate |
| **pytest** | Unit & integration tests | Intermediate |
| **Newman** | CLI Postman automation, CI/CD | Advanced |

---

## 📋 Test Data Setup

### Test Accounts

Before testing, create these accounts via registration:

```json
{
  "admin": {
    "email": "admin@test.com",
    "password": "Admin123!",
    "full_name": "Admin User",
    "phone": "+84901234567"
  },
  "owner": {
    "email": "owner@test.com",
    "password": "Owner123!",
    "full_name": "Hotel Owner",
    "phone": "+84901234568"
  },
  "user": {
    "email": "guest@test.com",
    "password": "Guest123!",
    "full_name": "Guest User",
    "phone": "+84901234569"
  }
}
```

### Promote to Roles (Admin-only)

After registration, admin must promote users:

```bash
# UPDATE user roles (Direct SQL or via admin endpoint)
UPDATE users SET role = 'ADMIN' WHERE email = 'admin@test.com';
UPDATE users SET role = 'OWNER' WHERE email = 'owner@test.com';
```

---

## 🚀 Quick Start - cURL Testing

### 1. Register User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "Password123!",
    "phone": "+84901234567"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "USER"
  },
  "message": "Registration successful"
}
```

### 2. Login & Get Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }' | jq '.'
```

**Extract token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}' \
  | jq -r '.data.access_token')

echo $TOKEN
```

### 3. Use Token in Requests

```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Complete Test Scenarios

### 🔐 Authentication Tests

#### Test: User Registration

```bash
# Valid registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "New User",
    "email": "newuser@test.com",
    "password": "SecurePass123!",
    "phone": "+84912345678"
  }'

# Expected: 201 Created
# ❌ Test: Invalid email format
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "User",
    "email": "invalid-email",
    "password": "Pass123!"
  }'
# Expected: 400 Bad Request
```

#### Test: User Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }'

# Expected: 200 OK with access_token and refresh_token
```

#### Test: Token Refresh

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"

# Expected: 200 OK with new access_token
```

#### Test: Get Profile

```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with user data
```

#### Test: Update Profile

```bash
curl -X PUT http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+84987654321"
  }'

# Expected: 200 OK with updated data
```

#### Test: Logout

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK
# Next request with this token should fail (blacklisted)
```

---

### 🏨 Hotels Tests

#### Test: List Hotels (Public)

```bash
# No authentication needed
curl -X GET "http://localhost:5000/api/hotels?page=1&per_page=10&city=Hanoi"

# Filters:
# - name: partial match
# - city: exact match
# - star_rating: >= number
# - price_min, price_max: room price range
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Grand Hotel",
      "city": "Hanoi",
      "description": "Luxury 5-star hotel",
      "star_rating": 5,
      "address": "123 Main St",
      "phone": "+84912345678",
      "image_url": "https://...",
      "average_rating": 4.5,
      "rooms_count": 150
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 45,
    "pages": 5
  }
}
```

#### Test: Get Hotel Detail

```bash
curl -X GET http://localhost:5000/api/hotels/1
```

#### Test: Create Hotel (ADMIN/OWNER only)

```bash
curl -X POST http://localhost:5000/api/hotels \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Hotel",
    "city": "Ho Chi Minh",
    "description": "Beautiful 4-star hotel",
    "star_rating": 4,
    "address": "456 Nguyen St",
    "phone": "+84912345679",
    "image_url": "https://example.com/hotel.jpg"
  }'

# Expected: 201 Created
```

#### Test: Update Hotel (Ownership scoped)

```bash
curl -X PUT http://localhost:5000/api/hotels/1 \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "star_rating": 5
  }'

# Expected: 200 OK
# ❌ If different owner: 403 Forbidden
```

#### Test: Delete Hotel (ADMIN only)

```bash
curl -X DELETE http://localhost:5000/api/hotels/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK
```

#### Test: Hotel Statistics

```bash
curl -X GET http://localhost:5000/api/hotels/1/stats \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected: occupancy rate, revenue, etc.
```

---

### 🏷️ Rooms Tests

#### Test: List Rooms

```bash
# All rooms
curl -X GET http://localhost:5000/api/rooms?page=1&per_page=20

# Filter by hotel
curl -X GET "http://localhost:5000/api/rooms?hotel_id=1&page=1&per_page=20"

# Filter by price and capacity
curl -X GET "http://localhost:5000/api/rooms?price_min=50&price_max=300&capacity_min=2"

# Filter by type
curl -X GET "http://localhost:5000/api/rooms?room_type=DELUXE"
```

**Room Types:** STANDARD, DELUXE, SUITE, PENTHOUSE

#### Test: Get Room Detail

```bash
curl -X GET http://localhost:5000/api/rooms/1
```

#### Test: Create Room (ADMIN/OWNER)

```bash
curl -X POST http://localhost:5000/api/rooms \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": 1,
    "room_number": "101",
    "room_type": "DELUXE",
    "price_per_night": 150.00,
    "capacity": 2,
    "amenities": "WiFi, AC, TV, Mini Bar",
    "description": "Cozy deluxe room with city view"
  }'

# Expected: 201 Created
```

#### Test: Check Availability

```bash
curl -X GET "http://localhost:5000/api/rooms/1/availability?check_in=2026-04-20&check_out=2026-04-25"

# Expected: true/false
```

#### Test: Availability Calendar

```bash
curl -X GET "http://localhost:5000/api/rooms/1/calendar?month=4&year=2026"

# Expected: Array of dates with availability status
```

#### Test: Update Room

```bash
curl -X PUT http://localhost:5000/api/rooms/1 \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_night": 200.00,
    "capacity": 3
  }'
```

#### Test: Delete Room

```bash
curl -X DELETE http://localhost:5000/api/rooms/1 \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

---

### 📅 Bookings Tests

#### Test: Create Booking

```bash
curl -X POST http://localhost:5000/api/bookings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "check_in": "2026-04-25",
    "check_out": "2026-04-28",
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "guest_phone": "+84901234567",
    "number_of_guests": 2,
    "special_requests": "High floor preferred"
  }'

# Expected: 201 Created with booking details
```

**Response includes:**
- booking_id
- total_price (calculated: nights × price_per_night)
- payment_record (payment_id created automatically)
- status: "PENDING"

#### Test: Get My Bookings

```bash
curl -X GET "http://localhost:5000/api/bookings/my?page=1&per_page=10" \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: All bookings for logged-in user
```

#### Test: Get Booking Detail

```bash
curl -X GET http://localhost:5000/api/bookings/1 \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: Full booking details
# ❌ If not owner/admin: 403 Forbidden
```

#### Test: List All Bookings (ADMIN/OWNER)

```bash
# ADMIN: all bookings
curl -X GET http://localhost:5000/api/bookings/list \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# OWNER: only their hotel's bookings
curl -X GET http://localhost:5000/api/bookings/list \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

#### Test: Confirm Booking (ADMIN/OWNER)

```bash
curl -X PATCH http://localhost:5000/api/bookings/1/confirm \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation_note": "Confirmed for VIP guest"
  }'

# Expected: 200 OK, status → "CONFIRMED"
```

#### Test: Complete Booking

```bash
curl -X PATCH http://localhost:5000/api/bookings/1/complete \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK, status → "COMPLETED"
# Only allowed if check_out date has passed
```

#### Test: Cancel Booking

```bash
curl -X PATCH http://localhost:5000/api/bookings/1/cancel \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cancellation_reason": "Emergency trip"
  }'

# Expected: 200 OK, status → "CANCELLED"
# Refund calculated based on penalty
```

**Cancellation Policy:**
- < 24 hrs before check-in: 50% refund
- ≥ 24 hrs before check-in: 100% refund
- After check-in: No refund

#### Test: Add Review to Booking

```bash
curl -X POST http://localhost:5000/api/bookings/1/review \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent service and clean rooms!"
  }'

# Expected: 201 Created
# Only allowed after booking is COMPLETED
# One review per booking maximum
```

#### Test: Get Room Reviews

```bash
curl -X GET "http://localhost:5000/api/bookings/room/1/reviews?sort_by=recent"

# sort_by: recent, helpful (likes), rating_high, rating_low
```

---

### 💳 Payments Tests

#### Test: Get Booking Payment

```bash
curl -X GET http://localhost:5000/api/payments/booking/1 \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: Payment record linked to booking
```

#### Test: Process Payment

```bash
curl -X POST http://localhost:5000/api/payments/process \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "payment_method": "BANK_TRANSFER",
    "amount": 450.00
  }'

# Expected: 200 OK with payment details
# Status: PAID (90% success rate in simulation)
# Status: FAILED (10% failure simulation)
```

**Payment Methods:**
- BANK_TRANSFER
- MOMO
- QR_CODE
- CASH

#### Test: Refund Payment (ADMIN only)

```bash
curl -X POST http://localhost:5000/api/payments/1/refund \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 225.00,
    "reason": "Cancellation penalty applied"
  }'

# Expected: 200 OK
# Only allowed for PAID status
```

#### Test: List Payments (ADMIN/OWNER)

```bash
curl -X GET "http://localhost:5000/api/payments/list?page=1&per_page=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# OWNER filter: only their hotels
```

#### Test: Payment Statistics

```bash
curl -X GET http://localhost:5000/api/payments/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 
# {
#   "total_revenue": 15000.00,
#   "by_method": {
#     "BANK_TRANSFER": 5000,
#     "MOMO": 7000,
#     "QR_CODE": 3000
#   },
#   "by_status": {
#     "PAID": 14000,
#     "FAILED": 1000
#   }
# }
```

---

### 👨‍💼 Admin Tests

#### Test: Admin Dashboard

```bash
curl -X GET http://localhost:5000/api/admin/dashboard \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: System-wide statistics
# {
#   "total_users": 150,
#   "total_hotels": 25,
#   "total_bookings": 1200,
#   "total_revenue": 500000,
#   "pending_bookings": 45,
#   "completed_bookings": 1100,
#   "cancelled_bookings": 55,
#   "occupancy_rate": 72.5
# }
```

#### Test: List Users

```bash
curl -X GET "http://localhost:5000/api/admin/users?page=1&per_page=50&role=USER" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filters: role (USER, OWNER, ADMIN)
```

#### Test: Get User Detail

```bash
curl -X GET http://localhost:5000/api/admin/users/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Test: Update User Role (ADMIN only)

```bash
curl -X PUT http://localhost:5000/api/admin/users/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "OWNER"
  }'

# Expected: 200 OK with updated user
```

#### Test: Get Audit Logs

```bash
curl -X GET "http://localhost:5000/api/admin/logs?action=login&user_id=1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Retrieved from MongoDB audit_logs collection
```

---

### 👤 Owner Tests

#### Test: Owner Dashboard

```bash
curl -X GET http://localhost:5000/api/owner/dashboard \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected:
# {
#   "total_hotels": 3,
#   "total_rooms": 45,
#   "occupancy_rate": 68.0,
#   "total_revenue": 125000,
#   "available_rooms": 14,
#   "pending_bookings": 8,
#   "recent_bookings": [...]
# }
```

#### Test: Get Owner's Hotels

```bash
curl -X GET http://localhost:5000/api/owner/hotels \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected: All hotels owned by this owner
```

#### Test: Get Owner's Rooms

```bash
curl -X GET "http://localhost:5000/api/owner/rooms?hotel_id=1" \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected: All rooms in their hotels
```

#### Test: Get Owner's Bookings

```bash
curl -X GET http://localhost:5000/api/owner/bookings \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected: All bookings for their hotel rooms
```

#### Test: Revenue Statistics

```bash
curl -X GET "http://localhost:5000/api/owner/revenue?period=monthly" \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected:
# {
#   "today": 5000,
#   "this_month": 85000,
#   "total": 250000,
#   "by_month": [
#     {"month": "January", "revenue": 20000},
#     {"month": "February", "revenue": 25000},
#     ...
#   ]
# }
```

#### Test: Hotel Statistics

```bash
curl -X GET http://localhost:5000/api/owner/hotel/1/stats \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Expected:
# {
#   "hotel_id": 1,
#   "occupancy_rate": 75.0,
#   "average_nightly_rate": 150,
#   "total_bookings": 500,
#   "total_revenue": 100000,
#   "rooms_status": {
#     "available": 10,
#     "occupied": 30,
#     "maintenance": 2
#   }
# }
```

---

### 📊 Reports Tests

#### Test: Revenue Report

```bash
curl -X GET http://localhost:5000/api/reports/revenue \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response groups by day/week/month
```

#### Test: Occupancy Report

```bash
curl -X GET "http://localhost:5000/api/reports/occupancy?hotel_id=1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Shows occupancy per room type, per floor, etc.
```

#### Test: Bookings Report

```bash
curl -X GET http://localhost:5000/api/reports/bookings \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Breakdown by status (PENDING, CONFIRMED, COMPLETED, CANCELLED)
```

#### Test: PDF Export

```bash
curl -X GET "http://localhost:5000/api/reports/export/pdf?report_type=revenue&start_date=2026-01-01&end_date=2026-04-18" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  --output report.pdf

# Expected: PDF file downloaded
```

#### Test: Excel Export

```bash
curl -X GET "http://localhost:5000/api/reports/export/excel?report_type=revenue" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  --output report.xlsx

# Expected: Excel file downloaded
```

---

## 🧪 Automated Testing with Postman

### Setup Postman Collection

1. **Create Environment Variables**

```json
{
  "name": "Hotel Management API",
  "values": [
    {"key": "base_url", "value": "http://localhost:5000/api", "enabled": true},
    {"key": "admin_token", "value": "", "enabled": true},
    {"key": "owner_token", "value": "", "enabled": true},
    {"key": "user_token", "value": "", "enabled": true},
    {"key": "hotel_id", "value": "", "enabled": true},
    {"key": "room_id", "value": "", "enabled": true},
    {"key": "booking_id", "value": "", "enabled": true}
  ]
}
```

2. **Create Pre-request Script** (for login requests)

```javascript
if (pm.request.body.raw) {
    var body = JSON.parse(pm.request.body.raw);
    if (body.email === "admin@test.com") {
        pm.variables.set("current_role", "admin");
    }
}
```

3. **Create Test Script** (save tokens)

```javascript
if (pm.response.code === 200 || pm.response.code === 201) {
    var jsonData = pm.response.json();
    if (jsonData.data && jsonData.data.access_token) {
        var role = pm.variables.get("current_role") || "user";
        pm.variables.set(role + "_token", jsonData.data.access_token);
        pm.variables.set("access_token", jsonData.data.access_token);
    }
    if (jsonData.data && jsonData.data.id) {
        pm.variables.set("last_id", jsonData.data.id);
    }
}

pm.test("Response status", function() {
    pm.expect(pm.response.code).to.be.oneOf([200, 201, 204]);
});
```

### Sample Postman Collection

```json
{
  "info": {
    "name": "Hotel Management API",
    "version": "1.0"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/register",
            "body": {
              "mode": "raw",
              "raw": "{\"full_name\": \"Test User\", \"email\": \"test@example.com\", \"password\": \"Pass123!\", \"phone\": \"+84901234567\"}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\"email\": \"test@example.com\", \"password\": \"Pass123!\"}"
            }
          }
        }
      ]
    }
  ]
}
```

---

## 🧬 Integration Tests with pytest

### Test File Structure

```
tests/
├── conftest.py              # Fixtures
├── test_auth.py             # Authentication tests
├── test_hotels.py           # Hotel CRUD tests
├── test_rooms.py            # Room tests
├── test_bookings.py         # Booking workflow tests
├── test_payments.py         # Payment tests
├── test_admin.py            # Admin tests
└── test_integration.py      # Full workflow tests
```

### conftest.py

```python
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Hotel, Room

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
def admin_user(app):
    """Create admin user"""
    user = User(
        full_name="Admin",
        email="admin@test.com",
        phone="+84901234567",
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
        full_name="Owner",
        email="owner@test.com",
        phone="+84901234568",
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
        full_name="Guest",
        email="guest@test.com",
        phone="+84901234569",
        role="USER"
    )
    user.set_password("Guest123!")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_token(client, admin_user):
    """Get admin token"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'Admin123!'
    })
    return response.json['data']['access_token']

@pytest.fixture
def owner_token(client, owner_user):
    """Get owner token"""
    response = client.post('/api/auth/login', json={
        'email': 'owner@test.com',
        'password': 'Owner123!'
    })
    return response.json['data']['access_token']

@pytest.fixture
def user_token(client, regular_user):
    """Get user token"""
    response = client.post('/api/auth/login', json={
        'email': 'guest@test.com',
        'password': 'Guest123!'
    })
    return response.json['data']['access_token']

@pytest.fixture
def sample_hotel(app, owner_user):
    """Create sample hotel"""
    hotel = Hotel(
        name="Test Hotel",
        city="Hanoi",
        description="Test Description",
        star_rating=4,
        address="123 Test St",
        phone="+84912345678",
        owner_id=owner_user.id
    )
    db.session.add(hotel)
    db.session.commit()
    return hotel

@pytest.fixture
def sample_room(app, sample_hotel):
    """Create sample room"""
    room = Room(
        hotel_id=sample_hotel.id,
        room_number="101",
        room_type="DELUXE",
        price_per_night=150.00,
        capacity=2,
        amenities="WiFi, AC",
        description="Cozy room"
    )
    db.session.add(room)
    db.session.commit()
    return room
```

### test_auth.py

```python
import pytest

class TestAuthentication:
    """Authentication endpoint tests"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'full_name': 'New User',
            'email': 'newuser@test.com',
            'password': 'Password123!',
            'phone': '+84901234567'
        })
        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['email'] == 'newuser@test.com'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'full_name': 'User',
            'email': 'invalid-email',
            'password': 'Password123!'
        })
        assert response.status_code == 400
        assert 'email' in response.json['errors']

    def test_login_success(self, client, regular_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'guest@test.com',
            'password': 'Guest123!'
        })
        assert response.status_code == 200
        assert 'access_token' in response.json['data']
        assert 'refresh_token' in response.json['data']

    def test_login_wrong_password(self, client, regular_user):
        """Test login with wrong password"""
        response = client.post('/api/auth/login', json={
            'email': 'guest@test.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401

    def test_get_profile(self, client, user_token, regular_user):
        """Test getting user profile"""
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {user_token}'
        })
        assert response.status_code == 200
        assert response.json['data']['email'] == 'guest@test.com'

    def test_logout(self, client, user_token):
        """Test user logout"""
        response = client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {user_token}'
        })
        assert response.status_code == 200
        
        # Next request should fail (token blacklisted)
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {user_token}'
        })
        assert response.status_code == 401
```

### test_bookings.py (Full Workflow)

```python
import pytest
from datetime import datetime, timedelta

class TestBookingWorkflow:
    """Test complete booking workflow"""

    def test_create_booking(self, client, user_token, sample_room):
        """Test creating a booking"""
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        response = client.post('/api/bookings', 
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'John Doe',
                'guest_email': 'john@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 2
            }
        )
        assert response.status_code == 201
        assert response.json['data']['status'] == 'PENDING'
        assert response.json['data']['total_price'] == 450.0  # 3 nights × 150
        return response.json['data']['id']

    def test_booking_confirmation_flow(self, client, admin_token, user_token, sample_room):
        """Test complete booking confirmation flow"""
        # Create booking
        booking_id = self.test_create_booking(client, user_token, sample_room)
        
        # Confirm booking (admin only)
        response = client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'confirmation_note': 'Confirmed'}
        )
        assert response.status_code == 200
        assert response.json['data']['status'] == 'CONFIRMED'
        
        # Check that email was sent (verify in logs)
        # Add review after completion would fail (status check)

    def test_room_unavailable_conflict(self, client, user_token, sample_room):
        """Test booking conflict - room already booked"""
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        # First booking succeeds
        response1 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Guest 1',
                'guest_email': 'g1@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        assert response1.status_code == 201
        
        # Overlapping booking should fail
        response2 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': (check_in + timedelta(days=1)).strftime('%Y-%m-%d'),
                'check_out': (check_out - timedelta(days=1)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest 2',
                'guest_email': 'g2@example.com',
                'guest_phone': '+84901234568',
                'number_of_guests': 1
            }
        )
        assert response2.status_code == 409  # Conflict

    def test_cancellation_penalty(self, client, user_token, admin_token, sample_room):
        """Test cancellation penalty calculation"""
        # Create booking for 5 days from now (enough time for full refund)
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Test Guest',
                'guest_email': 'test@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        booking_id = response.json['data']['id']
        total_price = response.json['data']['total_price']
        
        # Confirm payment first
        client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {admin_token}'})
        
        # Cancel (> 24 hours = full refund)
        response = client.patch(f'/api/bookings/{booking_id}/cancel',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'cancellation_reason': 'Test'}
        )
        assert response.status_code == 200
        penalty = response.json['data']['cancellation_penalty']
        assert penalty == 0  # Full refund
```

---

## 🚀 Running Tests

### Run All Tests

```bash
pytest tests/ -v --tb=short
```

### Run Specific Test File

```bash
pytest tests/test_auth.py -v
```

### Run Specific Test

```bash
pytest tests/test_auth.py::TestAuthentication::test_login_success -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Run in CI/CD

```bash
pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml
```

---

## 📊 Test Coverage Checklist

- [ ] Authentication (Register, Login, Logout, Refresh)
- [ ] Authorization (RBAC - ADMIN, OWNER, USER)
- [ ] Hotels (CRUD, Filters, Stats)
- [ ] Rooms (CRUD, Availability, Calendar)
- [ ] Bookings (Create, Confirm, Complete, Cancel, Review)
- [ ] Payments (Process, Refund, Stats)
- [ ] Admin (Dashboard, Users, Logs)
- [ ] Owner (Dashboard, Hotels, Revenue)
- [ ] Reports (Revenue, Occupancy, Exports)
- [ ] Error Handling (400, 401, 403, 404, 409, 500)
- [ ] Validation (Email, Dates, Phone)
- [ ] Pagination (Page, Per-page)
- [ ] Sorting (By date, price, rating)
- [ ] Filtering (By city, type, price range)

---

## 🐛 Error Testing

### Common Errors to Test

```bash
# 400 Bad Request - Invalid input
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid"}'

# 401 Unauthorized - Missing token
curl -X GET http://localhost:5000/api/auth/me

# 403 Forbidden - Insufficient permissions
curl -X DELETE http://localhost:5000/api/hotels/1 \
  -H "Authorization: Bearer $USER_TOKEN"

# 404 Not Found - Resource doesn't exist
curl -X GET http://localhost:5000/api/hotels/9999

# 409 Conflict - Room already booked
# (See test_room_unavailable_conflict)

# 500 Internal Server Error - Database error
# (Add try-catch tests in service layer)
```

---

## 📈 Performance Testing

### Load Testing with Apache Bench

```bash
# Test login endpoint
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:5000/api/auth/login

# Expected: > 100 req/s
```

### Load Testing with wrk

```bash
# Install: brew install wrk (macOS)
wrk -t12 -c400 -d30s http://localhost:5000/api/hotels

# t = threads, c = connections, d = duration
```

### Database Query Performance

```bash
# Monitor slow queries in PostgreSQL
# Add to PostgreSQL logs:
log_min_duration_statement = 100  # Log queries > 100ms

# Analyze slow queries
SELECT query, calls, mean_time FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```

---

## ✅ Final Test Checklist

Before deploying:

- [ ] All 50+ endpoints tested at least once
- [ ] Authentication flow working (register → login → authenticated request)
- [ ] Authorization enforced (users can't access admin endpoints)
- [ ] Payment simulation working (90% success rate)
- [ ] Email sending functional (check logs/console)
- [ ] MongoDB audit logging working
- [ ] Pagination working (page/per_page parameters)
- [ ] Filtering/Sorting working (hotel filters,  booking sorts)
- [ ] Error messages clear and helpful
- [ ] Response format consistent (all use success_response envelope)
- [ ] No SQL injection vulnerabilities
- [ ] No sensitive data in logs
- [ ] Database transactions working properly
- [ ] Connection pooling stable under load

---

## 📞 Troubleshooting Tests

### Tests passing locally but failing in CI/CD

- Check timezone settings
- Verify database initialization
- Check environment variables setup
- Ensure test data cleanup between runs

### Flaky tests

- Add retry logic: `@pytest.mark.flaky(reruns=3)`
- Increase timeouts for slow operations
- Mock external services (email, payment)

### Test database issues

- Use separate test database
- Clear data between tests with `db.session.rollback()`
- Don't rely on auto-increment IDs in tests

---

**Happy Testing! 🎉**

Next: See QUICK_START.md for running the backend server.
