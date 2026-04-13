import pytest
from unittest.mock import Mock, MagicMock
from flask import Flask
from src.presentation.controllers import ClientController
from src.application.use_cases import (
    CreateClientUseCase, GetClientUseCase, ListClientsUseCase,
    UpdateClientUseCase, DeleteClientUseCase
)
from src.application.dtos import ClientResponse
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError
from src.main import DependencyInjector, create_app


class TestClientController:
    @pytest.fixture
    def mock_use_cases(self):
        """Create mock use cases for testing"""
        return {
            'create': Mock(spec=CreateClientUseCase),
            'get': Mock(spec=GetClientUseCase),
            'list': Mock(spec=ListClientsUseCase),
            'update': Mock(spec=UpdateClientUseCase),
            'delete': Mock(spec=DeleteClientUseCase)
        }

    @pytest.fixture
    def controller(self, mock_use_cases):
        """Create controller with mocked use cases"""
        return ClientController(
            create_client_use_case=mock_use_cases['create'],
            get_client_use_case=mock_use_cases['get'],
            list_clients_use_case=mock_use_cases['list'],
            update_client_use_case=mock_use_cases['update'],
            delete_client_use_case=mock_use_cases['delete']
        )

    @pytest.fixture
    def sample_response(self):
        """Sample client response for tests"""
        return ClientResponse(
            id=1,
            name="João Silva",
            email="joao@email.com", 
            phone="11999999999",
            created_at="2023-01-01T12:00:00"
        )

    def test_create_client_success(self, controller, mock_use_cases, sample_response):
        # Arrange
        mock_use_cases['create'].execute.return_value = sample_response
        
        with Flask(__name__).test_request_context(
            '/api/clients',
            method='POST',
            json={'name': 'João Silva', 'email': 'joao@email.com', 'phone': '11999999999'}
        ):
            # Act
            result, status_code = controller.create_client()
        
        # Assert
        assert status_code == 201
        assert result['message'] == 'Client created successfully'
        assert result['client']['id'] == 1
        assert result['client']['name'] == 'João Silva'

    def test_create_client_empty_body(self, controller):
        # Arrange & Act
        with Flask(__name__).test_request_context('/api/clients', method='POST'):
            result, status_code = controller.create_client()
        
        # Assert
        assert status_code == 400
        assert 'Request body is required' in result['error']

    def test_create_client_already_exists(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['create'].execute.side_effect = ClientAlreadyExistsError("joao@email.com")
        
        with Flask(__name__).test_request_context(
            '/api/clients',
            method='POST',
            json={'name': 'João Silva', 'email': 'joao@email.com'}
        ):
            # Act
            result, status_code = controller.create_client()
        
        # Assert
        assert status_code == 409
        assert 'already exists' in result['error']

    def test_create_client_validation_error(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['create'].execute.side_effect = ValueError("Invalid email format")
        
        with Flask(__name__).test_request_context(
            '/api/clients',
            method='POST',
            json={'name': 'João', 'email': 'invalid-email'}
        ):
            # Act
            result, status_code = controller.create_client()
        
        # Assert
        assert status_code == 400
        assert 'Invalid email format' in result['error']

    def test_create_client_internal_error(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['create'].execute.side_effect = Exception("Database error")
        
        with Flask(__name__).test_request_context(
            '/api/clients',
            method='POST',
            json={'name': 'João', 'email': 'joao@email.com'}
        ):
            # Act
            result, status_code = controller.create_client()
        
        # Assert
        assert status_code == 500
        assert result['error'] == 'Internal server error'

    def test_get_client_success(self, controller, mock_use_cases, sample_response):
        # Arrange
        mock_use_cases['get'].execute.return_value = sample_response
        
        # Act
        result, status_code = controller.get_client(1)
        
        # Assert
        assert status_code == 200
        assert result['client']['id'] == 1
        assert result['client']['name'] == 'João Silva'

    def test_get_client_not_found(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['get'].execute.side_effect = ClientNotFoundError(client_id=999)
        
        # Act
        result, status_code = controller.get_client(999)
        
        # Assert
        assert status_code == 404
        assert 'not found' in result['error']

    def test_list_clients_success(self, controller, mock_use_cases, sample_response):
        # Arrange
        mock_use_cases['list'].execute.return_value = [sample_response]
        
        with Flask(__name__).test_request_context('/api/clients?page=1&per_page=10'):
            # Act
            result, status_code = controller.list_clients()
        
        # Assert
        assert status_code == 200
        assert len(result['clients']) == 1
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 10

    def test_list_clients_default_pagination(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['list'].execute.return_value = []
        
        with Flask(__name__).test_request_context('/api/clients'):
            # Act
            result, status_code = controller.list_clients()
        
        # Assert
        assert status_code == 200
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 10

    def test_update_client_success(self, controller, mock_use_cases, sample_response):
        # Arrange
        mock_use_cases['update'].execute.return_value = sample_response
        
        with Flask(__name__).test_request_context(
            '/api/clients/1',
            method='PUT',
            json={'name': 'João da Silva'}
        ):
            # Act
            result, status_code = controller.update_client(1)
        
        # Assert
        assert status_code == 200
        assert result['message'] == 'Client updated successfully'
        assert result['client']['id'] == 1

    def test_update_client_not_found(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['update'].execute.side_effect = ClientNotFoundError(client_id=999)
        
        with Flask(__name__).test_request_context(
            '/api/clients/999',
            method='PUT',
            json={'name': 'João da Silva'}
        ):
            # Act
            result, status_code = controller.update_client(999)
        
        # Assert
        assert status_code == 404
        assert 'not found' in result['error']

    def test_update_client_empty_body(self, controller):
        # Arrange & Act
        with Flask(__name__).test_request_context('/api/clients/1', method='PUT'):
            result, status_code = controller.update_client(1)
        
        # Assert
        assert status_code == 400
        assert 'Request body is required' in result['error']

    def test_delete_client_success(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['delete'].execute.return_value = True
        
        # Act
        result, status_code = controller.delete_client(1)
        
        # Assert
        assert status_code == 204
        assert result['message'] == 'Client deleted successfully'

    def test_delete_client_not_found(self, controller, mock_use_cases):
        # Arrange
        mock_use_cases['delete'].execute.side_effect = ClientNotFoundError(client_id=999)
        
        # Act
        result, status_code = controller.delete_client(999)
        
        # Assert
        assert status_code == 404
        assert 'not found' in result['error']


class TestDependencyInjector:
    def test_dependency_injector_initialization(self):
        # Act
        di = DependencyInjector(is_test=True)
        
        # Assert
        assert di.database is not None
        
        # Cleanup
        di.database.close()

    def test_get_client_repository(self):
        # Arrange
        di = DependencyInjector(is_test=True)
        
        # Act
        repository = di.get_client_repository()
        
        # Assert
        assert repository is not None
        
        # Cleanup
        di.database.close()

    def test_get_client_controller(self):
        # Arrange
        di = DependencyInjector(is_test=True)
        
        # Act
        controller = di.get_client_controller()
        
        # Assert
        assert controller is not None
        assert hasattr(controller, '_create_client_use_case')
        assert hasattr(controller, '_get_client_use_case')
        assert hasattr(controller, '_list_clients_use_case')
        assert hasattr(controller, '_update_client_use_case')
        assert hasattr(controller, '_delete_client_use_case')
        
        # Cleanup
        di.database.close()


class TestCreateApp:
    def test_create_app_test_mode(self):
        # Act
        app = create_app(is_test=True)
        
        # Assert
        assert app is not None
        assert isinstance(app, Flask)

    def test_create_app_production_mode(self):
        # Act
        app = create_app(is_test=False)
        
        # Assert
        assert app is not None
        assert isinstance(app, Flask)

    def test_health_check_endpoint(self):
        # Arrange
        app = create_app(is_test=True)
        client = app.test_client()
        
        # Act
        response = client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'