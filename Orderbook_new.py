from Order import Order
import pandas as pd
import bisect

class Orderbook_new(object):

    def __init__(self):
        # public:
        self.order_history = []
        # private:
        self._orderInedex = 0 # index for the incoming orders -> increment after adding order!
        self._bid_book_prices = [] # bid prices - list
        self._bid_book = {} # bid order book - dict
        self._ask_book_prices = [] # ask prices - list
        self._ask_book = {} # ask order book - dict


    def add_order_to_history(self, order):
        self._orderInedex += 1
        hist_order = order.asdict()
        hist_order['orderIndex'] = self._orderInedex
        self.order_history.append(hist_order)
        #print(order)

    def add_order_to_book(self, order):

        self.add_order_to_history(order)
        if order.side == 'buy':
            book_prices = self._bid_book_prices
            book = self._bid_book
        else: # order.side == 'sell'
            book_prices = self._ask_book_prices
            book = self._ask_book

        if (order.price in book_prices):
            book[order.price]['order_count'] += 1
            book[order.price]['contract_count'] += order.quantity
            book[order.price]['order_ids'].append(order.id)
            book[order.price]['orders'][order.id] = order.asdict()
        else:
            bisect.insort(book_prices, order.price)
            book[order.price] = {'order_count': 1,
                                 'contract_count': order.quantity,
                                 'order_ids': [order.id],
                                 'orders': {order.id: order.asdict()}}

        
    def remove_order(self, side, price, orderId):
        if side == 'buy':
            book_prices = self._bid_book_prices
            book = self._bid_book
        else: # order.side == 'sell'
            book_prices = self._ask_book_prices
            book = self._ask_book
        removed_valid_orderId = (book[price]['orders'].pop(orderId, False))
        if removed_valid_orderId:
            book[price]['order_count'] -= 1
            book[price]['contract_count'] -= removed_valid_orderId['quantity']
            book[price]['order_ids'].remove(orderId)
            if book[price]['order_count'] == 0:
                book_prices.remove(price)
        else:
            pass
    
    def reduce_order(self, side, price, quantity_to_reduce, orderId):
        if side == 'buy':
            book = self._bid_book
        else: # order.side == 'sell'
            book = self._ask_book
        if quantity_to_reduce < book[price]['orders'][orderId]['quantity']:
            book[price]['orders'][orderId]['quantity'] -= quantity_to_reduce
            book[price]['contract_count'] -= quantity_to_reduce
        else: # quantity_to_reduce >= resting quantity
            self.remove_order(side, price, orderId)

    def process_order(self, order):
        self.add_order_to_history(order)

        if order.side == 'buy':
            if order.price >= self._ask_book_prices[0]:
                pass
                # match order
            else:
                self.add_order_to_book(order)
        else:
            if order.price <= self._bid_book_prices[-1]:
                pass
                # match order 
            else:
                self.add_order_to_book(order)
    
    #def match_order(self, order):

            

            



o1 = Order(1, 100, 2,'buy', 1)
B1 = Orderbook_new()
B1.add_order_to_book(o1)
print(B1._bid_book)
B1.remove_order('buy', 100, 1)
print(B1._bid_book)
