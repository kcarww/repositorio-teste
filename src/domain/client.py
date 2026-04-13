from datetime import datetime
from typing import Optional
import re


class Client:
    def __init__(
        self,
        name: str,
        email: str,
        phone: Optional[str] = None,
        client_id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = client_id
        self._name = self._validate_name(name)
        self._email = self._validate_email(email)
        self._phone = self._validate_phone(phone) if phone else None
        self._created_at = created_at or datetime.now()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def update_name(self, name: str) -> None:
        self._name = self._validate_name(name)

    def update_email(self, email: str) -> None:
        self._email = self._validate_email(email)

    def update_phone(self, phone: str) -> None:
        self._phone = self._validate_phone(phone)

    @staticmethod
    def _validate_name(name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if len(name.strip()) > 120:
            raise ValueError("Name cannot exceed 120 characters")
        return name.strip()

    @staticmethod
    def _validate_email(email: str) -> str:
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        
        email = email.strip()
        if len(email) > 120:
            raise ValueError("Email cannot exceed 120 characters")
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        
        return email

    @staticmethod
    def _validate_phone(phone: str) -> str:
        if phone and len(phone.strip()) > 30:
            raise ValueError("Phone cannot exceed 30 characters")
        return phone.strip() if phone else None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __eq__(self, other) -> bool:
        if not isinstance(other, Client):
            return False
        return self.id == other.id and self.email == other.email

    def __str__(self) -> str:
        return f"Client(id={self.id}, name={self.name}, email={self.email})"