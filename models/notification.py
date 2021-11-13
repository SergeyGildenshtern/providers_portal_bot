from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    is_viewed = Column(Boolean)

    user = relationship('User', backref="notifications")

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.title}, {self.description}, {self.is_viewed}'
