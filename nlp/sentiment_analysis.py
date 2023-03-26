import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import logging
import json
import asyncio

log = logging.getLogger(__name__)
handler = logging.FileHandler('sentiment_report.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

class SentimentAnalysis():
    def __init__(self, config:dict):
        log.info("Running SentimentAnalysis")
        self.config = config
        #nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_store = {} # key: date, value: array of sentiment scores from the date

        with open('sentiment_report.log', 'w'):
            pass
    
    async def get_sentiment_store(self):
        #json_sentiment_store = json.dumps(self.sentiment_store, indent=2)
        return self.sentiment_store
    
    async def analyze_and_store_scores(self, article_store:dict):
        self.sentiment_store = {}
        for date in article_store:
            log.info(f"Computing sentiment scores for articles published on {date}")
            content_array = article_store[date]
            analyzed = await self._analyze_article_contents(content_array)
            # print(analyzed)
            self.sentiment_store[date] = analyzed
        log.info("Completed sentiment score calculation and storage")

    async def _analyze(self, text:str):
        score = self.analyzer.polarity_scores(text)
        return score

    async def _analyze_article_contents(self, contents:list):
        ''' Takes a list of contents'''
        scores = []
        for i in range(len(contents)):
            content = contents[i][:198]
            score = await self._analyze(content)
            scores.append(score)
        return scores

# sa = SentimentAnalysis({'key' : 'value'})
# score = sa._analyze("Credit Suisses ability to shoot itself in the foot is legendary but you would have thought its shareholders would have learned not to make matters worse. But no, the chairman of Saudi National Bank")
# print(score)