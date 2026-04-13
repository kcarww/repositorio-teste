import pytest
from datetime import datetime
from src.domain.client import Client


@pytest.fixture
def valid_client_data():
    return {
        'name': 'João Silva',
        'email': 'joao.silva@email.com',
        'phone': '11999999999'
    }


@pytest.fixture
def client_entity(valid_client_data):
    return Client(
        name=valid_client_data['name'],
        email=valid_client_data['email'],
        phone=valid_client_data['phone'],
        client_id=1,
        created_at=datetime(2023, 1, 1, 12, 0, 0)
    )


@pytest.fixture
def client_entity_list():
    return [
        Client(
            name='João Silva',
            email='joao@email.com',
            phone='11999999999',
            client_id=1,
            created_at=datetime(2023, 1, 1, 12, 0, 0)
        ),
        Client(
            name='Maria Santos',
            email='maria@email.com',
            phone='11888888888',
            client_id=2,
            created_at=datetime(2023, 1, 2, 12, 0, 0)
        )
    ]