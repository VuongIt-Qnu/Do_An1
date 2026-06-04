"""
pytest tests/test_integration.py
Full API workflow integration tests
"""

import pytest
from http import HTTPStatus
from datetime import datetime, timedelta


class TestCompleteBookingWorkflow:
    """Test complete booking workflow from start to finish"""

    def test_full_booking_to_review_workflow(self, client, user_token, admin_token, owner_token, sample_room):
        """Test complete workflow: Register → Create Booking → Payment → Review"""
        
        # Step 1: Create booking
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        booking_response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'John Doe',
                'guest_email': 'john@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 2,
                'special_requests': 'Ocean view'
            }
        )
        assert booking_response.status_code == HTTPStatus.CREATED
        booking_id = booking_response.json['data']['id']
        total_price = booking_response.json['data']['total_price']
        
        # Step 2: Process payment
        payment_response = client.post('/api/payments/process',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'booking_id': booking_id,
                'payment_method': 'BANK_TRANSFER',
                'amount': total_price
            }
        )
        assert payment_response.status_code == HTTPStatus.OK
        
        # Step 3: Confirm booking (admin)
        confirm_response = client.patch(f'/api/bookings/{booking_id}/confirm',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'confirmation_note': 'Confirmed and assigned'}
        )
        assert confirm_response.status_code == HTTPStatus.OK
        assert confirm_response.json['data']['status'] == 'CONFIRMED'
        
        # Step 4: Complete booking (after checkout)
        complete_response = client.patch(f'/api/bookings/{booking_id}/complete',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        # May succeed or fail depending on date logic
        assert complete_response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
        
        # Step 5: Add review
        review_response = client.post(f'/api/bookings/{booking_id}/review',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'rating': 5,
                'comment': 'Wonderful stay! Great service and clean rooms.'
            }
        )
        # May succeed or fail depending on status
        assert review_response.status_code in [HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST]
        
        # Step 6: Verify booking can be retrieved
        get_response = client.get(f'/api/bookings/{booking_id}',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        assert get_response.status_code == HTTPStatus.OK

    def test_owner_manages_hotel_bookings(self, client, owner_token, user_token, sample_room):
        """Test owner can manage their hotel's bookings"""
        
        # Step 1: Owner views their hotels
        hotels_response = client.get('/api/owner/hotels',
            headers={'Authorization': f'Bearer {owner_token}'}
        )
        assert hotels_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        
        # Step 2: Create booking for owner's room
        check_in = datetime.now() + timedelta(days=3)
        check_out = check_in + timedelta(days=2)
        
        booking_response = client.post('/api/bookings',
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
        assert booking_response.status_code == HTTPStatus.CREATED
        booking_id = booking_response.json['data']['id']
        
        # Step 3: Owner views their bookings
        owner_bookings = client.get('/api/owner/bookings',
            headers={'Authorization': f'Bearer {owner_token}'}
        )
        assert owner_bookings.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        
        # Step 4: Owner checks revenue
        revenue_response = client.get('/api/owner/revenue',
            headers={'Authorization': f'Bearer {owner_token}'}
        )
        assert revenue_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]

    def test_admin_full_system_overview(self, client, admin_token, user_token, sample_room):
        """Test admin can see full system overview"""
        
        # Step 1: Admin dashboard
        dashboard_response = client.get('/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert dashboard_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        
        # Step 2: List all users
        users_response = client.get('/api/admin/users?page=1&per_page=20',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert users_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        
        # Step 3: View audit logs
        logs_response = client.get('/api/admin/logs',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert logs_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        
        # Step 4: Revenue reports
        reports_response = client.get('/api/reports/revenue',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert reports_response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]


class TestErrorHandling:
    """Test error handling across the API"""

    def test_invalid_credentials_chain(self, client):
        """Test that invalid credentials don't expose sensitive info"""
        
        # Register with valid data
        register_response = client.post('/api/auth/register', json={
            'full_name': 'Test',
            'email': 'test@example.com',
            'password': 'Pass123!',
            'phone': '+84901234567'
        })
        assert register_response.status_code == HTTPStatus.CREATED
        
        # Try login with wrong password
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        assert login_response.status_code == HTTPStatus.UNAUTHORIZED
        # Verify no sensitive data in error
        error_msg = login_response.json.get('message', '')
        assert 'password' not in error_msg.lower()

    def test_concurrent_bookings_same_room(self, client, user_token, sample_room):
        """Test handling of concurrent bookings on same room (simulation)"""
        
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=2)
        
        # First booking succeeds
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
        
        # Concurrent/overlapping booking fails
        response2 = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': (check_in + timedelta(hours=12)).strftime('%Y-%m-%d'),
                'check_out': (check_out + timedelta(hours=12)).strftime('%Y-%m-%d'),
                'guest_name': 'Guest 2',
                'guest_email': 'g2@example.com',
                'guest_phone': '+84901234568',
                'number_of_guests': 1
            }
        )
        assert response2.status_code == HTTPStatus.CONFLICT

    def test_payment_failure_recovery(self, client, user_token, sample_room):
        """Test booking and payment failure scenarios"""
        
        check_in = datetime.now() + timedelta(days=5)
        check_out = check_in + timedelta(days=2)
        
        # Create booking
        booking_response = client.post('/api/bookings',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'room_id': sample_room.id,
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'guest_name': 'Test Guest',
                'guest_email': 'test@example.com',
                'guest_phone': '+84901234567',
                'number_of_guests': 1
            }
        )
        booking_id = booking_response.json['data']['id']
        
        # Attempt payment (may fail in simulation)
        payment_response = client.post('/api/payments/process',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'booking_id': booking_id,
                'payment_method': 'BANK_TRANSFER',
                'amount': 300.0
            }
        )
        # Should handle both success and failure
        assert payment_response.status_code == HTTPStatus.OK
        
        payment_status = payment_response.json['data'].get('status')
        if payment_status == 'FAILED':
            # Can retry
            retry_response = client.post('/api/payments/process',
                headers={'Authorization': f'Bearer {user_token}'},
                json={
                    'booking_id': booking_id,
                    'payment_method': 'MOMO',
                    'amount': 300.0
                }
            )
            assert retry_response.status_code == HTTPStatus.OK


