import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalysis():
    def __init__(self, config:dict):
        self.config = config
        #nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()

    def _analyze(self, text:str):
        score = self.analyzer.polarity_scores(text)
        return score

    def _analyze_article_contents(self, contents:list):
        scores = []
        for i in range(len(contents)):
            content = contents[i][:198]
            score = self._analyze(content)
            scores.append(score)
        return scores