"""
Service: Email Notifications
Sends transactional emails for booking confirmations, password resets, etc.
Uses Flask-Mail for SMTP.
"""
from flask import render_template_string
from flask_mail import Message
from ..extensions import mail
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, recipients: list, html_body: str) -> bool:
    """
    Send email via Flask-Mail (SMTP).
    In development, emails are printed to console instead.
    
    Args:
        subject: Email subject line
        recipients: List of recipient email addresses
        html_body: HTML content of the email
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
        )
        mail.send(msg)
        logger.info(f"Email sent to {recipients}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        return False


def send_booking_confirmation(user_name: str, user_email: str, booking_dict: dict) -> bool:
    """Send booking confirmation email"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Booking Confirmation</h2>
        <p>Dear {user_name},</p>
        <p>Your booking has been confirmed!</p>
        
        <h3>Booking Details:</h3>
        <ul>
            <li><strong>Hotel:</strong> {booking_dict.get('hotel_name')}</li>
            <li><strong>Room:</strong> {booking_dict.get('room_name')} ({booking_dict.get('room_type')})</li>
            <li><strong>Check-in:</strong> {booking_dict.get('check_in')}</li>
            <li><strong>Check-out:</strong> {booking_dict.get('check_out')}</li>
            <li><strong>Number of nights:</strong> {booking_dict.get('nights')}</li>
            <li><strong>Total Price:</strong> ${booking_dict.get('total_price')}</li>
            <li><strong>Status:</strong> {booking_dict.get('status')}</li>
        </ul>
        
        <p>Thank you for choosing us!</p>
        <p>Best regards,<br>Hotel Management System</p>
    </body>
    </html>
    """
    return send_email(
        subject="Booking Confirmation",
        recipients=[user_email],
        html_body=html
    )


def send_booking_confirmed_by_admin(booking, user_email: str) -> bool:
    """Send booking confirmation after admin approval"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Booking Confirmed by Management</h2>
        <p>Dear {booking.customer_name},</p>
        <p>Your booking #{booking.id} has been confirmed by our management team!</p>
        
        <h3>Booking Details:</h3>
        <ul>
            <li><strong>Booking ID:</strong> {booking.id}</li>
            <li><strong>Hotel:</strong> {booking.hotel.name if booking.hotel else 'N/A'}</li>
            <li><strong>Room:</strong> {booking.room.name if booking.room else 'N/A'}</li>
            <li><strong>Check-in:</strong> {booking.check_in}</li>
            <li><strong>Check-out:</strong> {booking.check_out}</li>
            <li><strong>Total Price:</strong> VND {booking.total_price:,.0f}</li>
            <li><strong>Status:</strong> {booking.status}</li>
        </ul>
        
        <p><strong>Important:</strong> Please arrive 30 minutes before your check-in time.</p>
        
        <p>Best regards,<br>Hotel Management System</p>
    </body>
    </html>
    """
    return send_email(
        subject="Booking Confirmed",
        recipients=[user_email],
        html_body=html
    )


def send_booking_cancelled(user_name: str, user_email: str, booking_id: int, reason: str) -> bool:
    """Send booking cancellation notification"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Booking Cancelled</h2>
        <p>Dear {user_name},</p>
        <p>Your booking #{booking_id} has been cancelled.</p>
        
        <h3>Cancellation Reason:</h3>
        <p>{reason or 'No reason provided'}</p>
        
        <p>If you have any questions, please contact our support team.</p>
        <p>Best regards,<br>Hotel Management System</p>
    </body>
    </html>
    """
    return send_email(
        subject="Booking Cancelled",
        recipients=[user_email],
        html_body=html
    )


def send_reset_password_email(user, reset_link: str) -> bool:
    """Send password reset email"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Password Reset Request</h2>
        <p>Dear {user.full_name},</p>
        <p>You requested a password reset. Click the link below to proceed:</p>
        
        <p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Reset Password
        </a></p>
        
        <p>This link expires in 2 hours.</p>
        <p>If you did not request this, ignore this email.</p>
        <p>Best regards,<br>Hotel Management System</p>
    </body>
    </html>
    """
    return send_email(
        subject="Password Reset Request",
        recipients=[user.email],
        html_body=html
    )


def send_payment_receipt(user_email: str, payment_dict: dict) -> bool:
    """Send payment receipt"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Payment Receipt</h2>
        <p>Thank you for your payment!</p>
        
        <h3>Payment Details:</h3>
        <ul>
            <li><strong>Amount:</strong> ${payment_dict.get('amount')}</li>
            <li><strong>Method:</strong> {payment_dict.get('method')}</li>
            <li><strong>Status:</strong> {payment_dict.get('status')}</li>
            <li><strong>Transaction ID:</strong> {payment_dict.get('transaction_ref', 'N/A')}</li>
            <li><strong>Date:</strong> {payment_dict.get('paid_at')}</li>
        </ul>
        
        <p>Best regards,<br>Hotel Management System</p>
    </body>
    </html>
    """
    return send_email(
        subject="Payment Receipt",
        recipients=[user_email],
        html_body=html
    )
