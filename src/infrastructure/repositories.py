from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.application.interfaces.client_repository import ClientRepository
from src.domain.client import Client
from src.domain.exceptions import ClientAlreadyExistsError
from src.infrastructure.models import ClientModel


class SQLAlchemyClientRepository(ClientRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, client: Client) -> Client:
        try:
            client_model = ClientModel(
                name=client.name,
                email=client.email,
                phone=client.phone
            )
            
            self._session.add(client_model)
            self._session.commit()
            
            return self._model_to_entity(client_model)
            
        except IntegrityError:
            self._session.rollback()
            raise ClientAlreadyExistsError(client.email)

    def find_by_id(self, client_id: int) -> Optional[Client]:
        client_model = self._session.query(ClientModel).filter_by(id=client_id).first()
        return self._model_to_entity(client_model) if client_model else None

    def find_by_email(self, email: str) -> Optional[Client]:
        client_model = self._session.query(ClientModel).filter_by(email=email).first()
        return self._model_to_entity(client_model) if client_model else None

    def find_all(self, limit: int = 100, offset: int = 0) -> List[Client]:
        client_models = (
            self._session.query(ClientModel)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._model_to_entity(model) for model in client_models]

    def update(self, client: Client) -> Client:
        try:
            client_model = self._session.query(ClientModel).filter_by(id=client.id).first()
            if not client_model:
                return None

            client_model.name = client.name
            client_model.email = client.email
            client_model.phone = client.phone

            self._session.commit()
            return self._model_to_entity(client_model)
            
        except IntegrityError:
            self._session.rollback()
            raise ClientAlreadyExistsError(client.email)

    def delete_by_id(self, client_id: int) -> bool:
        client_model = self._session.query(ClientModel).filter_by(id=client_id).first()
        if not client_model:
            return False

        self._session.delete(client_model)
        self._session.commit()
        return True

    def exists_by_email(self, email: str, exclude_id: int = None) -> bool:
        query = self._session.query(ClientModel).filter_by(email=email)
        if exclude_id:
            query = query.filter(ClientModel.id != exclude_id)
        
        return query.first() is not None

    def _model_to_entity(self, model: ClientModel) -> Client:
        return Client(
            name=model.name,
            email=model.email,
            phone=model.phone,
            client_id=model.id,
            created_at=model.created_at
        )