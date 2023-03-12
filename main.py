from arc.arc import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi
from graph.graph import Graph
import json
import logging

logging.basicConfig(level=logging.INFO)

def main():
    config = {
        'nlp': {
            'field': 'N/A'
        }
    }
    SNT = SentimentAnalysis(config)
    NAPI = NewsApi()
    G = Graph(config)

    arc = ARC(config, SNT, NAPI, G)
    arc.generate_graph(-1, 'Microsoft', '2023-02-12', '2023-03-11')

main()
