import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_ingestion import DataIngestion
from technical_analysis import TechnicalAnalysis
from datetime import datetime, timedelta
import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class SimpleMAStrategy(Strategy):
    """Simple Moving Average Crossover Strategy"""
    
    # Define parameters
    n1 = 50  # Fast MA
    n2 = 200  # Slow MA
    
    def init(self):
        # Calculate moving averages
        self.ma1 = self.I(backtesting.lib.SMA, self.data.Close, self.n1)
        self.ma2 = self.I(backtesting.lib.SMA, self.data.Close, self.n2)
        
    def next(self):
        # If fast MA crosses above slow MA, buy
        if crossover(self.ma1, self.ma2):
            self.buy()
        # If fast MA crosses below slow MA, sell
        elif crossover(self.ma2, self.ma1):
            self.sell()

class RSIStrategy(Strategy):
    """RSI Strategy"""
    
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    
    def init(self):
        # Calculate RSI
        self.rsi = self.I(backtesting.lib.RSI, self.data.Close, self.rsi_period)
        
    def next(self):
        # If RSI crosses below oversold level, buy
        if self.rsi[-2] > self.rsi_oversold and self.rsi[-1] <= self.rsi_oversold:
            self.buy()
        # If RSI crosses above overbought level, sell
        elif self.rsi[-2] < self.rsi_overbought and self.rsi[-1] >= self.rsi_overbought:
            self.sell()

class BacktestEngine:
    def __init__(self):
        self.data_ingestion = DataIngestion()
        self.technical_analysis = TechnicalAnalysis()
        
    def run_backtest(self, ticker, strategy_class, start_date=None, end_date=None, **kwargs):
        """Run backtest for a given ticker and strategy"""
        # Get data
        if start_date is None:
            start_date = datetime.today() - timedelta(days=365*3)  # 3 years
        if end_date is None:
            end_date = datetime.today()
            
        data = self.data_ingestion.get_stock_price_data(ticker, period=f'{(end_date - start_date).days}d')
        
        # Format data for backtesting
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Create and run backtest
        bt = Backtest(data, strategy_class, cash=10000, commission=.002, **kwargs)
        stats = bt.run()
        
        return stats, bt
    
    def optimize_strategy(self, ticker, strategy_class, param_grid, start_date=None, end_date=None):
        """Optimize strategy parameters"""
        # Get data
        if start_date is None:
            start_date = datetime.today() - timedelta(days=365*3)  # 3 years
        if end_date is None:
            end_date = datetime.today()
            
        data = self.data_ingestion.get_stock_price_data(ticker, period=f'{(end_date - start_date).days}d')
        
        # Format data for backtesting
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Create backtest
        bt = Backtest(data, strategy_class, cash=10000, commission=.002)
        
        # Optimize
        stats = bt.optimize(**param_grid, maximize='Sharpe Ratio')
        
        return stats, bt
        
    def plot_results(self, bt):
        """Plot backtest results"""
        bt.plot(open_browser=False)
        
    def evaluate_multiple_strategies(self, ticker, strategies, start_date=None, end_date=None):
        """Compare multiple strategies"""
        results = {}
        
        for name, strategy_class in strategies.items():
            stats, bt = self.run_backtest(ticker, strategy_class, start_date, end_date)
            results[name] = {
                'stats': stats,
                'bt': bt
            }
            
        # Compare key metrics
        comparison = pd.DataFrame({
            name: {
                'Return [%]': results[name]['stats']['Return [%]'],
                'Sharpe Ratio': results[name]['stats']['Sharpe Ratio'],
                'Max Drawdown [%]': results[name]['stats']['Max. Drawdown [%]'],
                'Win Rate [%]': results[name]['stats']['Win Rate [%]']
            } for name in strategies.keys()
        })
        
        return results, comparison
