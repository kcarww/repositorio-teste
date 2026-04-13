from typing import List
from src.application.interfaces.client_repository import ClientRepository
from src.application.dtos import (
    CreateClientRequest, UpdateClientRequest, ClientResponse, PaginationRequest
)
from src.domain.client import Client
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError


class CreateClientUseCase:
    def __init__(self, client_repository: ClientRepository):
        self._client_repository = client_repository

    def execute(self, request: CreateClientRequest) -> ClientResponse:
        # Check if client already exists
        if self._client_repository.exists_by_email(request.email):
            raise ClientAlreadyExistsError(request.email)

        # Create client entity
        client = Client(
            name=request.name,
            email=request.email,
            phone=request.phone
        )

        # Save client
        saved_client = self._client_repository.save(client)

        # Return response
        return self._to_response(saved_client)

    def _to_response(self, client: Client) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            created_at=client.created_at.isoformat()
        )


class GetClientUseCase:
    def __init__(self, client_repository: ClientRepository):
        self._client_repository = client_repository

    def execute(self, client_id: int) -> ClientResponse:
        client = self._client_repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id=client_id)

        return self._to_response(client)

    def _to_response(self, client: Client) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            created_at=client.created_at.isoformat()
        )


class ListClientsUseCase:
    def __init__(self, client_repository: ClientRepository):
        self._client_repository = client_repository

    def execute(self, pagination: PaginationRequest) -> List[ClientResponse]:
        clients = self._client_repository.find_all(
            limit=pagination.limit,
            offset=pagination.offset
        )

        return [self._to_response(client) for client in clients]

    def _to_response(self, client: Client) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            created_at=client.created_at.isoformat()
        )


class UpdateClientUseCase:
    def __init__(self, client_repository: ClientRepository):
        self._client_repository = client_repository

    def execute(self, client_id: int, request: UpdateClientRequest) -> ClientResponse:
        # Find existing client
        client = self._client_repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id=client_id)

        # Check if email is already taken by another client
        if request.email and request.email != client.email:
            if self._client_repository.exists_by_email(request.email, exclude_id=client_id):
                raise ClientAlreadyExistsError(request.email)

        # Update client fields
        if request.name is not None:
            client.update_name(request.name)
        if request.email is not None:
            client.update_email(request.email)
        if request.phone is not None:
            client.update_phone(request.phone)

        # Save updated client
        updated_client = self._client_repository.update(client)

        return self._to_response(updated_client)

    def _to_response(self, client: Client) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            created_at=client.created_at.isoformat()
        )


class DeleteClientUseCase:
    def __init__(self, client_repository: ClientRepository):
        self._client_repository = client_repository

    def execute(self, client_id: int) -> bool:
        # Check if client exists
        client = self._client_repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id=client_id)

        return self._client_repository.delete_by_id(client_id)