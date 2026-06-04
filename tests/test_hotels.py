"""
pytest tests/test_hotels.py
Hotel management endpoint tests
"""

import pytest
from http import HTTPStatus


class TestHotelsListing:
    """Hotel listing and filtering tests"""

    def test_list_hotels_public(self, client, sample_hotel):
        """Test listing hotels (no auth required)"""
        response = client.get('/api/hotels?page=1&per_page=10')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]

    def test_list_hotels_pagination(self, client, multiple_hotels):
        """Test hotel listing with pagination"""
        response = client.get('/api/hotels?page=1&per_page=2')
        
        assert response.status_code == HTTPStatus.OK
        pagination = response.json['pagination']
        assert pagination['page'] == 1
        assert pagination['per_page'] == 2
        assert pagination['total'] == 3

    def test_list_hotels_filter_by_city(self, client, multiple_hotels):
        """Test filtering hotels by city"""
        response = client.get('/api/hotels?city=Hanoi')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert len(data) > 0
        assert data[0]['city'] == 'Hanoi'

    def test_list_hotels_filter_by_star_rating(self, client, multiple_hotels):
        """Test filtering hotels by minimum star rating"""
        response = client.get('/api/hotels?star_rating=4')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        for hotel in data:
            assert hotel['star_rating'] >= 4

    def test_list_hotels_filter_by_name(self, client, multiple_hotels):
        """Test filtering hotels by name"""
        response = client.get('/api/hotels?name=Test%20Hotel%201')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        if len(data) > 0:
            assert 'Test Hotel 1' in data[0]['name']

    def test_list_hotels_invalid_page(self, client):
        """Test listing with invalid page number"""
        response = client.get('/api/hotels?page=999&per_page=10')
        
        # Should return empty list or error
        assert response.status_code == HTTPStatus.OK


class TestHotelDetail:
    """Hotel detail endpoint tests"""

    def test_get_hotel_detail(self, client, sample_hotel):
        """Test getting hotel detail"""
        response = client.get(f'/api/hotels/{sample_hotel.id}')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['id'] == sample_hotel.id
        assert data['name'] == sample_hotel.name
        assert data['city'] == sample_hotel.city

    def test_get_nonexistent_hotel(self, client):
        """Test getting non-existent hotel"""
        response = client.get('/api/hotels/99999')
        
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_hotel_detail_includes_rooms(self, client, sample_room):
        """Test that hotel detail includes rooms information"""
        response = client.get(f'/api/hotels/{sample_room.hotel_id}')
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert 'rooms_count' in data
        assert data['rooms_count'] >= 1


class TestCreateHotel:
    """Hotel creation tests"""

    def test_create_hotel_as_owner(self, client, owner_token, valid_hotel_data):
        """Test creating hotel as owner"""
        response = client.post('/api/hotels',
            headers={'Authorization': f'Bearer {owner_token}'},
            json=valid_hotel_data
        )
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json['data']
        assert data['name'] == valid_hotel_data['name']
        assert data['city'] == valid_hotel_data['city']
        assert 'id' in data

    def test_create_hotel_as_admin(self, client, admin_token, valid_hotel_data):
        """Test creating hotel as admin"""
        response = client.post('/api/hotels',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=valid_hotel_data
        )
        
        assert response.status_code == HTTPStatus.CREATED

    def test_create_hotel_as_user_forbidden(self, client, user_token, valid_hotel_data):
        """Test that regular user cannot create hotel"""
        response = client.post('/api/hotels',
            headers={'Authorization': f'Bearer {user_token}'},
            json=valid_hotel_data
        )
        
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_create_hotel_without_auth(self, client, valid_hotel_data):
        """Test creating hotel without authentication"""
        response = client.post('/api/hotels', json=valid_hotel_data)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_hotel_missing_fields(self, client, owner_token):
        """Test creating hotel with missing required fields"""
        response = client.post('/api/hotels',
            headers={'Authorization': f'Bearer {owner_token}'},
            json={'name': 'Hotel'}  # Missing other required fields
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_create_hotel_invalid_star_rating(self, client, owner_token):
        """Test creating hotel with invalid star rating"""
        data = {
            'name': 'Hotel',
            'city': 'Hanoi',
            'description': 'Test',
            'star_rating': 10,  # Invalid: should be 1-5
            'address': 'Test',
            'phone': '+84901234567'
        }
        response = client.post('/api/hotels',
            headers={'Authorization': f'Bearer {owner_token}'},
            json=data
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestUpdateHotel:
    """Hotel update tests"""

    def test_update_hotel_as_owner(self, client, owner_token, sample_hotel):
        """Test updating hotel as owner"""
        response = client.put(f'/api/hotels/{sample_hotel.id}',
            headers={'Authorization': f'Bearer {owner_token}'},
            json={
                'description': 'Updated description',
                'star_rating': 5
            }
        )
        
        assert response.status_code == HTTPStatus.OK
        data = response.json['data']
        assert data['description'] == 'Updated description'
        assert data['star_rating'] == 5

    def test_update_hotel_as_user_forbidden(self, client, user_token, sample_hotel):
        """Test that regular user cannot update hotel"""
        response = client.put(f'/api/hotels/{sample_hotel.id}',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'star_rating': 5}
        )
        
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_nonexistent_hotel(self, client, owner_token):
        """Test updating non-existent hotel"""
        response = client.put('/api/hotels/99999',
            headers={'Authorization': f'Bearer {owner_token}'},
            json={'name': 'Updated'}
        )
        
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestDeleteHotel:
    """Hotel deletion tests"""

    def test_delete_hotel_as_admin(self, client, admin_token, sample_hotel):
        """Test deleting hotel as admin"""
        hotel_id = sample_hotel.id
        response = client.delete(f'/api/hotels/{hotel_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == HTTPStatus.OK
        
        # Verify deletion
        response = client.get(f'/api/hotels/{hotel_id}')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_hotel_as_owner_forbidden(self, client, owner_token, sample_hotel):
        """Test that owner cannot delete hotel"""
        response = client.delete(f'/api/hotels/{sample_hotel.id}',
            headers={'Authorization': f'Bearer {owner_token}'}
        )
        
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_delete_hotel_as_user_forbidden(self, client, user_token, sample_hotel):
        """Test that user cannot delete hotel"""
        response = client.delete(f'/api/hotels/{sample_hotel.id}',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == HTTPStatus.FORBIDDEN


class TestHotelStatistics:
    """Hotel statistics tests"""

    def test_get_hotel_stats_as_owner(self, client, owner_token, sample_hotel):
        """Test getting hotel statistics as owner"""
        response = client.get(f'/api/hotels/{sample_hotel.id}/stats',
            headers={'Authorization': f'Bearer {owner_token}'}
        )
        
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        if response.status_code == HTTPStatus.OK:
            data = response.json['data']
            assert 'occupancy_rate' in data or 'total_bookings' in data

    def test_get_hotel_stats_unauthorized(self, client, sample_hotel):
        """Test getting hotel stats without auth"""
        response = client.get(f'/api/hotels/{sample_hotel.id}/stats')
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED
