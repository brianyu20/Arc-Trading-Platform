import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import logging
import json

log = logging.getLogger(__name__)

class SentimentAnalysis():
    def __init__(self, config:dict):
        log.info("Running SentimentAnalysis")
        self.config = config
        #nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_store = {} # key: date, value: array of sentiment scores from the date
    
    def get_sentiment_store(self):
        #json_sentiment_store = json.dumps(self.sentiment_store, indent=2)
        return self.sentiment_store
    
    def analyze_and_store_scores(self, article_store:dict):
        for date in article_store:
            log.info(f"Computing sentiment scores for articles published on {date}")
            content_array = article_store[date]
            self.sentiment_store[date] = self._analyze_article_contents(content_array)
        log.info("Completed sentiment score calculation and storage")

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

# sa = SentimentAnalysis({'key' : 'value'})
# score = sa._analyze("Credit Suisses ability to shoot itself in the foot is legendary but you would have thought its shareholders would have learned not to make matters worse. But no, the chairman of Saudi National Bank")
# print(score)