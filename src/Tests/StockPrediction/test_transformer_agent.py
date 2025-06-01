"""
Unit tests for TransformerAgent
"""
import unittest
import numpy as np
import pandas as pd
import torch
import os
import sys
import tempfile
import shutil

# Add project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.Agents.StockPrediction.transformer_agent import TransformerAgent, TransformerModel, PositionalEncoding

class TestTransformerAgent(unittest.TestCase):
    """Test cases for TransformerAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = TransformerAgent(
            input_dim=5,  # OHLCV = 5 features
            d_model=32,
            nhead=4,
            num_encoder_layers=2,
            dim_feedforward=128,
            dropout=0.1,
            model_dir=self.temp_dir
        )
        
        # Create dummy data for testing
        self.batch_size = 8
        self.seq_len = 20
        self.n_features = 5
        self.n_samples = 100
        
        self.X_train = np.random.randn(self.n_samples, self.seq_len, self.n_features)
        self.y_train = np.random.randint(0, 2, self.n_samples)
        
        self.X_val = np.random.randn(30, self.seq_len, self.n_features)
        self.y_val = np.random.randint(0, 2, 30)
        
    def tearDown(self):
        """Tear down test fixtures"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.input_dim, 5)
        self.assertEqual(self.agent.d_model, 32)
        self.assertTrue(hasattr(self.agent, 'model'))
        self.assertTrue(hasattr(self.agent, 'optimizer'))
        self.assertTrue(hasattr(self.agent, 'criterion'))
        
    def test_transformer_model(self):
        """Test the transformer model architecture"""
        model = self.agent.model
        
        # Check if model is a TransformerModel
        self.assertIsInstance(model, TransformerModel)
        
        # Test forward pass with dummy data
        x = torch.randn(self.batch_size, self.seq_len, self.n_features)
        output = model(x)
        
        # Check output shape (batch_size, 1)
        self.assertEqual(output.shape, (self.batch_size, 1))
        
        # Check if output values are between 0 and 1 (sigmoid output)
        self.assertTrue(torch.all(output >= 0))
        self.assertTrue(torch.all(output <= 1))
        
        # Test embedding extraction
        embeddings = model(x, return_embeddings=True)
        
        # Check embeddings shape (batch_size, d_model)
        self.assertEqual(embeddings.shape, (self.batch_size, model.d_model))
        
    def test_positional_encoding(self):
        """Test positional encoding"""
        d_model = 32
        pos_encoder = PositionalEncoding(d_model=d_model, dropout=0.1)
        
        # Create dummy input
        x = torch.randn(self.seq_len, self.batch_size, d_model)
        
        # Apply positional encoding
        out = pos_encoder(x)
        
        # Check output shape
        self.assertEqual(out.shape, x.shape)
        
        # Check that the output is different from the input (encoding was applied)
        self.assertFalse(torch.all(out == x))
        
    def test_train_model(self):
        """Test model training (minimal test to avoid long runtime)"""
        # Create smaller training data for quick test
        X_train_small = torch.FloatTensor(self.X_train[:20])
        y_train_small = torch.FloatTensor(self.y_train[:20]).unsqueeze(1)
        X_val_small = torch.FloatTensor(self.X_val[:10])
        y_val_small = torch.FloatTensor(self.y_val[:10]).unsqueeze(1)
        
        # Train for just 2 epochs
        history = self.agent.train(
            X_train_small.numpy(), 
            y_train_small.squeeze().numpy(), 
            X_val_small.numpy(), 
            y_val_small.squeeze().numpy(),
            batch_size=4,
            epochs=2,
            patience=1,
            model_name="test_model"
        )
        
        # Check if history contains expected keys
        for key in ['loss', 'accuracy', 'val_loss', 'val_accuracy']:
            self.assertIn(key, history)
            self.assertEqual(len(history[key]), 2)  # 2 epochs
            
    def test_save_load_model(self):
        """Test model saving and loading"""
        # Save model
        model_path = os.path.join(self.temp_dir, "test_model.pt")
        self.agent.save_model(model_path)
        
        # Check if model file exists
        self.assertTrue(os.path.exists(model_path))
        
        # Load model - make sure to use the same configuration as the original agent
        new_agent = TransformerAgent(
            input_dim=5,
            d_model=32,
            nhead=4,
            num_encoder_layers=2,
            dim_feedforward=128,  # Match the original dim_feedforward
            model_dir=self.temp_dir
        )
        new_agent.load_model(model_path)
        
        # Check if model parameters were loaded
        for p1, p2 in zip(self.agent.model.parameters(), new_agent.model.parameters()):
            self.assertTrue(torch.all(p1 == p2))
            
    def test_get_embeddings(self):
        """Test embedding extraction"""
        embeddings = self.agent.get_embeddings(self.X_val[:5])
        
        # Check embedding shape
        self.assertEqual(embeddings.shape, (5, self.agent.d_model))
        
    def test_predict(self):
        """Test model prediction"""
        predictions = self.agent.predict(self.X_val[:5])
        
        # Check prediction shape
        self.assertEqual(predictions.shape, (5, 1))
        
        # Check if predictions are between 0 and 1
        self.assertTrue(np.all(predictions >= 0))
        self.assertTrue(np.all(predictions <= 1))
        
    def test_evaluate(self):
        """Test model evaluation"""
        X = torch.FloatTensor(self.X_val[:5])
        y = torch.FloatTensor(self.y_val[:5]).unsqueeze(1)
        
        loss, acc = self.agent.evaluate(X, y)
        
        # Check if loss and accuracy are valid
        self.assertIsInstance(loss, float)
        self.assertIsInstance(acc, float)
        self.assertTrue(0 <= acc <= 1)

if __name__ == '__main__':
    unittest.main()
