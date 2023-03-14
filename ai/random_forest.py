import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import csv
from datetime import datetime, timedelta

class RandomForest():
    def __init__(self, config:dict):
        self.config = config
    
    def predict_next_stock_value(self, data):
    # Split the data into features (X) and labels (y)
        # Split the data into features (X) and labels (y)
        X = data[['pos', 'neg', 'neu', 'compound']]
        X.columns = ['pos', 'neg', 'neu', 'compound']  # Add this line
        y = data['stock']

        # Create a Random Forest model with 100 trees
        rf = RandomForestRegressor(n_estimators=100, random_state=42)

        # Fit the model to the training data
        rf.fit(X, y)

        # Predict the next stock value based on the most recent data point
        last_data_point = data.iloc[-1][['pos', 'neg', 'neu', 'compound']].values.reshape(1, -1)
        next_stock_value = rf.predict(last_data_point)

        return next_stock_value[0]
    
    def construct_pd_data(self, sentiment_store, stock_store):
        pos_array = []
        neg_array = []
        neu_array = []
        compound_array = []
        stock = []
        for date in sorted(sentiment_store.keys()):
            pos = 0
            neg = 0
            neu = 0
            compound = 0
            for sentiment_packet in sentiment_store[date]:
                pos += sentiment_packet['pos']
                neg += sentiment_packet['neg']
                neu += sentiment_packet['neu']
                compound += sentiment_packet['compound']
            pos_array.append(pos)
            neg_array.append(neg)
            neu_array.append(neu)
            compound_array.append(compound)
        data = pd.DataFrame({
            'pos' : pos_array,
            'neg' : neg_array,
            'neu' : neu_array,
            'compound' : compound_array,
            'stock': [271.32, 272.17, 269.32, 262.15, 258.06 ,252.67, 251.51, 249.22, 250.16, 249.42, 246.27, 251.11, 255.29, 256.87, 254.15, 253.70]
        })
        
        return data
    
    def get_stock_data(stock_data_dict):
        opens = []
        highs = []
        lows = []
        closes = []
        for date in stock_data_dict:
            opens.append(float(stock_data_dict[date]["1. open"]))
            highs.append(float(stock_data_dict[date]["2. high"]))
            lows.append(float(stock_data_dict[date]["3. low"]))
            closes.append(float(stock_data_dict[date]["4. close"]))
        return opens, highs, lows, closes

