"""
Marshmallow Schemas
For validation and serialization of models.
"""
from marshmallow import Schema, fields, validate, pre_load, post_load, ValidationError
from datetime import datetime


class UserSchema(Schema):
    """User schema for registration, login response"""
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(allow_none=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['ADMIN', 'OWNER', 'USER']))
    passport = fields.Str(allow_none=True)
    nationality = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    enabled = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'full_name', 'email', 'phone_number', 'password', 'role',
                  'passport', 'nationality', 'address', 'enabled', 'created_at', 'updated_at', 'last_login')


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UserResponseSchema(Schema):
    """User info response (without sensitive data)"""
    id = fields.Int()
    full_name = fields.Str()
    email = fields.Email()
    phone_number = fields.Str()
    role = fields.Str()
    passport = fields.Str()
    nationality = fields.Str()
    address = fields.Str()
    enabled = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class HotelSchema(Schema):
    """Hotel schema for CRUD operations"""
    id = fields.Int(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    star_rating = fields.Int(validate=validate.Range(min=1, max=5))
    enabled = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'owner_id', 'name', 'address', 'city', 'description', 
                  'phone', 'email', 'star_rating', 'enabled', 'created_at', 'updated_at')


class RoomSchema(Schema):
    """Room schema for creation and updates"""
    id = fields.Int(dump_only=True)
    hotel_id = fields.Int(dump_only=True)
    hotel_name = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    room_type = fields.Str(required=True)
    capacity = fields.Int(required=True, validate=validate.Range(min=1))
    price_per_night = fields.Decimal(required=True, places=2, as_string=True)
    area = fields.Decimal(allow_none=True, places=2, as_string=True)
    amenities = fields.Str(allow_none=True)  # comma-separated
    description = fields.Str(allow_none=True)
    main_image_url = fields.Url(allow_none=True)
    rating = fields.Decimal(dump_only=True, places=2, as_string=True)
    featured = fields.Bool()
    status = fields.Str(validate=validate.OneOf(['AVAILABLE', 'OCCUPIED', 'MAINTENANCE']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'hotel_id', 'hotel_name', 'name', 'room_type', 'capacity',
                  'price_per_night', 'area', 'amenities', 'description', 'main_image_url',
                  'rating', 'featured', 'status', 'created_at', 'updated_at')


class BookingSchema(Schema):
    """Booking schema for creation and updates"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    customer_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    customer_email = fields.Email(required=True)
    customer_phone = fields.Str(allow_none=True)
    hotel_id = fields.Int(required=True)
    hotel_name = fields.Str(dump_only=True)
    room_id = fields.Int(required=True)
    room_name = fields.Str(dump_only=True)
    room_type = fields.Str(dump_only=True)
    check_in = fields.Date(required=True)
    check_out = fields.Date(required=True)
    nights = fields.Int(dump_only=True)
    guests = fields.Int(required=True, validate=validate.Range(min=1))
    total_price = fields.Decimal(dump_only=True, places=2, as_string=True)
    status = fields.Str(dump_only=True)
    cancel_reason = fields.Str(allow_none=True)
    cancelled_at = fields.DateTime(dump_only=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'user_id', 'customer_name', 'customer_email', 'customer_phone',
                  'hotel_id', 'hotel_name', 'room_id', 'room_name', 'room_type',
                  'check_in', 'check_out', 'nights', 'guests', 'total_price',
                  'status', 'cancel_reason', 'cancelled_at', 'notes', 'created_at', 'updated_at')


class PaymentSchema(Schema):
    """Payment schema"""
    id = fields.Int(dump_only=True)
    booking_id = fields.Int(required=True)
    amount = fields.Decimal(required=True, places=2, as_string=True)
    method = fields.Str(validate=validate.OneOf(['CASH', 'BANK_TRANSFER', 'MOMO', 'QR']))
    status = fields.Str(validate=validate.OneOf(['PENDING', 'PAID', 'FAILED', 'REFUNDED']))
    transaction_ref = fields.Str(allow_none=True)
    paid_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'booking_id', 'amount', 'method', 'status', 'transaction_ref', 'paid_at', 'created_at')


class ReviewSchema(Schema):
    """Review schema"""
    id = fields.Int(dump_only=True)
    booking_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(dump_only=True)
    room_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('id', 'booking_id', 'user_id', 'user_name', 'room_id', 'rating', 'comment', 'created_at', 'updated_at')


# Response schemas
class TokenResponseSchema(Schema):
    """JWT token response schema"""
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserResponseSchema)


class SuccessResponseSchema(Schema):
    """Generic success response"""
    success = fields.Bool()
    message = fields.Str()
    data = fields.Dict(allow_none=True)


class ErrorResponseSchema(Schema):
    """Generic error response"""
    success = fields.Bool(dump_default=False)
    message = fields.Str()
    errors = fields.Dict(allow_none=True)
