from Order import Order
import pandas as pd
import bisect

class Orderbook_new(object):

    def __init__(self):
        # public:
        self.order_history = []
        self.trade_history = []
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
    
    def add_to_trade_history(self, price, quantity, resting_order_id, resting_time, incoming_order_id, incoming_time, incoming_side):
        resting_side = 'buy' if (incoming_side == 'sell') else 'sell' # eval counter-side
        self.trade_history.append({'price': price, 'quantity': quantity, 'resting_order_id': resting_order_id,
                                   'resting_side': resting_side, 'resting_time': resting_time,
                                   'incoming_order_id': incoming_order_id, 'incoming_time': incoming_time,
                                   'incoming_side': incoming_side})

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
        removed_valid_orderId = (book[price]['orders'].pop(orderId, None))
        if removed_valid_orderId:
            book[price]['order_count'] -= 1
            book[price]['contract_count'] -= removed_valid_orderId['quantity']
            book[price]['order_ids'].remove(orderId)
            if book[price]['order_count'] == 0:
                book_prices.remove(price)
        else:
            pass
    
    def reduce_order_by(self, side, price, quantity_to_reduce, orderId):
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
                # match order market
            else:
                self.add_order_to_book(order)
        else:
            if order.price <= self._bid_book_prices[-1]:
                pass
                # match order market
            else:
                self.add_order_to_book(order)
    
    def match_order_market(self, order):

        if order.side == 'buy':
            # check if price is below or above best price .. #missing
            book_prices = self._ask_book_prices
            book = self._ask_book
            quantity_to_trade = order.quantity
            while quantity_to_trade > 0:
                if (not book_prices):
                    print('Error - No orders to match!')
                    break
                market_price = book_prices[0] # best ask
                market_order_id = book[market_price]['order_ids'][0] # FIFO
                market_order_qnt = book[market_price]['orders'][market_order_id]['quantity']
                if quantity_to_trade <= market_order_qnt: # if equal then order is removed in reduce_order_by
                    self.add_to_trade_history(market_price, quantity_to_trade, market_order_id, 
                                              book[market_price]['orders'][market_order_id]['time'],
                                              order.id, order.time, order.side)
                    self.reduce_order_by('sell', market_price, quantity_to_trade, market_order_id)
                    print('Order successfully filled')
                    break # order is completely filled
                else: # if order.quantity > market_order_qnt
                    quantity_to_trade -= market_order_qnt
                    self.add_to_trade_history(market_price, market_order_qnt, market_order_id, 
                                              book[market_price]['orders'][market_order_id]['time'],
                                              order.id, order.time, order.side)
                    self.remove_order('sell', market_price, market_order_id)
                    

        else: # order.side == 'sell'
            book_prices = self._bid_book_prices
            book = self._bid_book
            quantity_to_trade = order.quantity
            while quantity_to_trade > 0:
                if (not book_prices):
                    print('Error - No orders to match!')
                    break
                market_price = book_prices[-1] # best bid
                market_order_id = book[market_price]['order_ids'][0] # FIFO
                market_order_qnt = book[market_price]['orders'][market_order_id]['quantity']
                if quantity_to_trade <= market_order_qnt: # if equal then order is removed in reduce_order_by
                    self.add_to_trade_history(market_price, quantity_to_trade, market_order_id, 
                                              book[market_price]['orders'][market_order_id]['time'],
                                              order.id, order.time, order.side)
                    self.reduce_order_by('buy', market_price, quantity_to_trade, market_order_id)
                    print('Order successfully filled')
                    break # order is completely filled
                else: # if order.quantity > market_order_qnt
                    quantity_to_trade -= market_order_qnt
                    self.add_to_trade_history(market_price, market_order_qnt, market_order_id, 
                                              book[market_price]['orders'][market_order_id]['time'],
                                              order.id, order.time, order.side)
                    self.remove_order('buy', market_price, market_order_id)






#o1 = Order(1, 100, 5,'buy', 1)
#o2 = Order(2, 101, 5,'sell', 2)
#B1 = Orderbook_new()
#B1.add_order_to_book(o1) # added to bid
#B1.add_order_to_book(o2)
#print(B1._bid_book)
#B1.remove_order('sell', 100, 2)
#o3 = Order(3, 100, 2,'sell', 3)
#B1.match_order_market(o3)
#print(B1._bid_book)
#print(B1.trade_history)