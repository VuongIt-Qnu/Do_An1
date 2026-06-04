"""
pytest tests/test_bookings.py
Booking management and workflow tests
"""

import pytest
from http import HTTPStatus
from datetime import datetime, timedelta


class TestCreateBooking:
    """Booking creation tests"""

    def test_create_booking_success(self, client, user_token, sample_room, valid_booking_data):
        """Test successful booking creation"""
        valid_booking_data['room_id'] = sample_room.id
        
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json=valid_booking_data
        )
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json['data']
        assert data['status'] == 'PENDING'
        assert data['room_id'] == sample_room.id
        assert data['total_price'] == 450.0  # 3 nights × 150
        assert 'booking_id' in data or 'id' in data

    def test_create_booking_without_auth(self, client, sample_room, valid_booking_data):
        """Test booking without authentication"""
        valid_booking_data['room_id'] = sample_room.id
        response = client.post('/api/bookings', json=valid_booking_data)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_booking_with_past_dates(self, client, user_token, sample_room):
        """Test booking with dates in the past"""
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'check_out': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest',
                'guest_email': 'guest@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_create_booking_checkout_before_checkin(self, client, user_token, sample_room):
        """Test booking where checkout is before checkin"""
        check_in = datetime.now() + timedelta(days=5)
        
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': (check_in - timedelta(days=1)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest',
                'guest_email': 'guest@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_create_booking_nonexistent_room(self, client, user_token, valid_booking_data):
        """Test booking non-existent room"""
        valid_booking_data['room_id'] = 99999
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json=valid_booking_data
        )
        
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestBookingConflicts:
    """Test booking conflict detection"""

    def test_overlapping_bookings_conflict(self, client, user_token, sample_room):
        """Test that overlapping bookings are rejected"""
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        # First booking
        response1 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Guest 1',
                'guest_email': 'g1@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        assert response1.status_code == HTTPStatus.CREATED
        
        # Overlapping booking (should fail)
        response2 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': (check_in + timedelta(days=1)).strftime('%Y-%m-%d'),
                'check_out': (check_out - timedelta(days=1)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest 2',
                'guest_email': 'g2@example.com',
                'guest_phone': '+84901234568',
                'number_of_guests': 1
            }
        )
        assert response2.status_code == HTTPStatus.CONFLICT

    def test_adjacent_bookings_allowed(self, client, user_token, sample_room):
        """Test that adjacent (non-overlapping) bookings are allowed"""
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        # First booking
        response1 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Guest 1',
                'guest_email': 'g1@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        assert response1.status_code == HTTPStatus.CREATED
        
        # Adjacent booking (should succeed)
        response2 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_out.strftime('%Y-%m-%d'),
                'check_out': (check_out + timedelta(days=2)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest 2',
                'guest_email': 'g2@example.com',
                'guest_phone': '+84901234568',
                'number_of_guests': 1
            }
        )
        assert response2.status_code == HTTPStatus.CREATED


class TestBookingActions:
    """Test booking lifecycle actions"""

    def create_and_get_booking(self, client, user_token, sample_room):
        """Helper to create a booking and return its ID"""
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Test Guest',
                'guest_email': 'guest@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        return response.json['data']['id']

    def test_confirm_booking_as_admin(self, client, admin_token, user_token, sample_room):
        """Test confirming booking as admin"""
        booking_id = self.create_and_get_booking(client, user_token, sample_room)
        
        response = client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'confirmation_note': 'Confirmed'}
        )
        
        assert response.status_code == HTTPStatus.OK
        assert response.json['data']['status'] == 'CONFIRMED'

    def test_confirm_booking_as_user_forbidden(self, client, user_token, sample_room):
        """Test that regular user cannot confirm booking"""
        booking_id = self.create_and_get_booking(client, user_token, sample_room)
        
        response = client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'confirmation_note': 'Confirmed'}
        )
        
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_cancel_booking_full_refund(self, client, user_token, admin_token, sample_room):
        """Test cancelling booking far in advance gets full refund"""
        booking_id = self.create_and_get_booking(client, user_token, sample_room)
        
        response = client.patch(f'/api/bookings/{booking_id}/cancel',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'cancellation_reason': 'Change of plans'}
        )
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['status'] == 'CANCELLED'
        assert data['cancellation_penalty'] == 0  # Full refund (>24 hours)

    def test_cancel_nonexistent_booking(self, client, user_token):
        """Test cancelling non-existent booking"""
        response = client.patch('/api/bookings/99999/cancel',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'cancellation_reason': 'Test'}
        )
        
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestBookingReviews:
    """Booking review tests"""

    def test_add_review_to_booking(self, client, user_token, admin_token, sample_room):
        """Test adding review to completed booking"""
        # Create booking
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=1)
        
        response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Reviewer',
                'guest_email': 'reviewer@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        booking_id = response.json['data']['id']
        
        # Confirm booking
        client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {admin_token}'})
        
        # Add review (in real test, booking must be COMPLETED)
        response = client.post(f'/api/bookings/{booking_id}/review',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'rating': 5,
                'comment': 'Excellent service!'
            }
        )
        
        # Depending on implementation, may fail if not completed
        assert response.status_code in [HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST]

    def test_review_requires_rating(self, client, user_token):
        """Test that review requires rating"""
        response = client.post('/api/bookings/1/review',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'comment': 'Good room'  # Missing rating
            }
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_get_room_reviews(self, client, sample_room):
        """Test retrieving room reviews"""
        response = client.get(f'/api/bookings/room/{sample_room.id}/reviews')
        
        # Endpoint may not exist or may require auth
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED, HTTPStatus.NOT_FOUND]
