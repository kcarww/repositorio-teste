from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.client import Client


class ClientRepository(ABC):
    """Abstract repository for client operations"""

    @abstractmethod
    def save(self, client: Client) -> Client:
        """Save a client and return the saved client with ID"""
        pass

    @abstractmethod
    def find_by_id(self, client_id: int) -> Optional[Client]:
        """Find a client by ID"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Client]:
        """Find a client by email"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Client]:
        """Find all clients with pagination"""
        pass

    @abstractmethod
    def update(self, client: Client) -> Client:
        """Update a client"""
        pass

    @abstractmethod
    def delete_by_id(self, client_id: int) -> bool:
        """Delete a client by ID, returns True if deleted, False if not found"""
        pass

    @abstractmethod
    def exists_by_email(self, email: str, exclude_id: int = None) -> bool:
        """Check if a client with email exists, optionally excluding a specific ID"""
        pass