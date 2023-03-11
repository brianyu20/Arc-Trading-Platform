import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalysis():
    def __init__(self, config:dict):
        self.config = config
        #nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_store = {} # key: date, value: array of sentiment scores from the date
    
    def get_sentiment_store(self):
        return self.sentiment_store
    
    def analyze_and_store_scores(self, article_store:dict):
        for date in article_store:
            content_array = article_store[date]
            self.sentiment_store[date] = self._analyze_article_contents(content_array)
            #print(self.sentiment_store[date])

    def _analyze(self, text:str):
        score = self.analyzer.polarity_scores(text)
        return score

    def _analyze_article_contents(self, contents:list):
        ''' Takes a list of contents'''
        scores = []
        for i in range(len(contents)):
            content = contents[i][:198]
            score = self._analyze(content)
            scores.append(score)
        return scores