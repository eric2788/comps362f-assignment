from typing import Tuple
from flask import Blueprint, request
from flask.wrappers import Response
from service.json import json_load
from model import Product, Stock
from service.response import bad_request, not_found, success_resp
from service.sql import DBSession
from threading import Lock

# an optional controller to control the product table
# perform CRUD operations for product with sqlite

app = Blueprint('product', __name__)

# assuming database doesn't have concurrcies facility
# so add lock here for avoid race conditions
productLock = Lock()

# get all products
@app.route('/', methods=['GET'])
def get_products():
    with DBSession(False, lock=productLock) as session:
        products = session.query(Product).all()
        return success_resp(list(map(lambda x: x.as_dict(), products)))

# get product by id
@app.route('/<int:id>')
def get_product(id):
    with DBSession(False, lock=productLock) as session:
        product = session.query(Product).get(id)
        if not product:
            return not_found(f'product not found with id={id}')
        else:
            return success_resp(product.as_dict())

# create product
@app.route('/', methods=['POST'])
def create_product():
    data = json_load(request.data)
    product, resp = parse_product(data)
    if resp:
        return resp
    product.stock = Stock(product=product)
    # I need to commit before return response so that `product.as_dict()` function will include a product id
    # so I set commit=False in DBSession and do it manually.
    with DBSession(False, lock=productLock) as session:
        session.add(product)
        session.commit()
        return success_resp(product.as_dict())

# update a product by id
@app.route('/<int:id>', methods=['PUT'])
def update_product(id):
    data = json_load(request.data)
    product, resp = parse_product(data)
    if resp:
        return resp
    with DBSession(lock=productLock) as session:
        prod = session.query(Product).get(id)
        prod.description = product.description # update description
        prod.price = product.price # update price
        return success_resp(prod.as_dict())

# delete a product by id
@app.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    with DBSession(lock=productLock) as session:
        product = session.query(Product).get(id)
        if not product:
            return not_found(f'product not found with id={id}')
        session.delete(product)
        return success_resp(product.as_dict())

# parse json payload to product
# second value will not be none if there are any invalid arguments
def parse_product(data: any) -> Tuple[Product, Tuple[Response, int]]:
    if not data: # no payload data
        return None, bad_request('invalid arguments')
    if 'price' not in data or 'description' not in data: # insufficient arguments
        return None, bad_request('insufficient arguments')
    if type(data['price']) != int: # price is not integer
        return None, bad_request('argument price is not a valid int')
    prod = Product(price=int(data['price']), description=str(data['description']))
    return prod, None



