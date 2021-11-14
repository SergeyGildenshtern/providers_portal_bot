from sqlalchemy import Column, Integer, String, Boolean

from models.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    is_admin = Column(Boolean)
    telegram_chat_id = Column(String)

    def __repr__(self):
        return f'{self.id}, {self.login}, {self.password}, {self.is_admin}, {self.telegram_chat_id}'
