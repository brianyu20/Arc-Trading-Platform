import alpaca_trade_api as tradeapi

class TradeSimulator():
    def __init__(self, config):
        self.config = config
        self.api_key = "AKYE8JNAP8EL97HL151W"
        self.api_secret = "ToGIXjSD5aRJDAYdpz2yC7gHQOwFNq4xXoNUPEcM"
        self.base_url = 'https://paper-api.alpaca.markets'
        self.api = tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
    
    def get_account(self):
        account = self.api.get_account()
        print(account)
        

ts = TradeSimulator({'key': 'value'})
ts.get_account()

