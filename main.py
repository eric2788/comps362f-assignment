from flask import Flask
# fetch date time on server start
from service.daytime import * 
from service.response import success_resp
from controller import market, product
from setup import setup_products
from service.request import mutable_port
from sys import argv

app = Flask(__name__)

# make index response to show the api is working
@app.route('/')
def show_status():
    return success_resp({'status': 'ok'})

if __name__ == '__main__':

    # custom port available from args
    port = argv[1] if len(argv) > 1 else None

    if port and port.isdigit():
        mutable_port = int(port) 
    
    # register blueprint (routed group)
    app.register_blueprint(market, url_prefix='/market')
    app.register_blueprint(product, url_prefix='/product')

    # setup tables from setup.py
    setup_products(reset=False)

    app.run(port=mutable_port)