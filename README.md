# COMPS362F Final Assignment

## Files

```log
comps362f-assignment
 ┣ controller
 ┃ ┣ market.py # market controller, perform buy, replenish, query
 ┃ ┣ product.py # product controller, perform CRUD of product tables
 ┃ ┗ __init__.py # combine them together
 ┣ model
 ┃ ┣ product.py # represent product table
 ┃ ┣ stock.py # represent stock table
 ┃ ┗ __init__.py # combine them together
 ┣ service
 ┃ ┣ daytime.py # for getting datetime
 ┃ ┣ json.py # for json parsing
 ┃ ┣ request.py # for client request
 ┃ ┣ response.py # for create response faster
 ┃ ┗ sql.py # for using session to perform database operation
 ┣ main.py # program main entrypoint
 ┣ market.db # sqlite database
 ┣ requirements.txt # dependencies to install before run
 ┣ setup.py # setup database before run
 ┗ test.py # for testing cases
```

## Instruction To Run

First, make sure you have python environment which has version `>= 3.9.7`

### Before you run either main program or unit tests

make sure to run `pip install -r requirements.txt` to install necessary dependencies.

third party libraries:

```py
sqlalchemy # for using orm in sql
flask # for rest service
```

### Run the program

- Run the main program

    - just run `python main.py` to start the web service.

- Run the unit tests

    - just run `python test.py` to start the unit tests.

#### Remarks

- `market.db` will be auto created if it doesn't exist, so no worry to delete it.

- It is optional to run `setup.py` to setup tables manually. The main program and the unit testing program will setup tables automatically before run.

- `main.py` can run via `python main.py [port]` so that to accept the `port` argument in order to listen on custom port. 

- `setup.py` can run via `python test.py [reset] [default amount]` so that to accept the `reset` and `default_amount` arguments:
    - if ``[reset] == 'reset'``, it will reset the databases before inserting products, or else it will insert the product which the table doesn't have.
    - if ``[default_amount]`` is an integer, it will set the default quantity on each products which are going to insert or update the quantity if the product exists.


### API

There are two base paths in the API

| Path | Description | Content |
| ----- | ----------- | ------- |
| `/market` | perform buy, replenish and query of products | (See below) |
| `/product` | perform CRUD operation of product tables | (See below) |


#### Market

All paths start with `/market`.

| Path | Method | Description | PayLoad | Response |
| ----- | ---------- | ------- | --------- | ------- |
| `/buy/<id>` | `POST` | buy a product | [BuyPayload](#buypayload) | [BuyResponse](#buyresponse) |
| `/replenish/<id>` | `PUT` | replenish a product | [ReplenishPayload](#replenishpayload) | [ReplenishResponse](#replenishresponse) |
| `/query/<id>` | `GET` | query a product | `NONE` | [StockResponse](#stockresponse) |


#### Product

All paths start with `/product`.

| Path | Method | Description | PayLoad | Response |
| ----- | ---------- | ------- | --------- | ------- |
| `/` | `GET` | get all products | `NONE` | List<[ProductResponse](#productresponse)> |
| `/` | `POST` | create a product (default quantity will be 0) | [ProductPayload](#productpayload) | [ProductResponse](#productresponse) |
| `/<id>` | `PUT` | update a product | [ProductPayload](#productpayload) | [ProductResponse](#productresponse) |
| `/<id>` | `DELETE` | delete a product | `NONE` | [ProductResponse](#productresponse) |


### Payloads

#### BuyPayload

```ts
{
    amount: number, // the amount of item to buy
    credit_card: string // a credit card number with 16 digits
}
```

#### ReplenishPayload

```ts
{
    amount: number  // the amount of product to replenish
}
```

#### ProductPayload

```ts
{
    description: string,
    price: number
}
```

### Responses

Each response will include an `exe_id` attribute, so the base response will look like this:

```ts
{
    data: any, // see below
    exe_id: string // execution id
}
```

And below shows the content of each type of response inside `data` key:

#### BuyResponse

```ts
{
    cost: number, // the total balance deducted from credit card
    status: string // either Success or Failure with reason
}
```

#### ReplenishResponse

```ts
{
    quantity: number, // the quantity of the product after replenish
    status: string // always show Success
}
```

#### StockResponse

product attributes with stock quantity.

```ts
{
    id: number,
    description: string,
    price: number,
    quantity: number
}
```


#### ProductResponse

just product attributes.

```ts
{
    id: number,
    description: string,
    price: number
}
```

### Common Error Responses

The response format will be like:

```ts
{
    exe_id: string,
    error: string // the error message
}
```

the above format will be responsed if the server returns status

- 404 Not Found
- 400 Bad Request


## Advanced Technologies

### Async Programming

async programming is beneficial when performing concurrent I/O bound tasks, such like web request and file / database operation.

In thread, this is hard to write code that is thread safe without using locks/queues etc. But when there are lot more complicated situtation, using multiple locks/conditions/queues etc will be more tricky and make the code harder readable. By using async programming, where the code will shift from one task will be easier to know by reading codes, and race conditions will be avoidable without using locking tools.

In unit testing, there is a test case that need to have two requests buying a product that arrive almost simultaneously, which I have done with using Thread.

To improved that testing, I can simplity using `asyncio.gather` to make better simultaneously requests by implementing async programming.

First, I will need to make post function become async

```py
async def post_async(path, data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, post, path, data)
```

Then, make a async test case that using `asyncio.gather`

```py
async def test_buy_product_simultaneously(self):

    async def buy_two_product():
        res =  await post_async('/market/buy/6', {
            'amount': 2,
            'credit_card': VALID_CREDIT_CARD
        })
        return res['data']['status']

    statues = await asyncio.gather(buy_two_product(), buy_two_product())
    self.assertNotEqual(statues[0], statues[1])
```

Finally, change `unittest.TestCase` to `unittest.IsolatedAsyncioTestCase` so that to run async test cases.

### Message Queues

Assume that the price of each product is unstable or there is a new product just released into the market, the client will not know without reloading the web page when there is no WebSocket. Therefore, in this case, the web page should show a real-time notification, and the subscriber/publisher model will be implemented and wrapped as WebSocket.

From the real cases, let say on the web page, a user may be able to subscribe to a product by adding a product into the "wish list", so when a product price is changed, they can know instantly and decide whether to buy that product with the new price. Also, when the user has subscribed to a new product notification, they will receive notifications when a new product has been released to the market.


Product A price changed:

![pubsub1](/assets/pubsub1.jpg)

Product B price changed:

![pubsub2](/assets/pubsub2.jpg)

A new product has been released.

![pubsub3](/assets/pubsub3.jpg)