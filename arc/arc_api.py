import logging
import asyncio
import os
from datetime import datetime, timedelta
from sapi import stock_api
from napi import news_api
from graph import graph
from nlp import sentiment_analysis
from trading import simulate
from ai import random_forest
from utils.time import increment_date, is_date_before, day_before, get_earliest_and_latest_dates
from utils.stock_dictionary import sp500_default, sp400_volatile_mid, sp500_volatile_big

log = logging.getLogger(__name__)
handler = logging.FileHandler('arc_report.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


class ARC():
    def __init__(self, config:dict, SNT:sentiment_analysis, NAPI, G, RF, SAPI, SIMULATOR):
        log.info("Running ARC")
        self.SNT:sentiment_analysis = SNT
        self.NAPI:news_api = NAPI
        self.graph:graph = G
        self.RF:random_forest = RF
        self.SAPI: stock_api = SAPI
        self.simulator:simulate = SIMULATOR

        self.companies = sp500_volatile_big
        with open('arc_report.log', 'w'):
            pass


    ############ Process functions ##############
    async def generate_graph(self, n_articles, topic, start, end):
        await self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = await self.get_article_store()

        await self.analyze_and_store_scores(article_store)
        sentiment_store = await self.get_sentiment_store()
        
        await self.show_graph(sentiment_store, topic)
    
    async def generate_next_stock(self, n_articles, topic, company_symbol, start, end, first_iteration:bool):
        await self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = await self.get_article_store()
        article_earliest_date, article_latest_date = get_earliest_and_latest_dates(article_store)
        log.info("Earliest article for %s on %s: %s", topic, article_earliest_date, article_store[article_earliest_date])
        log.info("Latest article for %s on %s: %s", topic, article_latest_date, article_store[article_latest_date])

        await self.analyze_and_store_scores(article_store)
        sentiment_store = await self.get_sentiment_store()
        sentiment_earliest_date, sentiment_latest_date = get_earliest_and_latest_dates(sentiment_store)
        log.info("Processed sentiment scores for articles from %s to %s", sentiment_earliest_date, sentiment_latest_date)

        await self.get_and_store_stock(company_symbol, start, end)
        stock_store = await self.get_stock_store()
        stock_earliest_date, stock_latest_date = get_earliest_and_latest_dates(stock_store)
        log.info("Earliest stock prices: on %s, open: %s, hight: %s, low: %s, close: %s", 
        stock_earliest_date, 
        stock_store[stock_earliest_date]['1. open'],
        stock_store[stock_earliest_date]['2. high'],
        stock_store[stock_earliest_date]['3. low'],
        stock_store[stock_earliest_date]['4. close'],
        )
        log.info("Latest stock prices: on %s, open: %s, hight: %s, low: %s, close: %s", 
        stock_latest_date, 
        stock_store[stock_latest_date]['1. open'],
        stock_store[stock_latest_date]['2. high'],
        stock_store[stock_latest_date]['3. low'],
        stock_store[stock_latest_date]['4. close'],
        )

        if first_iteration:
            await self.get_and_store_interest(start, end)
        interest_store = await self.get_interest_store()

        if first_iteration:
            await self.get_and_store_cpi(start, end)
        cpi_store = await self.get_cpi_store()

        sentiment_store, stock_store = await self.sync_sentiment_stock(sentiment_store, stock_store, start, end)

        data = await self.RF.construct_pd_data(sentiment_store, stock_store, interest_store, cpi_store)
        next_value = await self.RF.predict_next_stock_value(data)
        print(f"Prediction for {topic}, from learning {start} to {end}. Open, High, Low, Close. ",next_value)
        await self.show_sentiment_stock_graph(sentiment_store, topic, next_value)
        return next_value, await self.get_last_stock()
    
    async def generate_order(self, n_articles, topic, company_symbol, start, end, first_iteration:bool):
        predicted_value, previous_value = await self.generate_next_stock(n_articles, topic, company_symbol, start, end, first_iteration)
        await self.simulator.create_order(predicted_value, previous_value, company_symbol)
    
    async def generate_multiple_orders(self, n_articles, start, end):
        first_iteration = True
        for company_name in self.companies:
            await self.generate_order(n_articles, company_name, self.companies[company_name], start, end, first_iteration)
            first_iteration = False
            await asyncio.sleep(60)
        await self.record_made_orders()
        #self.listen_order_status()

    ############ simulate functions ##############
    async def get_made_orders(self):
        return await self.simulator.get_made_orders()
    
    async def record_made_orders(self):
        await self.simulator.record_made_orders()
    
    async def listen_order_status(self):
        self.simulator.connect()

    ############ arc functions ##############
    async def sync_sentiment_stock(self, sentiment_store:dict, stock_store:dict, start:str, end:str):
        curr_date = start
        while is_date_before(curr_date, end):
            if curr_date not in sentiment_store:
                temp_date = curr_date
                while temp_date not in sentiment_store and temp_date is not start:
                    temp_date = day_before(temp_date)
                if temp_date == start:
                    log.warning(f" temp_date iterating to find the last entry has just hit {start}")
                    sentiment_store[curr_date] = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
                sentiment_store[curr_date] = sentiment_store[temp_date]
            if curr_date not in stock_store:
                temp_date = curr_date
                while temp_date not in stock_store and temp_date is not start:
                    temp_date = day_before(temp_date)
                stock_store[curr_date] = stock_store[temp_date]
            curr_date = increment_date(curr_date)

        log.info(f" length of sentiment score: {len(sentiment_store)}")
        log.info(f" length of stock store: {len(stock_store)}")
        return sentiment_store, stock_store

    ############ news_api functions ##############
    async def get_articles(self, n_articles, topic, date):
        return await self.NAPI._make_request(n_articles=n_articles, topic=topic, date=date)
    
    async def get_and_store_articles_free(self, n_articles, topic, start, end):
        return await self.NAPI.store_articles_free(n_articles, topic, start, end)

    async def get_and_store_articles(self, n_articles, topic, start, end):
        '''
        use for paid version of NewsAPI
        '''
        await self.NAPI.store_articles(n_articles, topic, start, end)
    
    async def get_article_store(self):
        return await self.NAPI.get_article_store()
    
    ############ sentiment analysis functions ##############
    async def get_sentiment_store(self):
        return await self.SNT.get_sentiment_store()

    async def analyze_and_store_scores(self, article_store:dict):
        return await self.SNT.analyze_and_store_scores(article_store)

    async def analyze_article_contents(self, contents):
        return await self.SNT._analyze_article_contents(contents)

    async def analyze(self, text):
        return await self.SNT._analyze(text)

    ############ graphing functions ##############
    async def show_graph(self, sentiment_store:dict, topic):
        return await self.graph.graph_scores(sentiment_store, topic)
    
    async def show_sentiment_stock_graph(self, sentiment_store:dict, topic, prediction):
        return await self.graph.graph_scores_and_prediction(sentiment_store, topic, prediction)
    
    ############ stock_api functions ##############
    async def get_stock_store(self):
        return await self.SAPI.get_stock_store()
    
    async def get_last_stock(self):
        return await self.SAPI.get_last_stock()
    
    async def get_and_store_stock(self, company_symbol:str, start:str, end:str):
        return await self.SAPI.get_and_store_stock(company_symbol, start, end)
    
    async def get_interest_store(self):
        return await self.SAPI.get_interest_store()

    async def get_and_store_interest(self, start:str, end:str):
        return await self.SAPI.get_and_store_interest(start, end)

    async def get_cpi_store(self):
        return await self.SAPI.get_cpi_store()
    
    async def get_and_store_cpi(self, start:str, end:str):
        return await self.SAPI.get_and_store_cpi(start, end)
    




