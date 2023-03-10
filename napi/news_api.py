import aiohttp
import requests
import typing

class NewsApi():
    def __init__(self):
        self.apiKey = "b46a3358b0ea481c968794201c7e41e6"
    
    def make_request(self):
        url = (f'https://newsapi.org/v2/everything?q=economy&from=2023-03-08&sortBy=popularity&apiKey={self.apiKey}')

        response = requests.get(url)
        content = self.extract_content(response.json()['articles'][0])
        return content
    
    def extract_content(self, json:dict):
        return json['content']

