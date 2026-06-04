"""
Request Logging Middleware
Logs every incoming HTTP request to MongoDB (collection: request_logs).
Also logs to Flask app logger for console output.
"""
import time
from datetime import datetime, timezone
from flask import Flask, g, request
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTExtendedException


def register_logging_middleware(app: Flask) -> None:
    """Attach before/after request hooks to the Flask app"""

    @app.before_request
    def before_request():
        """Record start time before each request"""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Log request details to MongoDB after response is ready"""
        # Calculate response time
        duration_ms = int((time.time() - g.get("start_time", time.time())) * 1000)

        # Try to extract user_id from JWT without failing on missing/invalid tokens
        user_id = None
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                decoded = decode_token(token)
                user_id = decoded.get("sub")
        except (JWTExtendedException, Exception):
            pass  # Token absent or invalid — log as anonymous

        log_entry = {
            "method": request.method,
            "endpoint": request.path,
            "status_code": response.status_code,
            "response_time_ms": duration_ms,
            "user_id": user_id,
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "")[:200],
            "created_at": datetime.now(timezone.utc),
        }

        # Write to MongoDB asynchronously (best-effort — never fail the request)
        try:
            from ..extensions import mongo
            if mongo.db is not None:
                mongo.db.request_logs.insert_one(log_entry)
        except Exception as e:
            app.logger.warning(f"[Logging Middleware] MongoDB write failed: {e}")

        # Console log
        app.logger.info(
            f"{request.method} {request.path} → {response.status_code} "
            f"({duration_ms}ms) user={user_id}"
        )

        return response
