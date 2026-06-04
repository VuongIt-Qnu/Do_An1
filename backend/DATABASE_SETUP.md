# Database Setup Guide - CNPM2 Hotel System

## Prerequisites

- PostgreSQL 12+ installed and running
- MongoDB 5.0+ installed and running
- Database administration tools (psql, mongosh)

---

## PostgreSQL Setup (Business Data)

### 1. Create Database & User

```bash
# Connect as PostgreSQL superuser
psql -U postgres

# Create database
CREATE DATABASE hoteldb;

# Create user
CREATE USER hoteluser WITH PASSWORD 'hotelpass';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hoteldb TO hoteluser;
```

### 2. Connect as New User

```bash
psql -U hoteluser -d hoteldb -h localhost
```

### 3. Initialize SQLAlchemy Tables

The backend will auto-create tables on first run in development mode:

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize tables
python -c "
from app import create_app
from app.extensions import db

app = create_app('development')
with app.app_context():
    db.create_all()
    print('✅ All tables created successfully!')
"
```

### 4. Verify Tables

```bash
psql -U hoteluser -d hoteldb -h localhost

# List tables
\dt

# Should see tables:
# - users
# - hotels
# - rooms
# - bookings
# - payments
# - reviews
```

### 5. Insert Sample Data (Optional)

```sql
-- Insert roles
INSERT INTO users (id, full_name, email, phone_number, password_hash, role, created_at, updated_at)
VALUES 
  (1, 'Admin User', 'admin@hotel.com', '0123456789', 
   '$2b$12$...', 'ADMIN', NOW(), NOW()),
  (2, 'Owner User', 'owner@hotel.com', '0987654321',
   '$2b$12$...', 'OWNER', NOW(), NOW());

-- Insert a hotel
INSERT INTO hotels (owner_id, name, address, city, description, phone, email, star_rating, enabled, created_at, updated_at)
VALUES 
  (2, 'Saigon Paradise', '123 Nguyen Hue', 'Ho Chi Minh City', 
   'Luxury 5-star hotel in the heart of Saigon', '0123456789', 
   'info@saigonparadise.com', 5, true, NOW(), NOW());

-- Insert a room
INSERT INTO rooms (hotel_id, name, room_type, capacity, price_per_night, area, amenities, description, rating, featured, status, created_at, updated_at)
VALUES
  (1, 'Deluxe Room 101', 'Deluxe', 2, 150000.00, 30.0,
   'Wifi,TV,AC,Minibar,Balcony', 'Spacious room with city view', 4.5, true,
   'AVAILABLE', NOW(), NOW());
```

---

## MongoDB Setup (Logging & Audit)

### 1. Start MongoDB Service

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux (Ubuntu/Debian)
sudo service mongod start

# Docker
docker run -d -p 27017:27017 --name mongodb mongo

# Windows
# Start via MongoDB Compass or Services
```

### 2. Verify Connection

```bash
# Using mongosh
mongosh mongodb://localhost:27017

# Create database (implicit on first insert)
use hotel_logs
```

### 3. Create Collections (Auto-created by Python)

Collections are automatically created when first data is inserted:
- `audit_logs` - Audit trail of all important actions
- `request_logs` - HTTP request logging
- `user_activities` - User activity tracking

### 4. Create Indexes for Performance

```bash
mongosh mongodb://localhost:27017/hotel_logs

# Audit logs indexes
db.audit_logs.createIndex({ "user_id": 1, "created_at": -1 })
db.audit_logs.createIndex({ "action": 1 })
db.audit_logs.createIndex({ "target_type": 1, "target_id": 1 })

# Request logs indexes
db.request_logs.createIndex({ "created_at": -1 })
db.request_logs.createIndex({ "endpoint": 1 })
db.request_logs.createIndex({ "status_code": 1 })

# User activities indexes
db.user_activities.createIndex({ "user_id": 1, "created_at": -1 })
db.user_activities.createIndex({ "activity_type": 1 })

# TTL index: auto-delete logs after 90 days
db.request_logs.createIndex({ "created_at": 1 }, { expireAfterSeconds: 7776000 })
```

### 5. Verify Collections

```bash
mongosh mongodb://localhost:27017/hotel_logs

# List collections
show collections

# Check indexes
db.audit_logs.getIndexes()
```

---

## Database Connection Checklist

### PostgreSQL

```bash
# Test connectivity
psql -U hoteluser -d hoteldb -h localhost -c "SELECT 1;"
# Should return: 1

# View connection string
DATABASE_URL=postgresql://hoteluser:hotelpass@localhost:5432/hoteldb
```

### MongoDB

```bash
# Test connectivity
mongosh --eval "db.adminCommand('ping')"
# Should output: { ok: 1 }

# Connection string
MONGO_URI=mongodb://localhost:27017/hotel_logs
```

---

## Environment Variables (.env)

```
# PostgreSQL
DATABASE_URL=postgresql://hoteluser:hotelpass@localhost:5432/hoteldb

# MongoDB
MONGO_URI=mongodb://localhost:27017/hotel_logs

# Flask
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

---

## Docker Compose Alternative (Recommended)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: hoteluser
      POSTGRES_PASSWORD: hotelpass
      POSTGRES_DB: hoteldb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hoteluser"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7-alpine
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: hotel_logs
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:  # Optional - for caching, session store
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

Start all services:

```bash
docker-compose up -d

# Verify
docker-compose ps
```

Stop services:

```bash
docker-compose down
```

---

## Database Backup & Restore

### PostgreSQL Backup

```bash
# Backup
pg_dump -U hoteluser -d hoteldb > backup_hoteldb.sql

# Restore
psql -U hoteluser -d hoteldb < backup_hoteldb.sql
```

### MongoDB Backup

```bash
# Using mongodump
mongodump --db hotel_logs --out /path/to/backup

# Restore
mongorestore --db hotel_logs /path/to/backup
```

---

## Troubleshooting

### PostgreSQL Issues

```bash
# Check if PostgreSQL is running
pg_isready -U hoteluser

# View logs
tail -f /var/log/postgresql/postgresql.log

# Restart service
sudo service postgresql restart
```

### MongoDB Issues

```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# View logs
tail -f /var/log/mongodb/mongod.log

# Restart service
sudo service mongod restart
```

### Connection Refused

1. Verify service is running
2. Check port 5432 (PostgreSQL) and 27017 (MongoDB)
3. Verify credentials in `.env`
4. Firewall settings allow connections

---

**Database setup complete! ✅**

Proceed to `IMPLEMENTATION_GUIDE.md` for next steps.
