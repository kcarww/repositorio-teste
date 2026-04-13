from typing import Optional
from dataclasses import dataclass


@dataclass
class CreateClientRequest:
    name: str
    email: str
    phone: Optional[str] = None

    def __post_init__(self):
        if self.name:
            self.name = self.name.strip()
        if self.email:
            self.email = self.email.strip()
        if self.phone:
            self.phone = self.phone.strip()


@dataclass
class UpdateClientRequest:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if self.name:
            self.name = self.name.strip()
        if self.email:
            self.email = self.email.strip()
        if self.phone:
            self.phone = self.phone.strip()


@dataclass
class ClientResponse:
    id: int
    name: str
    email: str
    phone: Optional[str]
    created_at: str


@dataclass
class PaginationRequest:
    page: int = 1
    per_page: int = 10

    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.per_page < 1:
            self.per_page = 10
        if self.per_page > 100:
            self.per_page = 100

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page