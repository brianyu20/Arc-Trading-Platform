
class ARC():
    def __init__(self, config:dict, SNT, NAPI):
        self.SNT = SNT
        self.NAPI = NAPI
    
    def testing(self):
        return self.SNT.get_config()
    
    ############ news_api functions ##############
    def get_articles(self, n_articles, topic, date):
        return self.NAPI._make_request(n_articles=n_articles, topic=topic, date=date)
    
    def get_and_store_articles(self, n_articles, topic, start, end):
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

