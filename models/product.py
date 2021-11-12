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

    productOffers = relationship('offers')

    def __repr__(self):
        return [self.id, self.user_id, self.name, self.category, self.code, self.isConfirmed, self.specifications]