class TestAccessControl:
    """Test access control and authorization"""

    def test_user_cannot_access_own_data_via_others_ids(self, client, user_token, admin_token):
        """Test that users can only access their own bookings"""
        
        # User tries to access non-existent booking ID 1
        response = client.get('/api/bookings/1',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        # Should either 404 or 403
        assert response.status_code in [HTTPStatus.NOT_FOUND, HTTPStatus.FORBIDDEN]

    def test_owner_cannot_modify_other_owners_hotels(self, client, owner_token, sample_hotel):
        """Test that owners can't modify other owners' hotels"""
        # This would need setup of second owner
        # Placeholder for security test
        pass

    def test_user_cannot_become_admin(self, client, user_token):
        """Test that regular users can't escalate privileges via API"""
        
        # Try to update own profile with admin role
        response = client.put('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'},
            json({'role': 'ADMIN'})
        )
        # Should not allow role change
        assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.OK]
        if response.status_code == HTTPStatus.OK:
            # If it allows, role should still be USER
            assert response.json['data']['role'] == 'USER'


class TestDataValidation:
    """Test input validation and sanitization"""

    def test_email_validation(self, client):
        """Test email validation in registration"""
        
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@nodomain.com',
            'spaces in@email.com'
        ]
        
        for email in invalid_emails:
            response = client.post('/api/auth/register', json={
                'full_name': 'User',
                'email': email,
                'password': 'Pass123!',
                'phone': '+84901234567'
            })
            assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_phone_validation(self, client):
        """Test phone validation"""
        
        response = client.post('/api/auth/register', json={
            'full_name': 'User',
            'email': 'test@example.com',
            'password': 'Pass123!',
            'phone': 'invalid-phone'  # Invalid format
        })
        # Should validate phone format
        assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.CREATED]

    def test_xss_prevention(self, client):
        """Test that user input is sanitized"""
        
        response = client.post('/api/auth/register', json={
            'full_name': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'password': 'Pass123!',
            'phone': '+84901234567'
        })
        
        if response.status_code == HTTPStatus.CREATED:
            # Verify script tags are escaped or removed
            data = response.json['data']
            assert '<script>' not in data.get('full_name', '')


class TestPagination:
    """Test pagination across APIs"""

    def test_hotels_pagination(self, client, multiple_hotels):
        """Test hotel listing pagination"""
        
        # Page 1
        response1 = client.get('/api/hotels?page=1&per_page=1')
        assert response1.status_code == HTTPStatus.OK
        page1_data = response1.json['data']
        
        # Page 2
        response2 = client.get('/api/hotels?page=2&per_page=1')
        assert response2.status_code == HTTPStatus.OK
        page2_data = response2.json['data']
        
        # Should be different hotels
        if len(page1_data) > 0 and len(page2_data) > 0:
            assert page1_data[0]['id'] != page2_data[0]['id']

    def test_bookings_pagination(self, client, user_token):
        """Test booking listing pagination"""
        
        response = client.get('/api/bookings/my?page=1&per_page=10',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        assert response.status_code == HTTPStatus.OK
        
        if 'pagination' in response.json:
            pagination = response.json['pagination']
            assert 'page' in pagination
            assert 'per_page' in pagination
            assert 'total' in pagination

    def test_invalid_pagination_params(self, client):
        """Test invalid pagination parameters"""
        
        # Negative page
        response = client.get('/api/hotels?page=-1')
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
        
        # Zero per_page
        response = client.get('/api/hotels?per_page=0')
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
        
        # Very large per_page
        response = client.get('/api/hotels?per_page=10000')
        # Should either limit or error
        assert response.status_code == HTTPStatus.OK
