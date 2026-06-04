"""
Application Configuration
Supports: Development, Production, Testing environments
"""
import os
from datetime import timedelta


class BaseConfig:
    """Base configuration — shared across all environments"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    JSON_SORT_KEYS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # SQLAlchemy (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://hoteluser:hotelpass@localhost:5432/hoteldb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,       # Recycle connections every 5 minutes
        "pool_pre_ping": True,     # Verify connection before using from pool
        "pool_size": 10,
        "max_overflow": 20,
    }

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/hotel_logs")

    # Email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME", "noreply@hotel.com")

    # CORS
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]

    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(BaseConfig):
    """Development environment — verbose logging, debug mode"""
    DEBUG = True
    SQLALCHEMY_ECHO = True          # Log all SQL queries


class ProductionConfig(BaseConfig):
    """Production environment — strict security, no debug"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Force HTTPS in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


class TestingConfig(BaseConfig):
    """Testing environment — in-memory SQLite for speed"""
    TESTING = True
    DEBUG = True
    # Use SQLite for tests (no PostgreSQL needed)
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable CSRF and rate limiting in tests
    WTF_CSRF_ENABLED = False
    # Short JWT expiry for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # Disable actual email sending
    MAIL_SUPPRESS_SEND = True


# Map config name → class
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
