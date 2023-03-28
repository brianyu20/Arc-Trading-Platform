from arc.arc_api import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi
from graph.graph import Graph
from ai.random_forest import RandomForest
from sapi.stock_api import StockApi
from trading.simulate import TradeSimulator
from utils.stock_dictionary import sp500_default, sp400_volatile_mid, sp500_volatile_big
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

async def main():
    config = {
        'arc':{
            'companies': sp500_volatile_big
        },
        'sentiment_analysis': {
            'enable': True,
        },
        'news_api':{
            'api_key': "b46a3358b0ea481c968794201c7e41e6",
        },
        'graph': {
            'enable': True,
        },
        'random_forest': {
            'enable': True,
            'n_tree': 100,
            'n_random_state': 42,
        },
        'stock_api':{
            'api_key': "EG59IWIUZ1YFVP8L",
        },
        'simulator': {
            'api_key': "PKZ3OZDN4STTT73XRENB",
            'api_secret': "6fqxWQewRGy3nG8lo1yLd9lBIhUHACpb6bIiD40Y",
            'base_url': 'https://paper-api.alpaca.markets',
            'quantity': 10,
            'trail_percent': 0.2, #alpaca needs a value > 0.1
            'upper_percent': 0.04,
            'watchlist': {
                'enable': False
            }
        }
    }
    SNT = SentimentAnalysis(config)
    NAPI = NewsApi(config)
    G = Graph(config)
    RF = RandomForest(config)
    SAPI = StockApi(config)
    SIMULATOR = TradeSimulator(config)

    arc = ARC(config, SNT, NAPI, G, RF, SAPI, SIMULATOR)
    #await arc.generate_graph(-1, 'UBS', '2023-02-27', '2023-03-25')
    #await arc.generate_next_stock(-1, 'Microsoft', 'MSFT', '2023-02-27', '2023-03-26', True)
    #await arc.generate_order(-1, 'UBS', 'UBS', '2023-02-21', '2023-03-20')

    await arc.generate_multiple_orders(-1, '2023-02-27', '2023-03-26')
    #await arc.listen_order_status()

    # await arc.get_and_store_articles(30, 'Micsrosoft', '2023-02-13', '2023-03-12')
    # article_store = await arc.get_article_store()
    # await arc.analyze_and_store_scores(article_store)
    # sentiment_store = await arc.get_sentiment_store()
    # await arc.get_and_store_stock('MSFT', '2023-02-13', '2023-03-12')
    # stock_store = await arc.get_stock_store()
    # await arc.sync_sentiment_stock(sentiment_store, stock_store, '2023-02-13', '2023-03-12')
    
async def run():
    await main()

if __name__ == '__main__':
    asyncio.run(run())

