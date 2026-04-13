import pytest
from datetime import datetime
from src.domain.client import Client


class TestClient:
    def test_create_client_with_valid_data(self):
        # Arrange
        name = "João Silva"
        email = "joao.silva@email.com"
        phone = "11999999999"
        
        # Act
        client = Client(name=name, email=email, phone=phone)
        
        # Assert
        assert client.name == name
        assert client.email == email
        assert client.phone == phone
        assert client.id is None
        assert isinstance(client.created_at, datetime)

    def test_create_client_without_phone(self):
        # Arrange
        name = "João Silva"
        email = "joao.silva@email.com"
        
        # Act
        client = Client(name=name, email=email)
        
        # Assert
        assert client.name == name
        assert client.email == email
        assert client.phone is None

    def test_create_client_with_id_and_created_at(self):
        # Arrange
        name = "João Silva"
        email = "joao.silva@email.com"
        client_id = 1
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        client = Client(
            name=name, 
            email=email, 
            client_id=client_id, 
            created_at=created_at
        )
        
        # Assert
        assert client.id == client_id
        assert client.created_at == created_at

    def test_create_client_with_empty_name_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Client(name="", email="joao@email.com")

    def test_create_client_with_none_name_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Client(name=None, email="joao@email.com")

    def test_create_client_with_long_name_raises_error(self):
        # Arrange
        long_name = "a" * 121
        
        # Act & Assert
        with pytest.raises(ValueError, match="Name cannot exceed 120 characters"):
            Client(name=long_name, email="joao@email.com")

    def test_create_client_with_empty_email_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Client(name="João", email="")

    def test_create_client_with_invalid_email_raises_error(self):
        # Arrange
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user.domain.com",
            "user@domain"
        ]
        
        # Act & Assert
        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Client(name="João", email=invalid_email)

    def test_create_client_with_long_email_raises_error(self):
        # Arrange
        long_email = "a" * 115 + "@email.com"  # 115 + 10 = 125 characters
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email cannot exceed 120 characters"):
            Client(name="João", email=long_email)

    def test_create_client_with_long_phone_raises_error(self):
        # Arrange
        long_phone = "1" * 31
        
        # Act & Assert
        with pytest.raises(ValueError, match="Phone cannot exceed 30 characters"):
            Client(name="João", email="joao@email.com", phone=long_phone)

    def test_update_name(self):
        # Arrange
        client = Client(name="João", email="joao@email.com")
        new_name = "João Silva"
        
        # Act
        client.update_name(new_name)
        
        # Assert
        assert client.name == new_name

    def test_update_email(self):
        # Arrange
        client = Client(name="João", email="joao@email.com")
        new_email = "joao.silva@email.com"
        
        # Act
        client.update_email(new_email)
        
        # Assert
        assert client.email == new_email

    def test_update_phone(self):
        # Arrange
        client = Client(name="João", email="joao@email.com")
        new_phone = "11999999999"
        
        # Act
        client.update_phone(new_phone)
        
        # Assert
        assert client.phone == new_phone

    def test_to_dict(self):
        # Arrange
        client_id = 1
        name = "João Silva"
        email = "joao@email.com"
        phone = "11999999999"
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        client = Client(
            name=name,
            email=email,
            phone=phone,
            client_id=client_id,
            created_at=created_at
        )
        
        # Act
        result = client.to_dict()
        
        # Assert
        expected = {
            'id': client_id,
            'name': name,
            'email': email,
            'phone': phone,
            'created_at': created_at.isoformat()
        }
        assert result == expected

    def test_equality(self):
        # Arrange
        client1 = Client(name="João", email="joao@email.com", client_id=1)
        client2 = Client(name="João", email="joao@email.com", client_id=1)
        client3 = Client(name="Maria", email="maria@email.com", client_id=2)
        
        # Act & Assert
        assert client1 == client2
        assert client1 != client3
        assert client1 != "not a client"

    def test_string_representation(self):
        # Arrange
        client = Client(name="João Silva", email="joao@email.com", client_id=1)
        
        # Act
        result = str(client)
        
        # Assert
        expected = "Client(id=1, name=João Silva, email=joao@email.com)"
        assert result == expected

    def test_name_is_trimmed(self):
        # Arrange & Act
        client = Client(name="  João Silva  ", email="joao@email.com")
        
        # Assert
        assert client.name == "João Silva"

    def test_email_is_trimmed(self):
        # Arrange & Act
        client = Client(name="João", email="  joao@email.com  ")
        
        # Assert
        assert client.email == "joao@email.com"

    def test_phone_is_trimmed(self):
        # Arrange & Act
        client = Client(name="João", email="joao@email.com", phone="  11999999999  ")
        
        # Assert
        assert client.phone == "11999999999"