"""
Main script for Transformer-based Stock Price Prediction Model
This script demonstrates the integration of DataAgent, TransformerAgent, and EmbeddingAgent
for the first sprint of the project.
"""
import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse

import sys
import os

# Add project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.Agents.StockPrediction.data_agent import DataAgent
from src.Agents.StockPrediction.transformer_agent import TransformerAgent
from src.Agents.StockPrediction.embedding_agent import EmbeddingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("transformer_stock_prediction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Transformer-based Stock Price Prediction')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker symbol')
    parser.add_argument('--days', type=int, default=365*2, help='Number of days of historical data')
    parser.add_argument('--window-size', type=int, default=20, help='Window size for time series')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=30, help='Number of training epochs')
    parser.add_argument('--patience', type=int, default=10, help='Patience for early stopping')
    parser.add_argument('--embedding-dim', type=int, default=64, help='Embedding dimension')
    parser.add_argument('--learning-rate', type=float, default=0.001, help='Learning rate')
    
    return parser.parse_args()

def main():
    """Main function to run the transformer-based stock prediction pipeline"""
    args = parse_args()
    
    logger.info(f"Starting Transformer-based Stock Price Prediction for {args.ticker}")
    
    # Create directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    
    # Initialize agents
    data_agent = DataAgent(window_size=args.window_size)
    
    # Calculate date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
    
    logger.info(f"Fetching data for {args.ticker} from {start_date} to {end_date}")
    
    # Process data
    try:
        data_splits = data_agent.process_data(args.ticker, start_date, end_date)
        logger.info("Data processing completed successfully")
        
        # Initialize transformer agent
        transformer_agent = TransformerAgent(
            input_dim=5,  # OHLCV = 5 features
            d_model=args.embedding_dim,
            lr=args.learning_rate,
            model_dir="models"
        )
        
        # Train transformer model
        train_data = data_splits['train']
        val_data = data_splits['val']
        
        logger.info("Training Transformer model...")
        history = transformer_agent.train(
            train_windows=train_data['windows'],
            train_labels=train_data['labels'],
            val_windows=val_data['windows'],
            val_labels=val_data['labels'],
            batch_size=args.batch_size,
            epochs=args.epochs,
            patience=args.patience,
            model_name=f"{args.ticker}_transformer"
        )
        logger.info("Transformer model training completed")
        
        # Initialize embedding agent
        embedding_agent = EmbeddingAgent(
            transformer_agent=transformer_agent,
            output_dir="data/embeddings"
        )
        
        # Extract and save embeddings
        logger.info("Extracting and saving embeddings...")
        embedding_files = embedding_agent.process_data_splits(data_splits, args.ticker)
        logger.info(f"Embeddings saved to: {embedding_files}")
        
        # Visualize embeddings for training data
        train_embeddings = embedding_agent.extract_embeddings(
            train_data['windows'],
            train_data['labels'],
            train_data.get('dates', None),
            "train"
        )
        
        # Visualize embeddings
        plot_path = embedding_agent.visualize_embeddings(
            train_embeddings,
            train_data['labels'],
            f"{args.ticker} Training Embeddings Visualization"
        )
        logger.info(f"Embeddings visualization saved to {plot_path}")
        
        # Calculate and display accuracy on test set
        test_data = data_splits['test']
        test_loss, test_acc = transformer_agent.evaluate(
            torch.FloatTensor(test_data['windows']),
            torch.FloatTensor(test_data['labels']).unsqueeze(1)
        )
        logger.info(f"Test Loss: {test_loss:.4f} | Test Accuracy: {test_acc:.4f}")
        
        logger.info("Sprint 1 pipeline execution completed successfully")
        
        # Return success status
        return {
            "status": "success",
            "ticker": args.ticker,
            "embedding_files": embedding_files,
            "visualization": plot_path,
            "test_accuracy": test_acc
        }
        
    except Exception as e:
        logger.error(f"Error in pipeline execution: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    
    result = main()
    print(f"Result: {result['status']}")
