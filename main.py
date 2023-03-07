from arc.arc import ARC
from nlp.sentiment_analysis import SentimentAnalysis

def main():
    config = {
        'nlp': {
            'field': 'N/A'
        }
    }
    SNT = SentimentAnalysis(config)
    arc = ARC(config, SNT)


main()
