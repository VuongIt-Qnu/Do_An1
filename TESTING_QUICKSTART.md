# API Testing Documentation - Quick Reference

Complete testing setup for Hotel Management API with 50+ endpoints.

---

## 📂 What's Included

| File | Purpose |
|------|---------|
| **API_TESTING.md** | 📖 Complete testing guide (cURL, Postman, pytest) |
| **POSTMAN_COLLECTION.json** | 📮 Ready-to-import Postman collection |
| **tests/conftest.py** | 🔧 pytest fixtures & test setup |
| **tests/test_auth.py** | 🔐 Authentication tests (15 tests) |
| **tests/test_hotels.py** | 🏨 Hotel CRUD tests (18 tests) |
| **tests/test_bookings.py** | 📅 Booking workflow tests (12 tests) |
| **tests/test_integration.py** | 🔗 Full workflow integration tests (15 tests) |

---

## 🚀 Quick Start Options

### Option 1: Manual Testing with cURL (Fastest)

docker exec hotel_backend python seed.py

```bash
# Start backend
cd backend
python run.py

# Open new terminal
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","email":"test@example.com","password":"Pass123!","phone":"+84901234567"}'

# Login & save token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!"}' \
  | jq -r '.data.access_token')

# Make authenticated request
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

See **API_TESTING.md** for 50+ curl examples.

---

### Option 2: Visual Testing with Postman (Recommended)

#### Setup Postman

1. **Install Postman**: https://www.postman.com/downloads/
2. **Import Collection**:
   - Open Postman
   - Click "Import"
   - Select `POSTMAN_COLLECTION.json` from project root
3. **Configure Environment**:
   - Create environment named "Local"
   - Set variables:
     - `base_url` = `http://localhost:5000/api`
     - `access_token` = (auto-filled)
     - `admin_token` = (auto-filled)
   - Select environment in top-right

#### Test Workflow

1. Run **Register** request → Copy email
2. Run **Login** request → Auto-saves `access_token`
3. Run authenticated requests (Get Profile, etc.)
4. View response in "Response" tab

**Note:** All token variables auto-populate from response using Scripts tab.

---

### Option 3: Automated Testing with pytest (Best for CI/CD)

#### Setup

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

#### Test Files Structure

```
tests/
├── conftest.py              # Shared fixtures (users, tokens, data)
├── test_auth.py             # 15 auth tests
├── test_hotels.py           # 18 hotel tests
├── test_bookings.py         # 12 booking tests
└── test_integration.py      # 15 full workflow tests
```

#### Example: Run Authentication Tests

```bash
pytest tests/test_auth.py::TestUserLogin::test_login_success -v
```

---

## 📊 Test Coverage

**Total Tests:** 60+

| Category | Tests | Files |
|----------|-------|-------|
| Authentication | 15 | test_auth.py |
| Hotels | 18 | test_hotels.py |
| Bookings | 12 | test_bookings.py |
| Integration | 15 | test_integration.py |
| **Total** | **60** | **4 files** |

---

## 🔍 What Gets Tested

✅ **Authentication** - Register, login, token refresh, logout  
✅ **Authorization** - RBAC (ADMIN/OWNER/USER) enforcement  
✅ **CRUD Operations** - Create, read, update, delete for all resources  
✅ **Business Logic** - Price calculation, availability checking, penalties  
✅ **Error Handling** - 400, 401, 403, 404, 409, 500 errors  
✅ **Validation** - Email, phone, dates, required fields  
✅ **Conflicts** - Overlapping bookings, duplicate data  
✅ **Pagination** - Page, per_page, total calculations  
✅ **Access Control** - Users can only access their data  
✅ **Data Sanitization** - XSS prevention, HTML escaping  

---

## 🧪 Running Tests in Different Modes

### Mode 1: Quick Smoke Test (2 minutes)

```bash
pytest tests/test_auth.py::TestUserRegistration::test_register_success -v
pytest tests/test_hotels.py::TestHotelsListing::test_list_hotels_public -v
```

### Mode 2: Full Auth Testing (5 minutes)

```bash
pytest tests/test_auth.py -v
```

### Mode 3: Complete Test Suite (10 minutes)

```bash
pytest tests/ -v
```

### Mode 4: With Coverage Report (15 minutes)

