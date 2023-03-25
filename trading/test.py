from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest, StopLimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import asyncio

trading_client = TradingClient('PK6FR0MBDQ07K69GK946', 'sENHTtHmyaTktwreb2B9i8qHmXRlaCMYYzgv30e6', paper=True)

# preparing market order
market_order_data = MarketOrderRequest(
                    symbol="SPY",
                    qty=2,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    )

stop_order_data = StopOrderRequest(
                    symbol="SPY",
                    qty=2,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    stop_price= 200.00
                    )

# Market order
# market_order = trading_client.submit_order(
#                 order_data=market_order_data
#                )
# print('made 1')
# market_order = trading_client.submit_order(
#                 order_data=stop_order_data
#                )
# print('made 2')
orders = trading_client.get_orders()
print(orders)