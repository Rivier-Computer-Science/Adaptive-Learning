"""
Unit tests for EmbeddingAgent
"""
import unittest
import numpy as np
import pandas as pd
import os
import sys
import tempfile
import shutil

# Add project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.Agents.StockPrediction.transformer_agent import TransformerAgent
from src.Agents.StockPrediction.embedding_agent import EmbeddingAgent

class TestEmbeddingAgent(unittest.TestCase):
    """Test cases for EmbeddingAgent"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temp directories
        self.temp_dir = tempfile.mkdtemp()
        self.model_dir = os.path.join(self.temp_dir, "models")
        self.output_dir = os.path.join(self.temp_dir, "embeddings")
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize TransformerAgent for testing
        self.transformer_agent = TransformerAgent(
            input_dim=5,  # OHLCV = 5 features
            d_model=32,
            model_dir=self.model_dir
        )
        
        # Initialize EmbeddingAgent
        self.agent = EmbeddingAgent(
            transformer_agent=self.transformer_agent,
            output_dir=self.output_dir
        )
        
        # Create dummy data for testing
        self.seq_len = 20
        self.n_features = 5
        self.n_samples = 50
        
        self.windows = np.random.randn(self.n_samples, self.seq_len, self.n_features)
        self.labels = np.random.randint(0, 2, self.n_samples)
        self.dates = pd.date_range(start='2023-01-01', periods=self.n_samples).tolist()
        
    def tearDown(self):
        """Tear down test fixtures"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.transformer_agent, self.transformer_agent)
        self.assertEqual(self.agent.output_dir, self.output_dir)
        
    def test_extract_embeddings(self):
        """Test embedding extraction"""
        embeddings = self.agent.extract_embeddings(
            self.windows[:10], 
            self.labels[:10], 
            self.dates[:10], 
            "test"
        )
        
        # Check embedding shape
        self.assertEqual(embeddings.shape, (10, self.transformer_agent.d_model))
        
    def test_save_embeddings(self):
        """Test saving embeddings to CSV"""
        # Extract some embeddings
        embeddings = self.agent.extract_embeddings(
            self.windows[:10], 
            self.labels[:10], 
            self.dates[:10], 
            "test"
        )
        
        # Save embeddings
        filepath = self.agent.save_embeddings(
            embeddings,
            self.labels[:10],
            self.dates[:10],
            "test",
            "AAPL"
        )
        
        # Check if file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check if file is a CSV
        self.assertTrue(filepath.endswith('.csv'))
        
        # Load the CSV and check content
        df = pd.read_csv(filepath)
        
        # Check if columns are correct
        self.assertIn('label', df.columns)
        self.assertIn('date', df.columns)
        
        # Check number of embedding columns
        embedding_cols = [col for col in df.columns if col.startswith('embedding_')]
        self.assertEqual(len(embedding_cols), self.transformer_agent.d_model)
        
        # Check number of rows
        self.assertEqual(len(df), 10)
        
    def test_load_embeddings(self):
        """Test loading embeddings from CSV"""
        # Extract and save embeddings
        embeddings = self.agent.extract_embeddings(
            self.windows[:10], 
            self.labels[:10], 
            self.dates[:10], 
            "test"
        )
        
        filepath = self.agent.save_embeddings(
            embeddings,
            self.labels[:10],
            self.dates[:10],
            "test",
            "AAPL"
        )
        
        # Load embeddings
        loaded_embeddings, loaded_labels, loaded_dates = self.agent.load_embeddings(filepath)
        
        # Check shapes
        self.assertEqual(loaded_embeddings.shape, embeddings.shape)
        self.assertEqual(loaded_labels.shape, self.labels[:10].shape)
        self.assertEqual(len(loaded_dates), 10)
        
        # Check values
        np.testing.assert_array_almost_equal(loaded_embeddings, embeddings)
        np.testing.assert_array_equal(loaded_labels, self.labels[:10])
        
    def test_process_data_splits(self):
        """Test processing all data splits"""
        # Create data splits
        data_splits = {
            'train': {
                'windows': self.windows[:30],
                'labels': self.labels[:30],
                'dates': self.dates[:30]
            },
            'val': {
                'windows': self.windows[30:40],
                'labels': self.labels[30:40],
                'dates': self.dates[30:40]
            },
            'test': {
                'windows': self.windows[40:],
                'labels': self.labels[40:],
                'dates': self.dates[40:]
            }
        }
        
        # Process data splits
        embedding_files = self.agent.process_data_splits(data_splits, "AAPL")
        
        # Check if files were created for each split
        self.assertEqual(len(embedding_files), 3)
        for split in ['train', 'val', 'test']:
            self.assertIn(split, embedding_files)
            self.assertTrue(os.path.exists(embedding_files[split]))

if __name__ == '__main__':
    unittest.main()
