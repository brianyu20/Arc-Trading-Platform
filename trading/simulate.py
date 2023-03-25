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

class TradeSimulator():
    def __init__(self, config):
        self.config = config
        self.api_key = "PKBI8F204FHMRKC6V7ZN"
        self.api_secret = "JNvDPj7shik5HITNB2adtCqbEsMrJt2ZVn1FbDvK"
        self.base_url = 'https://paper-api.alpaca.markets'
        #self.api = tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
        self.client = TradingClient(self.api_key, self.api_secret, paper=True)
        self.api = tradeapi.REST(self.api_key, self.api_secret, base_url=self.base_url, api_version='v2')
        self.conn = Stream(self.api_key, self.api_secret, base_url=self.base_url, raw_data=True)

        self.made_orders:dict = {}
        self.processed_orders = {}

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
    
    def submit_stop_orders(self, symbol, stop_price):
        log.info("Submitting stop order for %s, at price %f", symbol, stop_price)
        self.api.submit_order(
            symbol=symbol,
            qty=1,
            side=OrderSide.SELL,
            type='stop',
            time_in_force= TimeInForce.DAY,
            stop_price=stop_price,
            #order_class='oco',
            take_profit=dict(
                limit_price=stop_price - 0.1,
            ),
            stop_loss=dict(
                stop_price=stop_price + 0.1,
            ),
        )

    async def on_message(self, message):
        if message['stream'] == 'trade_updates':
            if message['data']['event'] == 'fill':
                order_id = message['data']['order']['id']
                symbol = message['data']['order']['symbol']
                if symbol in self.temp_made_orders and order_id not in self.processed_orders:
                    stop_price = self.temp_made_orders[symbol]
                    await self.submit_stop_orders(symbol, stop_price)
                    self.processed_orders[order_id] = True
            else:
                print(f"status change for {message['data']['order']['symbol']}, {message['data']['event']}")
                log.info("Status change for %s: %s", message['data']['order']['symbol'], message['data']['event'] )
    
    def connect(self):
        log.info("websocket running...")
        print("websocket running...")
        self.conn.subscribe_trade_updates(self.on_message)
        self.conn.run()
    
    async def get_made_orders(self):
        return self.made_orders
    
    async def record_made_orders(self):
        cwd = os.getcwd()
        filename = os.path.join(cwd, 'made_orders')
        with open(filename, 'w') as outfile:
            json.dump(self.made_orders, outfile)

    async def create_order(self, prediction, last_stock, symbol):
        log.info("Checking conditions for order for %s", symbol)
        log.info("last stock information %s, %s, %s, %s", last_stock[0], last_stock[1], last_stock[1], last_stock[1])
        pred_open = float(prediction[0])
        pred_high = float(prediction[1])
        pred_low = float(prediction[2])
        pred_close = float(prediction[3])
        previous_open = float(last_stock[0])
        previous_high = float(last_stock[1])
        previous_low = float(last_stock[2])
        previous_close = float(last_stock[3])
        #log.info("Predictions: ", pred_open)
        #log.info("Last stock information: ", previous_open)
        if previous_close < pred_close:
            if pred_close < pred_high:
                #buy with stop price at pred_high
                log.warning("Create Condition Met: prev_close < pred_close and pred_close < pred_high.")
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    #stop_price=str(pred_high),
                    #limit_price=str(pred_low)
                )
                await self.submit_order(order)
                self.made_orders[symbol] = pred_high
            else:
                #buy with stop price at pred_close
                log.warning("Create Condition Met: prev_close < pred_close and pred_close > pred_high.")
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    #stop_price=str(pred_close),
                    #limit_price=str(pred_low)
                )
                await self.submit_order(order)
                self.made_orders[symbol] = pred_close
    
    async def submit_order(self, market_order):
        self.client.submit_order(market_order)

# ts = TradeSimulator({'key': 'value'})
# for name in ts.temp_made_orders:
#     ts.submit_stop_orders(name, ts.temp_made_orders[name])