import argparse
from gemini_agent import GeminiInvestmentAgent
import logging
import json
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("finance_ai.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_stock(ticker):
    """Analyze a stock using the investment agent"""
    try:
        agent = GeminiInvestmentAgent()
        result = agent.analyze_stock(ticker)
        
        # Handle case where result is None
        if result is None:
            error_message = f"Error: No analysis was generated for {ticker}. This may be due to API rate limits or service unavailability."
            logger.error(error_message)
            result = error_message
        
        # Save results
        os.makedirs('results', exist_ok=True)
        with open(f'results/{ticker}_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
            f.write(result)
            
        logger.info(f"Successfully analyzed {ticker}")
        return result
    except Exception as e:
        error_message = f"Error analyzing {ticker}: {str(e)}"
        logger.error(error_message)
        return error_message  # Return the error as a string instead of raising an exception

def run_backtest(ticker, strategy='sma'):
    """Run backtest for a stock"""
    try:
        # Import here instead of at the top level
        from backtest import BacktestEngine, SimpleMAStrategy, RSIStrategy
        import pandas as pd
        
        backtest_engine = BacktestEngine()
        
        if strategy.lower() == 'sma':
            stats, bt = backtest_engine.run_backtest(ticker, SimpleMAStrategy)
        elif strategy.lower() == 'rsi':
            stats, bt = backtest_engine.run_backtest(ticker, RSIStrategy)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
            
        # Save results
        os.makedirs('backtest_results', exist_ok=True)
        stats_dict = {k: str(v) if isinstance(v, pd.Timestamp) else v for k, v in stats._asdict().items()}
        with open(f'backtest_results/{ticker}_{strategy}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(stats_dict, f, indent=4)
            
        # Save plot
        bt.plot(filename=f'backtest_results/{ticker}_{strategy}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        logger.info(f"Successfully ran backtest for {ticker} using {strategy} strategy")
        return stats
    except ImportError as e:
        logger.error(f"Cannot run backtest: {str(e)}. Try installing required packages with: pip install matplotlib pandas backtrader")
        print("Error: Backtesting requires additional packages. Please run: pip install matplotlib pandas backtrader")
        raise
    except Exception as e:
        logger.error(f"Error running backtest for {ticker}: {str(e)}")
        raise

def compare_strategies(ticker):
    """Compare different trading strategies for a stock"""
    try:
        # Import here instead of at the top level
        from backtest import BacktestEngine, SimpleMAStrategy, RSIStrategy
        import pandas as pd
        
        backtest_engine = BacktestEngine()
        
        strategies = {
            'SMA': SimpleMAStrategy,
            'RSI': RSIStrategy
        }
        
        results, comparison = backtest_engine.evaluate_multiple_strategies(ticker, strategies)
        
        # Save results
        os.makedirs('backtest_results', exist_ok=True)
        comparison.to_csv(f'backtest_results/{ticker}_strategy_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        logger.info(f"Successfully compared strategies for {ticker}")
        return comparison
    except ImportError as e:
        logger.error(f"Cannot compare strategies: {str(e)}. Try installing required packages with: pip install matplotlib pandas backtrader")
        print("Error: Strategy comparison requires additional packages. Please run: pip install matplotlib pandas backtrader")
        raise
    except Exception as e:
        logger.error(f"Error comparing strategies for {ticker}: {str(e)}")
        raise

def print_all_alpha_vantage_data(ticker):
    """Print all available data from Alpha Vantage for a given ticker"""
    try:
        # Create the agent to access data_ingestion
        agent = GeminiInvestmentAgent()
        data_ingestion = agent.data_ingestion
        
        print(f"\n{'='*50}")
        print(f" ALL ALPHA VANTAGE DATA FOR: {ticker}")
        print(f"{'='*50}")
        
        # Get and print quote data
        print("\n--- QUOTE DATA ---")
        quote = data_ingestion.get_quote(ticker)
        print(json.dumps(quote, indent=2))
        
        # Get and print time series data
        print("\n--- TIME SERIES DATA (last 5 days) ---")
        try:
            time_series = data_ingestion.get_stock_price_data(ticker)
            print(time_series.tail(5))
        except Exception as e:
            print(f"Error fetching time series data: {str(e)}")
        
        # Get and print financial data
        print("\n--- FINANCIAL DATA ---")
        try:
            income = data_ingestion.get_income_statement(ticker)
            balance = data_ingestion.get_balance_sheet(ticker)
            cash_flow = data_ingestion.get_cash_flow(ticker)
            
            print("\nINCOME STATEMENT (first 5 columns):")
            if income is not None and not income.empty:
                print(income.iloc[:3, :5])
            
            print("\nBALANCE SHEET (first 5 columns):")
            if balance is not None and not balance.empty:
                print(balance.iloc[:3, :5])
            
            print("\nCASH FLOW (first 5 columns):")
            if cash_flow is not None and not cash_flow.empty:
                print(cash_flow.iloc[:3, :5])
        except Exception as e:
            print(f"Error fetching financial data: {str(e)}")
            
        logger.info(f"Successfully printed all data for {ticker}")
    except Exception as e:
        logger.error(f"Error printing data for {ticker}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finance AI Agent')
    parser.add_argument('--action', type=str, 
                        choices=['analyze', 'backtest', 'compare', 'print_data'], 
                        required=True,
                        help='Action to perform: analyze stock, run backtest, compare strategies, or print all available data')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    parser.add_argument('--strategy', type=str, default='sma', choices=['sma', 'rsi'],
                        help='Trading strategy for backtest')
    
    args = parser.parse_args()
    
    if args.action == 'analyze':
        result = analyze_stock(args.ticker)
        print(result)
    elif args.action == 'backtest':
        stats = run_backtest(args.ticker, args.strategy)
        print(stats)
    elif args.action == 'compare':
        comparison = compare_strategies(args.ticker)
        print(comparison)
    elif args.action == 'print_data':
        print_all_alpha_vantage_data(args.ticker)