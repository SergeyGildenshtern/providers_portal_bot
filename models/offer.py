from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Offer(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    seller_id = Column(Integer, ForeignKey('users.id'))
    buyer_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(String)
    quantity = Column(String)
    status = Column(String)
    created_at = Column(Date)

    product = relationship('Product', backref="offers")
    seller = relationship('User', foreign_keys=[seller_id])
    buyer = relationship('User', foreign_keys=[buyer_id])

    def __repr__(self):
        return f'{self.id}, {self.product_id}, {self.seller_id}, {self.buyer_id}, {self.amount}, {self.quantity}, {self.status}, {self.created_at}'
