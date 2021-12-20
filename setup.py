from service.sql import create_tables, DBSession
from model import Product, Stock
from random import randint
from sys import argv


# setup tables and preinsert products
def setup_products(reset=True, default_amount: int=None):
    # create tables
    create_tables()

    if reset:
        # delete all tables (if reset)
        with DBSession() as session:
            session.query(Product).delete()
            session.query(Stock).delete()
            print(f'Successfully reset all tables.')
    
    # insert at least 10 products
    products = [
        ('apple', 10),
        ('banana', 15),
        ('orange', 20),
        ('milk', 25),
        ('vegetable', 30),
        ('beef', 35),
        ('chocolate', 40),
        ('water', 45),
        ('milk tea', 50),
        ('beer', 55)
    ]

    inserts = []

    for (desc, price) in products:
        prod = Product(description=desc, price=price, stock=Stock(quantity=randint(0, 10) if not default_amount else default_amount))
        inserts.append(prod)

    with DBSession() as session:
        if reset: # if reset, just all all of them
            session.add_all(inserts)
            print(f'Successfully Inserted {len(products)} products.')
        else:
            changed = 0
            for product in inserts:
                # query whether there has same description
                exister = session.query(Product).filter_by(description=product.description).first()
                mutated = True
                if not exister:
                    # if not exist, just add it
                    session.add(product)
                elif default_amount and exister.stock.quantity != default_amount:
                    # if exist + default_amount is set but stock amount not equal, update the stocks
                    exister.stock.quantity = default_amount
                else:
                    mutated = False
                
                if mutated:
                    changed += 1
                
            print(f'Successfully Mutated {changed} products.')

    



if __name__ == '__main__':

    # reset and amount is customizable via port
    reset = argv[1] == 'reset' if len(argv) > 1 else False
    amount = argv[2] if len(argv) > 2 else None

    # safe parsing amount
    if amount and amount.isdigit():
        amount = int(amount)
    else:
        amount = None
        

    setup_products(reset=reset, default_amount=amount)

