import pytest
from src.application.dtos import (
    CreateClientRequest, UpdateClientRequest, ClientResponse, PaginationRequest
)
from datetime import datetime


class TestCreateClientRequest:
    def test_create_with_all_fields(self):
        # Act
        request = CreateClientRequest(
            name="João Silva",
            email="joao@email.com",
            phone="11999999999"
        )
        
        # Assert
        assert request.name == "João Silva"
        assert request.email == "joao@email.com"
        assert request.phone == "11999999999"

    def test_create_without_phone(self):
        # Act
        request = CreateClientRequest(
            name="João Silva",
            email="joao@email.com"
        )
        
        # Assert
        assert request.name == "João Silva"
        assert request.email == "joao@email.com"
        assert request.phone is None

    def test_trim_whitespace(self):
        # Act
        request = CreateClientRequest(
            name="  João Silva  ",
            email="  joao@email.com  ",
            phone="  11999999999  "
        )
        
        # Assert
        assert request.name == "João Silva"
        assert request.email == "joao@email.com"
        assert request.phone == "11999999999"


class TestUpdateClientRequest:
    def test_create_with_all_fields(self):
        # Act
        request = UpdateClientRequest(
            name="João Silva",
            email="joao@email.com",
            phone="11999999999"
        )
        
        # Assert
        assert request.name == "João Silva"
        assert request.email == "joao@email.com"
        assert request.phone == "11999999999"

    def test_create_with_no_fields(self):
        # Act
        request = UpdateClientRequest()
        
        # Assert
        assert request.name is None
        assert request.email is None
        assert request.phone is None

    def test_trim_whitespace(self):
        # Act
        request = UpdateClientRequest(
            name="  João Silva  ",
            email="  joao@email.com  ",
            phone="  11999999999  "
        )
        
        # Assert
        assert request.name == "João Silva"
        assert request.email == "joao@email.com"
        assert request.phone == "11999999999"


class TestClientResponse:
    def test_create_response(self):
        # Act
        response = ClientResponse(
            id=1,
            name="João Silva",
            email="joao@email.com",
            phone="11999999999",
            created_at="2023-01-01T12:00:00"
        )
        
        # Assert
        assert response.id == 1
        assert response.name == "João Silva"
        assert response.email == "joao@email.com"
        assert response.phone == "11999999999"
        assert response.created_at == "2023-01-01T12:00:00"

    def test_create_response_without_phone(self):
        # Act
        response = ClientResponse(
            id=1,
            name="João Silva",
            email="joao@email.com",
            phone=None,
            created_at="2023-01-01T12:00:00"
        )
        
        # Assert
        assert response.phone is None


class TestPaginationRequest:
    def test_create_with_valid_params(self):
        # Act
        pagination = PaginationRequest(page=2, per_page=20)
        
        # Assert
        assert pagination.page == 2
        assert pagination.per_page == 20
        assert pagination.offset == 20
        assert pagination.limit == 20

    def test_create_with_default_params(self):
        # Act
        pagination = PaginationRequest()
        
        # Assert
        assert pagination.page == 1
        assert pagination.per_page == 10
        assert pagination.offset == 0
        assert pagination.limit == 10

    def test_invalid_page_should_default_to_1(self):
        # Act
        pagination = PaginationRequest(page=0)
        
        # Assert
        assert pagination.page == 1

    def test_invalid_per_page_should_default_to_10(self):
        # Act
        pagination = PaginationRequest(per_page=0)
        
        # Assert
        assert pagination.per_page == 10

    def test_per_page_over_100_should_limit_to_100(self):
        # Act
        pagination = PaginationRequest(per_page=200)
        
        # Assert
        assert pagination.per_page == 100

    def test_offset_calculation(self):
        # Arrange & Act
        test_cases = [
            (1, 10, 0),
            (2, 10, 10),
            (3, 5, 10),
            (5, 20, 80)
        ]
        
        for page, per_page, expected_offset in test_cases:
            pagination = PaginationRequest(page=page, per_page=per_page)
            assert pagination.offset == expected_offset