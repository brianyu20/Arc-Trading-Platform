import matplotlib.pyplot as plt
import logging

log = logging.getLogger(__name__)

class Graph():
    def __init__(self, config:dict):
        log.info("Running Graph")
        self.config = config

    def graph_scores(self, sentiment_store:dict):
        log.info("Graphing sentiment store")
        fig, ax = plt.subplots(figsize=(10, 6))
    
        # Create lists to store the values for the plot
        dates = []
        neg = []
        neu = []
        pos = []
        compound = []
        
        # Loop through the dictionary and append values to the lists
        for date in sorted(sentiment_store.keys()):
            values = sentiment_store[date]
            dates.append(date)
            neg.append(self.add_scores(values, 'neg'))
            neu.append(self.add_scores(values, 'neu'))
            pos.append(self.add_scores(values, 'pos'))
            compound.append(self.add_scores(values, 'compound'))
            
        # Set up the x-axis and y-axis labels
        ax.set_ylabel("Sentiment Score")
        ax.set_xlabel("Date")
        
        # Create a line plot for each sentiment score
        ax.plot(dates, neg, color="red", label="Negative")
        ax.plot(dates, neu, color="grey", label="Neutral")
        ax.plot(dates, pos, color="green", label="Positive")
        ax.plot(dates, compound, color="blue", label="Compound")
        
        # Add a legend and show the plot
        ax.legend()
        #plt.show()
        plt.savefig('data.png')
    
    def add_scores(self, score_array:list, score_type:str):
        added_score = 0
        for i in range(len(score_array)):
            added_score += score_array[i][score_type]
        return added_score