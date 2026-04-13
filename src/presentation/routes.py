from flask import Blueprint
from src.presentation.controllers import ClientController


def create_client_routes(client_controller: ClientController) -> Blueprint:
    client_routes = Blueprint('clients', __name__, url_prefix='/api/clients')

    @client_routes.route('', methods=['POST'])
    def create_client():
        return client_controller.create_client()

    @client_routes.route('/<int:client_id>', methods=['GET'])
    def get_client(client_id: int):
        return client_controller.get_client(client_id)

    @client_routes.route('', methods=['GET'])
    def list_clients():
        return client_controller.list_clients()

    @client_routes.route('/<int:client_id>', methods=['PUT'])
    def update_client(client_id: int):
        return client_controller.update_client(client_id)

    @client_routes.route('/<int:client_id>', methods=['DELETE'])
    def delete_client(client_id: int):
        return client_controller.delete_client(client_id)

    return client_routes