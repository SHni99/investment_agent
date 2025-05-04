import streamlit as st
import pandas as pd
import os
from datetime import datetime
from main import analyze_stock, run_backtest, compare_strategies, print_all_alpha_vantage_data
import io
import sys
import json

st.set_page_config(
    page_title="Finance AI Agent",
    layout="wide"
)

def capture_output(func, *args, **kwargs):
    """Capture both stdout and return value from a function"""
    # Create StringIO object to capture stdout
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        # Execute the function
        result = func(*args, **kwargs)
        # Get the captured output
        output = new_stdout.getvalue()
        return result, output
    finally:
        # Reset stdout
        sys.stdout = old_stdout

st.title("Finance AI Agent 📈")
st.markdown("""
Enter a stock ticker symbol to analyze the investment potential, 
run backtests, compare trading strategies, or view all available data.
""")

with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT, GOOGL)", "AAPL").upper()
    action = st.selectbox(
        "Select Action",
        ["analyze", "backtest", "compare", "print_data"],
        format_func=lambda x: {
            "analyze": "Analyze Stock",
            "backtest": "Run Backtest",
            "compare": "Compare Strategies",
            "print_data": "Print All Data"
        }.get(x, x)
    )
    
    if action == "backtest":
        strategy = st.selectbox(
            "Select Strategy",
            ["sma", "rsi"],
            format_func=lambda x: {
                "sma": "Simple Moving Average",
                "rsi": "Relative Strength Index"
            }.get(x, x)
        )

# Main content area
st.header(f"Results for {ticker}")

if st.button("Run Analysis", type="primary"):
    with st.spinner(f"Processing {ticker}..."):
        try:
            if action == "analyze":
                st.subheader("Investment Analysis")
                result = analyze_stock(ticker)
                st.markdown(result)
                
                # Show recently saved file
                st.success("Analysis saved to results folder")
                
            elif action == "backtest":
                st.subheader(f"Backtest Results - {strategy.upper()} Strategy")
                try:
                    result, output = capture_output(run_backtest, ticker, strategy)
                    
                    # Display backtest statistics
                    if result:
                        stats_df = pd.DataFrame.from_dict(result._asdict(), orient='index', columns=['Value'])
                        st.dataframe(stats_df)
                    
                    # Display any text output
                    if output:
                        with st.expander("Detailed Output"):
                            st.text(output)
                    
                    # Show backtest chart if available
                    recent_files = [f for f in os.listdir('backtest_results') 
                                   if f.endswith('.html') and ticker in f and strategy in f]
                    if recent_files:
                        recent_file = sorted(recent_files)[-1]  # Get the most recent file
                        file_path = os.path.join('backtest_results', recent_file)
                        with open(file_path, 'r') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=600)
                        st.success(f"Backtest results saved to {file_path}")
                    
                except ImportError:
                    st.error("Backtesting requires additional packages. Please run: pip install matplotlib pandas backtrader")
                except Exception as e:
                    st.error(f"Error during backtest: {str(e)}")
                
            elif action == "compare":
                st.subheader("Strategy Comparison")
                try:
                    result, output = capture_output(compare_strategies, ticker)
                    
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result)
                    
                    if output:
                        with st.expander("Detailed Output"):
                            st.text(output)
                    
                    # Find the most recent comparison CSV file
                    recent_files = [f for f in os.listdir('backtest_results') 
                                   if f.endswith('.csv') and ticker in f and 'comparison' in f]
                    if recent_files:
                        st.success(f"Comparison saved to backtest_results folder")
                        
                except ImportError:
                    st.error("Strategy comparison requires additional packages. Please run: pip install matplotlib pandas backtrader")
                except Exception as e:
                    st.error(f"Error during strategy comparison: {str(e)}")
                
            elif action == "print_data":
                st.subheader("All Available Alpha Vantage Data")
                
                # Use a container to better manage the output
                with st.container():
                    output_container = st.empty()
                    
                    # Capture the printed output
                    result, output = capture_output(print_all_alpha_vantage_data, ticker)
                    
                    # Display the output in the container
                    output_container.text(output)
                
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")

# Footer
st.markdown("---")
st.markdown("📊 Finance AI Agent powered by Alpha Vantage and Gemini AI")
