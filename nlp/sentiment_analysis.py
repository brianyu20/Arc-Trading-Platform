import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalysis():
    def __init__(self, config:dict):
        self.config = config
        #nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()

    def _analyze(self, text:str):
        scores = self.analyzer.polarity_scores(text)
        return scores
