from arc.arc import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi
import json

def main():
    config = {
        'nlp': {
            'field': 'N/A'
        }
    }
    SNT = SentimentAnalysis(config)
    NAPI = NewsApi()
    arc = ARC(config, SNT, NAPI)
    arc.get_and_store_articles(2, 'economy', '2023-03-01', '2023-03-11')
    article_store = arc.get_article_store()

    arc.analyze_and_store_scores(article_store)
    sentiment_store = arc.get_sentiment_store()

    json_sentiment_store = json.dumps(sentiment_store, indent=2)
    print(json_sentiment_store)

main()
