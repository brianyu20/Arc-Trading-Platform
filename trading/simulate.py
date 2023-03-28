import alpaca_trade_api as tradeapi
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca_trade_api import Stream
import logging
import asyncio
import json
import os

log = logging.getLogger(__name__)
handler = logging.FileHandler('alpaca_report.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

class TradeSimulator():
    def __init__(self, config):
        self.config = config['simulator']
        self.api_key = self.config['api_key']
        self.api_secret = self.config['api_secret']
        self.base_url = self.config['base_url']
        self.quantity = self.config['quantity']
        self.trail_percent = self.config['trail_percent']
        self.upper_percent = self.config['upper_percent']
        self.api = tradeapi.REST(self.api_key, self.api_secret, base_url=self.base_url, api_version='v2')
        self.conn = Stream(self.api_key, self.api_secret, base_url=self.base_url, raw_data=True)

        self.made_orders:dict = {}
        self.processed_orders = {}

        if self.config['watchlist']['enable']:
            watchlist_name = 'unordered stocks'
            watchlist = self.api.create_watchlist(watchlist_name=watchlist_name)
            if watchlist:
                watchlists = self.api.get_watchlists()
                resp_watchlist = next((w for w in watchlists if w.name == watchlist_name), None)
                self.watchlist_id = resp_watchlist.id
            else:
                log.warning("watchlist was not created successfully")

        with open('alpaca_report.log', 'w'):
            pass
    
    def get_account(self):
        account = self.api.get_account()
        print(account)
    
    def connect(self):
        log.info("websocket running...")
        print("websocket running...")
        self.conn.subscribe_trade_updates(self.on_message)
        self.conn.run()
    
    async def get_made_orders(self):
        return self.made_orders
    
    async def submit_stop_sell_order(self, symbol, stop_price):
        log.info("Submitting stop sell order for %s, at price %f", symbol, stop_price)
        self.api.submit_order(
            symbol=symbol,
            qty=self.quantity,
            side=OrderSide.SELL,
            type='stop',
            time_in_force= TimeInForce.DAY,
            stop_price=stop_price,
        )
    
    async def submit_trailing_sell_order(self, symbol, trail_percent):
        current_price = await self.get_current_price(symbol)
        trail_amount = current_price * trail_percent
        stop_price = current_price - trail_amount
        log.info("Submitting trailing stop sell order for %s, at current price %s, with stop price %s", symbol, current_price, stop_price)
        self.api.submit_order(
            symbol=symbol,
            qty=self.quantity,
            side=OrderSide.SELL,
            type='trailing_stop',
            time_in_force= TimeInForce.DAY,
            trail_percent=trail_percent,
            # trail_price=stop_price,
        )
    
    async def submit_limit_sell_order(self, symbol):
        current_price = await self.get_current_price(symbol)
        limit_price = str(round(current_price + (current_price*self.upper_percent), 2))
        log.info("Submitting limit stop sell order for %s, at current price %s, with limit price %s", symbol, current_price, limit_price)
        self.api.submit_order(
            symbol=symbol,
            qty=self.quantity,
            side=OrderSide.SELL,
            type='limit',
            time_in_force= TimeInForce.DAY,
            limit_price=limit_price,
        )

    async def submit_stop_buy_order(self, symbol, stop_price):
        log.info("Submitting stop buy order for %s, at price %s", symbol, stop_price)
        self.api.submit_order(
            symbol=symbol,
            qty=self.quantity,
            side=OrderSide.BUY,
            type='stop',
            time_in_force= TimeInForce.DAY,
            stop_price=stop_price,
        )

    async def on_message(self, message):
        if message['stream'] == 'trade_updates':
            if message['data']['event'] == 'fill':
                order_id = message['data']['order']['id']
                symbol = message['data']['order']['symbol']
                if symbol in self.made_orders and order_id not in self.processed_orders:
                    #await self.submit_trailing_sell_order(symbol, self.trail_percent)
                    await self.submit_limit_sell_order(symbol)
                    self.processed_orders[order_id] = True
            else:
                print(f"status change for {message['data']['order']['symbol']}, {message['data']['event']}")
                log.info("Status change for %s: %s", message['data']['order']['symbol'], message['data']['event'] )
    
    # async def on_message(self, message):
    #     if message['stream'] == 'trade_updates':
    #         if message['data']['event'] == 'canceled':
    #             order_id = message['data']['order']['id']
    #             symbol = message['data']['order']['symbol']
    #             # stop_price = self.made_orders[symbol]
    #             #await self.submit_stop_sell_order(symbol, stop_price)
    #             await self.submit_limit_sell_order('BABA')
    #             self.processed_orders[order_id] = True
    #         else:
    #             print(f"status change for {message['data']['order']['symbol']}, {message['data']['event']}")
    #             log.info("Status change for %s: %s", message['data']['order']['symbol'], message['data']['event'] )

    async def record_made_orders(self):
        cwd = os.getcwd()
        filename = os.path.join(cwd, 'made_orders')
        with open(filename, 'w') as outfile:
            json.dump(self.made_orders, outfile)

    async def create_order(self, prediction, last_stock, symbol):
        log.info("Checking conditions for order for %s", symbol)
        log.info("last stock information %s, %s, %s, %s", last_stock[0], last_stock[1], last_stock[1], last_stock[1])
        pred_open = round(float(prediction[0]), 2)
        pred_high = round(float(prediction[1]), 2)
        pred_low = round(float(prediction[2]), 2)
        pred_close = round(float(prediction[3]), 2)
        previous_open = round(float(last_stock[0]), 2)
        previous_high = round(float(last_stock[1]), 2)
        previous_low = round(float(last_stock[2]), 2)
        previous_close = round(float(last_stock[3]), 2)
        if previous_close < pred_close:
            if pred_close < pred_high:
                log.warning("Create Condition Met: prev_close < pred_close and pred_close < pred_high.")
                await self.submit_stop_buy_order(symbol, str(min(pred_low, pred_close)))
                self.made_orders[symbol] = min(pred_low, pred_close)
            else:
                log.warning("Create Condition Met: prev_close < pred_close and pred_close > pred_high.")
                await self.submit_stop_buy_order(symbol, str(min(pred_low, pred_close)))
                self.made_orders[symbol] = min(pred_low, pred_close)
        else:
            if self.config['watchlist']['enable']:
                resp = self.api.add_to_watchlist(self.watchlist_id, symbol)
                log.info("Added to watchlist: %s", symbol)

    async def get_current_price(self, symbol):
        last_trade = self.api.get_latest_trade(symbol)
        return float(last_trade.price)

# ts = TradeSimulator({
#         'simulator': {
#                 'api_key': "PKZ3OZDN4STTT73XRENB",
#                 'api_secret': "6fqxWQewRGy3nG8lo1yLd9lBIhUHACpb6bIiD40Y",
#                 'base_url': 'https://paper-api.alpaca.markets',
#                 'quantity': 10,
#                 'trail_percent': 0.4,
#                 'upper_percent': 0.04,
#                 'watchlist': {
#                     'enable': False
#                 }
#             }
#         })

# watchlists = ts.api.get_watchlists()

# # Find the watchlist with the desired name
# watchlist_name = 'unordered stocks'
# watchlist = next((w for w in watchlists if w.name == watchlist_name), None)
# if watchlist:
#     ts.watchlist_id = watchlist.id
# else:
#     print("watchlist was not created successfully")

# ts.api.add_to_watchlist(ts.watchlist_id, 'AAPL')
# ts.connect()