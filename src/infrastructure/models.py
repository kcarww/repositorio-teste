from sqlalchemy import Column, Integer, String, DateTime, func
from src.infrastructure.database import Base


class ClientModel(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at
        }