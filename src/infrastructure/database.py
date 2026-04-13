import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

Base = declarative_base()


class DatabaseConfig:
    def __init__(self):
        self.host = config('DATABASE_HOST', default='localhost')
        self.port = config('DATABASE_PORT', default='3306')
        self.name = config('DATABASE_NAME', default='clientes_db')
        self.user = config('DATABASE_USER', default='root')
        self.password = config('DATABASE_PASSWORD', default='1234')
        self.test_name = config('TEST_DATABASE_NAME', default='clientes_db_test')

    def get_database_url(self, is_test: bool = False) -> str:
        if is_test:
            # Use SQLite in memory for tests to avoid external dependencies
            return "sqlite:///:memory:"
        
        db_name = self.name
        return (
            f"mysql+pymysql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{db_name}"
        )


class Database:
    def __init__(self, is_test: bool = False):
        self._config = DatabaseConfig()
        self._engine = create_engine(
            self._config.get_database_url(is_test),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self._session_maker = sessionmaker(bind=self._engine)

    @property
    def engine(self):
        return self._engine

    def create_tables(self):
        Base.metadata.create_all(self._engine)

    def get_session(self):
        return self._session_maker()

    def close(self):
        self._engine.dispose()