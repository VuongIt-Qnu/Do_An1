# 🏨 Hotel Management System — CNPM2

> **Hệ thống Quản lý Khách sạn** — Nâng cấp từ CNPM1 sang kiến trúc Fullstack hiện đại (ReactJS + Flask REST API + PostgreSQL + MongoDB)

---

## 📋 Mục lục

- [Tổng quan hệ thống](#-tổng-quan-hệ-thống)
- [So sánh CNPM1 vs CNPM2](#-so-sánh-cnpm1-vs-cnpm2)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Flow hoạt động](#-flow-hoạt-động)
- [Danh sách chức năng](#-danh-sách-chức-năng)
- [Phân quyền hệ thống](#-phân-quyền-hệ-thống)
- [Database Design](#-database-design)
- [Rủi ro và hạn chế](#-rủi-ro-và-hạn-chế)
- [Hướng phát triển thêm](#-hướng-phát-triển-thêm)

---

## 🌐 Tổng quan hệ thống

**Hotel Management System CNPM2** là phiên bản nâng cấp toàn diện từ đồ án CNPM1, chuyển đổi từ kiến trúc monolithic (Spring Boot + Thymeleaf/JSP) sang kiến trúc **Fullstack hiện đại** với frontend SPA và backend REST API độc lập.

Hệ thống hướng tới mô hình **đa khách sạn, đa vai trò**, cho phép nhiều chủ khách sạn (Owner) quản lý tài sản của mình trên cùng một nền tảng — tiếp cận mô hình SaaS trong thực tế doanh nghiệp.

### Mục tiêu chính

- Tách biệt hoàn toàn Frontend và Backend (decoupled architecture)
- Mở rộng phân quyền: bổ sung vai trò **Owner** (chủ khách sạn)
- Hỗ trợ **đa ngôn ngữ** (Tiếng Việt / Tiếng Anh)
- Tích hợp thanh toán trực tuyến (mô phỏng Bank / MoMo)
- Áp dụng kiểm thử đầy đủ (Unit Test, API Test, UI Test)
- Containerize bằng Docker, deploy lên server thực tế

---

## 📊 So sánh CNPM1 vs CNPM2

| Tiêu chí | CNPM1 | CNPM2 |
|---|---|---|
| **Kiến trúc** | Monolithic (Spring Boot) | Decoupled Fullstack (SPA + REST API) |
| **Backend** | Java Spring Boot 3.5.7 | Python Flask REST API |
| **Frontend** | Thymeleaf / JSP (server-side render) | ReactJS + Bootstrap (SPA, client-side render) |
| **Database chính** | PostgreSQL | PostgreSQL |
| **Database phụ** | MongoDB (cơ bản) | MongoDB (logging, audit, activity tracking) |
| **Xác thực** | Spring Security (Session-based) | JWT (Stateless) |
| **Phân quyền** | ADMIN, USER | ADMIN, OWNER, USER |
| **Đa khách sạn** | ❌ Không hỗ trợ | ✅ Hỗ trợ (mỗi Owner quản lý khách sạn riêng) |
| **Đa ngôn ngữ** | ❌ | ✅ Tiếng Việt / Tiếng Anh |
| **Thanh toán online** | ❌ | ✅ Mô phỏng Bank / MoMo |
| **Hủy phòng có điều kiện** | ❌ | ✅ Theo thời gian và mức phí |
| **Xuất báo cáo** | Xem trên web | ✅ Xuất PDF / Excel |
| **Đánh giá phòng** | Có (cơ bản) | ✅ Đánh giá sau khi hoàn tất booking |
| **Thông báo Email** | ❌ | ✅ Đặt phòng, duyệt, hủy |
| **Kiểm thử** | Không có | Unit Test, Postman API Test, Selenium UI Test |
| **DevOps** | Chạy local | Docker + Deploy lên server |
| **Logging** | Không có | MongoDB audit_logs, request_logs |

---

## 🛠️ Công nghệ sử dụng

### Frontend

| Công nghệ | Phiên bản | Mục đích |
|---|---|---|
| **ReactJS** | 18.x | Framework SPA chính |
| **Bootstrap** | 5.x | UI Component, responsive layout |
| **React Router** | 6.x | Điều hướng client-side |
| **Axios** | 1.x | HTTP client gọi REST API |
| **i18next** | Latest | Đa ngôn ngữ (VI/EN) |
| **React Hook Form** | Latest | Quản lý form |

### Backend

| Công nghệ | Phiên bản | Mục đích |
|---|---|---|
| **Python** | 3.11+ | Ngôn ngữ backend |
| **Flask** | 3.x | Web framework REST API |
| **Flask-JWT-Extended** | Latest | Xác thực JWT |
| **Flask-SQLAlchemy** | Latest | ORM cho PostgreSQL |
| **Flask-PyMongo** | Latest | Kết nối MongoDB |
| **Flask-CORS** | Latest | Xử lý CORS |
| **Flask-Mail** | Latest | Gửi email thông báo |
| **Marshmallow** | Latest | Serialization / Validation |
| **Celery** *(optional)* | Latest | Background tasks (email async) |

### Database

| Database | Loại | Mục đích |
|---|---|---|
| **PostgreSQL** | Relational (SQL) | Dữ liệu nghiệp vụ chính |
| **MongoDB** | NoSQL (Document) | Logging, audit, user activity |

### Testing

| Công nghệ | Mục đích |
|---|---|
| **pytest** | Unit Test cho backend Flask |
| **Postman / Newman** | API Test tự động hóa |
| **Selenium** | UI Test / End-to-End |

### DevOps

| Công nghệ | Mục đích |
|---|---|
| **Docker** | Containerize frontend, backend, database |
| **Docker Compose** | Orchestrate multi-container |
| **Nginx** | Reverse proxy, serve React build |

---

## 🏗️ Kiến trúc hệ thống

Hệ thống CNPM2 được tổ chức theo mô hình **3-tier architecture** kết hợp **SOA (Service-Oriented Architecture)**:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │             ReactJS SPA (Port 3000)                 │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│   │  │  Admin   │ │  Owner   │ │   User   │            │   │
│   │  │Dashboard │ │Dashboard │ │  Pages   │            │   │
│   │  └──────────┘ └──────────┘ └──────────┘            │   │
│   │         i18n (VI/EN)    Bootstrap 5                 │   │
│   └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS / REST API (JSON)
                            │ JWT Bearer Token
┌───────────────────────────▼─────────────────────────────────┐
│                       API GATEWAY LAYER                      │
│                    Nginx Reverse Proxy                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      SERVICE LAYER                           │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           Flask REST API (Port 5000)                │   │
│   │                                                     │   │
│   │  /api/auth     /api/bookings    /api/hotels         │   │
│   │  /api/users    /api/rooms       /api/payments       │   │
│   │  /api/reports  /api/reviews     /api/admin          │   │
│   │                                                     │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│   │  │   Auth   │ │Booking   │ │  Payment Service │    │   │
│   │  │ Service  │ │ Service  │ │  (Bank/MoMo sim) │    │   │
│   │  └──────────┘ └──────────┘ └──────────────────┘    │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│   │  │  Room    │ │ Report   │ │  Email Service   │    │   │
│   │  │ Service  │ │ Service  │ │  (Flask-Mail)    │    │   │
│   │  └──────────┘ └──────────┘ └──────────────────┘    │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────┬────────────────────┬─────────────────────┘
                   │                    │
        ┌──────────▼──────┐   ┌─────────▼──────────┐
        │   PostgreSQL    │   │      MongoDB        │
        │   (Port 5432)   │   │    (Port 27017)     │
        │                 │   │                     │
        │ - users/roles   │   │ - audit_logs        │
        │ - hotels        │   │ - request_logs      │
        │ - rooms         │   │ - user_activities   │
        │ - bookings      │   │                     │
        │ - payments      │   └─────────────────────┘
        │ - invoices      │
        └─────────────────┘
```

### Cấu trúc thư mục dự án

```
hotel-management-cnpm2/
├── frontend/                    # ReactJS Application
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components (Admin, Owner, User)
│   │   ├── services/            # API service calls (Axios)
│   │   ├── context/             # React Context (Auth, Language)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── i18n/                # Locale files (vi.json, en.json)
│   │   └── utils/               # Helper functions
│   └── package.json
│
├── backend/                     # Flask REST API
│   ├── app/
│   │   ├── models/              # SQLAlchemy models (PostgreSQL)
│   │   ├── schemas/             # Marshmallow schemas
│   │   ├── routes/              # API Blueprint routes
│   │   ├── services/            # Business logic layer
│   │   ├── middleware/          # JWT auth, logging middleware
│   │   └── config.py            # App configuration
│   ├── tests/                   # pytest unit tests
│   ├── requirements.txt
│   └── run.py
│
├── docker-compose.yml           # Multi-container orchestration
├── nginx/
│   └── nginx.conf               # Reverse proxy config
└── README.md
```

---

## 🔄 Flow hoạt động

### 1. Flow Booking (Đặt phòng)

```
User                     ReactJS                  Flask API              PostgreSQL
 │                          │                          │                      │
 │── Chọn phòng + ngày ────►│                          │                      │
 │                          │── GET /api/rooms ────────►│                      │
 │                          │                          │── Query rooms ───────►│
 │                          │                          │◄── Room list ─────────│
 │                          │◄── Room data ────────────│                      │
 │◄── Hiển thị phòng khả dụng│                          │                      │
 │                          │                          │                      │
 │── Nhập thông tin + Submit►│                          │                      │
 │                          │── POST /api/bookings ────►│                      │
 │                          │   (JWT Bearer Token)      │── Check availability►│
 │                          │                          │◄── Available ─────────│
 │                          │                          │── Insert booking ────►│
 │                          │                          │── Update room_avail ──►│
 │                          │                          │◄── Booking created ───│
 │                          │◄── Booking response ─────│                      │
 │                          │                          │── Send email (async) ─►│
 │◄── Xác nhận đặt phòng ───│                          │                      │
 │                          │                          │── Log to MongoDB ─────►│
```

### 2. Flow Admin duyệt booking

```
Admin                    ReactJS                  Flask API              PostgreSQL
 │                          │                          │                      │
 │── Vào trang Booking Mgmt►│                          │                      │
 │                          │── GET /api/admin/bookings►│                      │
 │                          │   (ADMIN role required)  │── Query bookings ────►│
 │                          │◄── Booking list ─────────│◄── Data ──────────────│
 │◄── Danh sách pending ────│                          │                      │
 │                          │                          │                      │
 │── Click "Duyệt" ─────────►│                          │                      │
 │                          │── PATCH /api/bookings/id ►│                      │
 │                          │   {status: CONFIRMED}    │── Update status ─────►│
 │                          │                          │◄── Updated ───────────│
 │                          │                          │── Email to customer ──►│
 │◄── Cập nhật trạng thái ──│                          │── Audit log (MongoDB)─►│
```

### 3. Flow Owner quản lý khách sạn

```
Owner                    ReactJS                  Flask API              PostgreSQL
 │                          │                          │                      │
 │── Login (role=OWNER) ───►│                          │                      │
 │                          │── POST /api/auth/login ──►│── Verify JWT ────────►│
 │◄── JWT Token + role ─────│◄── {token, role:OWNER} ──│                      │
 │                          │                          │                      │
 │── Vào Owner Dashboard ───►│                          │                      │
 │                          │── GET /api/owner/hotels ─►│                      │
 │                          │   (OWNER role only)       │── WHERE owner_id=X ──►│
 │◄── Khách sạn của Owner ──│◄── Hotel list ───────────│◄── Hotels data ───────│
 │                          │                          │                      │
 │── Thêm/Sửa phòng ─────────►│                          │                      │
 │                          │── POST /api/owner/rooms ─►│                      │
 │                          │   (hotel_id validated)    │── Insert room ───────►│
 │◄── Thành công ───────────│◄── Room created ──────────│◄── Confirmed ─────────│
```

---

## ✅ Danh sách chức năng

### Chức năng kế thừa từ CNPM1 ✅

| # | Chức năng | Module | Trạng thái |
|---|---|---|---|
| 1 | Đăng ký tài khoản | Auth | ✅ Kế thừa & cải tiến |
| 2 | Đăng nhập hệ thống | Auth | ✅ Chuyển sang JWT |
| 3 | Quên mật khẩu / Reset | Auth | ✅ Kế thừa |
| 4 | Phân quyền ADMIN / USER | RBAC | ✅ Mở rộng thêm OWNER |
| 5 | Xem danh sách phòng | Room | ✅ Kế thừa |
| 6 | Xem chi tiết phòng | Room | ✅ Kế thừa |
| 7 | Đặt phòng | Booking | ✅ Nâng cấp (multi-room) |
| 8 | Lịch sử đặt phòng của User | Booking | ✅ Kế thừa |
| 9 | Quản lý phòng (CRUD) | Admin | ✅ Kế thừa |
| 10 | Quản lý khách hàng (CRUD) | Admin | ✅ Kế thừa |
| 11 | Quản lý đặt phòng (duyệt) | Admin | ✅ Kế thừa |
| 12 | Báo cáo doanh thu (ngày/tháng/năm) | Admin | ✅ Nâng cấp |
| 13 | Đánh giá phòng | Review | ✅ Cải tiến (post-checkout) |

### Chức năng mới trong CNPM2 🆕

| # | Chức năng | Module | Ưu tiên |
|---|---|---|---|
| 14 | Hỗ trợ đa ngôn ngữ (VI/EN) | i18n | 🔴 Cao |
| 15 | Vai trò Owner – quản lý khách sạn riêng | RBAC / Owner | 🔴 Cao |
| 16 | Quản lý đa khách sạn (hotels table) | Owner | 🔴 Cao |
| 17 | Thanh toán trực tuyến (Bank/MoMo mô phỏng) | Payment | 🔴 Cao |
| 18 | Quản lý hủy phòng có điều kiện | Booking/Rules | 🔴 Cao |
| 19 | Xuất báo cáo doanh thu (PDF / Excel) | Report | 🔴 Cao |
| 20 | Thông báo Email tự động | Email | 🔴 Cao |
| 21 | Đánh giá chỉ sau khi hoàn tất booking | Review | 🟡 Trung bình |
| 22 | Audit log (MongoDB) | Logging | 🟡 Trung bình |
| 23 | Request log / User activity tracking | Logging | 🟡 Trung bình |
| 24 | Kiểm tra trùng ngày đặt (room_availability) | Booking | 🔴 Cao |

### Chức năng nâng cao (nếu có thời gian) 🔬

| # | Chức năng | Ghi chú |
|---|---|---|
| 25 | Thanh toán QR | Tích hợp VietQR |
| 26 | Thanh toán USDT | Mức nghiên cứu / mô phỏng |
| 27 | Tích hợp API bản đồ | Google Maps / Leaflet.js |

---

## 🔐 Phân quyền hệ thống

Hệ thống CNPM2 áp dụng **RBAC (Role-Based Access Control)** với 3 vai trò chính:

```
┌─────────────────────────────────────────────────────────────┐
│                    PHÂN QUYỀN HỆ THỐNG                      │
├──────────────┬──────────────────────────────────────────────┤
│    ADMIN     │  Toàn quyền hệ thống                        │
│              │  - Quản lý tất cả users, owners, bookings   │
│              │  - Xem báo cáo toàn hệ thống                │
│              │  - Phê duyệt/khóa tài khoản Owner           │
│              │  - Xem audit logs                            │
├──────────────┼──────────────────────────────────────────────┤
│    OWNER     │  Chủ khách sạn – quản lý khách sạn riêng    │
│              │  - Quản lý hotels của mình (CRUD)            │
│              │  - Quản lý rooms thuộc hotel của mình        │
│              │  - Xem và duyệt bookings của hotel mình      │
│              │  - Xem báo cáo doanh thu hotel mình          │
│              │  - Thiết lập chính sách hủy phòng            │
├──────────────┼──────────────────────────────────────────────┤
│     USER     │  Khách đặt phòng                             │
│              │  - Xem danh sách phòng khả dụng              │
│              │  - Đặt phòng / Hủy phòng (theo chính sách)   │
│              │  - Xem lịch sử booking cá nhân               │
│              │  - Đánh giá phòng sau khi checkout           │
│              │  - Thanh toán trực tuyến                     │
└──────────────┴──────────────────────────────────────────────┘
```

### Ma trận quyền truy cập API

| Endpoint | ADMIN | OWNER | USER | Ghi chú |
|---|:---:|:---:|:---:|---|
| `GET /api/rooms` | ✅ | ✅ | ✅ | Public |
| `POST /api/rooms` | ✅ | ✅ | ❌ | Owner chỉ tạo room của hotel mình |
| `PUT /api/rooms/:id` | ✅ | ✅* | ❌ | *Owner chỉ sửa room của mình |
| `DELETE /api/rooms/:id` | ✅ | ✅* | ❌ | *Giới hạn theo hotel_id |
| `GET /api/bookings` | ✅ | ✅* | ❌ | *Lọc theo hotel |
| `POST /api/bookings` | ✅ | ❌ | ✅ | |
| `PATCH /api/bookings/:id` | ✅ | ✅* | ✅** | **Chỉ hủy của mình |
| `GET /api/admin/users` | ✅ | ❌ | ❌ | |
| `GET /api/reports` | ✅ | ✅* | ❌ | *Chỉ hotel của mình |
| `GET /api/admin/logs` | ✅ | ❌ | ❌ | |
| `GET /api/hotels` | ✅ | ✅* | ✅ | *Lọc theo owner |

---

## 🗄️ Database Design

### PostgreSQL — Cơ sở dữ liệu nghiệp vụ

```sql
-- ==========================================
-- BẢNG NGƯỜI DÙNG & PHÂN QUYỀN
-- ==========================================

users
├── id              BIGSERIAL PRIMARY KEY
├── full_name       VARCHAR(100) NOT NULL
├── email           VARCHAR(100) UNIQUE NOT NULL
├── phone_number    VARCHAR(20)
├── password_hash   VARCHAR(255) NOT NULL
├── role_id         INT REFERENCES roles(id)    -- FK → roles
├── passport        VARCHAR(50)
├── nationality     VARCHAR(50)
├── address         TEXT
├── enabled         BOOLEAN DEFAULT TRUE
├── created_at      TIMESTAMP DEFAULT NOW()
└── updated_at      TIMESTAMP

roles
├── id              SERIAL PRIMARY KEY
├── name            VARCHAR(20) NOT NULL   -- ADMIN, OWNER, USER
└── description     TEXT

-- ==========================================
-- BẢNG KHÁCH SẠN (ĐA KHÁCH SẠN)
-- ==========================================

hotels
├── id              BIGSERIAL PRIMARY KEY
├── owner_id        BIGINT REFERENCES users(id)  -- FK → users (Owner)
├── name            VARCHAR(200) NOT NULL
├── address         TEXT
├── city            VARCHAR(100)
├── description     TEXT
├── phone           VARCHAR(20)
├── email           VARCHAR(100)
├── star_rating     INT CHECK (star_rating BETWEEN 1 AND 5)
├── enabled         BOOLEAN DEFAULT TRUE
├── created_at      TIMESTAMP DEFAULT NOW()
└── updated_at      TIMESTAMP

-- ==========================================
-- BẢNG PHÒNG
-- ==========================================

room_types
├── id              SERIAL PRIMARY KEY
├── name            VARCHAR(50) NOT NULL   -- Standard, Deluxe, Suite, ...
└── description     TEXT

rooms
├── id              BIGSERIAL PRIMARY KEY
├── hotel_id        BIGINT REFERENCES hotels(id)        -- FK → hotels
├── room_type_id    INT REFERENCES room_types(id)       -- FK → room_types
├── name            VARCHAR(100) NOT NULL
├── capacity        INT NOT NULL
├── price_per_night NUMERIC(12, 2) NOT NULL
├── area            NUMERIC(6, 2)
├── amenities       TEXT                 -- JSON string: ["Wifi","TV","AC"]
├── description     TEXT
├── main_image_url  TEXT
├── rating          NUMERIC(3, 2) DEFAULT 5.0
├── featured        BOOLEAN DEFAULT FALSE
├── status          VARCHAR(20) DEFAULT 'AVAILABLE'  -- AVAILABLE, OCCUPIED, MAINTENANCE
├── created_at      TIMESTAMP DEFAULT NOW()
└── updated_at      TIMESTAMP

room_availability
├── id              BIGSERIAL PRIMARY KEY
├── room_id         BIGINT REFERENCES rooms(id)
├── date            DATE NOT NULL
├── is_available    BOOLEAN DEFAULT TRUE
└── booking_id      BIGINT REFERENCES bookings(id)

-- ==========================================
-- BẢNG KHÁCH HÀNG
-- ==========================================

customers
├── id              BIGSERIAL PRIMARY KEY
├── user_id         BIGINT REFERENCES users(id)   -- null nếu guest
├── full_name       VARCHAR(100) NOT NULL
├── email           VARCHAR(100)
├── phone           VARCHAR(20)
├── passport        VARCHAR(50)
├── nationality     VARCHAR(50)
└── created_at      TIMESTAMP DEFAULT NOW()

-- ==========================================
-- BẢNG ĐẶT PHÒNG
-- ==========================================

bookings
├── id              BIGSERIAL PRIMARY KEY
├── user_id         BIGINT REFERENCES users(id)       -- người đặt (null nếu guest)
├── customer_id     BIGINT REFERENCES customers(id)   -- FK → customers
├── hotel_id        BIGINT REFERENCES hotels(id)
├── check_in        DATE NOT NULL
├── check_out       DATE NOT NULL
├── guests          INT
├── total_price     NUMERIC(12, 2)
├── status          VARCHAR(20) DEFAULT 'PENDING'  -- PENDING, CONFIRMED, CANCELLED, COMPLETED
├── cancel_reason   TEXT
├── cancelled_at    TIMESTAMP
├── notes           TEXT
├── created_at      TIMESTAMP DEFAULT NOW()
└── updated_at      TIMESTAMP

booking_rooms                    -- Một booking có thể có nhiều phòng
├── id              BIGSERIAL PRIMARY KEY
├── booking_id      BIGINT REFERENCES bookings(id)
├── room_id         BIGINT REFERENCES rooms(id)
├── price_at_booking NUMERIC(12, 2)     -- Lưu giá tại thời điểm đặt
└── nights          INT

-- ==========================================
-- BẢNG THANH TOÁN
-- ==========================================

payments
├── id              BIGSERIAL PRIMARY KEY
├── booking_id      BIGINT REFERENCES bookings(id)
├── amount          NUMERIC(12, 2) NOT NULL
├── method          VARCHAR(50)   -- CASH, BANK_TRANSFER, MOMO, QR
├── status          VARCHAR(20)   -- PENDING, PAID, REFUNDED, FAILED
├── transaction_ref VARCHAR(100)  -- Mã giao dịch từ cổng thanh toán
├── paid_at         TIMESTAMP
└── created_at      TIMESTAMP DEFAULT NOW()

invoices
├── id              BIGSERIAL PRIMARY KEY
├── booking_id      BIGINT REFERENCES bookings(id)
├── payment_id      BIGINT REFERENCES payments(id)
├── invoice_number  VARCHAR(50) UNIQUE NOT NULL
├── issued_at       TIMESTAMP DEFAULT NOW()
└── pdf_url         TEXT    -- Đường dẫn file PDF hóa đơn

-- ==========================================
-- BẢNG ĐÁNH GIÁ & CHÍNH SÁCH
-- ==========================================

reviews
├── id              BIGSERIAL PRIMARY KEY
├── booking_id      BIGINT REFERENCES bookings(id)   -- Chỉ review khi booking COMPLETED
├── user_id         BIGINT REFERENCES users(id)
├── room_id         BIGINT REFERENCES rooms(id)
├── rating          INT CHECK (rating BETWEEN 1 AND 5)
├── comment         TEXT
├── created_at      TIMESTAMP DEFAULT NOW()
└── updated_at      TIMESTAMP

rules                            -- Chính sách hủy phòng
├── id              SERIAL PRIMARY KEY
├── hotel_id        BIGINT REFERENCES hotels(id)
├── name            VARCHAR(100)
├── cancel_before_hours INT     -- Được hủy miễn phí trước X giờ
├── penalty_percent NUMERIC(5, 2) -- Phí hủy tính theo % tổng tiền
└── description     TEXT
```

### MongoDB — Logging & Audit

```json
// Collection: audit_logs
{
  "_id": ObjectId,
  "user_id": 123,
  "user_email": "admin@hotel.com",
  "role": "ADMIN",
  "action": "BOOKING_APPROVED",
  "target_type": "booking",
  "target_id": 456,
  "details": { "booking_id": 456, "old_status": "PENDING", "new_status": "CONFIRMED" },
  "ip_address": "192.168.1.1",
  "created_at": ISODate("2025-01-15T10:30:00Z")
}

// Collection: request_logs
{
  "_id": ObjectId,
  "method": "POST",
  "endpoint": "/api/bookings",
  "status_code": 201,
  "response_time_ms": 145,
  "user_id": 789,
  "ip_address": "10.0.0.5",
  "user_agent": "Mozilla/5.0...",
  "created_at": ISODate("2025-01-15T10:30:00Z")
}

// Collection: user_activities
{
  "_id": ObjectId,
  "user_id": 789,
  "activity_type": "VIEW_ROOM",
  "metadata": { "room_id": 12, "hotel_id": 3 },
  "session_id": "abc123",
  "created_at": ISODate("2025-01-15T10:29:50Z")
}
```

### Sơ đồ quan hệ (ERD tóm tắt)

```
roles ──< users >──────────────── hotels
                │                    │
                │                    │── rooms >──── room_types
                │                    │      │
                │                    │      └──< room_availability
                │                    │
                └──< bookings >──────┘
                        │
                        ├──< booking_rooms >── rooms
                        ├──< payments
                        ├──< invoices
                        └──< reviews
```

---

## ⚠️ Rủi ro và hạn chế

### Rủi ro kỹ thuật

| Rủi ro | Mức độ | Biện pháp giảm thiểu |
|---|:---:|---|
| Chuyển đổi công nghệ backend (Java → Python) | 🔴 Cao | Tái sử dụng logic nghiệp vụ từ CNPM1, viết test đầy đủ |
| Đồng bộ dữ liệu giữa PostgreSQL và MongoDB | 🟡 Trung bình | Ghi MongoDB asynchronously, không block main flow |
| Tích hợp cổng thanh toán bên thứ 3 | 🟡 Trung bình | Dùng sandbox/mock API, tách Payment Service độc lập |
| Race condition khi đặt phòng cùng lúc | 🔴 Cao | Dùng DB transaction + table lock trên room_availability |
| Bảo mật JWT token | 🟡 Trung bình | Refresh token, blacklist token khi logout |
| CORS configuration sai khi deploy | 🟢 Thấp | Cấu hình CORS rõ ràng trong Nginx và Flask |

### Hạn chế phạm vi đồ án

- Thanh toán Bank/MoMo chỉ ở mức **mô phỏng** (không kết nối thực tế vì yêu cầu đăng ký doanh nghiệp)
- Tính năng thanh toán USDT và QR chỉ triển khai **nếu có thời gian** (mục 2.3)
- Email notification dùng SMTP cơ bản, chưa có retry mechanism
- Chưa tối ưu hiệu năng cho quy mô lớn (không có caching Redis)
- API bản đồ phụ thuộc vào quota miễn phí của Google Maps / OpenStreetMap

---

## 🚀 Hướng phát triển thêm

### Ngắn hạn (trong phạm vi đồ án)

- Hoàn thiện toàn bộ chức năng mục 2.2 với kiểm thử đầy đủ
- Viết tài liệu API (Swagger/OpenAPI)
- Deploy hệ thống lên VPS/server thực tế bằng Docker Compose

### Trung hạn

- Tích hợp **Redis** để cache danh sách phòng khả dụng, tăng hiệu suất
- Thêm **WebSocket** để cập nhật trạng thái phòng real-time
- Tích hợp thanh toán thực tế qua **VNPay** hoặc **MoMo API** chính thức
- Bổ sung **CI/CD pipeline** với GitHub Actions

### Dài hạn

- Chuyển sang kiến trúc **Microservices** (tách Auth Service, Booking Service, Payment Service)
- Tích hợp **Elasticsearch** cho tìm kiếm phòng nâng cao
- Phát triển ứng dụng **Mobile** (React Native) cho User
- Tích hợp **AI chatbot** hỗ trợ tư vấn đặt phòng
- Thanh toán bằng USDT (nghiên cứu Web3 integration)

---

## 📁 Cấu trúc thư mục dự án (dự kiến)

```
CNPM2/
├── README.md                       ← File này
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── frontend/                        ← ReactJS App
│   ├── src/
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   ├── owner/
│   │   │   └── user/
│   │   ├── components/
│   │   ├── i18n/
│   │   │   ├── vi.json
│   │   │   └── en.json
│   │   └── services/
│   └── package.json
└── backend/                         ← Flask REST API
    ├── app/
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── hotel.py
    │   │   ├── room.py
    │   │   ├── booking.py
    │   │   └── payment.py
    │   ├── routes/
    │   │   ├── auth.py
    │   │   ├── bookings.py
    │   │   ├── hotels.py
    │   │   ├── rooms.py
    │   │   ├── payments.py
    │   │   ├── reports.py
    │   │   └── admin.py
    │   ├── services/
    │   └── middleware/
    ├── tests/
    │   ├── test_auth.py
    │   ├── test_bookings.py
    │   └── test_rooms.py
    └── requirements.txt
```

---

## 👨‍💻 Thông tin đồ án

| Thông tin | Chi tiết |
|---|---|
| **Môn học** | Công nghệ Phần mềm 2 (CNPM2) |
| **Hệ thống** | Quản lý Khách sạn (Hotel Management System) |
| **Nâng cấp từ** | CNPM1 — Spring Boot + PostgreSQL + MongoDB |
| **Công nghệ mới** | ReactJS + Flask REST API + PostgreSQL + MongoDB |
| **Kiến trúc** | Decoupled Fullstack / SOA |
| **Phiên bản** | 2.0.0 |

---

*README này được tạo dựa trên phân tích codebase CNPM1 (Spring Boot 3.5.7 / Java 17) và tài liệu hướng phát triển CNPM2.*