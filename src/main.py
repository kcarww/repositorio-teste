from flask import Flask
from flask_cors import CORS
from src.infrastructure.database import Database
from src.infrastructure.repositories import SQLAlchemyClientRepository
from src.application.use_cases import (
    CreateClientUseCase, GetClientUseCase, ListClientsUseCase,
    UpdateClientUseCase, DeleteClientUseCase
)
from src.presentation.controllers import ClientController
from src.presentation.routes import create_client_routes


class DependencyInjector:
    def __init__(self, is_test: bool = False):
        self.database = Database(is_test=is_test)
        self.database.create_tables()
        
    def get_client_repository(self):
        session = self.database.get_session()
        return SQLAlchemyClientRepository(session)
    
    def get_client_controller(self):
        repository = self.get_client_repository()
        
        create_client_use_case = CreateClientUseCase(repository)
        get_client_use_case = GetClientUseCase(repository)
        list_clients_use_case = ListClientsUseCase(repository)
        update_client_use_case = UpdateClientUseCase(repository)
        delete_client_use_case = DeleteClientUseCase(repository)
        
        return ClientController(
            create_client_use_case=create_client_use_case,
            get_client_use_case=get_client_use_case,
            list_clients_use_case=list_clients_use_case,
            update_client_use_case=update_client_use_case,
            delete_client_use_case=delete_client_use_case
        )


def create_app(is_test: bool = False) -> Flask:
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Dependency injection
    di = DependencyInjector(is_test=is_test)
    client_controller = di.get_client_controller()
    
    # Register routes
    client_routes = create_client_routes(client_controller)
    app.register_blueprint(client_routes)
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)