import pytest
from src.domain.exceptions import (
    DomainError, ClientNotFoundError, ClientAlreadyExistsError, InvalidClientDataError
)


class TestDomainExceptions:
    def test_domain_error_is_exception(self):
        # Act & Assert
        assert issubclass(DomainError, Exception)

    def test_client_not_found_error_with_id(self):
        # Arrange
        client_id = 123
        
        # Act
        error = ClientNotFoundError(client_id=client_id)
        
        # Assert
        assert str(error) == "Client with id 123 not found"
        assert isinstance(error, DomainError)

    def test_client_not_found_error_with_email(self):
        # Arrange
        email = "test@email.com"
        
        # Act
        error = ClientNotFoundError(email=email)
        
        # Assert
        assert str(error) == "Client with email test@email.com not found"
        assert isinstance(error, DomainError)

    def test_client_not_found_error_without_params(self):
        # Act
        error = ClientNotFoundError()
        
        # Assert
        assert str(error) == "Client not found"
        assert isinstance(error, DomainError)

    def test_client_already_exists_error(self):
        # Arrange
        email = "existing@email.com"
        
        # Act
        error = ClientAlreadyExistsError(email)
        
        # Assert
        assert str(error) == "Client with email existing@email.com already exists"
        assert isinstance(error, DomainError)

    def test_invalid_client_data_error(self):
        # Act & Assert
        assert issubclass(InvalidClientDataError, DomainError)