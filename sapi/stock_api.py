import requests
import json
import logging
from datetime import datetime, timedelta
import aiohttp
import asyncio
import os
from utils.time import increment_date, first_day_of_month, month_before

log = logging.getLogger(__name__)
handler = logging.FileHandler('stock_report.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

class StockApi():
    def __init__(self, config:dict):
        self.config = config
        self.api_key = "EG59IWIUZ1YFVP8L"
        self.stock_store = {}
        self.interest_store = {}
        self.cpi_store = {}
        self.inflation_store = {}
        self.unemployment_store = {}
        self.company_store = {}
        with open('stock_report.log', 'w'):
            pass

    ''' stock functions '''
    async def get_stock_store(self):
        return self.stock_store
    
    async def get_last_stock(self):
        for date in self.stock_store:
            open = self.stock_store[date]['1. open']
            high = self.stock_store[date]['2. high']
            low = self.stock_store[date]['3. low']
            close = self.stock_store[date]['4. close']
            last_stock_array = [open, high, low, close]
            break
        return last_stock_array

    async def get_and_store_stock(self, company_symbol:str, start:str, end:str):
        content = await self.make_request(company_symbol)
        self.stock_store = {}
        for date in content:
            if self.is_date_before(start, date) and self.is_date_before(date, end):
                # log.info(f"successfully fetched {date}. storing in stock_store: {content[date]}")
                self.stock_store[date] = content[date]

    async def make_request(self, company_symbol: str):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={company_symbol}&apikey={self.api_key}&outputsize=compact"
        log.info("Fetching stock information...")
        log.info(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.json()
                return content["Time Series (Daily)"]
    
    ''' interest functions '''
    async def get_interest_store(self):
        return self.interest_store
    
    async def get_and_store_interest(self, start:str, end:str):
        content = await self.make_interest_request()
        date_value_dict = {}
        for i in range(len(content)):
            date_value_dict[content[i]['date']] = content[i]['value']

        curr_date = start
        while self.is_date_before(curr_date, end):
            first_day = first_day_of_month(curr_date)
            if first_day not in date_value_dict:
                before = month_before(first_day)
                self.interest_store[curr_date] = date_value_dict[month_before(first_day)]
            else:
                self.interest_store[curr_date] = date_value_dict[first_day]
            curr_date = increment_date(curr_date)

    async def make_interest_request(self) -> list:
        log.info("Fetching interests information...")
        url = f"https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey={self.api_key}"
        log.info(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.json()
                return content['data']
    
    ''' cpi functions '''
    async def get_cpi_store(self):
        return self.cpi_store
    
    async def get_and_store_cpi(self, start:str, end:str):
        content = await self.make_cpi_request()
        date_value_dict = {}
        for i in range(len(content)):
            date_value_dict[content[i]['date']] = content[i]['value']
       
        curr_date = start
        while self.is_date_before(curr_date, end):
            first_day = first_day_of_month(curr_date)
            if first_day not in date_value_dict:
                before = month_before(first_day)
                self.cpi_store[curr_date] = date_value_dict[month_before(first_day)]
            else:
                self.cpi_store[curr_date] = date_value_dict[first_day]
            curr_date = increment_date(curr_date)
        
    async def make_cpi_request(self):
        log.info("Fetching CPI information...")
        url = f"https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey={self.api_key}"
        log.info(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.json()
                return content['data']

    ''' unemployment functions '''
    def get_unemployment_store(self):
        return self.unemployment_store
    
    def make_unemployment_request(self):
        pass

    def is_date_before(self, date1_str, date2_str):
        date1 = datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.strptime(date2_str, '%Y-%m-%d')

        return date1 <= date2
    
    ''' company information functions'''
    #TODO: gets published every year in June
    def get_company_store(self):
        return self.company_store
    
    def make_company_request(self, symbol:str):
        log.info("Fetching Company information...")
        url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={self.api_key}"
        response = requests.get(url)
        content = response.json()["annualReports"]

    
    
    