import aiohttp
import requests
import typing

class NewsApi():
    def __init__(self):
        self.apiKey = "b46a3358b0ea481c968794201c7e41e6"
    
    def _make_request(self, n_articles:int):
        url = (f'https://newsapi.org/v2/everything?q=economy&from=2023-03-08&sortBy=popularity&apiKey={self.apiKey}')

        response = requests.get(url)
        #want this to be an array of contents
        contents = self.extract_contents(response.json()['articles'], n_articles)
        return contents
    
    def extract_contents(self, article_array, n_articles):
        contents = []
        for i in range(n_articles):
            content = self.extract_content(article_array[i])
            contents.append(content)
        return contents

    def extract_content(self, json:dict):
        return json['content']

