class DomainError(Exception):
    """Base exception for domain errors"""
    pass


class ClientNotFoundError(DomainError):
    """Raised when a client is not found"""
    def __init__(self, client_id: int = None, email: str = None):
        if client_id:
            message = f"Client with id {client_id} not found"
        elif email:
            message = f"Client with email {email} not found"
        else:
            message = "Client not found"
        super().__init__(message)


class ClientAlreadyExistsError(DomainError):
    """Raised when trying to create a client that already exists"""
    def __init__(self, email: str):
        message = f"Client with email {email} already exists"
        super().__init__(message)


class InvalidClientDataError(DomainError):
    """Raised when client data is invalid"""
    pass