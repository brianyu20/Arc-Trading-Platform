import aiohttp
import requests
import typing
from datetime import datetime, timedelta
import json
import logging
import asyncio

log = logging.getLogger(__name__)

class NewsApiError(Exception):
    pass

class NewsApi():
    def __init__(self):
        log.info("Running NewsAPI")
        self.apiKey = "b46a3358b0ea481c968794201c7e41e6"
        self.article_store:dict = {} # key = date; value = list of contents of articles from the key date
    
    async def get_article_store(self):
        return self.article_store
    
    async def store_articles_free(self, n_articles:int, topic:str, start:str, end:str):
        url = (f'https://newsapi.org/v2/everything?q={topic}&from={start}&to={end}&sortBy=popularity&apiKey={self.apiKey}')
        print(url)
        log.info(f"Making get request to {url}")
        response = requests.get(url)
        if response.json()['status'] == 'error':
            log.error(f"received status: {response.json()['status']}. Msg: {response.json()['message']}. Exiting")
            return

        contents_and_dates = self.extract_contents_and_date(response.json()['articles'], n_articles)
        for date, content in contents_and_dates:
            curr_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
            log.info(f"Processing articles pusblished on {curr_date}")
            if curr_date not in self.article_store:
                self.article_store[curr_date] = []
            self.article_store[curr_date].append(content)
        log.info(f"Completed processing {topic} articles from {start} to {end}")
    
    async def store_articles(self, n_articles:int, topic:str, start:str, end:str):
        ''' 
        inclusive of start date, exclusive of end date
        Can fail if news api is on free developer mode and requests > 100 for the day
        '''
        
        curr_date = start
        while curr_date != end:
            contents = await self._make_request(n_articles=n_articles, topic=topic, date=curr_date)
            self.article_store[curr_date] = contents
            curr_date = self.increment_date(curr_date)

    async def _make_request(self, n_articles:int, topic:str, date:str):
        url = (f'https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy=popularity&apiKey={self.apiKey}')

        response = requests.get(url)
        # this is an array of just the contents from the response
        contents = self.extract_contents(response.json()['articles'], n_articles)

        return contents
    
    def extract_contents_and_date(self, article_array, n_articles):
        contents_and_dates = []
        n_articles = n_articles if n_articles > -1 else len(article_array)
        for i in range(n_articles):
            content = self.extract_content(article_array[i])
            date = self.extract_date(article_array[i])
            content_and_date = (date, content)
            contents_and_dates.append(content_and_date)
        return contents_and_dates

    def extract_contents(self, article_array, n_articles):
        contents = []
        n_articles = n_articles if n_articles > -1 else len(article_array)
        for i in range(n_articles):
            content = self.extract_content(article_array[i])
            contents.append(content)
        return contents

    def extract_content(self, json:dict):
        return json['content']
    
    def extract_date(self, json:dict):
        return json['publishedAt']

    def increment_date(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        incremented_date = date + timedelta(days=1)
        return incremented_date.strftime('%Y-%m-%d')