"""
Service: Audit Logging (MongoDB)
Logs all important actions to MongoDB for audit trail.
"""
from datetime import datetime
from flask import request
from ..extensions import mongo
import logging

logger = logging.getLogger(__name__)


def log_audit(action: str, user_id: int = None, target_type: str = None,
              target_id: int = None, details: dict = None,
              status: str = "SUCCESS") -> bool:
    """
    Log an action to MongoDB audit_logs collection.
    
    Args:
        action: Action performed (e.g., "BOOKING_CREATED", "USER_LOGIN")
        user_id: ID of user performing the action
        target_type: Type of target (e.g., "booking", "user", "hotel")
        target_id: ID of the target
        details: Additional details as dict
        status: Result status ("SUCCESS", "FAILED", etc.)
    
    Returns:
        True if logged successfully
    """
    try:
        log_entry = {
            "action": action,
            "user_id": user_id,
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "status": status,
            "ip_address": request.remote_addr if request else None,
            "user_agent": request.user_agent.string if request else None,
            "created_at": datetime.utcnow(),
        }
        
        mongo.db.audit_logs.insert_one(log_entry)
        return True
    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")
        return False


def log_request(endpoint: str, method: str, status_code: int,
                response_time_ms: int, user_id: int = None) -> bool:
    """
    Log API request details to MongoDB request_logs collection.
    """
    try:
        log_entry = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "user_id": user_id,
            "ip_address": request.remote_addr if request else None,
            "user_agent": request.user_agent.string if request else None,
            "created_at": datetime.utcnow(),
        }
        
        mongo.db.request_logs.insert_one(log_entry)
        return True
    except Exception as e:
        logger.error(f"Failed to log request: {e}")
        return False


def log_user_activity(user_id: int, activity_type: str, metadata: dict = None) -> bool:
    """
    Log user activity to MongoDB user_activities collection.
    For analytics: page views, clicks, searches, etc.
    """
    try:
        log_entry = {
            "user_id": user_id,
            "activity_type": activity_type,
            "metadata": metadata or {},
            "session_id": request.cookies.get("session") if request else None,
            "ip_address": request.remote_addr if request else None,
            "created_at": datetime.utcnow(),
        }
        
        mongo.db.user_activities.insert_one(log_entry)
        return True
    except Exception as e:
        logger.error(f"Failed to log user activity: {e}")
        return False


def get_audit_logs(filters: dict = None, limit: int = 100) -> list:
    """
    Retrieve audit logs from MongoDB with optional filtering.
    """
    try:
        filters = filters or {}
        logs = list(mongo.db.audit_logs.find(filters).sort("created_at", -1).limit(limit))
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log['_id'] = str(log['_id'])
            log['created_at'] = log['created_at'].isoformat() if log.get('created_at') else None
        return logs
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        return []
