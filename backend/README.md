# Hotel Management System CNPM2 - Backend (Flask REST API)

## 🎯 Status: ✅ READY FOR DEVELOPMENT

Complete backend implementation for CNPM2 Hotel Management System with REST API, JWT authentication, role-based access control, and comprehensive business logic.

---

## ✨ What's Included

### 🏗️ Architecture
- **Framework**: Flask 3.0.3 REST API
- **Database**: PostgreSQL (business data) + MongoDB (audit logs)
- **Authentication**: JWT tokens (access + refresh)
- **Authorization**: Role-Based Access Control (ADMIN, OWNER, USER)
- **ORM**: SQLAlchemy 2.0 with connection pooling

### 📦 Components

#### Models (6 total)
- `User` - With bcrypt password hashing
- `Hotel` - Multi-owner support
- `Room` - With amenities and ratings
- `Booking` - Full lifecycle management
- `Payment` - Multiple payment methods
- `Review` - Post-checkout reviews

#### Schemas (11 total)
Marshmallow validation schemas for all models + response envelopes

#### API Routes (50+ Endpoints)
- **Authentication** (8) - register, login, profile, password reset
- **Hotels** (6) - CRUD, stats, multi-hotel support
- **Rooms** (6) - Filtering, availability calendar
- **Bookings** (9) - Create, confirm, complete, cancel, review
- **Payments** (5) - Process, refund, stats
- **Admin** (5) - Dashboard, user management, audit logs
- **Owner** (7) - Dashboard, hotel stats, revenue analytics
- **Reports** (4) - Revenue, occupancy, bookings, PDF/Excel export

#### Services (4 files)
- **BookingService** - Availability checking, price calculation, penalty logic
- **EmailService** - Transactional emails (confirmations, resets, receipts)
- **PaymentService** - Payment simulation (Bank, MoMo, QR)
- **LoggingService** - MongoDB audit trail (action logs, request logs, user activity)

#### Middleware
- **AuthMiddleware** - JWT verification, role checking
- **ResponseHelpers** - Consistent JSON envelopes
- **Validators** - Email, dates, sanitization

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Install Python 3.10+
python --version

# PostgreSQL 12+
psql --version

# MongoDB 5.0+
mongosh --version
```

### Setup
```bash
# 1. Create environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env → DATABASE_URL, MONGO_URI, etc.

# 4. Initialize database
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.extensions import db; db.create_all()"

# 5. Run
python run.py
```

**Server running at:** http://localhost:5000

### Quicktest
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test", "email":"test@example.com", "password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "password":"pass123"}'

# List hotels
curl http://localhost:5000/api/hotels
```

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| **QUICK_START.md** | 5-minute setup guide (START HERE) |
| **IMPLEMENTATION_GUIDE.md** | Complete API docs, setup steps, examples |
| **DATABASE_SETUP.md** | PostgreSQL & MongoDB setup, Docker Compose |
| **DEVELOPMENT_SUMMARY.md** | Project summary, statistics, architecture |

---

## 🔐 Security Features

✅ Password hashing (bcrypt)
✅ JWT with expiration + refresh tokens
✅ Token blacklist for logout
✅ Role-based access control (ADMIN, OWNER, USER)
✅ CORS configured
✅ SQL injection protection (ORM)
✅ Email validation & string sanitization
✅ Audit logging to MongoDB

---

## 📊 Project Statistics

| Metric | Count |
|--------|-------|
| Models | 6 |
| Schemas | 11 |
| API Endpoints | 50+ |
| Service Files | 4 |
| Routes Files | 8 |
| Lines of Code | 3,500+ |

---

## 🛣️ API Overview

### Authentication
```
POST   /api/auth/register         - Register
POST   /api/auth/login            - Login
POST   /api/auth/refresh          - Refresh token
POST   /api/auth/logout           - Logout
GET    /api/auth/me               - Get profile
PUT    /api/auth/me               - Update profile
```

### Hotels & Rooms
```
GET    /api/hotels                - List (public)
POST   /api/hotels                - Create (ADMIN/OWNER)
GET    /api/rooms                 - List with filters
POST   /api/rooms                 - Create (ADMIN/OWNER)
GET    /api/rooms/<id>/availability - Check dates
```

