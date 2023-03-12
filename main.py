from arc.arc import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi
from graph.graph import Graph
from ai.random_forest import RandomForest
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
    RF = RandomForest(config)

    arc = ARC(config, SNT, NAPI, G, RF)
    #arc.generate_graph(30, 'Nasdaq', '2023-02-12', '2023-03-11')
    arc.get_next_stock(30, 'Microsoft', '2023-02-12', '2023-03-11')

main()
