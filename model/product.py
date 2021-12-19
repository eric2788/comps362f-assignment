from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from service.sql import Base

# a sql table that represent product

class Product(Base):

    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # product description
    description = Column(String(50))

    # product price
    price = Column(Integer)

    # product stock (with quantity)
    stock = relationship("Stock", back_populates="product", cascade='all, delete', uselist=False)


    # to json serializable
    def as_dict(self) -> dict():
        return {
            'id': self.id,
            'description': self.description,
            'price': self.price
        }




