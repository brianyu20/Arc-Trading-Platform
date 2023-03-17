import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import json
import logging

log = logging.getLogger(__name__)

class RandomForest():
    def __init__(self, config:dict):
        self.config = config
    
    def predict_next_stock_value(self, data):
        log.info("Running model")
        # Split the data into features (X) and labels (y)
        X_sentiment = data[['pos', 'neg', 'neu', 'compound']]
        X_stock = data[['open', 'high', 'low', 'close', 'volume', 'interest', 'cpi']]
        y = data[['next_open', 'next_high', 'next_low', 'next_close']]

        # Create a Random Forest model with 100 trees
        rf = RandomForestRegressor(n_estimators=100, random_state=42)

        # Fit the model to the training data
        rf.fit(X_sentiment.join(X_stock), y)

        # Predict the next stock values based on the most recent data point
        last_data_point = data.iloc[-1][['pos', 'neg', 'neu', 'compound', 'open', 'high', 'low', 'close', 'volume', 'interest', 'cpi']].values.reshape(1, -1)
        next_stock_values = rf.predict(last_data_point)

        return next_stock_values[0]
    
    def construct_pd_data(self, sentiment_store, stock_store, interest_store, cpi_store):
        log.info("Parsing stores to build arrays...")
        pos_array = []
        neg_array = []
        neu_array = []
        compound_array = []
        opens, highs, lows, closes, volumes = self.get_stock_data(stock_store)
        interests = self.get_interest_data(interest_store)
        cpis = self.get_cpi_data(cpi_store)
        next_opens = opens[1:] + [np.nan]
        next_highs = highs[1:] + [np.nan]
        next_lows = lows[1:] + [np.nan]
        next_closes = closes[1:] + [np.nan]
        
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
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes,
            'interest': interests,
            'cpi': cpis,
            'next_open': next_opens,
            'next_high': next_highs,
            'next_low': next_lows,
            'next_close': next_closes
        })
        
        data.dropna(subset=['next_open', 'next_high', 'next_low', 'next_close'], inplace=True)
        
        return data
    
    def get_stock_data(self, stock_store):
        log.info("Parsing stocks")
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        for date in stock_store:
            open = float(stock_store[date]["1. open"])
            close = float(stock_store[date]["4. close"])
            log.info(f"Extracted {date}: open: {open}, close:{close}")
            opens.append(float(stock_store[date]["1. open"]))
            highs.append(float(stock_store[date]["2. high"]))
            lows.append(float(stock_store[date]["3. low"]))
            closes.append(float(stock_store[date]["4. close"]))
            volumes.append(float(stock_store[date]["6. volume"]))
        return opens, highs, lows, closes, volumes

    def get_interest_data(self, interest_store):
        log.info("Parsing interests")
        interests = []
        for date in interest_store:
            interests.append(interest_store[date])
        return interests

    def get_cpi_data(self, cpi_store):
        log.info("Parsing Customer Price Index")
        cpis = []
        for date in cpi_store:
            cpis.append(cpi_store[date])
        return cpis