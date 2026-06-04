# ⚡ CNPM2 Backend - Quick Setup Guide

## 5-Minute Setup

### 1️⃣ Prerequisites
- Python 3.10+
- PostgreSQL 12+ (running)
- MongoDB 5.0+ (running)

### 2️⃣ Clone & Setup Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows cmd
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Database
```bash
# Create .env from template
cp .env.example .env

# Edit .env — change these:
# - DATABASE_URL=postgresql://hoteluser:hotelpass@localhost:5432/hoteldb
# - MONGO_URI=mongodb://localhost:27017/hotel_logs
# - MAIL_USERNAME, MAIL_PASSWORD (optional)
```

### 5️⃣ Initialize Database
```bash
# Create PostgreSQL tables
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.extensions import db; db.create_all(); print('✅ Database ready')"
```

### 6️⃣ Run Backend
```bash
python run.py
```

✅ **Backend running at:** http://localhost:5000

---

## 🧪 Quick Testing

### Test Using cURL

```bash
# 1. Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'

# Response: { "success": true, "data": { "user": {...}, "access_token": "..." } }

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# 3. Get Profile (use access_token from response)
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. List Hotels (public)
curl http://localhost:5000/api/hotels

# 5. List Rooms with Filters
curl "http://localhost:5000/api/rooms?hotel_id=1&min_price=100&max_price=500&page=1&per_page=10"
```

### Test Using Postman

1. Import collection: (see postman_collection.json if available)
2. Set variable: `base_url = http://localhost:5000`
3. Set variable: `access_token` from login response
4. Run requests

---

## 📋 API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get profile
- `PUT /api/auth/me` - Update profile
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Hotels
- `GET /api/hotels` - List all hotels (public)
- `GET /api/hotels/<id>` - Hotel detail with rooms
- `POST /api/hotels` - Create hotel (ADMIN/OWNER)
- `PUT /api/hotels/<id>` - Update hotel (ADMIN/OWNER)
- `DELETE /api/hotels/<id>` - Disable hotel (ADMIN)
- `GET /api/hotels/<id>/stats` - Hotel statistics

### Rooms
- `GET /api/rooms` - List rooms with filters
- `GET /api/rooms/<id>` - Room detail with reviews
- `GET /api/rooms/<id>/availability` - Check availability calendar
- `POST /api/rooms` - Create room (ADMIN/OWNER)
- `PUT /api/rooms/<id>` - Update room (ADMIN/OWNER)
- `DELETE /api/rooms/<id>` - Delete room (ADMIN)

### Bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings` - List bookings (ADMIN/OWNER)
- `GET /api/bookings/my` - My bookings (USER)
- `GET /api/bookings/<id>` - Booking detail
- `PATCH /api/bookings/<id>/confirm` - Confirm booking (ADMIN/OWNER)
- `PATCH /api/bookings/<id>/complete` - Mark completed (ADMIN/OWNER)
- `PATCH /api/bookings/<id>/cancel` - Cancel booking
- `POST /api/bookings/<id>/review` - Post review (USER)
- `GET /api/bookings/<id>/reviews` - Get room reviews

### Payments
- `GET /api/payments/booking/<booking_id>` - Payment detail
- `POST /api/payments/process` - Process payment
- `POST /api/payments/refund/<id>` - Refund payment (ADMIN)
- `GET /api/payments/list` - List payments (ADMIN/OWNER)
- `GET /api/payments/stats` - Payment statistics

### Admin
- `GET /api/admin/dashboard` - Admin dashboard
- `GET /api/admin/users` - List users
- `GET /api/admin/users/<id>` - User detail
- `PUT /api/admin/users/<id>` - Update user role/status
- `GET /api/admin/logs` - Audit logs from MongoDB

### Owner
- `GET /api/owner/dashboard` - Owner dashboard
- `GET /api/owner/hotels` - Owner's hotels
- `GET /api/owner/rooms` - Owner's rooms
- `GET /api/owner/bookings` - Owner's bookings
- `GET /api/owner/revenue` - Revenue statistics
- `GET /api/owner/hotel/<hotel_id>/stats` - Hotel detailed stats

### Reports
- `GET /api/reports/revenue` - Revenue report (daily/monthly/yearly)
- `GET /api/reports/occupancy` - Room occupancy report
- `GET /api/reports/bookings` - Booking statistics
- `GET /api/reports/export/pdf` - Export report as PDF
- `GET /api/reports/export/excel` - Export report as Excel

---

## 🔐 Default Test Accounts

After database initialization, create test accounts:

```sql
-- Create ADMIN user (if needed)
INSERT INTO users (full_name, email, phone_number, password_hash, role, enabled, created_at, updated_at)
VALUES ('Admin', 'admin@hotel.com', '0123456789', '$2b$12$...', 'ADMIN', true, NOW(), NOW());

-- Create OWNER user
INSERT INTO users (full_name, email, phone_number, password_hash, role, enabled, created_at, updated_at)
VALUES ('Owner', 'owner@hotel.com', '0987654321', '$2b$12$...', 'OWNER', true, NOW(), NOW());
```

Or register through API:

```bash
# Register as USER
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name": "User", "email": "user@hotel.com", "password": "pass123"}'

# Admin/Owner role can be changed via admin API
```

---

## 🆘 Troubleshooting

### `ModuleNotFoundError: No module named 'app'`
**Solution:** Run from backend directory, activate venv first
```bash
cd backend
source venv/bin/activate
python run.py
```

### `postgresql: Connection refused`
**Solution:** Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql

# Linux
sudo service postgresql start

# Verify
psql --version
```

### `pymongo.errors.ConnectionFailure`
**Solution:** Ensure MongoDB is running
```bash
# macOS
brew services start mongodb-community

# Linux
sudo service mongod start

# Verify
mongosh --eval "db.adminCommand('ping')"
```

### `sqlalchemy.exc.ProgrammingError: relation "users" does not exist`
**Solution:** Initialize database tables
```bash
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.extensions import db; db.create_all()"
```

### JWT token errors
**Solution:** Ensure `JWT_SECRET_KEY` is set in `.env`

### Email sending fails
**Solution:** Gmail only — enable [App Passwords](https://myaccount.google.com/apppasswords), use that password in `.env`

---

## 📚 Documentation Files

- **DATABASE_SETUP.md** - Complete database setup with Docker
- **IMPLEMENTATION_GUIDE.md** - Full API documentation & examples
- **DEVELOPMENT_SUMMARY.md** - Project summary & statistics

---

## 🚀 Next Steps

1. ✅ Setup backend & run server
2. 🏗️ Build React frontend in `../frontend/`
3. 🧪 Write tests (pytest, Postman)
4. 🐳 Containerize with Docker
5. 📤 Deploy to server (VPS, Heroku, AWS)

---

**Happy Coding! 🎉**

For full guides, see: `IMPLEMENTATION_GUIDE.md`, `DATABASE_SETUP.md`
