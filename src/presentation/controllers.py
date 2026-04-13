from flask import request, jsonify
from typing import Dict, Any, Tuple
from src.application.use_cases import (
    CreateClientUseCase, GetClientUseCase, ListClientsUseCase, 
    UpdateClientUseCase, DeleteClientUseCase
)
from src.application.dtos import (
    CreateClientRequest, UpdateClientRequest, PaginationRequest
)
from src.domain.exceptions import (
    ClientNotFoundError, ClientAlreadyExistsError, DomainError
)


class ClientController:
    def __init__(
        self,
        create_client_use_case: CreateClientUseCase,
        get_client_use_case: GetClientUseCase,
        list_clients_use_case: ListClientsUseCase,
        update_client_use_case: UpdateClientUseCase,
        delete_client_use_case: DeleteClientUseCase
    ):
        self._create_client_use_case = create_client_use_case
        self._get_client_use_case = get_client_use_case
        self._list_clients_use_case = list_clients_use_case
        self._update_client_use_case = update_client_use_case
        self._delete_client_use_case = delete_client_use_case

    def create_client(self) -> Tuple[Dict[str, Any], int]:
        try:
            try:
                data = request.get_json()
            except Exception:
                return {'error': 'Request body is required'}, 400
                
            if data is None or (isinstance(data, dict) and not data):
                return {'error': 'Request body is required'}, 400

            request_dto = CreateClientRequest(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone')
            )

            response = self._create_client_use_case.execute(request_dto)
            
            return {
                'message': 'Client created successfully',
                'client': {
                    'id': response.id,
                    'name': response.name,
                    'email': response.email,
                    'phone': response.phone,
                    'created_at': response.created_at
                }
            }, 201

        except ClientAlreadyExistsError as e:
            return {'error': str(e)}, 409
        except ValueError as e:
            return {'error': str(e)}, 400
        except DomainError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error'}, 500

    def get_client(self, client_id: int) -> Tuple[Dict[str, Any], int]:
        try:
            response = self._get_client_use_case.execute(client_id)
            
            return {
                'client': {
                    'id': response.id,
                    'name': response.name,
                    'email': response.email,
                    'phone': response.phone,
                    'created_at': response.created_at
                }
            }, 200

        except ClientNotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Internal server error'}, 500

    def list_clients(self) -> Tuple[Dict[str, Any], int]:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            pagination = PaginationRequest(page=page, per_page=per_page)
            clients = self._list_clients_use_case.execute(pagination)

            return {
                'clients': [
                    {
                        'id': client.id,
                        'name': client.name,
                        'email': client.email,
                        'phone': client.phone,
                        'created_at': client.created_at
                    }
                    for client in clients
                ],
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_items': len(clients)
                }
            }, 200

        except Exception as e:
            return {'error': 'Internal server error'}, 500

    def update_client(self, client_id: int) -> Tuple[Dict[str, Any], int]:
        try:
            try:
                data = request.get_json()
            except Exception:
                return {'error': 'Request body is required'}, 400
                
            if data is None or (isinstance(data, dict) and not data):
                return {'error': 'Request body is required'}, 400

            request_dto = UpdateClientRequest(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone')
            )

            response = self._update_client_use_case.execute(client_id, request_dto)
            
            return {
                'message': 'Client updated successfully',
                'client': {
                    'id': response.id,
                    'name': response.name,
                    'email': response.email,
                    'phone': response.phone,
                    'created_at': response.created_at
                }
            }, 200

        except ClientNotFoundError as e:
            return {'error': str(e)}, 404
        except ClientAlreadyExistsError as e:
            return {'error': str(e)}, 409
        except ValueError as e:
            return {'error': str(e)}, 400
        except DomainError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error'}, 500

    def delete_client(self, client_id: int) -> Tuple[Dict[str, Any], int]:
        try:
            self._delete_client_use_case.execute(client_id)
            return {'message': 'Client deleted successfully'}, 204

        except ClientNotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Internal server error'}, 500