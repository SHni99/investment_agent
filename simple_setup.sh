#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment created and activated!"

# Upgrade pip
pip install --upgrade pip

# Install core packages with specific versions compatible with Python 3.13
echo "Installing core data science packages..."
pip install numpy==2.2.0
pip install pandas==2.1.2
pip install matplotlib==3.8.2

# Install other main dependencies
echo "Installing other dependencies..."
pip install yfinance alpha_vantage finnhub-python python-dotenv

# Install Google Gemini packages with specific compatible versions
echo "Installing Google Gemini API packages..."
pip install google-generativeai==0.3.1

# Install LangChain with all necessary dependencies
echo "Installing LangChain and dependencies..."
pip install "langchain>=0.0.267,<0.1.0"  # Explicitly install compatible version
pip install langchain_core langchain_community  # Required components
pip install langchain-google-genai==0.0.5

# Install other necessary packages
pip install requests pydantic==1.10.8  # Use older pydantic that works with LangChain 0.0.x

# Add debugging info
echo "Verifying installation..."
pip list | grep -E 'langchain|google-generative'

# Create helper script to fix imports if needed
cat > fix_imports.py << 'EOF'
#!/usr/bin/env python3
import os
import re

def fix_file(filepath, old_import, new_import):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if old_import in content:
        updated_content = content.replace(old_import, new_import)
        with open(filepath, 'w') as f:
            f.write(updated_content)
        print(f"Updated imports in {filepath}")
        return True
    return False

# Fix common import issues
fix_file('agent.py', 
         'from langchain.agents import initialize_agent, Tool', 
         'from langchain_core.agents import initialize_agent, Tool')

print("\nIf you still have import errors, please run: python fix_imports.py")
EOF

chmod +x fix_imports.py

echo "Basic environment setup complete!"
echo ""
echo "To activate this environment in the future, run:"
echo "source venv/bin/activate"
echo ""
echo "To start using the finance AI agent, run:"
echo "python main.py --action analyze --ticker AAPL"
