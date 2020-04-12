#Class definition: Order


class Order(object):

    def __init__(self, id, price, quantity, side, time):
        #private:
        self.id = id
        self.price = price
        self.quantity = quantity
        self.side = side
        self.time = time

    def asdict(self):
        return {'orderId': self.id,
                'price': self.price,
                'quantity': self.quantity,
                'side': self.side,
                'time': self.time}

    def __str__(self):
        '''str method to print information about order'''
        return str(self.asdict())

