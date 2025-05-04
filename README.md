# Finance AI Agent

An intelligent AI-powered financial assistant that helps with investment analysis, portfolio management, and financial decision making.

## Live Demo

The application is deployed and available at:
[https://investment-aiagent.streamlit.app/](https://investment-aiagent.streamlit.app/)

## Features

- Financial data analysis
- Investment recommendations
- Portfolio tracking
- Market insights
- Natural language processing for financial queries

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finance_ai_agent.git
cd finance_ai_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application locally:
```bash
streamlit run app.py
```

## API Setup for Developers

This application requires several API keys to function properly. Follow these steps to set up the necessary APIs:

### 1. Financial Data API (e.g., Alpha Vantage, Yahoo Finance)

1. Register for an account at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Obtain your API key
3. Add to your environment variables or `.env` file:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 2. OpenAI API (for natural language processing)

1. Create an account at [OpenAI](https://platform.openai.com/signup)
2. Navigate to API section and create a new API key
3. Add to your environment variables or `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. Streamlit Deployment (optional)

1. Create an account at [Streamlit](https://streamlit.io/)
2. Follow their [deployment guide](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)
3. Connect your GitHub repository to Streamlit

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OPENAI_API_KEY=your_openai_key
OTHER_API_KEY=your_other_key
```

Then load these variables in your application:

```python
import os
from dotenv import load_dotenv

load_dotenv()
alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
```

## Usage

[Include screenshots and examples of how to use the application]

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
