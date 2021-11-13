from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    category = Column(String)
    code = Column(String)
    is_confirmed = Column(Boolean)
    specifications = Column(String)

    user = relationship('User', backref="products")

    def __repr__(self):
        return f'{self.id}, {self.user_id}, {self.name}, {self.category}, {self.code}, {self.is_confirmed}, {self.specifications}'
