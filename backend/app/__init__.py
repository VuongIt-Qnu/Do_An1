"""
Application Factory
Creates and configures the Flask application instance.
"""
from flask import Flask, jsonify, request as flask_request, make_response
from .config import config_map
from .extensions import db, jwt, mongo, mail, cors, ma, token_blacklist


def create_app(env: str = "development") -> Flask:
    """
    Flask application factory.

    Args:
        env: Environment name — 'development', 'production', or 'testing'

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # ── Load Configuration ──────────────────────────────────────────
    config_class = config_map.get(env, config_map["development"])
    app.config.from_object(config_class)

    # ── Initialize Extensions ────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    mongo.init_app(app)
    mail.init_app(app)
    ma.init_app(app)

    # Flask-CORS — khởi tạo với wildcard để đảm bảo hoạt động
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}},
                  allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
                  methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                  supports_credentials=False)

    # ── CORS Fallback — đảm bảo headers luôn được gửi kể cả khi có lỗi ─
    @app.before_request
    def handle_preflight():
        """Xử lý OPTIONS preflight request trước khi route handler chạy"""
        if flask_request.method == "OPTIONS":
            resp = make_response()
            resp.headers["Access-Control-Allow-Origin"]  = flask_request.headers.get("Origin", "*")
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            resp.headers["Access-Control-Max-Age"]       = "3600"
            return resp, 200

    @app.after_request
    def add_cors_headers(response):
        """Đảm bảo CORS header có mặt trên MỌI response (kể cả error 4xx/5xx)"""
        origin = flask_request.headers.get("Origin", "")
        # Trong dev cho phép tất cả, production giới hạn theo CORS_ORIGINS
        allowed_origins = app.config.get("CORS_ORIGINS", [])
        if env == "development" or origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"]  = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Vary"] = "Origin"
        return response

    # ── JWT Callbacks ────────────────────────────────────────────────
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if JWT token has been revoked (logged out)"""
        return jwt_payload["jti"] in token_blacklist

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has been revoked"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"success": False, "message": "Authentication required"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"success": False, "message": "Invalid token"}), 422

    # ── Health Check Endpoint ────────────────────────────────────────
    @app.route("/health")
    def health():
        """Used by Docker healthcheck and load balancers"""
        return jsonify({"status": "ok", "service": "hotel-api", "version": "2.0.0"}), 200

    # ── Favicon (tránh 500 khi browser tự request) ───────────────────
    @app.route("/favicon.ico")
    def favicon():
        return "", 204  # No Content — không có favicon, trả về rỗng

    # ── Root ─────────────────────────────────────────────────────
    @app.route("/")
    def root():
        return jsonify({
            "success": True,
            "message": "Hotel Management API v2.0 — Backend running",
            "api": "/api",
            "health": "/health",
        }), 200

    # ── API Index ─────────────────────────────────────────────────
    @app.route("/api/")
    @app.route("/api")
    def api_index():
        """API endpoint index — lists all available routes"""
        return jsonify({
            "success": True,
            "message": "Hotel Management API v2.0",
            "endpoints": {
                "auth":     "/api/auth   (register, login, logout, profile)",
                "hotels":   "/api/hotels (list, detail, create, update)",
                "rooms":    "/api/rooms  (list, detail, availability, reviews)",
                "bookings": "/api/bookings (create, list, confirm, cancel, review)",
                "payments": "/api/payments (process, refund, list, stats)",
                "admin":    "/api/admin  (dashboard, users, hotels, logs) [ADMIN]",
                "owner":    "/api/owner  (dashboard, hotels, rooms, revenue) [OWNER]",
                "reports":  "/api/reports (revenue, occupancy, export pdf/excel) [ADMIN|OWNER]",
            },
            "health": "/health",
            "docs": "Xem Readme_run.md để biết chi tiết từng endpoint",
        }), 200

    # ── Register Blueprints ──────────────────────────────────────────
    _register_blueprints(app)

    # ── Register Error Handlers ──────────────────────────────────────
    _register_error_handlers(app)

    # ── Register Middleware ──────────────────────────────────────────
    _register_middleware(app)

    # ── Create DB Tables (dev/test only) ─────────────────────────────
    with app.app_context():
        # Import models so SQLAlchemy can register them
        from .models import User, Hotel, Room, Booking, Payment, Review  # noqa: F401
        if env in ("development", "testing"):
            db.create_all()

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints with /api prefix"""
    from .routes.auth import auth_bp
    from .routes.rooms import rooms_bp
    from .routes.hotels import hotels_bp
    from .routes.bookings import bookings_bp
    from .routes.payments import payments_bp
    from .routes.admin import admin_bp
    from .routes.owner import owner_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp,     url_prefix="/api/auth")
    app.register_blueprint(rooms_bp,    url_prefix="/api/rooms")
    app.register_blueprint(hotels_bp,   url_prefix="/api/hotels")
    app.register_blueprint(bookings_bp, url_prefix="/api/bookings")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp,    url_prefix="/api/admin")
    app.register_blueprint(owner_bp,    url_prefix="/api/owner")
    app.register_blueprint(reports_bp,  url_prefix="/api/reports")


def _register_error_handlers(app: Flask) -> None:
    """Register global HTTP error handlers"""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "message": "Bad request", "error": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "message": "Forbidden — insufficient permissions"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"success": False, "message": "Validation error", "error": str(e)}), 422

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


def _register_middleware(app: Flask) -> None:
    """Register request/response middleware"""
    from .middleware.logging_middleware import register_logging_middleware
    register_logging_middleware(app)
