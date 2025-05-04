import pandas as pd
import numpy as np
import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from config import ALPHA_VANTAGE_API_KEY

class DataIngestion:
    def __init__(self):
        self.av_ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        self.av_fd = FundamentalData(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        
    def get_stock_price_data(self, ticker, period='1y'):
        """Get historical stock price data using yfinance"""
        data = yf.download(ticker, period=period, auto_adjust=True)
        return data
    
    def get_alpha_vantage_data(self, ticker):
        """Get data from Alpha Vantage API"""
        data, meta_data = self.av_ts.get_daily(symbol=ticker, outputsize='full')
        return data
        
    def get_quote(self, ticker):
        """Get real-time quote using Alpha Vantage"""
        try:
            data, meta_data = self.av_ts.get_quote_endpoint(symbol=ticker)
            return {
                "c": float(data["05. price"].iloc[0]),  # Current price - fixed deprecation warning
                "o": float(data["02. open"].iloc[0]),   # Open price - fixed deprecation warning
                "h": float(data["03. high"].iloc[0]),   # High price - fixed deprecation warning
                "l": float(data["04. low"].iloc[0]),    # Low price - fixed deprecation warning
                "pc": float(data["08. previous close"].iloc[0])  # Previous close - fixed deprecation warning
            }
        except Exception as e:
            print(f"Error getting quote: {str(e)}")
            # Fallback to yfinance
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(period="2d")
            if len(hist) >= 2:
                return {
                    "c": hist.iloc[-1]["Close"],
                    "o": hist.iloc[-1]["Open"],
                    "h": hist.iloc[-1]["High"],
                    "l": hist.iloc[-1]["Low"],
                    "pc": hist.iloc[-2]["Close"]
                }
            else:
                return {"error": "Failed to get quote data"}
    
    def get_financials(self, ticker):
        """Get financial statements"""
        income_statement, _ = self.av_fd.get_income_statement_annual(ticker)
        balance_sheet, _ = self.av_fd.get_balance_sheet_annual(ticker)
        cash_flow, _ = self.av_fd.get_cash_flow_annual(ticker)
        return {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow
        }
    
    def get_company_news(self, ticker, from_date, to_date):
        """Get company news using yfinance as a fallback"""
        ticker_data = yf.Ticker(ticker)
        news = ticker_data.news
        return news
    

    def get_income_statement(self, ticker):
        """Get income statement data"""
        try:
            financials = self.get_financials(ticker)
            if 'income_statement' in financials:
                return financials['income_statement']
            return None
        except Exception as e:
            print(f"Error fetching income statement: {str(e)}")
            return None

    def get_balance_sheet(self, ticker):
        """Get balance sheet data"""
        try:
            financials = self.get_financials(ticker)
            if 'balance_sheet' in financials:
                return financials['balance_sheet']
            return None
        except Exception as e:
            print(f"Error fetching balance sheet: {str(e)}")
            return None
            
    def get_cash_flow(self, ticker):
        """Get cash flow data"""
        try:
            financials = self.get_financials(ticker)
            if 'cash_flow' in financials:
                return financials['cash_flow']
            return None
        except Exception as e:
            print(f"Error fetching cash flow: {str(e)}")
            return None
