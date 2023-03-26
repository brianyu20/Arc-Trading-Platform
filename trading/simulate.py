import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca_trade_api import Stream
import logging
import asyncio
import json
import os
import websocket
import zlib

log = logging.getLogger(__name__)
handler = logging.FileHandler('alpaca_report.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

class TradeSimulator():
    def __init__(self, config):
        self.config = config
        self.api_key = "PK0PQWC9STA02VCBC3L0"
        self.api_secret = "6RhjGgxKLw178pB1DuwLVSRKzUBSTCIencq5N28p"
        self.base_url = 'https://paper-api.alpaca.markets'
        #self.api = tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
        self.client = TradingClient(self.api_key, self.api_secret, paper=True)
        self.api = tradeapi.REST(self.api_key, self.api_secret, base_url=self.base_url, api_version='v2')
        self.conn = Stream(self.api_key, self.api_secret, base_url=self.base_url, raw_data=True)

        self.made_orders:dict = {}
        self.processed_orders = {}

        with open('alpaca_report.log', 'w'):
            pass

        self.temp_made_orders = {
            # 'MMM' : 103.43,
            # 'AMZN': 99.06,
            'BA': 201.23,
            'CSCO': 50.11,
            'C': 44.67,
            'KO': 60.06,
            'DD': 68.43,
            'HD': 288.16,
            'IBM': 124.19,
            'INTC': 29.68,
            'JNJ': 152.88,
            'JPM': 127.82,
            'MRK': 105.11,
            'WFC': 38.6
        }
    
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
            qty=1,
            side=OrderSide.SELL,
            type='stop',
            time_in_force= TimeInForce.DAY,
            stop_price=stop_price,
        )
    
    async def submit_stop_buy_order(self, symbol, stop_price):
        log.info("Submitting stop buy order for %s, at price %f", symbol, stop_price)
        self.api.submit_order(
            symbol=symbol,
            qty=1,
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
                if symbol in self.temp_made_orders and order_id not in self.processed_orders:
                    stop_price = self.temp_made_orders[symbol]
                    await self.submit_stop_sell_order(symbol, stop_price)
                    self.processed_orders[order_id] = True
            else:
                print(f"status change for {message['data']['order']['symbol']}, {message['data']['event']}")
                log.info("Status change for %s: %s", message['data']['order']['symbol'], message['data']['event'] )
    
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
                #buy with stop price at pred_high
                log.warning("Create Condition Met: prev_close < pred_close and pred_close < pred_high.")
                await self.submit_stop_buy_order(symbol, str(pred_high))
                self.made_orders[symbol] = pred_high
            else:
                #buy with stop price at pred_close
                log.warning("Create Condition Met: prev_close < pred_close and pred_close > pred_high.")
                await self.submit_stop_buy_order(symbol, str(pred_close))
                self.made_orders[symbol] = pred_close

ts = TradeSimulator({'key': 'value'})
# for name in ts.temp_made_orders:
#     ts.submit_stop_orders(name, ts.temp_made_orders[name])
ts.connect()