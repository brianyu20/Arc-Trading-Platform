import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import logging
import asyncio

log = logging.getLogger(__name__)

class TradeSimulator():
    def __init__(self, config):
        self.config = config
        self.api_key = "PKWS1SIML3R0BIRXXAY9"
        self.api_secret = "6Vd4GciP7HHb6ll7Teej74IuXuaLCBt3oV5iteia"
        self.base_url = 'https://paper-api.alpaca.markets'
        #self.api = tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
        self.client = TradingClient(self.api_key, self.api_secret, paper=True)
    
    def get_account(self):
        account = self.api.get_account()
        print(account)
    
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
                    stop_price=pred_high,
                    limit_price=pred_low
                )
                self.submit_order(order)
            else:
                #buy with stop price at pred_close
                log.warning("Create Condition Met: prev_close < pred_close and pred_close > pred_high.")
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    stop_price=pred_close,
                    limit_price=pred_low
                )
                self.submit_order(order) 
    
    def submit_order(self, market_order):
        self.client.submit_order(market_order)
        
