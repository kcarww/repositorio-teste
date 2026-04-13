import pytest
from unittest.mock import Mock, patch, create_autospec
from src.presentation.controllers import ClientController
from src.application.use_cases import CreateClientUseCase, GetClientUseCase
from src.main import DependencyInjector, create_app
from src.application.dtos import ClientResponse
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError


class TestMainCoverage:
    """Tests to improve main.py coverage"""
    
    def test_dependency_injector_initialization(self):
        # Act
        di = DependencyInjector(is_test=True)
        
        # Assert
        assert di.database is not None
        di.database.close()

    def test_dependency_injector_get_methods(self):
        # Arrange
        di = DependencyInjector(is_test=True)
        
        # Act
        repository = di.get_client_repository()
        controller = di.get_client_controller()
        
        # Assert
        assert repository is not None
        assert controller is not None
        
        # Cleanup
        di.database.close()

    def test_create_app_health_endpoint(self):
        # Arrange
        app = create_app(is_test=True)
        
        # Act
        with app.test_client() as client:
            response = client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_create_app_creates_blueprint(self):
        # Act
        app = create_app(is_test=True)
        
        # Assert
        assert app is not None
        # Verify blueprint is registered
        assert any('clients' in rule.rule for rule in app.url_map.iter_rules())


class TestRoutesCoverage:
    """Tests to improve routes.py coverage"""
    
    def test_client_routes_creation(self):
        # Arrange
        from src.presentation.routes import create_client_routes
        from src.presentation.controllers import ClientController
        from unittest.mock import Mock
        
        mock_controller = Mock(spec=ClientController)
        
        # Act
        blueprint = create_client_routes(mock_controller)
        
        # Assert
        assert blueprint is not None
        assert blueprint.name == 'clients'
        assert blueprint.url_prefix == '/api/clients'

    def test_routes_endpoints_exist(self):
        # Arrange
        app = create_app(is_test=True)
        
        # Act & Assert
        with app.app_context():
            rules = list(app.url_map.iter_rules())
            endpoint_rules = [rule.rule for rule in rules]
            
            # Check that our API endpoints exist
            assert any('/api/clients' in rule for rule in endpoint_rules)
            assert any('/health' in rule for rule in endpoint_rules)


class TestControllerErrorHandling:
    """Tests to improve controller error handling coverage"""
    
    def test_controller_create_none_request_body(self):
        # Arrange
        mock_use_cases = {
            'create': Mock(),
            'get': Mock(),  
            'list': Mock(),
            'update': Mock(),
            'delete': Mock()
        }
        
        controller = ClientController(
            create_client_use_case=mock_use_cases['create'],
            get_client_use_case=mock_use_cases['get'],
            list_clients_use_case=mock_use_cases['list'],
            update_client_use_case=mock_use_cases['update'],
            delete_client_use_case=mock_use_cases['delete']
        )
        
        # Act & Assert
        # Test error handling code paths
        app = create_app(is_test=True)
        with app.test_request_context('/api/clients', method='POST', json=None):
            result, status_code = controller.create_client()
            assert status_code == 400  # Empty body error

    def test_app_registration_coverage(self):
        # Arrange & Act
        app = create_app(is_test=True)
        
        # Assert - Test that CORS is enabled and routes are registered
        assert app is not None
        
        # Test that our endpoints are accessible
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200
            
            # Test that client endpoints exist (will get 400/404 but endpoint exists)
            response = client.post('/api/clients', json={})
            assert response.status_code in [400, 422]  # Bad request but endpoint exists


class TestRepositoryErrorHandling:
    """Tests to improve repository error handling"""
    
    def test_repository_update_with_duplicate_email(self):
        # This test covers the integrity error handling in update method
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.infrastructure.database import Base
        from src.infrastructure.repositories import SQLAlchemyClientRepository
        from src.infrastructure.models import ClientModel
        from src.domain.client import Client
        
        # Arrange
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        repository = SQLAlchemyClientRepository(session)
        
        # Create two clients
        client1 = Client("João", "joao@email.com", "11999999999")
        client2 = Client("Maria", "maria@email.com", "11888888888")
        
        saved_client1 = repository.save(client1)
        saved_client2 = repository.save(client2)
        
        # Act - Try to update client2 with client1's email
        saved_client2.update_email("joao@email.com")
        
        # Assert - Should raise ClientAlreadyExistsError
        from src.domain.exceptions import ClientAlreadyExistsError
        with pytest.raises(ClientAlreadyExistsError):
            repository.update(saved_client2)
        
        session.close()

    def test_database_close_method(self):
        # Test the close method of Database class
        from src.infrastructure.database import Database
        
        # Arrange
        db = Database(is_test=True)
        
        # Act
        db.close()  # This should not raise any error
        
        # Assert - if we get here, close() worked