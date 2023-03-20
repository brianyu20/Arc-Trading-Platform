from arc.arc_api import ARC
from nlp.sentiment_analysis import SentimentAnalysis
from napi.news_api import NewsApi
from graph.graph import Graph
from ai.random_forest import RandomForest
from sapi.stock_api import StockApi
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)


async def main():
    config = {
        'nlp': {
            'field': 'N/A'
        }
    }
    SNT = SentimentAnalysis(config)
    NAPI = NewsApi()
    G = Graph(config)
    RF = RandomForest(config)
    SAPI = StockApi(config)

    arc = ARC(config, SNT, NAPI, G, RF, SAPI)
    #await arc.generate_graph(-1, 'Credit Suisse', '2023-02-16', '2023-03-15')
    await arc.generate_next_stock(-1, 'Tesla', 'TSLA', '2023-02-21', '2023-03-20')

    # await arc.get_and_store_articles(30, 'Microsoft', '2023-02-13', '2023-03-12')
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
