#!/bin/bash

# Set project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="${PROJECT_DIR}/venv"

echo "===================================="
echo "Setting up Finance AI Agent Environment"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
echo "Detected Python version: ${PYTHON_VERSION}"

# If Python 3.13 (which is quite new), warn about potential compatibility issues
if [[ "${PYTHON_VERSION}" == 3.13* ]]; then
    echo "⚠️  Warning: Python 3.13 is detected, which is very new and might have compatibility issues with some packages."
    echo "If you encounter errors, consider using Python 3.9-3.11 instead."
    echo ""
    read -p "Would you like to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup aborted."
        exit 1
    fi
fi

# Check if virtual environment already exists
if [ -d "${VENV_DIR}" ]; then
    echo "A virtual environment already exists at ${VENV_DIR}"
    read -p "Do you want to remove it and create a new one? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "${VENV_DIR}"
    else
        echo "Using existing virtual environment."
        source "${VENV_DIR}/bin/activate" || {
            echo "Failed to activate existing virtual environment."
            exit 1
        }
        echo "Virtual environment activated!"
        echo "To start analyzing stocks, use:"
        echo "python main.py --action analyze --ticker AAPL"
        exit 0
    fi
fi

echo "Creating virtual environment in ${VENV_DIR}..."

# Create virtual environment
python3 -m venv "${VENV_DIR}" || {
    echo "Failed to create virtual environment. Make sure python3-venv is installed."
    echo "On Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "On macOS: pip3 install virtualenv"
    exit 1
}

echo "Virtual environment created successfully!"
echo "Activating virtual environment..."

# Activate virtual environment
source "${VENV_DIR}/bin/activate" || {
    echo "Failed to activate virtual environment."
    exit 1
}

echo "Installing required packages..."
# Install requirements with verbose output
pip install --upgrade pip -v

# Install packages one by one to identify problematic packages
echo "Installing packages individually for better error tracking..."

# Create a temporary directory for logs
LOGS_DIR="${PROJECT_DIR}/install_logs"
mkdir -p "${LOGS_DIR}"

# Read requirements.txt and install packages one by one
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ ]] && continue
    [[ -z "${line// }" ]] && continue
    
    # Extract package name (before any version specifier)
    package=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | cut -d'!' -f1 | tr -d '[:space:]')
    
    echo "Installing $package..."
    pip install "$line" -v > "${LOGS_DIR}/${package}_install.log" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Failed to install $package. See ${LOGS_DIR}/${package}_install.log for details."
        echo "Continuing with other packages..."
    else
        echo "✓ Successfully installed $package"
    fi
done < "${PROJECT_DIR}/requirements.txt"

# Special handling for TA-Lib
echo "Installing TA-Lib (this may take a few minutes)..."
pip install --no-binary ta-lib ta-lib -v > "${LOGS_DIR}/ta-lib_install.log" 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to install TA-Lib directly."
    echo "You may need to install system dependencies first:"
    echo "- On Ubuntu/Debian: sudo apt-get install build-essential ta-lib"
    echo "- On macOS: brew install ta-lib"
    echo "See ${LOGS_DIR}/ta-lib_install.log for detailed error information."
    
    # Alternative installation suggestion for macOS users
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        echo "For macOS users, here's an alternative installation approach:"
        echo "1. Exit this script (Ctrl+C if not already done)"
        echo "2. Activate the virtual environment: source ${VENV_DIR}/bin/activate"
        echo "3. Run: brew install ta-lib"
        echo "4. Run: LDFLAGS='-L/usr/local/opt/ta-lib/lib' CPPFLAGS='-I/usr/local/opt/ta-lib/include' pip install ta-lib"
    fi
else
    echo "✓ Successfully installed TA-Lib"
fi

# Special handling for critical packages that failed
if [ -f "${LOGS_DIR}/pandas_install.log" ] && grep -q "error" "${LOGS_DIR}/pandas_install.log"; then
    echo ""
    echo "Critical package pandas failed to install. Attempting to install compatible version..."
    pip install "pandas<2.0.0" -v > "${LOGS_DIR}/pandas_retry_install.log" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Still unable to install pandas. This is a critical dependency."
        echo "You might need to downgrade your Python version or try:"
        echo "source ${VENV_DIR}/bin/activate && pip install pandas==1.5.3"
    else
        echo "✓ Successfully installed pandas (alternate version)"
    fi
fi

if [ -f "${LOGS_DIR}/numpy_install.log" ] && grep -q "error" "${LOGS_DIR}/numpy_install.log"; then
    echo ""
    echo "Critical package numpy failed to install. Attempting to install compatible version..."
    pip install "numpy<1.24.0" -v > "${LOGS_DIR}/numpy_retry_install.log" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Still unable to install numpy. This is a critical dependency."
        echo "You might need to downgrade your Python version or try:"
        echo "source ${VENV_DIR}/bin/activate && pip install numpy==1.22.4"
    else
        echo "✓ Successfully installed numpy (alternate version)"
    fi
fi

echo ""
echo "===================================="
echo "Installation Summary"
echo "===================================="
echo "Installation logs are saved in: ${LOGS_DIR}"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "source ${VENV_DIR}/bin/activate"
echo ""
echo "To start analyzing stocks, use:"
echo "python main.py --action analyze --ticker AAPL"
echo ""
echo "If you encountered errors with pandas or numpy:"
echo "1. These are critical packages for data analysis"
echo "2. Python 3.13 might not be fully compatible with the latest versions"
echo "3. Try creating a new virtual environment with Python 3.9-3.11:"
echo "   python3.9 -m venv venv_py39"
echo "   source venv_py39/bin/activate"
echo "   Then run the setup script again"
echo ""
echo "Happy investing!"
