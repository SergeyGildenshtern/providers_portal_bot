from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from models.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    isAdmin = Column(Boolean)

    userInfo = relationship('users_info')
    userProducts = relationship('products')
    userNotifications = relationship('notifications')
    userOffers = relationship('offers')

    def __repr__(self):
        return [self.id, self.login, self.password, self.isAdmin]
