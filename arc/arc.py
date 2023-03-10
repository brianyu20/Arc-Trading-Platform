
class ARC():
    def __init__(self, config:dict, SNT, NAPI):
        self.SNT = SNT
        self.NAPI = NAPI
    
    def testing(self):
        return self.SNT.get_config()
    
    def get_article(self):
        return self.NAPI.make_request()
    
    def analyze(self, text):
        return self.SNT._analyze(text)

