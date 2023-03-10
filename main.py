from arc.arc import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi

def main():
    config = {
        'nlp': {
            'field': 'N/A'
        }
    }
    SNT = SentimentAnalysis(config)
    NAPI = NewsApi()
    arc = ARC(config, SNT, NAPI)
    content = arc.get_article()
    content.split('[')
    content = content[:197]
    print(content)
    score = arc.analyze(content)
    print(score)

main()
