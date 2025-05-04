"""
Custom implementation of InvestmentAgent that uses Google Generative AI (Gemini) directly
"""
import json
from typing import List, Dict, Any, Callable
import google.generativeai as genai
import yfinance as yf
import time
from config import GOOGLE_API_KEY
from data_ingestion import DataIngestion
from datetime import datetime, timedelta

class Tool:
    """Simple tool definition class"""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

class GeminiInvestmentAgent:
    def __init__(self):
        # Initialize data ingestion for Alpha Vantage
        self.data_ingestion = DataIngestion()
        self.technical_analysis = None  # Initialize as needed
        self.price_predictor = None  # Initialize as needed
        
        # Configure Google Generative AI
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Use models directly from the list of available models
        model_candidates = [
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-pro-vision",  # Try this as fallback
            "models/gemini-2.0-pro-exp"  # Experimental model as last resort
        ]
        
        # Try each model until one works
        self.model = None
        for model_name in model_candidates:
            try:
                print(f"Attempting to initialize model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                test_response = self.model.generate_content("Hello")
                print(f"Successfully connected to model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to initialize model {model_name}: {str(e)}")
        
        if self.model is None:
            print("WARNING: Could not initialize any Gemini model!")
            # Set a placeholder model - this will fail later but prevents immediate crash
            self.model = genai.GenerativeModel(model_candidates[0])
        
        # Initialize tools
        self.tools = self._create_tools()
        
    def _create_tools(self) -> List[Dict[str, Any]]:
        """Create tools for the agent to use"""
        tools = []
        
        # Real stock data tool using Alpha Vantage
        def get_stock_data(ticker):
            """Get basic stock data"""
            try:
                # Get real-time quote from Alpha Vantage
                quote = self.data_ingestion.get_quote(ticker)
                
                # Get some historical data
                hist_data = self.data_ingestion.get_stock_price_data(ticker, period='1mo')
                
                # Calculate key metrics
                monthly_change = None
                if len(hist_data) > 0:
                    monthly_change = round(((hist_data.iloc[-1]["Close"] - hist_data.iloc[0]["Close"]) / 
                                          hist_data.iloc[0]["Close"]) * 100, 2)
                
                # Format the response
                return json.dumps({
                    "ticker": ticker,
                    "current_price": quote.get("c", "N/A"),
                    "previous_close": quote.get("pc", "N/A"),
                    "daily_change": round(((quote.get("c", 0) - quote.get("pc", 0)) / quote.get("pc", 1)) * 100, 2) 
                                    if "c" in quote and "pc" in quote else "N/A",
                    "daily_range": f"{quote.get('l', 'N/A')} - {quote.get('h', 'N/A')}",
                    "monthly_change_percent": monthly_change
                })
            except Exception as e:
                return f"Error fetching stock data: {str(e)}"
        
        tools.append({
            "name": "StockData",
            "description": "Get basic stock data for a ticker symbol. Input should be a valid ticker symbol like AAPL.",
            "function": get_stock_data
        })
        
        # Financial data tool using Alpha Vantage
        def get_financial_metrics(ticker):
            """Get key financial metrics"""
            try:
                financials = self.data_ingestion.get_financials(ticker)
                
                # Extract key metrics from financial statements
                income = financials.get("income_statement")
                balance = financials.get("balance_sheet")
                
                metrics = {"ticker": ticker}
                
                # Safe extraction of financial metrics
                if income is not None and not income.empty:
                    metrics["revenue"] = float(income["totalRevenue"].iloc[0]) if "totalRevenue" in income else "N/A"
                    metrics["net_income"] = float(income["netIncome"].iloc[0]) if "netIncome" in income else "N/A"
                    metrics["eps"] = float(income["reportedEPS"].iloc[0]) if "reportedEPS" in income else "N/A"
                
                if balance is not None and not balance.empty:
                    metrics["total_assets"] = float(balance["totalAssets"].iloc[0]) if "totalAssets" in balance else "N/A"
                    metrics["total_liabilities"] = float(balance["totalLiabilities"].iloc[0]) if "totalLiabilities" in balance else "N/A"
                
                return json.dumps(metrics)
            except Exception as e:
                return f"Error fetching financial data: {str(e)}"
        
        tools.append({
            "name": "FinancialMetrics",
            "description": "Get key financial metrics for a company. Input should be a valid ticker symbol like AAPL.",
            "function": get_financial_metrics
        })
        
        # Company news tool
        def get_company_news(ticker):
            """Get recent company news"""
            try:
                # Get news from yfinance via data_ingestion
                today = datetime.now().strftime("%Y-%m-%d")
                one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                
                news = self.data_ingestion.get_company_news(ticker, one_month_ago, today)
                
                # Format news for output
                news_summary = []
                for item in news[:5]:  # Limit to 5 news items
                    news_summary.append({
                        "title": item.get("title", "No title"),
                        "summary": item.get("summary", "No summary available")[:150] + "...",
                        "published": item.get("published", "Unknown date")
                    })
                
                return json.dumps(news_summary)
            except Exception as e:
                return f"Error fetching company news: {str(e)}"
        
        tools.append({
            "name": "CompanyNews",
            "description": "Get recent news about a company. Input should be a valid ticker symbol like AAPL.",
            "function": get_company_news
        })
        
        return tools
    
    # def get_technical_indicators(self, ticker, series_type='close'):
    #     """Get key technical indicators"""
    #     try:
    #         # Get historical data to calculate indicators
    #         hist_data = self.data_ingestion.get_stock_price_data(ticker, period='200d')
    #         if hist_data is None or hist_data.empty:
    #             return {"rsi": "N/A", "sma_50": "N/A", "sma_200": "N/A", 
    #                     "macd": "N/A", "macd_signal": "N/A", "macd_hist": "N/A"}
                        
    #         # Calculate RSI
    #         delta = hist_data['Close'].diff()
    #         gain = delta.where(delta > 0, 0)
    #         loss = -delta.where(delta < 0, 0)
    #         avg_gain = gain.rolling(window=14).mean()
    #         avg_loss = loss.rolling(window=14).mean()
    #         rs = avg_gain / avg_loss
    #         rsi = 100 - (100 / (1 + rs))
            
    #         # Calculate SMA
    #         sma_50 = hist_data['Close'].rolling(window=50).mean()
    #         sma_200 = hist_data['Close'].rolling(window=200).mean()
            
    #         # Calculate MACD
    #         exp1 = hist_data['Close'].ewm(span=12, adjust=False).mean()
    #         exp2 = hist_data['Close'].ewm(span=26, adjust=False).mean()
    #         macd = exp1 - exp2
    #         signal = macd.ewm(span=9, adjust=False).mean()
            
    #         return {
    #             'rsi': round(rsi.iloc[-1], 2) if not rsi.empty else "N/A",
    #             'sma_50': round(sma_50.iloc[-1], 2) if not sma_50.empty else "N/A",
    #             'sma_200': round(sma_200.iloc[-1], 2) if not sma_200.empty else "N/A",
    #             'macd': round(macd.iloc[-1], 2) if not macd.empty else "N/A",
    #             'macd_signal': round(signal.iloc[-1], 2) if not signal.empty else "N/A",
    #             'macd_hist': round((macd - signal).iloc[-1], 2) if not macd.empty and not signal.empty else "N/A"
    #         }
    #     except Exception as e:
    #         print(f"Error calculating technical indicators: {str(e)}")
    #         return {"rsi": "N/A", "sma_50": "N/A", "sma_200": "N/A", 
    #                 "macd": "N/A", "macd_signal": "N/A", "macd_hist": "N/A"}
        
    def get_company_overview(self, ticker):
        """Get company overview with key metrics"""
        try:
            ticker_data = yf.Ticker(ticker)
            info = ticker_data.info
            
            return {
                'MarketCap': info.get('marketCap', 'N/A'),
                'PERatio': info.get('trailingPE', 'N/A'),
                'EPS': info.get('trailingEps', 'N/A'),
                'Beta': info.get('beta', 'N/A'),
                'DividendYield': info.get('dividendYield', 'N/A'),
                '52WeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52WeekLow': info.get('fiftyTwoWeekLow', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching company overview: {str(e)}")
            return {
                'MarketCap': 'N/A',
                'PERatio': 'N/A',
                'EPS': 'N/A',
                'Beta': 'N/A',
                'DividendYield': 'N/A',
                '52WeekHigh': 'N/A',
                '52WeekLow': 'N/A'
            }
    
    def get_key_financial_metrics(self, ticker):
        """Extract just key metrics from financial statements"""
        try:
            # Use data_ingestion.get_financials instead
            financials = self.data_ingestion.get_financials(ticker)
            
            # Get most recent quarter/year data
            income = financials.get('income_statement')
            balance = financials.get('balance_sheet')
            
            # Create metrics dictionary
            metrics = {
                'Revenue': 'N/A',
                'NetIncome': 'N/A',
                'DebtToEquity': 'N/A'
            }
            
            # Extract data if available
            if income is not None and not income.empty:
                if 'totalRevenue' in income:
                    metrics['Revenue'] = income['totalRevenue'].iloc[0]
                if 'netIncome' in income:
                    metrics['NetIncome'] = income['netIncome'].iloc[0]
                    
            if balance is not None and not balance.empty:
                # Calculate debt to equity if possible
                if 'totalShareholderEquity' in balance and 'shortLongTermDebtTotal' in balance:
                    try:
                        equity = float(balance['totalShareholderEquity'].iloc[0])
                        debt = float(balance['shortLongTermDebtTotal'].iloc[0])
                        if equity != 0:
                            metrics['DebtToEquity'] = round(debt / equity, 2)
                    except (ValueError, TypeError):
                        pass
                        
            return metrics
            
        except Exception as e:
            print(f"Error calculating financial metrics: {str(e)}")
            return {
                'Revenue': 'N/A',
                'NetIncome': 'N/A',
                'DebtToEquity': 'N/A'
            }
        
    def analyze_stock(self, ticker):
        """Analyze a stock and provide investment recommendation"""
        print(f"\n{'='*50}")
        print(f" FETCHING ALPHA VANTAGE DATA FOR: {ticker}")
        print(f"{'='*50}")
        
        # Pre-fetch real data from Alpha Vantage
        # 1. Get stock price data
        try:
            print("Fetching real-time quote data...")
            quote_data = self.data_ingestion.get_quote(ticker)
            print(f"Quote data received: {quote_data}")
            
            print("\nFetching historical stock data...")
            historical_data = self.data_ingestion.get_stock_price_data(ticker, period='1y')
            print(f"Historical data shape: {historical_data.shape}")
            print(f"Latest price data: \n{historical_data.tail(1)}")
            
            # Calculate key metrics
            current_price = quote_data.get("c", "N/A")
            prev_close = quote_data.get("pc", "N/A")
            daily_change = "N/A"
            if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)):
                daily_change = round((current_price - prev_close) / prev_close * 100, 2)
            
            # Get company overview
            print("Fetching company overview...")
            # Fix: Replace self.av_fd with self.data_ingestion.av_fd in get_company_overview method
            overview = self.get_company_overview(ticker)
            
            # Get financial metrics
            print("Fetching financial metrics...")
            # Fix: Make sure self.get_financials is properly defined or use self.data_ingestion.get_financials
            financials = self.get_key_financial_metrics(ticker)

            print("\n--- DEBUG DATA ---")
            print(f"\nCOMPANY OVERVIEW:")
            print(json.dumps(overview, indent=2))

            print(f"\nFINANCIAL METRICS:")
            print(json.dumps(financials, indent=2))
            print("\n------------------\n")

        except Exception as e:
            print(f"Error fetching stock price data: {str(e)}")
            quote_data = {}
            historical_data = None
            current_price = "N/A"
            prev_close = "N/A"
            daily_change = "N/A"
            overview = {"MarketCap": "N/A", "PERatio": "N/A", "EPS": "N/A", "Beta": "N/A", 
                    "52WeekLow": "N/A", "52WeekHigh": "N/A"}
            financials = {"Revenue": "N/A", "NetIncome": "N/A", "DebtToEquity": "N/A"}
            
        # Handle API rate limits and generate response
        try:
            print(f"\n{'='*50}")
            print(" SENDING DATA TO GEMINI FOR ANALYSIS")
            print(f"{'='*50}")
            
            max_retries = 3
            retry_count = 0
            retry_delay = 60


            prompt = f"""
                You are an experienced financial advisor analyzing {ticker}. 
                Based on the following data, provide a comprehensive investment analysis and recommendation:

                STOCK PRICE DATA:
                Current Price: {current_price}
                Previous Close: {prev_close}
                Daily Change: {daily_change}
                Latest Trading Data: 
                {historical_data.tail(3).to_string() if historical_data is not None else 'No historical data available'}

                COMPANY OVERVIEW:
                Market Cap: {overview['MarketCap']}
                P/E Ratio: {overview['PERatio']}
                EPS: {overview['EPS']}
                Beta: {overview['Beta']}
                52-Week Range: {overview['52WeekLow']} - {overview['52WeekHigh']}

                KEY FINANCIAL METRICS:
                Revenue: {financials['Revenue']}
                Net Income: {financials['NetIncome']}
                Debt-to-Equity: {financials.get('DebtToEquity', 'N/A')}

                ANALYSIS POINTS TO COVER:
                1. Recent price performance and trends
                2. Technical analysis indicators evaluation
                3. Fundamental analysis and valuation
                4. Price targets and potential risks
                5. Investment recommendation (Buy/Hold/Sell) with justification

                Format your response as a professional financial advisor would.
                """
                             
            while retry_count < max_retries:
                try:
                    response = self.model.generate_content(prompt)
                    if response is None or not hasattr(response, 'text') or response.text is None:
                        print("Warning: Received empty response from Gemini API")
                        return f"Analysis could not be generated for {ticker}. The API returned an empty response."
                    return response.text
                except Exception as e:
                    print(f"Error during Gemini API call: {str(e)}")
                    retry_count += 1
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            
            # If we exhausted all retries
            return f"Analysis for {ticker} failed after {max_retries} attempts due to API rate limits. Please try again later."
        
        except Exception as e:
            return f"Error analyzing {ticker}: {str(e)}"
