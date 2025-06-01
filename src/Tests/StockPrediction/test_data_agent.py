"""
Unit tests for DataAgent
"""
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.Agents.StockPrediction.data_agent import DataAgent

class TestDataAgent(unittest.TestCase):
    """Test cases for DataAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = DataAgent(window_size=10)
        self.ticker = "AAPL"
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.window_size, 10)
        
    def test_fetch_data(self):
        """Test fetching data from yfinance"""
        df = self.agent.fetch_data(self.ticker, self.start_date, self.end_date)
        
        # Check if DataFrame is returned
        self.assertIsInstance(df, pd.DataFrame)
        
        # Check if OHLCV columns are present
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            self.assertIn(col, df.columns)
            
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
    def test_clean_data(self):
        """Test data cleaning"""
        # Create a DataFrame with missing values
        df = pd.DataFrame({
            'Open': [100, 101, np.nan, 103],
            'High': [105, np.nan, 107, 108],
            'Low': [95, 96, 97, np.nan],
            'Close': [101, 102, 103, 104],
            'Volume': [1000, 1100, 1200, 1300]
        })
        
        df_cleaned = self.agent.clean_data(df)
        
        # Check if missing values were filled
        self.assertEqual(df_cleaned.isnull().sum().sum(), 0)
        
    def test_normalize_data(self):
        """Test data normalization"""
        # Create a sample DataFrame
        df = pd.DataFrame({
            'Open': [100, 101, 102, 103],
            'High': [105, 106, 107, 108],
            'Low': [95, 96, 97, 98],
            'Close': [101, 102, 103, 104],
            'Volume': [1000, 1100, 1200, 1300]
        })
        
        df_norm = self.agent.normalize_data(df)
        
        # Check if normalization was applied (mean should be close to 0)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            self.assertAlmostEqual(df_norm[col].mean(), 0, delta=1e-10)
            self.assertAlmostEqual(df_norm[col].std(), 1, delta=1e-10)
            
    def test_create_windows(self):
        """Test window creation"""
        # Create a sample DataFrame
        df = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'High': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115],
            'Low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105],
            'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
        })
        
        # Set window size to 5 for test
        self.agent.window_size = 5
        
        windows, labels, dates = self.agent.create_windows(df)
        
        # Check window shape
        self.assertEqual(windows.shape, (6, 5, 5))  # 6 windows, window_size=5, 5 features
        
        # Check label shape
        self.assertEqual(labels.shape, (6,))
        
        # Check if labels are binary
        for label in labels:
            self.assertIn(label, [0, 1])
            
    def test_split_data(self):
        """Test data splitting"""
        # Create dummy data
        windows = np.random.randn(100, 10, 5)
        labels = np.random.randint(0, 2, 100)
        dates = [datetime.now() + timedelta(days=i) for i in range(100)]
        
        splits = self.agent.split_data(windows, labels, dates)
        
        # Check if all splits exist
        for split in ['train', 'val', 'test']:
            self.assertIn(split, splits)
            
        # Check train size (70%)
        self.assertEqual(len(splits['train']['windows']), 70)
        
        # Check val size (15%)
        self.assertEqual(len(splits['val']['windows']), 15)
        
        # Check test size (15%)
        self.assertEqual(len(splits['test']['windows']), 15)
        
    def test_process_data(self):
        """Test end-to-end data processing pipeline"""
        data_splits = self.agent.process_data(self.ticker, self.start_date, self.end_date)
        
        # Check if all splits exist
        for split in ['train', 'val', 'test', 'original_data']:
            self.assertIn(split, data_splits)
            
        # Check if original data is a DataFrame
        self.assertIsInstance(data_splits['original_data'], pd.DataFrame)
        
        # Check if windows, labels, and dates exist in each split
        for split in ['train', 'val', 'test']:
            self.assertIn('windows', data_splits[split])
            self.assertIn('labels', data_splits[split])
            self.assertIn('dates', data_splits[split])
            
            # Check window shape (should have window_size and 5 features)
            self.assertEqual(data_splits[split]['windows'].shape[1], self.agent.window_size)
            self.assertEqual(data_splits[split]['windows'].shape[2], 5)  # 5 features for OHLCV

if __name__ == '__main__':
    unittest.main()
