"""
Response Helpers
Provides consistent JSON response structure across all API endpoints.

Response envelope format:
    {
        "success": true,
        "data": { ... },
        "message": "Optional message"
    }
    or
    {
        "success": false,
        "message": "Error description",
        "errors": { "field": ["error detail"] }
    }
"""
import math
from flask import jsonify, request as flask_request


def success_response(data=None, message: str = None, status_code: int = 200):
    """
    Standard success response.

    Args:
        data: Response payload (dict, list, or None)
        message: Optional human-readable message
        status_code: HTTP status code (default 200)

    Returns:
        (Flask Response, int) tuple
    """
    body = {"success": True}
    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    return jsonify(body), status_code


def error_response(message: str, status_code: int = 400, errors=None):
    """
    Standard error response.

    Args:
        message: Human-readable error description
        status_code: HTTP error status code
        errors: Optional dict of field-level validation errors

    Returns:
        (Flask Response, int) tuple
    """
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status_code


def get_page_args(default_per_page: int = 20, max_per_page: int = 100):
    """
    Parse and clamp pagination query parameters.
    Returns (page, per_page) both guaranteed >= 1.
    """
    page = max(1, flask_request.args.get("page", 1, type=int) or 1)
    per_page = min(
        max(1, flask_request.args.get("per_page", default_per_page, type=int) or default_per_page),
        max_per_page,
    )
    return page, per_page


def paginated_response(items: list, total: int, page: int, per_page: int):
    """
    Paginated list response with metadata.

    Args:
        items: List of serialized items for the current page
        total: Total count of all matching records
        page: Current page number (1-indexed)
        per_page: Items per page

    Returns:
        (Flask Response, int) tuple
    """
    total_pages = math.ceil(total / per_page) if per_page > 0 else 1
    return jsonify({
        "success": True,
        "items": items,   # FIX: use "items" key (frontend expects .items)
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    }), 200
