import aiohttp
import requests
import typing
from datetime import datetime, timedelta
import json

class NewsApi():
    def __init__(self):
        self.apiKey = "b46a3358b0ea481c968794201c7e41e6"
        self.article_store:dict = {} # key = date; value = list of contents of articles from the key date
    
    def get_article_store(self):
        return self.article_store
    
    def store_articles(self, n_articles:int, topic:str, start:str, end:str):
        ''' inclusive of start date, exclusive of end date'''
        curr_date = start
        while curr_date != end:
            contents = self._make_request(n_articles=n_articles, topic=topic, date=curr_date)
            self.article_store[curr_date] = contents
            curr_date = self.increment_date(curr_date)
        
        # json_dict = json.dumps(self.article_store, indent=2)
        # print(json_dict)

    def _make_request(self, n_articles:int, topic:str, date:str):
        url = (f'https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy=popularity&apiKey={self.apiKey}')

        response = requests.get(url)
        # this is an array of just the contents from the response
        contents = self.extract_contents(response.json()['articles'], n_articles)
        
        return contents
    
    def extract_contents(self, article_array, n_articles):
        contents = []
        n_articles = n_articles if n_articles > -1 else len(article_array)
        for i in range(n_articles):
            content = self.extract_content(article_array[i])
            contents.append(content)
        return contents

    def extract_content(self, json:dict):
        return json['content']

    def increment_date(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        incremented_date = date + timedelta(days=1)
        return incremented_date.strftime('%Y-%m-%d')