### Bookings & Payments
```
POST   /api/bookings              - Create booking
GET    /api/bookings/my           - My bookings
PATCH  /api/bookings/<id>/cancel  - Cancel
POST   /api/payments/process      - Process payment
```

### Admin & Owner
```
GET    /api/admin/dashboard       - Admin stats (ADMIN)
GET    /api/owner/dashboard       - Owner stats (OWNER)
GET    /api/owner/revenue         - Revenue analytics
```

### Reports
```
GET    /api/reports/revenue       - Revenue report
GET    /api/reports/export/pdf    - PDF export
GET    /api/reports/export/excel  - Excel export
```

---

## 💾 Database

### PostgreSQL Schema
```
users → hotels → rooms → bookings
           ↓
       payments → invoices
           ↓
       reviews
```

### MongoDB Collections
- `audit_logs` - All system actions
- `request_logs` - HTTP requests
- `user_activities` - User behavior tracking

---

## 🔧 Configuration

### Environment Variables
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@localhost:5432/hoteldb
MONGO_URI=mongodb://localhost:27017/hotel_logs
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Supported Environments
- `development` - Debug mode, SQL echo enabled
- `production` - No debug, SSL cookies
- `testing` - In-memory SQLite database

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Manual Testing (cURL)
See **QUICK_START.md** for curl examples

### API Testing (Postman)
1. Import collection (if available)
2. Set `base_url` variable
3. Login to get `access_token`
4. Run requests

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/              ✅ 6 models
│   ├── schemas/             ✅ 11 schemas
│   ├── routes/              ✅ 8 files, 50+ endpoints
│   ├── services/            ✅ 4 service files
│   ├── middleware/          ✅ Auth, logging
│   ├── utils/               ✅ Validators, helpers
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
├── tests/                   (ready for unit tests)
├── run.py                   ✅ Entry point
├── requirements.txt         ✅ Dependencies
├── .env.example             ✅ Configuration template
├── .gitignore
├── QUICK_START.md          ✅ Quick setup guide
├── IMPLEMENTATION_GUIDE.md ✅ Full documentation
├── DATABASE_SETUP.md       ✅ Database guide
└── DEVELOPMENT_SUMMARY.md  ✅ Project summary
```

---

## 🚀 Next Steps

1. **Read QUICK_START.md** for immediate setup
2. **Setup databases** (PostgreSQL + MongoDB)
3. **Configure .env** with your credentials
4. **Run backend server** (`python run.py`)
5. **Test API endpoints** (curl, Postman, or Insomnia)
6. **Build React frontend** in `../frontend/`
7. **Write tests** (pytest, Postman)
8. **Deploy with Docker** (see DATABASE_SETUP.md)

---

## 🆘 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `psql --version`
- Verify MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
- Check connection strings in `.env`

### Module Import Errors
- Run from `backend/` directory
- Ensure venv is activated
- Run: `pip install -r requirements.txt` again

### JWT Token Errors
- Verify `JWT_SECRET_KEY` is set in `.env`
- Ensure token is sent in `Authorization: Bearer TOKEN` header

### Email Sending Fails
- Gmail only: Enable [App Passwords](https://myaccount.google.com/apppasswords)
- Use app password (not regular login password)

---

## 📋 Checklist - Ready to Use ✅

- ✅ All models implemented
- ✅ All schemas created
- ✅ All API routes working
- ✅ Authentication & authorization complete
- ✅ Services layer implemented
- ✅ MongoDB logging integrated
- ✅ Email service ready
- ✅ Payment simulation ready
- ✅ Error handling & validation
- ✅ CORS configured
- ✅ Configuration management
- ✅ Documentation complete

---

## 📞 Support

- Check **QUICK_START.md** for quick setup
- Read **IMPLEMENTATION_GUIDE.md** for detailed API docs
- See **DATABASE_SETUP.md** for database issues
- Review **DEVELOPMENT_SUMMARY.md** for architecture

---

## 📄 License

This is a university project (CNPM2) for educational purposes.

---

**Backend Status: 🟢 READY FOR DEVELOPMENT**

Start with: `cat QUICK_START.md`

Happy coding! 🚀
