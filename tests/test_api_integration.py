import pytest
import json
from sqlalchemy import create_engine
from src.main import create_app
from src.infrastructure.database import Base


@pytest.fixture(scope="function")
def app():
    """Create test app with test database"""
    # Create test app with SQLite in memory
    app = create_app(is_test=True)
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def client(app):
    """Test client for making HTTP requests"""
    return app.test_client()


@pytest.fixture(autouse=True)
def setup_database(app):
    """Setup and teardown database for each test"""
    with app.app_context():
        # Tables are created automatically in the app factory
        yield
        # No need for explicit cleanup with SQLite in memory


class TestClientAPI:
    def test_health_check(self, client):
        # Act
        response = client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_create_client_with_valid_data(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Act
        response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Client created successfully'
        assert data['client']['name'] == 'João Silva'
        assert data['client']['email'] == 'joao.silva@email.com'
        assert data['client']['phone'] == '11999999999'
        assert data['client']['id'] is not None

    def test_create_client_without_phone(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com'
        }
        
        # Act
        response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['client']['phone'] is None

    def test_create_client_with_invalid_data(self, client):
        # Arrange
        client_data = {
            'name': '',
            'email': 'invalid-email'
        }
        
        # Act
        response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_client_with_existing_email(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Create first client
        client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        # Try to create another client with same email
        client_data['name'] = 'Maria Santos'
        
        # Act
        response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_get_client_by_id(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Create client first
        create_response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        client_id = json.loads(create_response.data)['client']['id']
        
        # Act
        response = client.get(f'/api/clients/{client_id}')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['client']['id'] == client_id
        assert data['client']['name'] == 'João Silva'
        assert data['client']['email'] == 'joao.silva@email.com'

    def test_get_nonexistent_client(self, client):
        # Act
        response = client.get('/api/clients/999')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_list_clients(self, client):
        # Arrange
        clients_data = [
            {'name': 'João Silva', 'email': 'joao@email.com', 'phone': '11999999999'},
            {'name': 'Maria Santos', 'email': 'maria@email.com', 'phone': '11888888888'}
        ]
        
        # Create clients
        for client_data in clients_data:
            client.post(
                '/api/clients',
                data=json.dumps(client_data),
                content_type='application/json'
            )
        
        # Act
        response = client.get('/api/clients')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['clients']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10

    def test_list_clients_with_pagination(self, client):
        # Arrange
        clients_data = [
            {'name': f'Client {i}', 'email': f'client{i}@email.com'} 
            for i in range(1, 16)  # 15 clients
        ]
        
        # Create clients
        for client_data in clients_data:
            client.post(
                '/api/clients',
                data=json.dumps(client_data),
                content_type='application/json'
            )
        
        # Act
        response = client.get('/api/clients?page=2&per_page=5')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['clients']) == 5
        assert data['pagination']['page'] == 2
        assert data['pagination']['per_page'] == 5

    def test_update_client(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Create client first
        create_response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        client_id = json.loads(create_response.data)['client']['id']
        
        # Update data
        update_data = {
            'name': 'João da Silva',
            'email': 'joao.dasilva@email.com',
            'phone': '11888888888'
        }
        
        # Act
        response = client.put(
            f'/api/clients/{client_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Client updated successfully'
        assert data['client']['name'] == 'João da Silva'
        assert data['client']['email'] == 'joao.dasilva@email.com'
        assert data['client']['phone'] == '11888888888'

    def test_update_nonexistent_client(self, client):
        # Arrange
        update_data = {'name': 'João da Silva'}
        
        # Act
        response = client.put(
            '/api/clients/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error']

    def test_partial_update_client(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Create client first
        create_response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        client_id = json.loads(create_response.data)['client']['id']
        
        # Update only name
        update_data = {'name': 'João da Silva'}
        
        # Act
        response = client.put(
            f'/api/clients/{client_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['client']['name'] == 'João da Silva'
        assert data['client']['email'] == 'joao.silva@email.com'  # Unchanged
        assert data['client']['phone'] == '11999999999'  # Unchanged

    def test_delete_client(self, client):
        # Arrange
        client_data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com',
            'phone': '11999999999'
        }
        
        # Create client first
        create_response = client.post(
            '/api/clients',
            data=json.dumps(client_data),
            content_type='application/json'
        )
        client_id = json.loads(create_response.data)['client']['id']
        
        # Act
        response = client.delete(f'/api/clients/{client_id}')
        
        # Assert
        assert response.status_code == 204
        
        # Verify client is deleted
        get_response = client.get(f'/api/clients/{client_id}')
        assert get_response.status_code == 404

    def test_delete_nonexistent_client(self, client):
        # Act
        response = client.delete('/api/clients/999')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error']