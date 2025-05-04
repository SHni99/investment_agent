import streamlit as st
import logging
from main import analyze_stock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting Streamlit app")

try:
    # Basic UI
    st.title("Finance AI Agent")
    st.write("If you can see this, Streamlit is working correctly!")
    
    # Test input
    ticker = st.text_input("Enter a ticker symbol", "AAPL")
    
    if st.button("Submit"):
        st.info(f"Analyzing {ticker}... This may take a minute.")
        logger.info(f"User submitted ticker: {ticker}")
        
        try:
            # Get analysis from Gemini
            analysis_result = analyze_stock(ticker)
            
            # Display results
            st.subheader(f"Analysis for {ticker}")
            st.markdown(analysis_result)
            
            st.success(f"Analysis for {ticker} completed successfully!")
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            st.error(f"Error analyzing {ticker}: {str(e)}")

except Exception as e:
    logger.error(f"Error in Streamlit app: {str(e)}")
    st.error(f"An error occurred: {str(e)}")