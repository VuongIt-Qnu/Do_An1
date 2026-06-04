# Hướng Dẫn Chạy Dự Án CNPM2 — Hotel Management System

> Stack: **Flask REST API** · **ReactJS 18** · **PostgreSQL 15** · **MongoDB 7** · **Docker Compose** · **Nginx**

---

## Mục Lục

1. [Yêu Cầu Hệ Thống](#1-yêu-cầu-hệ-thống)
2. [Cài Đặt Nhanh (Quick Start)](#2-cài-đặt-nhanh-quick-start)
3. [Cấu Hình Môi Trường](#3-cấu-hình-môi-trường)
4. [Chạy Với Docker Compose](#4-chạy-với-docker-compose)
5. [Chạy Thủ Công (Không Dùng Docker)](#5-chạy-thủ-công-không-dùng-docker)
6. [Kiểm Tra Hệ Thống](#6-kiểm-tra-hệ-thống)
7. [Tài Khoản Demo](#7-tài-khoản-demo)
8. [Các Lệnh Thường Dùng](#8-các-lệnh-thường-dùng)
9. [Xử Lý Lỗi Thường Gặp](#9-xử-lý-lỗi-thường-gặp)
10. [Dừng Và Dọn Dẹp](#10-dừng-và-dọn-dẹp)

---

## 1. Yêu Cầu Hệ Thống

| Phần mềm | Phiên bản tối thiểu | Kiểm tra |
|-----------|---------------------|---------|
| Docker Desktop | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ (tích hợp trong Docker Desktop) | `docker compose version` |
| Git | 2.x | `git --version` |
| RAM | 4 GB trống | — |
| Disk | 5 GB trống | — |

> **Không cần** cài Python, Node.js, PostgreSQL, hay MongoDB trên máy — Docker lo hết.

---

## 2. Cài Đặt Nhanh (Quick Start)

```bash
# 1. Clone project (hoặc mở thư mục project đã có)
cd CNPM2

# 2. Tạo file .env từ template
cp .env.example .env

# 3. Khởi động toàn bộ hệ thống
docker compose up --build

# 4. Truy cập ứng dụng
# http://localhost:80  →  ReactJS Frontend
# http://localhost:5000/api  →  Flask REST API
```

Lần đầu build mất khoảng **3–5 phút** (tải images, cài dependencies).

---

## 3. Cấu Hình Môi Trường

### 3.1 Tạo file `.env`

```bash
cp .env.example .env
```

### 3.2 Chỉnh sửa `.env`

Mở file `.env` và cập nhật các giá trị quan trọng:

```ini
# ── Bắt buộc phải đổi trong production ────────────────────────────
SECRET_KEY=thay-bang-chuoi-bi-mat-manh-it-nhat-32-ky-tu
JWT_SECRET_KEY=thay-bang-jwt-secret-khac-voi-secret-key

# ── Database (giữ nguyên nếu dùng Docker) ─────────────────────────
POSTGRES_DB=hoteldb
POSTGRES_USER=hoteluser
POSTGRES_PASSWORD=hotelpass
DATABASE_URL=postgresql://hoteluser:hotelpass@postgres:5432/hoteldb

# ── MongoDB ────────────────────────────────────────────────────────
MONGO_URI=mongodb://mongo:27017/hotel_logs

# ── Email (tuỳ chọn — không cần để test) ──────────────────────────
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password   # Dùng App Password của Gmail, không phải mật khẩu thường

# ── Frontend URL ───────────────────────────────────────────────────
FRONTEND_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:5000
```

> **Lưu ý Gmail App Password:** Vào Google Account → Security → 2-Step Verification → App passwords.
> Nếu không cần gửi email thật, để trống `MAIL_USERNAME` — hệ thống vẫn chạy bình thường.

---

## 4. Chạy Với Docker Compose

### 4.1 Môi Trường Development (Mặc Định)

```bash
# Build và khởi động tất cả services (chạy ở foreground — thấy log)
docker compose up --build

# Hoặc chạy ở background (detached mode)
docker compose up --build -d
```

**Các service sẽ khởi động theo thứ tự:**
1. `postgres` → PostgreSQL 15 (port 5432)
2. `mongo` → MongoDB 7 (port 27017)
3. `backend` → Flask API (port 5000) — chờ postgres + mongo healthy
4. `frontend` → ReactJS (port 3000) — chờ backend
5. `nginx` → Reverse Proxy (port 80) — điều phối traffic

### 4.2 Kiểm Tra Trạng Thái

```bash
# Xem trạng thái tất cả containers
docker compose ps

# Kết quả mong đợi:
# NAME               STATUS          PORTS
# hotel_postgres     healthy         0.0.0.0:5432->5432/tcp
# hotel_mongo        healthy         0.0.0.0:27017->27017/tcp
# hotel_backend      healthy         0.0.0.0:5000->5000/tcp
# hotel_frontend     running         0.0.0.0:3000->3000/tcp
# hotel_nginx        running         0.0.0.0:80->80/tcp
```

### 4.3 Xem Log

```bash
# Log tất cả services
docker compose logs -f

# Log một service cụ thể
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### 4.4 Môi Trường Production

```bash
# Dùng file override cho production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

> File `docker-compose.prod.yml` cần tạo thêm nếu deploy lên server thật (thêm SSL, bỏ volume mount source code...).

---

## 5. Chạy Thủ Công (Không Dùng Docker)

Dùng khi muốn debug hoặc develop từng phần riêng.

### 5.1 Backend (Flask)

**Yêu cầu:** Python 3.11+, PostgreSQL đang chạy, MongoDB đang chạy.

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env trong thư mục backend (copy từ root .env)
# Đổi host database từ "postgres" → "localhost", "mongo" → "localhost"
# DATABASE_URL=postgresql://hoteluser:hotelpass@localhost:5432/hoteldb
# MONGO_URI=mongodb://localhost:27017/hotel_logs

# Khởi tạo database (chỉ lần đầu)
# psql -U hoteluser -d hoteldb -f ../database/schema.sql

# Chạy Flask development server
python run.py
# → API chạy tại http://localhost:5000
```

### 5.2 Frontend (ReactJS)

**Yêu cầu:** Node.js 20+, npm 10+.

```bash
cd frontend

# Cài dependencies
npm install

# Tạo file .env.local
echo "REACT_APP_API_URL=http://localhost:5000" > .env.local

# Chạy development server
npm start
# → App chạy tại http://localhost:3000
```

---

## 6. Kiểm Tra Hệ Thống

### 6.1 Health Checks

```bash
# Nginx (entry point)
curl http://localhost/health
# → {"status": "ok", "service": "nginx"}

# Flask Backend
curl http://localhost:5000/health
# → {"status": "ok", "service": "hotel-api", "version": "2.0.0"}

# API qua Nginx proxy
curl http://localhost/api/health
# → Tương tự kết quả backend
```

### 6.2 Test API với curl

```bash
# Đăng ký user mới
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"Test123!","phone":"+84901234567"}'

# Đăng nhập
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Lấy danh sách phòng (public)
curl http://localhost:5000/api/rooms/

# Lấy thông tin cá nhân (cần Bearer token)
TOKEN="<access_token từ login>"
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 6.3 Chạy Unit Tests

```bash
# Đi vào container backend
docker compose exec backend bash

# Chạy tất cả tests
cd /app
pytest tests/ -v

# Chạy test với coverage report
pytest tests/ -v --cov=app --cov-report=html

# Chạy một file test cụ thể
pytest tests/test_auth.py -v

# Chạy theo keyword
pytest tests/ -v -k "test_login"
```

Hoặc chạy từ máy host (nếu đã có virtualenv):
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### 6.4 Kết Nối Database Trực Tiếp

```bash
# Kết nối PostgreSQL
docker exec -it hotel_postgres psql -U hoteluser -d hoteldb

# Xem các bảng
\dt

# Xem users
SELECT id, full_name, email, role FROM users;

# Thoát
\q

# Kết nối MongoDB
docker exec -it hotel_mongo mongosh

# Xem collections
show collections

# Xem audit logs
db.audit_logs.find().limit(5).pretty()

# Thoát
exit
```

---

## 7. Tài Khoản Demo

Sau khi schema.sql chạy, hệ thống có sẵn các tài khoản seed:

| Role | Email | Password | Quyền |
|------|-------|----------|-------|
| ADMIN | admin@hotel.com | Admin123! | Toàn quyền hệ thống |
| OWNER | owner@hotel.com | Owner123! | Quản lý khách sạn của mình |
| USER | user@hotel.com | User123! | Đặt phòng, xem lịch sử |

> Tài khoản demo được tạo trong `database/schema.sql` phần seed data.
> Trong môi trường production, hãy xoá seed data và tạo admin thật.

---

## 8. Các Lệnh Thường Dùng

### Docker Compose

```bash
# Khởi động (build lại nếu có thay đổi code)
docker compose up --build

# Khởi động không build lại
docker compose up

# Dừng nhưng giữ data
docker compose stop

# Dừng và xoá containers (data volumes vẫn còn)
docker compose down

# Dừng và xoá cả volumes (MẤT TOÀN BỘ DATA DB)
docker compose down -v

# Restart một service
docker compose restart backend

# Xem log realtime của service
docker compose logs -f backend

# Chạy lệnh trong container
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec postgres psql -U hoteluser -d hoteldb
```

### Quản Lý Database

```bash
# Reset database (xoá data + tạo lại schema)
docker compose down -v
docker compose up -d postgres mongo
# Đợi healthy rồi mới restart backend
docker compose up -d backend frontend nginx

# Backup PostgreSQL
docker compose exec postgres pg_dump -U hoteluser hoteldb > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL
docker compose exec -T postgres psql -U hoteluser -d hoteldb < backup_20240101.sql
```

### Cập Nhật Code

```bash
# Backend thay đổi: hot reload tự động (vì mount volume ./backend:/app)
# Chỉ cần save file, Flask tự restart

# Frontend thay đổi: hot reload tự động (vì mount ./frontend/src:/app/src)

# Thay đổi requirements.txt hoặc package.json: cần rebuild
docker compose up --build backend     # rebuild backend
docker compose up --build frontend    # rebuild frontend
```

---

## 9. Xử Lý Lỗi Thường Gặp

### ❌ Lỗi: Port đã được dùng

```
Error: Bind for 0.0.0.0:5432 failed: port is already allocated
```

**Giải pháp:**
```bash
# Tìm process dùng port 5432
# Windows:
netstat -ano | findstr :5432

# macOS/Linux:
lsof -i :5432

# Tắt PostgreSQL local nếu đang chạy
# Windows: Services → PostgreSQL → Stop
# macOS: brew services stop postgresql
# Linux: sudo systemctl stop postgresql
```

### ❌ Lỗi: Backend không kết nối được database

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Giải pháp:**
```bash
# Kiểm tra postgres có healthy chưa
docker compose ps postgres
# Nếu chưa healthy, đợi thêm 30 giây rồi kiểm tra log
docker compose logs postgres

# Restart backend sau khi postgres healthy
docker compose restart backend
```

### ❌ Lỗi: Frontend không gọi được API

```
Network Error / CORS error trong browser console
```

**Giải pháp:**
```bash
# Kiểm tra REACT_APP_API_URL trong .env
# Khi dùng Docker: phải là http://localhost:5000 (gọi từ browser, không phải container)
# Kiểm tra backend có đang chạy không
curl http://localhost:5000/health

# Kiểm tra Nginx có proxy đúng không
curl http://localhost/api/health
```

### ❌ Lỗi: `ModuleNotFoundError` khi chạy Flask

```bash
# Rebuild container backend
docker compose up --build backend
```

### ❌ Lỗi: Database schema không được áp dụng

```bash
# Xem log của postgres khi khởi động
docker compose logs postgres | grep -i "error\|schema\|init"

# Schema chỉ chạy lần ĐẦU TIÊN khi volume trống
# Nếu volume đã tồn tại, schema không chạy lại
# Để chạy lại: xoá volume
docker compose down -v
docker compose up -d
```

### ❌ Lỗi: `Permission denied` khi chạy tests

```bash
docker compose exec backend bash -c "chmod +x /app && pytest tests/ -v"
```

---

## 10. Dừng Và Dọn Dẹp

```bash
# ── Dừng nhẹ (giữ data, có thể start lại) ─────────────────────────
docker compose stop

# ── Dừng và xoá containers (data vẫn còn trong volumes) ───────────
docker compose down

# ── Dọn sạch hoàn toàn (XOÁ CẢ DATA) ─────────────────────────────
docker compose down -v --remove-orphans

# ── Dọn Docker system (xoá images cũ, cache) ──────────────────────
docker system prune -f
docker volume prune -f   # CẢNH BÁO: xoá tất cả volumes không dùng
```

---

## Cấu Trúc Thư Mục

```
CNPM2/
├── backend/                 # Flask REST API
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API blueprints
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Auth decorators
│   │   └── utils/           # Helpers, validators
│   ├── tests/               # Pytest test suite
│   ├── requirements.txt
│   ├── run.py               # Entry point
│   └── Dockerfile
├── frontend/                # ReactJS SPA
│   ├── src/
│   │   ├── pages/           # UI pages (user/admin/owner/auth)
│   │   ├── components/      # Shared components
│   │   ├── services/        # Axios API calls
│   │   ├── context/         # AuthContext (React Context)
│   │   └── i18n/            # Translations (vi/en)
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── schema.sql           # PostgreSQL schema + seed data
├── nginx/
│   └── nginx.conf           # Reverse proxy config
├── docker-compose.yml       # Multi-container setup
├── .env.example             # Environment variables template
├── README.md                # Architecture & design docs
└── Readme_run.md            # This file — deployment guide
```

---

## API Endpoints Tóm Tắt

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/api/auth/register` | Public | Đăng ký |
| POST | `/api/auth/login` | Public | Đăng nhập → JWT |
| POST | `/api/auth/refresh` | Refresh Token | Làm mới Access Token |
| POST | `/api/auth/logout` | Bearer | Đăng xuất (blacklist token) |
| GET | `/api/auth/me` | Bearer | Thông tin cá nhân |
| GET | `/api/rooms/` | Public | Danh sách phòng (filter/paging) |
| GET | `/api/rooms/<id>` | Public | Chi tiết phòng |
| POST | `/api/bookings/` | Optional | Tạo booking |
| GET | `/api/bookings/my` | Bearer | Lịch sử booking của tôi |
| PATCH | `/api/bookings/<id>/confirm` | ADMIN/OWNER | Xác nhận booking |
| PATCH | `/api/bookings/<id>/cancel` | Optional | Huỷ booking |
| POST | `/api/payments/process` | Optional | Thanh toán |
| GET | `/api/admin/dashboard` | ADMIN | Thống kê tổng quan |
| GET | `/api/admin/users` | ADMIN | Quản lý users |
| GET | `/api/owner/hotels` | OWNER | Danh sách khách sạn của tôi |
| GET | `/api/reports/revenue` | ADMIN/OWNER | Báo cáo doanh thu |
| GET | `/api/reports/export/pdf` | ADMIN/OWNER | Xuất PDF |
| GET | `/api/reports/export/excel` | ADMIN/OWNER | Xuất Excel |

---

*Tài liệu này dành cho CNPM2 — Hotel Management System. Phát triển bởi nhóm sinh viên, dùng cho mục đích học thuật.*
