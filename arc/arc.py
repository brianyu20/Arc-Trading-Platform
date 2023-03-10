
class ARC():
    def __init__(self, config:dict, SNT, NAPI):
        self.SNT = SNT
        self.NAPI = NAPI
    
    def testing(self):
        return self.SNT.get_config()
    
    ############ news_api functions ##############
    def get_articles(self, n_articles):
        return self.NAPI._make_request(n_articles=n_articles)
    
    ############ sentiment analysis functions ##############
    def analyze_article_contents(self, contents):
        return self.SNT._analyze_article_contents(contents)

    def analyze(self, text):
        return self.SNT._analyze(text)

