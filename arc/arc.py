import logging

log = logging.getLogger(__name__)

class ARC():
    def __init__(self, config:dict, SNT, NAPI, G, RF):
        log.info("Running ARC")
        self.SNT = SNT
        self.NAPI = NAPI
        self.graph = G
        self.RF = RF

    ############ Process functions ##############
    def generate_graph(self, n_articles, topic, start, end):
        self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = self.get_article_store()

        self.analyze_and_store_scores(article_store)
        sentiment_store = self.get_sentiment_store()
        
        self.show_graph(sentiment_store)
    
    def get_next_stock(self, n_articles, topic, start, end):
        self.get_and_store_articles_free(n_articles, topic, start, end)
        article_store = self.get_article_store()

        self.analyze_and_store_scores(article_store)
        sentiment_store = self.get_sentiment_store()

        data = self.RF.construct_pd_data(sentiment_store)
        next_value = self.RF.predict_next_stock_value(data)
        print(next_value)

        
    ############ news_api functions ##############
    def get_articles(self, n_articles, topic, date):
        return self.NAPI._make_request(n_articles=n_articles, topic=topic, date=date)
    
    def get_and_store_articles_free(self, n_articles, topic, start, end):
        return self.NAPI.store_articles_free(n_articles, topic, start, end)

    def get_and_store_articles(self, n_articles, topic, start, end):
        '''
        use for paid version of NewsAPI
        '''
        self.NAPI.store_articles(n_articles, topic, start, end)
    
    def get_article_store(self):
        return self.NAPI.get_article_store()
    
    ############ sentiment analysis functions ##############
    def get_sentiment_store(self):
        return self.SNT.get_sentiment_store()

    def analyze_and_store_scores(self, article_store:dict):
        return self.SNT.analyze_and_store_scores(article_store)

    def analyze_article_contents(self, contents):
        return self.SNT._analyze_article_contents(contents)

    def analyze(self, text):
        return self.SNT._analyze(text)

    ############ sentiment analysis functions ##############
    def show_graph(self, sentiment_store:dict):
        return self.graph.graph_scores(sentiment_store)