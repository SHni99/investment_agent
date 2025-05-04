import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model Parameters
LSTM_SEQUENCE_LENGTH = 60  # Days of historical data for prediction

# Trading Parameters
DEFAULT_PORTFOLIO_SIZE = 5  # Number of stocks in portfolio
RISK_TOLERANCE = "moderate"  # Options: conservative, moderate, aggressive
