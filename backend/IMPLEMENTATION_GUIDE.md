# CNPM2 Backend - Implementation Guide & Quick Start

## ✅ What's Been Implemented

### 🏗️ Architecture & Structure

- **Models**: All 6 main models fully implemented
  - User (with bcrypt password hashing)
  - Hotel (multi-owner support)
  - Room (with amenities, rating)
  - Booking (with status tracking)
  - Payment (with multiple methods)
  - Review (post-checkout reviews)

- **Schemas**: Marshmallow validation schemas for all models
  - UserSchema, HotelSchema, RoomSchema, BookingSchema, PaymentSchema, ReviewSchema
  - Response schemas (TokenResponse, SuccessResponse, ErrorResponse)

- **Authentication & Authorization**
  - JWT token-based authentication (access + refresh tokens)
  - Role-based access control (ADMIN, OWNER, USER)
  - Password hashing with bcrypt
  - Token blacklist for logout

- **Services** (Business Logic Layer)
  - BookingService: availability checking, price calculation
  - EmailService: transactional emails (booking confirmation, password reset, receipts)
  - PaymentService: payment creation, simulation (Bank, MoMo, QR)
  - LoggingService: MongoDB audit trail logging

- **Middleware**
  - Auth middleware: role checking, current user retrieval
  - Response helpers: consistent JSON response envelopes
  - Validators: email validation, string sanitization, date validation

- **API Routes** (Blueprints)
  - `/api/auth` - register, login, refresh, logout, password reset, profile
  - `/api/hotels` - CRUD hotels, owner-scoped access
  - `/api/rooms` - CRUD rooms, filtering by hotel/type/price
  - `/api/bookings` - create/list/update/cancel bookings
  - `/api/payments` - create/process/refund payments
  - `/api/admin` - admin dashboard, user management
  - `/api/owner` - owner dashboard, hotel management
  - `/api/reports` - revenue reports, booking statistics

### 🔐 Security Features

- ✅ Password hashing (bcrypt)
- ✅ JWT with expiration + refresh token
- ✅ CSRF protection ready
- ✅ Role-based access control
- ✅ Email validation & sanitization
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configured

### 💾 Database

- **PostgreSQL**: All business data (users, hotels, rooms, bookings, payments, reviews)
- **MongoDB**: Audit logs, request logs, user activity tracking

### 📧 Email Integration

- Flask-Mail configured (Gmail SMTP by default)
- Can send: booking confirmations, cancellations, password resets, payment receipts
- Non-blocking: errors logged, don't block main flow

---

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.10+**
2. **PostgreSQL 12+** (running, database created)
3. **MongoDB 5.0+** (running on localhost:27017)
4. **Python venv** or **Conda** for environment management

### Step 1: Setup Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create `.env` file in backend directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret

# PostgreSQL
DATABASE_URL=postgresql://hoteluser:hotelpass@localhost:5432/hoteldb

# MongoDB
MONGO_URI=mongodb://localhost:27017/hotel_logs

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Frontend
FRONTEND_URL=http://localhost:3000
```

### Step 4: Initialize Database

```bash
# Create tables in PostgreSQL
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.extensions import db; db.create_all(); print('✅ Database tables created')"
```

### Step 5: Run Backend Server

```bash
python run.py
```

Server will start at **http://localhost:5000**

---

## 📚 API Documentation

### Authentication Endpoints

#### Register
```bash
POST /api/auth/register
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "0123456789",
  "password": "securepassword123"
}
```
*Response:* JWT access_token, refresh_token, user object

#### Login
```bash
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Logout
```bash
POST /api/auth/logout
Authorization: Bearer <access_token>
```

---

### Hotel Endpoints

#### Get All Hotels (Public)
```bash
GET /api/hotels?city=HoChiMinh&search=Luxury&page=1&per_page=12
```

#### Create Hotel (OWNER/ADMIN)
```bash
POST /api/hotels
Authorization: Bearer <token>
{
  "name": "Hotel Paradise",
  "address": "123 Mai Street",
  "city": "Ho Chi Minh City",
  "description": "5-star luxury hotel",
  "phone": "0123456789",
  "email": "info@paradise.com",
  "star_rating": 5
}
```

