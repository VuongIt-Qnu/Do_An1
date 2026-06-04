-- =============================================================================
-- Hotel Management System - CNPM2
-- PostgreSQL Database Schema (v2.1 — aligned with SQLAlchemy models)
-- =============================================================================

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. USERS
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id                  BIGSERIAL PRIMARY KEY,
    full_name           VARCHAR(100)  NOT NULL,
    email               VARCHAR(100)  NOT NULL UNIQUE,
    phone_number        VARCHAR(20),
    password_hash       VARCHAR(255)  NOT NULL,

    -- Role stored as plain string: ADMIN | OWNER | USER
    role                VARCHAR(20)   NOT NULL DEFAULT 'USER',

    -- Profile extras
    passport            VARCHAR(50),
    nationality         VARCHAR(50),
    address             TEXT,

    -- Account state
    enabled             BOOLEAN       NOT NULL DEFAULT TRUE,

    -- Password reset
    reset_token         VARCHAR(100),
    reset_token_expiry  TIMESTAMP,

    -- Timestamps
    created_at          TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email   ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role    ON users(role);

-- =============================================================================
-- 2. HOTELS
-- =============================================================================
CREATE TABLE IF NOT EXISTS hotels (
    id          BIGSERIAL PRIMARY KEY,
    owner_id    BIGINT       REFERENCES users(id) ON DELETE SET NULL,

    name        VARCHAR(200) NOT NULL,
    address     TEXT,
    city        VARCHAR(100),
    description TEXT,
    phone       VARCHAR(20),
    email       VARCHAR(100),
    star_rating INTEGER      DEFAULT 3 CHECK (star_rating BETWEEN 1 AND 5),

    -- Visibility / approval workflow
    enabled     BOOLEAN      NOT NULL DEFAULT TRUE,
    approved    BOOLEAN      NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hotels_owner_id ON hotels(owner_id);
CREATE INDEX IF NOT EXISTS idx_hotels_city     ON hotels(city);

-- =============================================================================
-- 3. ROOMS
-- =============================================================================
CREATE TABLE IF NOT EXISTS rooms (
    id              BIGSERIAL     PRIMARY KEY,
    hotel_id        BIGINT        NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,

    name            VARCHAR(100)  NOT NULL,
    room_type       VARCHAR(50)   NOT NULL,   -- Standard | Deluxe | Suite | Family | Presidential
    capacity        INTEGER       NOT NULL CHECK (capacity > 0),
    price_per_night NUMERIC(12,2) NOT NULL CHECK (price_per_night >= 0),
    area            NUMERIC(6,2),             -- m²

    amenities       TEXT,                     -- Comma-separated: "WiFi,AC,TV,Minibar"
    description     TEXT,
    main_image_url  TEXT,

    -- Average rating (cache updated by trigger / application)
    rating          NUMERIC(3,2)  DEFAULT 5.0 CHECK (rating BETWEEN 0 AND 5),

    featured        BOOLEAN       NOT NULL DEFAULT FALSE,

    -- Status: AVAILABLE | OCCUPIED | MAINTENANCE
    status          VARCHAR(20)   NOT NULL DEFAULT 'AVAILABLE'
                    CHECK (status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE')),

    -- Timestamps
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rooms_hotel_id  ON rooms(hotel_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status    ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_rooms_featured  ON rooms(featured);

-- =============================================================================
-- 4. BOOKINGS
-- =============================================================================
CREATE TABLE IF NOT EXISTS bookings (
    id              BIGSERIAL     PRIMARY KEY,

    -- Authenticated user (NULL for guest bookings)
    user_id         BIGINT        REFERENCES users(id) ON DELETE SET NULL,

    -- Guest / contact info (always filled)
    customer_name   VARCHAR(100)  NOT NULL,
    customer_email  VARCHAR(100)  NOT NULL,
    customer_phone  VARCHAR(20),

    -- Location
    hotel_id        BIGINT        REFERENCES hotels(id) ON DELETE SET NULL,
    room_id         BIGINT        REFERENCES rooms(id)  ON DELETE SET NULL,

    -- Dates
    check_in        DATE          NOT NULL,
    check_out       DATE          NOT NULL,
    CHECK (check_out > check_in),

    guests          INTEGER       NOT NULL DEFAULT 1 CHECK (guests > 0),
    total_price     NUMERIC(12,2),

    -- Status flow: PENDING → CONFIRMED → COMPLETED | CANCELLED
    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','CONFIRMED','COMPLETED','CANCELLED')),

    cancel_reason   TEXT,
    cancelled_at    TIMESTAMP,
    notes           TEXT,

    -- Timestamps
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_user_id   ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_hotel_id  ON bookings(hotel_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room_id   ON bookings(room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status    ON bookings(status);

-- =============================================================================
-- 5. PAYMENTS
-- =============================================================================
CREATE TABLE IF NOT EXISTS payments (
    id              BIGSERIAL     PRIMARY KEY,
    booking_id      BIGINT        NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,

    amount          NUMERIC(12,2) NOT NULL,
    method          VARCHAR(50)   DEFAULT 'BANK_TRANSFER',
    -- Method values: CASH | BANK_TRANSFER | MOMO | QR_CODE

    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    -- Status values: PENDING | PAID | REFUNDED | FAILED

    transaction_ref VARCHAR(100),
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_status     ON payments(status);

-- =============================================================================
-- 6. REVIEWS
-- =============================================================================
CREATE TABLE IF NOT EXISTS reviews (
    id          BIGSERIAL  PRIMARY KEY,
    booking_id  BIGINT     REFERENCES bookings(id) ON DELETE CASCADE,
    user_id     BIGINT     REFERENCES users(id)    ON DELETE SET NULL,
    room_id     BIGINT     NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,

    rating      INTEGER    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,

    -- Timestamps
    created_at  TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP  NOT NULL DEFAULT NOW(),

    -- One review per booking
    CONSTRAINT uq_review_booking UNIQUE (booking_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_room_id ON reviews(room_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);

-- =============================================================================
-- AUTO-UPDATE updated_at TRIGGER
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER trg_hotels_updated_at
    BEFORE UPDATE ON hotels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER trg_rooms_updated_at
    BEFORE UPDATE ON rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER trg_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER trg_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SEED DATA
-- Schema này chỉ tạo cấu trúc bảng.
-- Dữ liệu mẫu (demo accounts, hotels, rooms, bookings) được tạo bằng:
--
--   docker exec -it hotel_backend python seed.py
--
-- Tài khoản demo sau khi chạy seed.py:
--   ADMIN  : admin@hotel.com   / Admin@123
--   OWNER1 : owner1@hotel.com  / Owner@123
--   OWNER2 : owner2@hotel.com  / Owner@123
--   USER1  : user1@hotel.com   / User@123
--   USER2  : user2@hotel.com   / User@123
-- =============================================================================