```bash
pytest tests/ -v --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Mode 5: Only Failed Tests

```bash
pytest tests/ -v --last-failed
```

---

## 🛠️ Common Testing Tasks

### Test User Registration Flow

```bash
pytest tests/test_auth.py::TestUserRegistration -v
```

### Test Booking Conflicts

```bash
pytest tests/test_bookings.py::TestBookingConflicts::test_overlapping_bookings_conflict -v
```

### Test Admin Access Control

```bash
pytest tests/test_auth.py::TestRoleBasedAccess -v
```

### Test Complete Booking Workflow

```bash
pytest tests/test_integration.py::TestCompleteBookingWorkflow::test_full_booking_to_review_workflow -v
```

### Test Data Validation

```bash
pytest tests/test_integration.py::TestDataValidation -v
```

---

## 📋 Test Data Overview

### Test Users (Auto-created by pytest)

```python
admin_user     → admin@test.com / Admin123!  (ADMIN)
owner_user     → owner@test.com / Owner123!  (OWNER)
regular_user   → guest@test.com / Guest123!  (USER)
```

### Test Hotels (Auto-created)

- Test Hotel in Hanoi (5-star)
- Test Hotel in Ho Chi Minh (4-star)
- Test Hotel in Da Nang (3-star)

### Test Rooms (Auto-created)

- STANDARD: $100/night, 1 capacity
- DELUXE: $150/night, 2 capacity
- SUITE: $250/night, 4 capacity

---

## 🔧 Fixtures Available in Tests

```python
# Users
admin_user, owner_user, regular_user

# Tokens
admin_token, owner_token, user_token

# Resources
sample_hotel, multiple_hotels
sample_room, multiple_rooms

# Test Data
valid_user_data, valid_hotel_data, 
valid_room_data, valid_booking_data

# Helpers
helpers.get_auth_header(token)
helpers.assert_success_response(data)
```

---

## 📈 Performance Testing

### Load Testing with Apache Bench

```bash
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:5000/api/auth/login

# Expected: > 100 req/sec
```

### Load Testing with wrk

```bash
wrk -t12 -c400 -d30s http://localhost:5000/api/hotels

# t = threads, c = connections, d = duration
```

---

## ❌ Error Testing Examples

### Test 400 Bad Request

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid"}'  # Missing required fields

# Expected: 400 Bad Request
```

### Test 401 Unauthorized

```bash
curl -X GET http://localhost:5000/api/auth/me
# No Authorization header

# Expected: 401 Unauthorized
```

### Test 403 Forbidden

```bash
TOKEN=$(curl -s ... login user ...)
curl -X DELETE http://localhost:5000/api/hotels/1 \
  -H "Authorization: Bearer $TOKEN"

# Expected: 403 Forbidden (user insufficient permissions)
```

### Test 404 Not Found

```bash
curl -X GET http://localhost:5000/api/hotels/99999

# Expected: 404 Not Found
```

### Test 409 Conflict

```bash
# Try to book same room for overlapping dates
curl -X POST http://localhost:5000/api/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "check_in": "2026-04-25", "check_out": "2026-04-28", ...}'

# If another booking overlaps:
# Expected: 409 Conflict
```

---

## 🐛 Debugging Tests

### Run test with print output

```bash
pytest tests/test_auth.py::TestUserLogin -v -s
# -s = show print statements
```

### Run with detailed traceback

```bash
pytest tests/test_auth.py -v --tb=long
```

### Run with pdb debugger

```bash
pytest tests/test_auth.py -v --pdb
# Drops into debugger on failure
```

### Generate junit XML for CI/CD

```bash
pytest tests/ --junitxml=results.xml --cov=app --cov-report=xml
```

---

## 💾 Database for Testing

By default, pytest uses **in-memory SQLite** to avoid modifying production database.

Configure in `app/config.py`:

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
```

Data is auto-created by fixtures via `db.create_all()`.

---

## 📞 Troubleshooting

### "Module not found" error

```bash
# Ensure you're in correct directory
cd backend

# Ensure venv is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Tests pass locally but fail in CI/CD

- Check environment variables in CI/CD
- Verify database initialization
- Check timezone settings
- Ensure test database isolation

### Flaky tests

- Add retry logic: `@pytest.mark.flaky(reruns=3)`
- Increase timeouts for slow operations
- Mock external services (email, payment)

### Out of memory

- Reduce `per_page` in pagination tests
- Don't create massive datasets
- Use `db.session.rollback()` between tests

---

## 📚 Additional Resources

| File | Purpose |
|------|---------|
| **QUICK_START.md** | 5-minute backend setup |
| **IMPLEMENTATION_GUIDE.md** | Detailed API documentation |
| **DATABASE_SETUP.md** | PostgreSQL & MongoDB setup |
| **README.md (backend)** | Backend overview |

---

## ✅ Before Deploying

- [ ] All pytest tests passing: `pytest tests/ -v`
- [ ] Postman collection testing complete
- [ ] cURL examples tested
- [ ] Error scenarios validated
- [ ] Performance acceptable (> 100 req/sec)
- [ ] No sensitive data in logs
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] Authorization enforced
- [ ] Pagination working

---

## 🎯 Next Steps

1. **Start Backend**: `python run.py`
2. **Choose Testing Method**:
   - Quick: cURL examples
   - Visual: Postman collection
   - Automated: pytest suite
3. **Test Core Flows**: Auth → Hotels → Bookings → Payments
4. **Run Full Suite**: `pytest tests/ -v`
5. **Generate Report**: `pytest tests/ --cov=app --cov-report=html`

---

**Happy Testing! 🎉**

For detailed examples and API documentation, see **API_TESTING.md**
