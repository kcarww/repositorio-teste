import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database import Base, Database
from src.infrastructure.models import ClientModel
from src.infrastructure.repositories import SQLAlchemyClientRepository
from src.domain.client import Client
from src.domain.exceptions import ClientAlreadyExistsError


@pytest.fixture
def test_database():
    """Create test database with SQLite in memory"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    yield session
    session.close()


@pytest.fixture
def repository(test_database):
    """Create repository instance with test database"""
    return SQLAlchemyClientRepository(test_database)


@pytest.fixture
def sample_client():
    """Create a sample client for tests"""
    return Client(
        name="João Silva",
        email="joao.silva@email.com",
        phone="11999999999"
    )


class TestClientModel:
    def test_create_client_model(self, test_database):
        # Arrange
        client_model = ClientModel(
            name="João Silva",
            email="joao@email.com",
            phone="11999999999"
        )
        
        # Act
        test_database.add(client_model)
        test_database.commit()
        
        # Assert
        assert client_model.id is not None
        assert client_model.name == "João Silva"
        assert client_model.email == "joao@email.com"
        assert client_model.phone == "11999999999"
        assert client_model.created_at is not None

    def test_client_model_to_dict(self, test_database):
        # Arrange
        client_model = ClientModel(
            name="Maria Santos",
            email="maria@email.com",
            phone="11888888888"
        )
        test_database.add(client_model)
        test_database.commit()
        
        # Act
        result = client_model.to_dict()
        
        # Assert
        assert result['id'] == client_model.id
        assert result['name'] == "Maria Santos"
        assert result['email'] == "maria@email.com"
        assert result['phone'] == "11888888888"
        assert result['created_at'] == client_model.created_at


class TestSQLAlchemyClientRepository:
    def test_save_client(self, repository, sample_client):
        # Act
        result = repository.save(sample_client)
        
        # Assert
        assert result.id is not None
        assert result.name == sample_client.name
        assert result.email == sample_client.email
        assert result.phone == sample_client.phone

    def test_save_duplicate_email_raises_error(self, repository, sample_client):
        # Arrange
        repository.save(sample_client)
        duplicate_client = Client(
            name="Maria Santos",
            email="joao.silva@email.com",  # Same email
            phone="11888888888"
        )
        
        # Act & Assert
        with pytest.raises(ClientAlreadyExistsError):
            repository.save(duplicate_client)

    def test_find_by_id_existing(self, repository, sample_client):
        # Arrange
        saved_client = repository.save(sample_client)
        
        # Act
        found_client = repository.find_by_id(saved_client.id)
        
        # Assert
        assert found_client is not None
        assert found_client.id == saved_client.id
        assert found_client.name == sample_client.name
        assert found_client.email == sample_client.email

    def test_find_by_id_nonexistent(self, repository):
        # Act
        result = repository.find_by_id(999)
        
        # Assert
        assert result is None

    def test_find_by_email_existing(self, repository, sample_client):
        # Arrange
        repository.save(sample_client)
        
        # Act
        found_client = repository.find_by_email(sample_client.email)
        
        # Assert
        assert found_client is not None
        assert found_client.email == sample_client.email

    def test_find_by_email_nonexistent(self, repository):
        # Act
        result = repository.find_by_email("nonexistent@email.com")
        
        # Assert
        assert result is None

    def test_find_all_empty(self, repository):
        # Act
        result = repository.find_all()
        
        # Assert
        assert result == []

    def test_find_all_with_clients(self, repository):
        # Arrange
        client1 = Client("João Silva", "joao@email.com", "11999999999")
        client2 = Client("Maria Santos", "maria@email.com", "11888888888")
        repository.save(client1)
        repository.save(client2)
        
        # Act
        result = repository.find_all()
        
        # Assert
        assert len(result) == 2
        assert result[0].name in ["João Silva", "Maria Santos"]
        assert result[1].name in ["João Silva", "Maria Santos"]

    def test_find_all_with_pagination(self, repository):
        # Arrange
        for i in range(5):
            client = Client(f"Client {i}", f"client{i}@email.com", f"1199999{i:04d}")
            repository.save(client)
        
        # Act
        result = repository.find_all(limit=2, offset=1)
        
        # Assert
        assert len(result) == 2

    def test_update_client_existing(self, repository, sample_client):
        # Arrange
        saved_client = repository.save(sample_client)
        saved_client.update_name("João da Silva")
        saved_client.update_phone("11777777777")
        
        # Act
        updated_client = repository.update(saved_client)
        
        # Assert
        assert updated_client.name == "João da Silva"
        assert updated_client.phone == "11777777777"

    def test_update_client_nonexistent(self, repository):
        # Arrange
        client = Client("João Silva", "joao@email.com", "11999999999", client_id=999)
        
        # Act
        result = repository.update(client)
        
        # Assert
        assert result is None

    def test_delete_by_id_existing(self, repository, sample_client):
        # Arrange
        saved_client = repository.save(sample_client)
        
        # Act
        result = repository.delete_by_id(saved_client.id)
        
        # Assert
        assert result is True
        assert repository.find_by_id(saved_client.id) is None

    def test_delete_by_id_nonexistent(self, repository):
        # Act
        result = repository.delete_by_id(999)
        
        # Assert
        assert result is False

    def test_exists_by_email_true(self, repository, sample_client):
        # Arrange
        repository.save(sample_client)
        
        # Act
        result = repository.exists_by_email(sample_client.email)
        
        # Assert
        assert result is True

    def test_exists_by_email_false(self, repository):
        # Act
        result = repository.exists_by_email("nonexistent@email.com")
        
        # Assert
        assert result is False

    def test_exists_by_email_exclude_id(self, repository, sample_client):
        # Arrange
        saved_client = repository.save(sample_client)
        
        # Act
        result = repository.exists_by_email(sample_client.email, exclude_id=saved_client.id)
        
        # Assert
        assert result is False


class TestDatabase:
    def test_database_config_default_values(self, monkeypatch):
        # Arrange & Act
        for env_var in (
            'DATABASE_HOST',
            'DATABASE_PORT',
            'DATABASE_NAME',
            'DATABASE_USER',
            'DATABASE_PASSWORD',
            'TEST_DATABASE_NAME',
        ):
            monkeypatch.delenv(env_var, raising=False)

        from src.infrastructure.database import DatabaseConfig
        config = DatabaseConfig()
        
        # Assert
        assert config.host == 'localhost'
        assert config.port == '3306'
        assert config.name == 'clientes_db'
        assert config.user == 'root'
        assert config.password == '1234'  # Valor configurado pelo usuário

    def test_database_config_test_url(self):
        # Arrange & Act
        from src.infrastructure.database import DatabaseConfig
        config = DatabaseConfig()
        test_url = config.get_database_url(is_test=True)
        
        # Assert
        assert test_url == "sqlite:///:memory:"

    def test_database_config_production_url(self):
        # Arrange & Act
        from src.infrastructure.database import DatabaseConfig
        config = DatabaseConfig()
        prod_url = config.get_database_url(is_test=False)
        
        # Assert
        assert "mysql+pymysql" in prod_url
        assert "clientes_db" in prod_url

    def test_database_initialization(self):
        # Act
        db = Database(is_test=True)
        
        # Assert
        assert db.engine is not None
        
        # Cleanup
        db.close()

    def test_database_get_session(self):
        # Arrange
        db = Database(is_test=True)
        
        # Act
        session = db.get_session()
        
        # Assert
        assert session is not None
        
        # Cleanup
        session.close()
        db.close()

    def test_database_create_tables(self):
        # Arrange
        db = Database(is_test=True)
        
        # Act
        db.create_tables()  # Should not raise any exception
        
        # Assert - if we get here without exception, test passed
        assert True
        
        # Cleanup
        db.close()
