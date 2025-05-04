import pandas as pd
import numpy as np
import talib

class TechnicalAnalysis:
    def __init__(self, data=None):
        self.data = data
        
    def set_data(self, data):
        """Set the price data to analyze"""
        self.data = data
        
    def calculate_rsi(self, period=14):
        """Calculate Relative Strength Index"""
        if self.data is None:
            raise ValueError("Data not set. Call set_data() first.")
        self.data['RSI'] = talib.RSI(self.data['Close'].values, timeperiod=period)
        return self.data['RSI']
    
    def calculate_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """Calculate Moving Average Convergence Divergence"""
        if self.data is None:
            raise ValueError("Data not set. Call set_data() first.")
        macd, signal, hist = talib.MACD(
            self.data['Close'].values,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        self.data['MACD'] = macd
        self.data['MACD_Signal'] = signal
        self.data['MACD_Hist'] = hist
        return self.data[['MACD', 'MACD_Signal', 'MACD_Hist']]
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if self.data is None:
            raise ValueError("Data not set. Call set_data() first.")
        upper, middle, lower = talib.BBANDS(
            self.data['Close'].values, 
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev
        )
        self.data['BB_Upper'] = upper
        self.data['BB_Middle'] = middle
        self.data['BB_Lower'] = lower
        return self.data[['BB_Upper', 'BB_Middle', 'BB_Lower']]
    
    def get_technical_indicators(self):
        """Calculate all technical indicators"""
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        
        # Add more indicators as needed
        self.data['SMA_50'] = talib.SMA(self.data['Close'].values, timeperiod=50)
        self.data['SMA_200'] = talib.SMA(self.data['Close'].values, timeperiod=200)
        self.data['EMA_20'] = talib.EMA(self.data['Close'].values, timeperiod=20)
        
        return self.data
        
    def get_signals(self):
        """Generate trading signals based on technical indicators"""
        signals = {}
        
        # RSI signals
        if self.data['RSI'].iloc[-1] < 30:
            signals['RSI'] = 'Oversold (Buy Signal)'
        elif self.data['RSI'].iloc[-1] > 70:
            signals['RSI'] = 'Overbought (Sell Signal)'
        else:
            signals['RSI'] = 'Neutral'
            
        # MACD signals
        if self.data['MACD_Hist'].iloc[-1] > 0 and self.data['MACD_Hist'].iloc[-2] <= 0:
            signals['MACD'] = 'Bullish Crossover (Buy Signal)'
        elif self.data['MACD_Hist'].iloc[-1] < 0 and self.data['MACD_Hist'].iloc[-2] >= 0:
            signals['MACD'] = 'Bearish Crossover (Sell Signal)'
        else:
            signals['MACD'] = 'No Crossover'
            
        # Moving Average signals
        if self.data['Close'].iloc[-1] > self.data['SMA_200'].iloc[-1]:
            signals['Trend'] = 'Bullish (Above 200 SMA)'
        else:
            signals['Trend'] = 'Bearish (Below 200 SMA)'
            
        return signals
