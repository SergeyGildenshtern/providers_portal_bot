from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from models.database import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    is_viewed = Column(Boolean)

    def __repr__(self):
        return [self.id, self.user_id, self.title, self.description, self.is_viewed]
