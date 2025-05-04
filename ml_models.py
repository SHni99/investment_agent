import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from config import LSTM_SEQUENCE_LENGTH

class StockDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class PricePredictor:
    def __init__(self, sequence_length=LSTM_SEQUENCE_LENGTH):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, df):
        """Prepare data for LSTM model"""
        # Select features
        data = df[['Open', 'High', 'Low', 'Close', 'Volume']].values
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:i + self.sequence_length])
            # Predict next day's close price (4th column)
            y.append(scaled_data[i + self.sequence_length, 3:4])
            
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Convert to torch tensors
        X_train = torch.FloatTensor(X_train)
        X_test = torch.FloatTensor(X_test)
        y_train = torch.FloatTensor(y_train)
        y_test = torch.FloatTensor(y_test)
        
        return X_train, X_test, y_train, y_test
    
    def train(self, df, epochs=100, batch_size=32, learning_rate=0.001):
        """Train the LSTM model"""
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        
        train_dataset = StockDataset(X_train, y_train)
        test_dataset = StockDataset(X_test, y_test)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size)
        
        # Initialize model
        input_size = X_train.shape[2]  # Number of features
        self.model = LSTMModel(input_size)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0
            for X_batch, y_batch in train_loader:
                # Forward pass
                outputs = self.model(X_batch)
                loss = criterion(outputs, y_batch)
                
                # Backward and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            self.model.eval()
            val_loss = 0
            with torch.no_grad():
                for X_batch, y_batch in test_loader:
                    outputs = self.model(X_batch)
                    loss = criterion(outputs, y_batch)
                    val_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(test_loader):.4f}')
                
        return self.model
    
    def predict(self, df, days_ahead=1):
        """Make predictions using the trained model"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
            
        # Prepare the most recent data
        data = df[['Open', 'High', 'Low', 'Close', 'Volume']].values[-self.sequence_length:]
        scaled_data = self.scaler.transform(data)
        
        # Convert to tensor
        X = torch.FloatTensor(scaled_data).unsqueeze(0)  # Add batch dimension
        
        # Make prediction
        self.model.eval()
        with torch.no_grad():
            next_day = self.model(X)
        
        # For multi-day predictions
        predictions = []
        current_sequence = scaled_data
        
        for _ in range(days_ahead):
            # Make next prediction
            X = torch.FloatTensor(current_sequence).unsqueeze(0)
            self.model.eval()
            with torch.no_grad():
                next_pred = self.model(X).numpy()
                
            # Create a dummy row with the predicted close price
            last_row = current_sequence[-1].copy()
            last_row[3] = next_pred[0][0]  # Set Close price
            
            # Remove first row and add new prediction
            current_sequence = np.vstack([current_sequence[1:], last_row])
            
            # Scale back to original range (only the close price)
            dummy_row = np.zeros((1, 5))
            dummy_row[0, 3] = next_pred[0][0]
            unscaled = self.scaler.inverse_transform(dummy_row)
            predictions.append(unscaled[0, 3])
            
        return predictions
