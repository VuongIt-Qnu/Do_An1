"""
Flask Extension Instances
Initialize here (without app context) to avoid circular imports.
Bound to the app in create_app() via .init_app(app).
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# SQLAlchemy — PostgreSQL ORM
db = SQLAlchemy()

# JWT Manager — token-based authentication
jwt = JWTManager()

# PyMongo — MongoDB client (logging, audit)
mongo = PyMongo()

# Flask-Mail — email notifications
mail = Mail()

# CORS — Cross-Origin Resource Sharing
cors = CORS()

# Marshmallow — serialization & validation
ma = Marshmallow()

# In-memory token blacklist for logout
# In production, replace with Redis: redis.sadd('blacklist', jti)
token_blacklist: set = set()
