import requests
import json
from datetime import datetime, timedelta

class StockApi():
    def __init__(self, config:dict):
        self.config = config
        self.api_key = "EG59IWIUZ1YFVP8L"
        self.stock_store = {}
    
    def get_stock_store(self):
        return self.stock_store

    def get_and_store_stock(self, company_symbol:str, start:str, end:str):
        content = self.make_request(company_symbol)
        for date in content:
            if self.is_date_before(start, date) and self.is_date_before(date, end):
                self.stock_store[date] = content[date]

    def make_request(self, company_symbol:str):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={company_symbol}&apikey={self.api_key}&outputsize=compact"
        response = requests.get(url)
        content = response.json()["Time Series (Daily)"]
        return content

    def is_date_before(self, date1_str, date2_str):
        # Convert the date strings to datetime objects
        date1 = datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.strptime(date2_str, '%Y-%m-%d')

        # Check if date1 is before date2 or the same date
        return date1 <= date2

