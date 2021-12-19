from typing import Tuple
from flask import Blueprint, request
from flask.wrappers import Response
from model.product import Product
from service.json import json_load
from model import Stock, Product
from service.response import bad_request, not_found, success_resp
from service.sql import DBSession
from threading import Lock

# the main controller for assignment
# to do the buy, replenish, query operation mentioned from assignment.

app = Blueprint('market', __name__)

# this lock is to avoid race conditions
marketLock = Lock()


# a stock processor that perform buy and replenish operation 
class StockProcessor:

    def __init__(self, amount: int, id: int, lock=None) -> None:
        self.amount = amount
        self.id = id
        self.lock = lock

    # buy a product
    def withdraw(self) -> Tuple[Response, int]: 
        with DBSession(lock=self.lock) as session:
            product = session.query(Product).get(self.id)
            if not product:
                return not_found(f'not found product with id={self.id}')
            stock = product.stock
            status = 'Success'
            balance = 0
            # sufficient quantity
            if stock.quantity >= self.amount:
                stock.quantity -= self.amount # reduce the amount
                balance = self.amount * product.price # show the consume cost
            else: # insufficient quantity
                status = 'Failure (insufficent quantity)' # status change failure and cost show 0
            return success_resp({
                'status': status,
                'cost': balance
            })

    # replenish a product
    def deposit(self) -> Tuple[Response, int]:
        with DBSession(lock=self.lock) as session:
            stock = session.query(Stock).get(self.id)
            if not stock:
                return not_found(f'not found product with id={self.id}')
            stock.quantity += self.amount # add the amount 
            return success_resp({'status': 'Success', 'quantity': stock.quantity}) # quantity show the current amount


# query a product
@app.route('/query/<int:id>', methods = ['GET'])
def query_product(id):
    with DBSession(lock=marketLock, commit=False) as session:
        product = session.query(Product).get(id)
        if not product:
            return not_found(f'not found product with id={id}')
        data = product.as_dict() # serialize the product
        data['quantity'] = product.stock.quantity # add quantity attribute from stock
        return success_resp(data)

# buy a product
@app.route('/buy/<int:id>', methods = ['POST'])
def buy_product(id):
    data = json_load(request.data)
    processer, resp = check_valid(id, data) 
    if resp: 
        return resp
    return processer.withdraw()

# replenish a product
@app.route('/replenish/<int:id>', methods=['PUT'])
def replenish_product(id):
    data = json_load(request.data)
    processer, resp = check_valid(id, data, False)
    if resp:
        return resp
    return processer.deposit()


# prechecking whether the payload is valid
# the second value will be not none if the argument is invalid
def check_valid(id, data: any, withdraw=True) -> Tuple[StockProcessor, Tuple[Response, int]]:
    if not data: # no payload data
        return None, bad_request('insufficient arguments')

    if 'amount' not in data: # no amount in data
        return None, bad_request('lack of `amount` argument')

    if type(data['amount']) != int: # the amount is not integer
        return None, bad_request('`amount` value should be an integer')

    amount = int(data['amount'])

    if withdraw: # if buy a product

        if 'credit_card' not in data: # no credit_card in data
            return None, bad_request('lack of `credit_card` argument')

        credit_card = str(data['credit_card'])

        if len(credit_card) != 16 or not credit_card.isdigit(): # not 16 length or not digit
            return None, bad_request('`credit_card` value should be 16 length of digits')

    # pass the lock into StockProcessor so that to do synchonize
    return StockProcessor(amount=amount, id=id, lock=marketLock), None


