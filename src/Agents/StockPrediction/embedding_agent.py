"""
EmbeddingAgent - Extracts and saves Transformer embeddings with corresponding labels.
"""
import numpy as np
import pandas as pd
import os
import torch
from typing import Dict, Tuple, List, Any, Optional
import logging
from datetime import datetime
import matplotlib.pyplot as plt

from src.Agents.StockPrediction.transformer_agent import TransformerAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingAgent:
    """
    EmbeddingAgent is responsible for extracting embeddings from the Transformer model
    and saving them with corresponding labels for use with XGBoost.
    """
    def __init__(self, transformer_agent: TransformerAgent, output_dir: str = "./data/embeddings"):
        """
        Initialize the EmbeddingAgent.
        
        Args:
            transformer_agent: Trained TransformerAgent instance
            output_dir: Directory to save the embeddings
        """
        self.transformer_agent = transformer_agent
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"EmbeddingAgent initialized with output_dir={output_dir}")
    
    def extract_embeddings(self, 
                          windows: np.ndarray, 
                          labels: np.ndarray, 
                          dates: List[Any] = None, 
                          set_name: str = "dataset") -> np.ndarray:
        """
        Extract embeddings from the Transformer model for the given windows.
        
        Args:
            windows: Input windows of shape [n_samples, window_size, n_features]
            labels: Labels of shape [n_samples]
            dates: Optional list of dates corresponding to each window
            set_name: Name of the dataset (e.g., "train", "val", "test")
            
        Returns:
            Extracted embeddings of shape [n_samples, d_model]
        """
        logger.info(f"Extracting embeddings for {len(windows)} {set_name} windows")
        
        # Extract embeddings using the transformer agent
        embeddings = self.transformer_agent.get_embeddings(windows)
        
        logger.info(f"Extracted {len(embeddings)} embeddings with shape {embeddings.shape}")
        return embeddings
    
    def save_embeddings(self, 
                        embeddings: np.ndarray, 
                        labels: np.ndarray, 
                        dates: List[Any] = None, 
                        set_name: str = "dataset",
                        ticker: str = "UNKNOWN") -> str:
        """
        Save extracted embeddings with corresponding labels to CSV.
        
        Args:
            embeddings: Extracted embeddings
            labels: Corresponding labels
            dates: Optional list of dates
            set_name: Name of the dataset
            ticker: Stock ticker symbol
            
        Returns:
            Path to the saved embeddings file
        """
        logger.info(f"Saving {len(embeddings)} embeddings for {ticker} {set_name} set")
        
        # Create a DataFrame to store embeddings and labels
        df_embeddings = pd.DataFrame(embeddings)
        
        # Add embedding dimension column names
        for i in range(embeddings.shape[1]):
            df_embeddings = df_embeddings.rename(columns={i: f"embedding_{i}"})
        
        # Add label column
        df_embeddings['label'] = labels
        
        # Add date column if dates are provided
        if dates is not None:
            df_embeddings['date'] = dates
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{set_name}_embeddings_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to CSV
        df_embeddings.to_csv(filepath, index=False)
        
        logger.info(f"Embeddings saved to {filepath}")
        return filepath
    
    def process_data_splits(self, 
                           data_splits: Dict[str, Any], 
                           ticker: str = "UNKNOWN") -> Dict[str, str]:
        """
        Process all data splits (train, val, test) and save embeddings for each.
        
        Args:
            data_splits: Dictionary with train, val, test data
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with paths to saved embedding files
        """
        logger.info(f"Processing all data splits for {ticker}")
        
        embedding_files = {}
        
        # Process each data split
        for split_name in ['train', 'val', 'test']:
            if split_name in data_splits:
                split_data = data_splits[split_name]
                windows = split_data['windows']
                labels = split_data['labels']
                dates = split_data.get('dates', None)
                
                # Extract embeddings
                embeddings = self.extract_embeddings(windows, labels, dates, split_name)
                
                # Save embeddings
                filepath = self.save_embeddings(embeddings, labels, dates, split_name, ticker)
                embedding_files[split_name] = filepath
        
        logger.info(f"Processed all data splits. Embedding files: {embedding_files}")
        return embedding_files
    
    def load_embeddings(self, filepath: str) -> Tuple[np.ndarray, np.ndarray, Optional[List]]:
        """
        Load embeddings, labels, and optionally dates from a CSV file.
        
        Args:
            filepath: Path to the embeddings CSV file
            
        Returns:
            Tuple of (embeddings, labels, dates)
        """
        logger.info(f"Loading embeddings from {filepath}")
        
        # Read CSV file
        df = pd.read_csv(filepath)
        
        # Extract labels
        labels = df['label'].values
        
        # Extract dates if available
        dates = None
        if 'date' in df.columns:
            dates = df['date'].tolist()
        
        # Extract embeddings (all columns except 'label' and 'date')
        embedding_cols = [col for col in df.columns if col not in ['label', 'date']]
        embeddings = df[embedding_cols].values
        
        logger.info(f"Loaded {len(embeddings)} embeddings with shape {embeddings.shape}")
        return embeddings, labels, dates
    
    def visualize_embeddings(self, embeddings: np.ndarray, labels: np.ndarray, title: str = "Embeddings Visualization"):
        """
        Visualize embeddings using dimensionality reduction (PCA).
        
        Args:
            embeddings: Embeddings to visualize
            labels: Corresponding labels
            title: Plot title
        """
        logger.info(f"Visualizing {len(embeddings)} embeddings")
        
        # Use PCA for dimensionality reduction
        from sklearn.decomposition import PCA
        
        # Reduce to 2 dimensions for visualization
        pca = PCA(n_components=2)
        embeddings_2d = pca.fit_transform(embeddings)
        
        # Plot
        plt.figure(figsize=(10, 8))
        
        # Separate points by label
        label_0_indices = np.where(labels == 0)[0]
        label_1_indices = np.where(labels == 1)[0]
        
        # Plot points
        plt.scatter(embeddings_2d[label_0_indices, 0], embeddings_2d[label_0_indices, 1], 
                   c='red', label='Down (0)', alpha=0.7)
        plt.scatter(embeddings_2d[label_1_indices, 0], embeddings_2d[label_1_indices, 1], 
                   c='green', label='Up (1)', alpha=0.7)
        
        # Add labels and legend
        plt.title(title)
        plt.xlabel(f"PCA 1 (Explained Variance: {pca.explained_variance_ratio_[0]:.2f})")
        plt.ylabel(f"PCA 2 (Explained Variance: {pca.explained_variance_ratio_[1]:.2f})")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save the figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(os.path.join(self.output_dir, 'plots'), exist_ok=True)
        plot_path = os.path.join(self.output_dir, 'plots', f"embeddings_pca_{timestamp}.png")
        plt.savefig(plot_path)
        plt.close()
        
        logger.info(f"Embeddings visualization saved to {plot_path}")
        return plot_path
