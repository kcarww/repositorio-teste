import pytest
from unittest.mock import Mock
from datetime import datetime
from src.application.use_cases import (
    CreateClientUseCase, GetClientUseCase, ListClientsUseCase,
    UpdateClientUseCase, DeleteClientUseCase
)
from src.application.dtos import (
    CreateClientRequest, UpdateClientRequest, PaginationRequest
)
from src.application.interfaces.client_repository import ClientRepository
from src.domain.client import Client
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError


class TestCreateClientUseCase:
    def test_execute_with_valid_data_should_create_client(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.exists_by_email.return_value = False
        repository_mock.save.return_value = client_entity
        
        use_case = CreateClientUseCase(repository_mock)
        request = CreateClientRequest(
            name="João Silva",
            email="joao.silva@email.com",
            phone="11999999999"
        )
        
        # Act
        response = use_case.execute(request)
        
        # Assert
        assert response.id == 1
        assert response.name == "João Silva"
        assert response.email == "joao.silva@email.com"
        assert response.phone == "11999999999"
        repository_mock.exists_by_email.assert_called_once_with("joao.silva@email.com")
        repository_mock.save.assert_called_once()

    def test_execute_with_existing_email_should_raise_error(self):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.exists_by_email.return_value = True
        
        use_case = CreateClientUseCase(repository_mock)
        request = CreateClientRequest(
            name="João Silva",
            email="joao.silva@email.com"
        )
        
        # Act & Assert
        with pytest.raises(ClientAlreadyExistsError):
            use_case.execute(request)
        
        repository_mock.exists_by_email.assert_called_once_with("joao.silva@email.com")
        repository_mock.save.assert_not_called()


class TestGetClientUseCase:
    def test_execute_with_existing_client_should_return_client(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        
        use_case = GetClientUseCase(repository_mock)
        
        # Act
        response = use_case.execute(1)
        
        # Assert
        assert response.id == 1
        assert response.name == "João Silva"
        assert response.email == "joao.silva@email.com"
        repository_mock.find_by_id.assert_called_once_with(1)

    def test_execute_with_nonexistent_client_should_raise_error(self):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = None
        
        use_case = GetClientUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ClientNotFoundError):
            use_case.execute(999)
        
        repository_mock.find_by_id.assert_called_once_with(999)


class TestListClientsUseCase:
    def test_execute_should_return_clients_list(self, client_entity_list):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_all.return_value = client_entity_list
        
        use_case = ListClientsUseCase(repository_mock)
        pagination = PaginationRequest(page=1, per_page=10)
        
        # Act
        response = use_case.execute(pagination)
        
        # Assert
        assert len(response) == 2
        assert response[0].id == 1
        assert response[0].name == "João Silva"
        assert response[1].id == 2
        assert response[1].name == "Maria Santos"
        repository_mock.find_all.assert_called_once_with(limit=10, offset=0)

    def test_execute_with_empty_list_should_return_empty(self):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_all.return_value = []
        
        use_case = ListClientsUseCase(repository_mock)
        pagination = PaginationRequest(page=1, per_page=10)
        
        # Act
        response = use_case.execute(pagination)
        
        # Assert
        assert len(response) == 0
        repository_mock.find_all.assert_called_once_with(limit=10, offset=0)


class TestUpdateClientUseCase:
    def test_execute_with_valid_data_should_update_client(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        repository_mock.exists_by_email.return_value = False
        repository_mock.update.return_value = client_entity
        
        use_case = UpdateClientUseCase(repository_mock)
        request = UpdateClientRequest(
            name="João da Silva",
            email="joao.silva@newemail.com",
            phone="11888888888"
        )
        
        # Act
        response = use_case.execute(1, request)
        
        # Assert
        assert response.id == 1
        repository_mock.find_by_id.assert_called_once_with(1)
        repository_mock.exists_by_email.assert_called_once_with("joao.silva@newemail.com", exclude_id=1)
        repository_mock.update.assert_called_once()

    def test_execute_with_nonexistent_client_should_raise_error(self):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = None
        
        use_case = UpdateClientUseCase(repository_mock)
        request = UpdateClientRequest(name="João da Silva")
        
        # Act & Assert
        with pytest.raises(ClientNotFoundError):
            use_case.execute(999, request)
        
        repository_mock.find_by_id.assert_called_once_with(999)

    def test_execute_with_existing_email_should_raise_error(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        repository_mock.exists_by_email.return_value = True
        
        use_case = UpdateClientUseCase(repository_mock)
        request = UpdateClientRequest(email="existing@email.com")
        
        # Act & Assert
        with pytest.raises(ClientAlreadyExistsError):
            use_case.execute(1, request)

    def test_execute_with_same_email_should_not_check_existence(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        repository_mock.update.return_value = client_entity
        
        use_case = UpdateClientUseCase(repository_mock)
        request = UpdateClientRequest(email="joao.silva@email.com")  # Same email
        
        # Act
        response = use_case.execute(1, request)
        
        # Assert
        assert response.id == 1
        repository_mock.exists_by_email.assert_not_called()

    def test_execute_with_partial_update_should_update_only_provided_fields(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        repository_mock.update.return_value = client_entity
        
        use_case = UpdateClientUseCase(repository_mock)
        request = UpdateClientRequest(name="João da Silva")  # Only name
        
        # Act
        response = use_case.execute(1, request)
        
        # Assert
        assert response.id == 1
        repository_mock.update.assert_called_once()


class TestDeleteClientUseCase:
    def test_execute_with_existing_client_should_delete(self, client_entity):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = client_entity
        repository_mock.delete_by_id.return_value = True
        
        use_case = DeleteClientUseCase(repository_mock)
        
        # Act
        result = use_case.execute(1)
        
        # Assert
        assert result is True
        repository_mock.find_by_id.assert_called_once_with(1)
        repository_mock.delete_by_id.assert_called_once_with(1)

    def test_execute_with_nonexistent_client_should_raise_error(self):
        # Arrange
        repository_mock = Mock(spec=ClientRepository)
        repository_mock.find_by_id.return_value = None
        
        use_case = DeleteClientUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ClientNotFoundError):
            use_case.execute(999)
        
        repository_mock.find_by_id.assert_called_once_with(999)
        repository_mock.delete_by_id.assert_not_called()