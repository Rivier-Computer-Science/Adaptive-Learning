"""
DataAgent - Fetches, cleans, normalizes, and segments OHLCV data into windows.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Tuple, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAgent:
    """
    DataAgent is responsible for fetching OHLCV data, cleaning it,
    normalizing it, and segmenting it into fixed-length windows.
    """
    
    def __init__(self, window_size: int = 20):
        """
        Initialize DataAgent with specified window size.
        
        Args:
            window_size: Number of days in each window (default: 20)
        """
        self.window_size = window_size
        logger.info(f"DataAgent initialized with window_size={window_size}")
    
    def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch OHLCV data for a specific ticker using yfinance.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            logger.info(f"Successfully fetched {len(df)} rows of data for {ticker}")
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean OHLCV data by handling missing values.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning data with shape {df.shape}")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            logger.warning(f"Found missing values: {missing_values}")
            
            # Forward fill missing values
            df_cleaned = df.ffill()
            
            # If there are still missing values at the beginning, backward fill
            df_cleaned = df_cleaned.bfill()
            
            logger.info(f"Missing values after cleaning: {df_cleaned.isnull().sum().sum()}")
            return df_cleaned
        
        logger.info("No missing values found in data")
        return df
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize OHLCV data using z-score normalization.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Normalized DataFrame
        """
        logger.info(f"Normalizing data with shape {df.shape}")
        
        # Store original index for later
        original_index = df.index
        
        # Get columns to normalize
        ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in ohlcv_cols if col in df.columns]
        
        # Create a copy to avoid modifying the original DataFrame
        df_norm = df.copy()
        
        # Z-score normalization for each column
        for col in available_cols:
            mean = df[col].mean()
            std = df[col].std()
            # Handle std as a scalar - properly extract the float value to avoid FutureWarning
            std_value = std.iloc[0] if hasattr(std, 'iloc') else float(std)
            if std_value > 0:
                df_norm[col] = (df[col] - mean) / std_value
            else:
                logger.warning(f"Standard deviation is zero for {col}, skipping normalization")
        
        logger.info("Data normalization completed")
        return df_norm
    
    def create_windows(self, df: pd.DataFrame, label_type: str = 'binary') -> Tuple[np.ndarray, np.ndarray, List[pd.Timestamp]]:
        """
        Create fixed-length windows from OHLCV data and generate labels.
        
        Args:
            df: DataFrame with normalized OHLCV data
            label_type: Type of label to generate ('binary' for up/down classification)
            
        Returns:
            Tuple of (windows, labels, dates):
                - windows: 3D array of shape (n_windows, window_size, n_features)
                - labels: Array of labels (1 for price up, 0 for price down)
                - dates: List of dates corresponding to the end of each window
        """
        logger.info(f"Creating windows with window_size={self.window_size}")
        
        # Ensure we have enough data
        if len(df) < self.window_size + 1:
            logger.error(f"Not enough data to create windows. Need at least {self.window_size + 1} rows.")
            raise ValueError(f"Not enough data to create windows. Need at least {self.window_size + 1} rows.")
        
        # Get available OHLCV columns
        ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in ohlcv_cols if col in df.columns]
        
        # Create arrays for windows and labels
        n_windows = len(df) - self.window_size
        n_features = len(available_cols)
        windows = np.zeros((n_windows, self.window_size, n_features))
        labels = np.zeros(n_windows)
        dates = []
        
        # Fill windows and create labels
        for i in range(n_windows):
            # Extract window
            window_data = df[available_cols].iloc[i:i+self.window_size].values
            windows[i] = window_data
            
            # Create label for next day (binary classification: 1 if price goes up, 0 if down)
            if label_type == 'binary':
                current_close = float(df['Close'].iloc[i+self.window_size-1])
                next_close = float(df['Close'].iloc[i+self.window_size])
                labels[i] = 1 if next_close > current_close else 0
            
            # Store the end date of the window
            dates.append(df.index[i+self.window_size-1])
        
        logger.info(f"Created {n_windows} windows with shape {windows.shape}")
        return windows, labels, dates
    
    def split_data(self, windows: np.ndarray, labels: np.ndarray, dates: List[pd.Timestamp], 
                   train_ratio: float = 0.7, val_ratio: float = 0.15) -> Dict[str, Any]:
        """
        Split data into training, validation, and test sets.
        
        Args:
            windows: 3D array of windows
            labels: Array of labels
            dates: List of dates
            train_ratio: Ratio of data for training
            val_ratio: Ratio of data for validation
            
        Returns:
            Dictionary with train, validation, and test data
        """
        logger.info(f"Splitting data with ratios: train={train_ratio}, val={val_ratio}, test={1-train_ratio-val_ratio}")
        
        n_samples = len(windows)
        train_size = int(n_samples * train_ratio)
        val_size = int(n_samples * val_ratio)
        
        # Create train, validation, and test splits
        train_windows = windows[:train_size]
        train_labels = labels[:train_size]
        train_dates = dates[:train_size]
        
        val_windows = windows[train_size:train_size+val_size]
        val_labels = labels[train_size:train_size+val_size]
        val_dates = dates[train_size:train_size+val_size]
        
        test_windows = windows[train_size+val_size:]
        test_labels = labels[train_size+val_size:]
        test_dates = dates[train_size+val_size:]
        
        logger.info(f"Data split: train={len(train_windows)}, val={len(val_windows)}, test={len(test_windows)}")
        
        return {
            'train': {
                'windows': train_windows,
                'labels': train_labels,
                'dates': train_dates
            },
            'val': {
                'windows': val_windows,
                'labels': val_labels,
                'dates': val_dates
            },
            'test': {
                'windows': test_windows,
                'labels': test_labels,
                'dates': test_dates
            }
        }
    
    def process_data(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        End-to-end data processing pipeline: fetch, clean, normalize, window, and split.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            Dictionary with processed data
        """
        logger.info(f"Processing data for {ticker} from {start_date} to {end_date}")
        
        # Fetch data
        df = self.fetch_data(ticker, start_date, end_date)
        
        # Clean data
        df_cleaned = self.clean_data(df)
        
        # Normalize data
        df_normalized = self.normalize_data(df_cleaned)
        
        # Create windows and labels
        windows, labels, dates = self.create_windows(df_normalized)
        
        # Split data
        data_splits = self.split_data(windows, labels, dates)
        
        # Add the original dataframe for reference
        data_splits['original_data'] = df
        
        logger.info(f"Data processing completed for {ticker}")
        return data_splits
