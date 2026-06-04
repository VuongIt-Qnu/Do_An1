"""
Auth Middleware — Role-based access control decorators.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.user import User
from ..extensions import db


def safe_get_jwt_identity():
    """Returns JWT identity or None — never raises RuntimeError."""
    try:
        return get_jwt_identity()
    except RuntimeError:
        return None


def role_required(*roles: str):
    """Verify JWT + check role. Returns 403 if wrong role, 401/422 if bad token."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if user is None:
                return jsonify({"success": False, "message": "User not found"}), 404
            if not user.enabled:
                return jsonify({"success": False, "message": "Account is disabled"}), 403
            if user.role not in roles:
                return jsonify({
                    "success": False,
                    "message": f"Forbidden. Required roles: {list(roles)}"
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user() -> User | None:
    """Return current authenticated User from DB, or None."""
    user_id = safe_get_jwt_identity()
    if user_id is None:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def optional_jwt(fn):
    """
    Optional JWT for PUBLIC endpoints (room listing, hotel listing, etc.)
    - Always succeeds, even with invalid/stale tokens.
    - Invalid token → treated as anonymous (identity = None).
    - Use @jwt_required() for protected endpoints where token must be valid.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass  # Invalid/stale token → treat as anonymous, never block
        return fn(*args, **kwargs)
    return wrapper
