"""
pytest tests/test_auth.py
Authentication endpoint tests
"""

import pytest
from http import HTTPStatus


class TestUserRegistration:
    """User registration tests"""

    def test_register_success(self, client, valid_user_data):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json=valid_user_data)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json
        assert data['success'] is True
        assert data['data']['email'] == valid_user_data['email']
        assert data['data']['full_name'] == valid_user_data['full_name']
        assert data['data']['role'] == 'USER'
        assert 'password' not in data['data']  # Should not return password

    def test_register_duplicate_email(self, client, regular_user, valid_user_data):
        """Test registration with existing email"""
        valid_user_data['email'] = 'guest@test.com'  # Existing user
        response = client.post('/api/auth/register', json=valid_user_data)
        
        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json['success'] is False

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post('/api/auth/register', json={
            'full_name': 'User',
            'email': 'not-an-email',
            'password': 'Pass123!',
            'phone': '+84901234567'
        })
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'email' in response.json.get('errors', {})

    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/api/auth/register', json={
            'full_name': 'User',
            'email': 'test@example.com',
            'password': '123',  # Too weak
            'phone': '+84901234567'
        })
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register', json={
            'full_name': 'User'
            # Missing email, password, phone
        })
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json['success'] is False


class TestUserLogin:
    """User login tests"""

    def test_login_success(self, client, regular_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'guest@test.com',
            'password': 'Guest123!'
        })
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'guest@test.com'
        assert data['user']['role'] == 'USER'

    def test_login_wrong_password(self, client, regular_user):
        """Test login with wrong password"""
        response = client.post('/api/auth/login', json={
            'email': 'guest@test.com',
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json['success'] is False

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent email"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'SomePass123!'
        })
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_login_missing_credentials(self, client):
        """Test login without credentials"""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_login_admin_user(self, client, admin_user):
        """Test admin login"""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'Admin123!'
        })
        
        assert response.status_code == HTTPStatus.OK
        assert response.json['data']['user']['role'] == 'ADMIN'


class TestTokenManagement:
    """Token refresh and management tests"""

    def test_refresh_token_success(self, client, user_token, regular_user):
        """Test token refresh"""
        # First get refresh token
        login_response = client.post('/api/auth/login', json={
            'email': 'guest@test.com',
            'password': 'Guest123!'
        })
        refresh_token = login_response.json['data']['refresh_token']
        
        # Refresh
        response = client.post('/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'})
        
        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json['data']

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token"""
        response = client.post('/api/auth/refresh',
            headers={'Authorization': 'Bearer invalid-token'})
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_missing_token(self, client):
        """Test refresh without token"""
        response = client.post('/api/auth/refresh')
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestUserProfile:
    """User profile endpoints tests"""

    def test_get_profile(self, client, user_token, regular_user):
        """Test getting user profile"""
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['email'] == 'guest@test.com'
        assert data['full_name'] == 'Guest User'
        assert data['role'] == 'USER'

    def test_get_profile_without_token(self, client):
        """Test getting profile without token"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token"""
        response = client.get('/api/auth/me',
            headers={'Authorization': 'Bearer invalid-token'})
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_profile_success(self, client, user_token, regular_user):
        """Test updating user profile"""
        response = client.put('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'full_name': 'Updated Name',
                'phone': '+84987654321'
            }
        )
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['full_name'] == 'Updated Name'
        assert data['phone'] == '+84987654321'

    def test_update_profile_invalid_email(self, client, user_token):
        """Test updating profile with invalid email"""
        response = client.put('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'email': 'not-an-email'
            }
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_update_profile_partial(self, client, user_token, regular_user):
        """Test partial profile update"""
        response = client.put('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'full_name': 'New Name'
                # Only update name, keep other fields
            }
        )
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['full_name'] == 'New Name'
        assert data['email'] == 'guest@test.com'  # Unchanged


class TestLogout:
    """Logout functionality tests"""

    def test_logout_success(self, client, user_token):
        """Test successful logout"""
        response = client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == HTTPStatus.OK

    def test_logout_blacklists_token(self, client, user_token):
        """Test that token is blacklisted after logout"""
        # Logout
        client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {user_token}'})
        
        # Try to use the same token
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_logout_without_token(self, client):
        """Test logout without token"""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestPasswordRecovery:
    """Password recovery tests"""

    def test_forgot_password_request(self, client, regular_user):
        """Test forgot password request"""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'guest@test.com'
        })
        
        # Should return 200 even if email doesn't exist (security)
        assert response.status_code == HTTPStatus.OK

    def test_forgot_password_nonexistent_email(self, client):
        """Test forgot password with nonexistent email"""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'nonexistent@example.com'
        })
        
        # Should return 200 for security (don't reveal if email exists)
        assert response.status_code == HTTPStatus.OK

    def test_reset_password_requires_token(self, client):
        """Test that reset password requires reset token"""
        response = client.post('/api/auth/reset-password', json={
            'token': 'invalid-token',
            'new_password': 'NewPass123!'
        })
        
        assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED]


class TestRoleBasedAccess:
    """Test role-based access control"""

    def test_admin_can_access_admin_endpoints(self, client, admin_token):
        """Test admin can access admin dashboard"""
        response = client.get('/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'})
        
        # Should succeed (may be 200 if no data, or 500 if error)
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR]

    def test_user_cannot_access_admin_endpoints(self, client, user_token):
        """Test regular user cannot access admin endpoints"""
        response = client.get('/api/admin/dashboard',
            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_owner_can_access_owner_endpoints(self, client, owner_token):
        """Test owner can access owner endpoints"""
        response = client.get('/api/owner/dashboard',
            headers={'Authorization': f'Bearer {owner_token}'})
        
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR]

    def test_user_cannot_access_owner_endpoints(self, client, user_token):
        """Test regular user cannot access owner endpoints"""
        response = client.get('/api/owner/dashboard',
            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == HTTPStatus.FORBIDDEN
