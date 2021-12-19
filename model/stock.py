from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from service.sql import Base

# a sql table represent Stock

class Stock(Base):

    __tablename__ = 'stocks'

    # product id
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    product = relationship("Product", back_populates="stock", uselist=False)

    # quantity of that product
    quantity = Column(Integer, default=0)

    # to json serializable
    def as_dict(self) -> dict():
        return {
            'product_id': self.product_id,
            'quantity': self.quantity
        }

