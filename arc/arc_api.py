import logging
import asyncio
from datetime import datetime, timedelta
from sapi import stock_api
log = logging.getLogger(__name__)

class ARC():
    def __init__(self, config:dict, SNT, NAPI, G, RF, SAPI):
        log.info("Running ARC")
        self.SNT = SNT
        self.NAPI = NAPI
        self.graph = G
        self.RF = RF
        self.SAPI: stock_api = SAPI

    ############ Process functions ##############
    async def generate_graph(self, n_articles, topic, start, end):
        await self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = await self.get_article_store()

        await self.analyze_and_store_scores(article_store)
        sentiment_store = await self.get_sentiment_store()
        
        await self.show_graph(sentiment_store, topic)
    
    async def generate_next_stock(self, n_articles, topic, company_symbol, start, end):
        await self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = await self.get_article_store()

        await self.analyze_and_store_scores(article_store)
        sentiment_store = await self.get_sentiment_store()

        await self.get_and_store_stock(company_symbol, start, end)
        stock_store = await self.get_stock_store()

        await self.get_and_store_interest(start, end)
        interest_store = await self.get_interest_store()

        await self.get_and_store_cpi(start, end)
        cpi_store = await self.get_cpi_store()

        sentiment_store, stock_store = await self.sync_sentiment_stock(sentiment_store, stock_store, start, end)

        data = self.RF.construct_pd_data(sentiment_store, stock_store, interest_store, cpi_store)
        next_value = self.RF.predict_next_stock_value(data)
        print(f"Prediction for {topic}, from learning {start} to {end}. Open, High, Low, Close. ",next_value)
        await self.show_sentiment_stock_graph(sentiment_store, topic, next_value)

    ############ arc functions ##############
    async def sync_sentiment_stock(self, sentiment_store:dict, stock_store:dict, start:str, end:str):
        curr_date = start
        while self.is_date_before(curr_date, end):
            if curr_date not in sentiment_store:
                temp_date = curr_date
                while temp_date not in sentiment_store and temp_date is not start:
                    temp_date = self.day_before(temp_date)
                if temp_date == start:
                    log.warning(f" temp_date iterating to find the last entry has just hit {start}")
                    sentiment_store[curr_date] = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
                sentiment_store[curr_date] = sentiment_store[temp_date]
            if curr_date not in stock_store:
                temp_date = curr_date
                while temp_date not in stock_store and temp_date is not start:
                    temp_date = self.day_before(temp_date)
                stock_store[curr_date] = stock_store[temp_date]
            curr_date = self.increment_date(curr_date)

        log.info(f" length of sentiment score: {len(sentiment_store)}")
        log.info(f" length of stock store: {len(stock_store)}")
        return sentiment_store, stock_store

    ############ news_api functions ##############
    async def get_articles(self, n_articles, topic, date):
        return self.NAPI._make_request(n_articles=n_articles, topic=topic, date=date)
    
    async def get_and_store_articles_free(self, n_articles, topic, start, end):
        return self.NAPI.store_articles_free(n_articles, topic, start, end)

    async def get_and_store_articles(self, n_articles, topic, start, end):
        '''
        use for paid version of NewsAPI
        '''
        self.NAPI.store_articles(n_articles, topic, start, end)
    
    async def get_article_store(self):
        return self.NAPI.get_article_store()
    
    ############ sentiment analysis functions ##############
    async def get_sentiment_store(self):
        return self.SNT.get_sentiment_store()

    async def analyze_and_store_scores(self, article_store:dict):
        return self.SNT.analyze_and_store_scores(article_store)

    async def analyze_article_contents(self, contents):
        return self.SNT._analyze_article_contents(contents)

    async def analyze(self, text):
        return self.SNT._analyze(text)

    ############ graphing functions ##############
    async def show_graph(self, sentiment_store:dict, topic):
        return self.graph.graph_scores(sentiment_store, topic)
    
    async def show_sentiment_stock_graph(self, sentiment_store:dict, topic, prediction):
        return self.graph.graph_scores_and_prediction(sentiment_store, topic, prediction)
    
    ############ stock_api functions ##############
    async def get_stock_store(self):
        return self.SAPI.get_stock_store()
    
    async def get_and_store_stock(self, company_symbol:str, start:str, end:str):
        return self.SAPI.get_and_store_stock(company_symbol, start, end)
    
    async def get_interest_store(self):
        return self.SAPI.get_interest_store()

    async def get_and_store_interest(self, start:str, end:str):
        return self.SAPI.get_and_store_interest(start, end)

    async def get_cpi_store(self):
        return self.SAPI.get_cpi_store()
    
    async def get_and_store_cpi(self, start:str, end:str):
        return self.SAPI.get_and_store_cpi(start, end)
    
    ############ helper functions ##############
    def increment_date(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        incremented_date = date + timedelta(days=1)
        return incremented_date.strftime('%Y-%m-%d')
    
    def is_date_before(self, date1_str, date2_str):
        # Convert the date strings to datetime objects
        date1 = datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.strptime(date2_str, '%Y-%m-%d')

        # Check if date1 is before date2
        return date1 <= date2
    
    def day_before(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        day_before = date + timedelta(days=-1)
        return day_before.strftime('%Y-%m-%d')