---

### Booking Endpoints

#### Create Booking
```bash
POST /api/bookings
{
  "room_id": 1,
  "check_in": "2025-02-01",
  "check_out": "2025-02-05",
  "guests": 2,
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "0123456789"
}
```

#### Get User Bookings
```bash
GET /api/bookings
Authorization: Bearer <access_token>
```

#### Cancel Booking
```bash
PATCH /api/bookings/<booking_id>
Authorization: Bearer <token>
{
  "status": "CANCELLED",
  "cancel_reason": "Change of plans"
}
```

---

### Payment Endpoints

#### Create Payment
```bash
POST /api/payments
Authorization: Bearer <token>
{
  "booking_id": 1,
  "amount": 250000,
  "method": "BANK_TRANSFER"
}
```

#### Process Payment (Simulate)
```bash
POST /api/payments/<payment_id>/process
{
  "method": "bank",  // "bank", "momo", "qr"
  "success": true
}
```

---

## 🧪 Testing

### Run Backend Tests
```bash
pytest tests/ -v
```

### Test with Postman/Insomnia
1. Import collection from `postman_collection.json`
2. Set `base_url` variable: `http://localhost:5000`
3. Set bearer token after login
4. Run requests

### Manual Testing (cURL)

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'

# Get hotels
curl http://localhost:5000/api/hotels
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Marshmallow validation
│   ├── routes/              # API blueprints
│   ├── services/            # Business logic
│   ├── middleware/          # Auth, logging, etc.
│   ├── utils/               # Helpers, validators
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   └── __init__.py          # App factory
├── tests/                   # Unit tests
├── run.py                   # Entry point
├── requirements.txt         # Dependencies
└── .env.example            # Environment template
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | App environment |
| `SECRET_KEY` | change-this | Flask secret key |
| `DATABASE_URL` | postgresql://hoteluser:hotelpass@localhost:5432/hoteldb | PostgreSQL connection |
| `MONGO_URI` | mongodb://localhost:27017/hotel_logs | MongoDB connection |
| `JWT_SECRET_KEY` | change-jwt-secret | JWT signing key |
| `JWT_ACCESS_TOKEN_EXPIRES_HOURS` | 24 | Access token lifetime |
| `JWT_REFRESH_TOKEN_EXPIRES_DAYS` | 30 | Refresh token lifetime |

---

## 🚨 Common Issues & Solutions

### Issue: `ProgrammingError: relation "users" does not exist`
**Solution**: Initialize database tables
```bash
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.extensions import db; db.create_all()"
```

### Issue: `ConnectionRefusedError: cannot connect to PostgreSQL`
**Solution**: Ensure PostgreSQL is running
```bash
# macOS with Homebrew
brew services start postgresql

# Linux
sudo service postgresql start

# Windows
# Start via SQL Server admin panel
```

### Issue: `ConnectionFailure: cannot connect to MongoDB`
**Solution**: Ensure MongoDB is running
```bash
# macOS
brew services start mongodb-community

# Linux
sudo service mongod start

# Windows
# Start MongoDB Server from Control Panel
```

### Issue: Email sending fails
**Solution**: Check Gmail settings
- Enable 2-factor authentication
- Generate [App Password](https://myaccount.google.com/apppasswords)
- Use app password in `.env` not regular password

---

## 📈 Next Steps

1. **Frontend**: Build React SPA in `../frontend/`
2. **Testing**: Write comprehensive pytest tests
3. **Documentation**: Generate Swagger/OpenAPI docs
4. **Deployment**: Containerize with Docker, deploy to server
5. **Monitoring**: Setup logging dashboard, error tracking

---

## 📞 Support

For issues or questions:
1. Check logs in `VSCODE_TARGET_SESSION_LOG`
2. Review error responses in JSON format
3. Verify environment variables in `.env`
4. Check database connections (PostgreSQL + MongoDB)

---

**Happy Coding! 🎉**
