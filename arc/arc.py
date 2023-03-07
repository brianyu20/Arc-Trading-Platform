
class ARC():
    def __init__(self, config:dict, SNT):
        self.SNT = SNT
    
    def testing(self):
        return self.SNT.get_config()