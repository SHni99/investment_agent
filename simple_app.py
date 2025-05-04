import streamlit as st
import logging
from main import analyze_stock
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("streamlit_app.log", mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Finance AI Agent",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
    }
    .subheader {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .analysis-section {
        border-left: 3px solid #1E88E5;
        padding-left: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Functions to get company info and logo
def get_company_info(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        return info
    except:
        return None

def get_stock_price_history(ticker, period="1y"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return None

# Session state initialization
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

logger.info("Starting Streamlit app")

try:
    # Sidebar
    with st.sidebar:
        st.markdown("## Settings")
        
        # Analysis type options
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Basic Analysis", "Detailed Analysis", "Technical Analysis"]
        )
        
        # Time period options
        time_period = st.selectbox(
            "Time Period",
            ["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"]
        )
        
        # History of analyzed stocks
        if st.session_state.analysis_history:
            st.markdown("## Recent Analysis")
            for recent_ticker in st.session_state.analysis_history[-5:]:
                if st.button(f"📈 {recent_ticker}", key=f"history_{recent_ticker}"):
                    st.query_params["ticker"] = recent_ticker
        
    # Main content
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown('<p class="main-header">Finance AI Agent</p>', unsafe_allow_html=True)
        st.markdown("AI-powered stock market analysis and insights")
        
        # Logo container for selected company
        logo_container = st.empty()
        
        # Input section
        ticker = st.text_input("Enter a ticker symbol", "AAPL")
        col_button1, col_button2 = st.columns([1, 2])
        with col_button1:
            submit_button = st.button("Analyze", use_container_width=True)
        with col_button2:
            popular_tickers = st.selectbox("Popular Tickers", 
                                          ["", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"])
            if popular_tickers and popular_tickers != "":
                ticker = popular_tickers
    
    with col2:
        # Price chart will go here
        chart_container = st.empty()
    
    # Analysis section
    if submit_button or ticker != "":
        try:
            # Add to history
            if ticker not in st.session_state.analysis_history:
                st.session_state.analysis_history.append(ticker)
            
            # Show company info
            company_info = get_company_info(ticker)
            if company_info and 'longName' in company_info:
                with col1:
                    logo_container.markdown(f"### {company_info['longName']} ({ticker})")
                    if 'sector' in company_info and 'industry' in company_info:
                        st.markdown(f"**Sector:** {company_info['sector']} | **Industry:** {company_info['industry']}")
            
            # Show stock price chart
            price_history = get_stock_price_history(ticker)
            if price_history is not None and not price_history.empty:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=price_history.index,
                    open=price_history['Open'],
                    high=price_history['High'],
                    low=price_history['Low'],
                    close=price_history['Close'],
                    name='Price'
                ))
                fig.update_layout(
                    title=f'{ticker} Stock Price',
                    xaxis_title='Date',
                    yaxis_title='Price (USD)',
                    xaxis_rangeslider_visible=False,
                    height=400
                )
                chart_container.plotly_chart(fig, use_container_width=True)
            
            # Analysis progress
            st.info(f"Analyzing {ticker}... This may take a minute.")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress while waiting for analysis
            for i in range(100):
                status_text.text(f"Processing: {'▰' * (i//10)}{'▱' * (10-i//10)} {i+1}%")
                progress_bar.progress(i + 1)
                time.sleep(0.01)  # Simulate processing time
            
            # Get analysis from Gemini
            logger.info(f"User submitted ticker: {ticker}")
            analysis_result = analyze_stock(ticker)
            
            # Display results in tabs
            st.markdown('<p class="subheader">Analysis Results</p>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["AI Analysis", "Market Data"])
            
            with tab1:
                st.markdown(f"<div class='analysis-section'>{analysis_result}</div>", unsafe_allow_html=True)
                st.success(f"Analysis for {ticker} completed successfully!")
                
                # Download button for analysis
                csv_buffer = BytesIO()
                pd.DataFrame({"Analysis": [analysis_result]}).to_csv(csv_buffer, index=False)
                csv_bytes = csv_buffer.getvalue()
                b64 = base64.b64encode(csv_bytes).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{ticker}_analysis.csv">Download Analysis as CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            with tab2:
                # Display key market data
                if company_info:
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    
                    with metrics_col1:
                        st.metric("Market Cap", f"${company_info.get('marketCap', 'N/A'):,}" if isinstance(company_info.get('marketCap'), (int, float)) else "N/A")
                    
                    with metrics_col2:
                        st.metric("P/E Ratio", f"{company_info.get('trailingPE', 'N/A'):.2f}" if isinstance(company_info.get('trailingPE'), (int, float)) else "N/A")
                    
                    with metrics_col3:
                        st.metric("52W High", f"${company_info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(company_info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A")
                    
                    with metrics_col4:
                        st.metric("52W Low", f"${company_info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(company_info.get('fiftyTwoWeekLow'), (int, float)) else "N/A")
                    
                    # Display more detailed information
                    st.markdown("### Financial Overview")
                    fin_col1, fin_col2 = st.columns(2)
                    
                    with fin_col1:
                        st.write("**Revenue:** ", f"${company_info.get('totalRevenue', 'N/A'):,}" if isinstance(company_info.get('totalRevenue'), (int, float)) else "N/A")
                        st.write("**Gross Profit:** ", f"${company_info.get('grossProfits', 'N/A'):,}" if isinstance(company_info.get('grossProfits'), (int, float)) else "N/A")
                        st.write("**EPS (TTM):** ", company_info.get('trailingEps', 'N/A'))
                    
                    with fin_col2:
                        st.write("**Dividend Yield:** ", f"{company_info.get('dividendYield', 'N/A') * 100:.2f}%" if isinstance(company_info.get('dividendYield'), (int, float)) else "N/A")
                        st.write("**Beta:** ", company_info.get('beta', 'N/A'))
                        st.write("**Volume:** ", f"{company_info.get('volume', 'N/A'):,}" if isinstance(company_info.get('volume'), (int, float)) else "N/A")
        
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            st.error(f"Error analyzing {ticker}: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("#### About Finance AI Agent")
    st.markdown("This tool uses AI to analyze stocks and provide insights based on market data and company performance.")

except Exception as e:
    logger.error(f"Error in Streamlit app: {str(e)}")
    st.error(f"An error occurred: {str(e)}")