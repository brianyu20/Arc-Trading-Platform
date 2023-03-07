
class SentimentAnalysis():
    def __init__(self, config:dict):
        self.config = config

    def get_config(self):
        return self.config

SA = SentimentAnalysis({'a': 'b'})
print(SA.get_config())