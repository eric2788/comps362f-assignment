import unittest
import subprocess
from service.request import get, post, put
from urllib.error import HTTPError
from random import randint
from threading import Thread


VALID_CREDIT_CARD = ''.join([f'{randint(0, 9)}' for _ in range(16)])

INVALID_CREDIT_CARD = 'haiwdhiawhidawihdhiaw'


class TestWebService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # reset all tables first
        subprocess.run(['python', 'setup.py', 'reset', '2'])
        # run app server
        cls.server_proc = subprocess.Popen(['python', 'main.py'])

    @classmethod
    def tearDownClass(cls):
        cls.server_proc.terminate()

    # Test1: A query about a product returns the correct product attributes.
    def test_query_product(self):
        expected = {
            'id': 1,
            'quantity': 2,
            'description': 'apple',
            'price': 10
        }
        self.assertDictEqual(get('/market/query/1')['data'], expected)

    # Test2: Buying a product with sufficient stock in the server succeeds and the quantity
    # in stock is updated
    def test_buy_product(self):
        expected_resp = {
            'cost': 30,
            'status': 'Success'
        }
        resp = post('/market/buy/2', {
            'credit_card': VALID_CREDIT_CARD,
            'amount': 2
        })['data']
        self.assertDictEqual(expected_resp, resp)

        # after buy
        expected_resp = {
            'id': 2,
            'quantity': 0,
            'description': 'banana',
            'price': 15
        }
        self.assertDictEqual(get('/market/query/2')['data'], expected_resp)

    # Buying a product with insufficient stock in the server fails and the quantity in
    # stock remains unchanged
    def test_buy_product_insufficent(self):
        expected_resp = {
            'cost': 0,
            'status': 'Failure (insufficent quantity)'
        }
        resp = post('/market/buy/3', {
            'credit_card': VALID_CREDIT_CARD,
            'amount': 3
        })['data']
        self.assertDictEqual(expected_resp, resp)

        # remain unchanged
        expected_resp = {
            'id': 3,
            'quantity': 2,
            'description': 'orange',
            'price': 20
        }
        self.assertDictEqual(get('/market/query/3')['data'], expected_resp)

    # Test4: Replenishing a product updates the server’s quantity in stock
    def test_replenish_product(self):
        expected_resp = {
            'quantity': 5,
            'status': 'Success'
        }
        resp = put('/market/replenish/4', {'amount': 3})['data']
        self.assertDictEqual(expected_resp, resp)

        # query a product should show the new quantity
        expected_resp = {
            'quantity': 5,
            'id': 4,
            'description': 'milk',
            'price': 25
        }
        self.assertDictEqual(get('/market/query/4')['data'], expected_resp)

    # Test5: When the product ID does not exist, the server returns the 404 status code.
    def test_product_id_non_exist(self):
        with self.assertRaises(HTTPError) as e:
            get('/market/query/999')
            self.assertEqual(e.exception.status, 404)

    # Test6: When some required input data are missing or invalid, the server returns the
    # 400 status code
    def test_invalid_or_missing_arguments(self):
        # test buy without credit card
        with self.assertRaises(HTTPError) as e:
            post('/market/buy/5', {'amount': 1})
            self.assertEqual(e.exception.status, 400)

        # test invalid credit card
        with self.assertRaises(HTTPError) as e:
            post('/market/buy/5', {
                'amount': 1,
                'credit_card': INVALID_CREDIT_CARD
            })
            self.assertEqual(e.exception.status, 400)

        # test invalid amount
        with self.assertRaises(HTTPError) as e:
            post('/market/buy/5', {
                'amount': 'infinite',
                'credit_card': VALID_CREDIT_CARD
            })
            self.assertEqual(e.exception.status, 400)

    # Test7: If two requests for buying the same product arrive almost simultaneously and
    # the quantity in stock is insufficient for the second request, the server must not
    # mistakenly fulfill the second request
    def test_buy_product_simultaneously(self):
        
        statues = [None] * 2

        def buy_two_product(index):
            status = post('/market/buy/6', {
                'amount': 2,
                'credit_card': VALID_CREDIT_CARD
            })['data']['status']
            nonlocal statues
            statues[index] = status

        threads = [ Thread(target=buy_two_product, args=(i, )) for i in range(2) ]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertNotEqual(statues[0], statues[1])

if __name__ == '__main__':
    unittest.main()
