"""
TransformerAgent - Implements a Transformer model for extracting temporal features from OHLCV windows.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Tuple, Any, List, Optional
import logging
import os
from datetime import datetime
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransformerModel(nn.Module):
    """
    Transformer model for time series prediction on OHLCV data.
    """
    def __init__(self, 
                 input_dim: int, 
                 d_model: int = 64, 
                 nhead: int = 4, 
                 num_encoder_layers: int = 2, 
                 dim_feedforward: int = 256, 
                 dropout: float = 0.1, 
                 activation: str = "relu",
                 output_dim: int = 1):
        """
        Initialize the Transformer model.
        
        Args:
            input_dim: Number of input features (OHLCV = 5)
            d_model: Size of embeddings in the transformer
            nhead: Number of attention heads
            num_encoder_layers: Number of transformer encoder layers
            dim_feedforward: Dimension of the feedforward network
            dropout: Dropout rate
            activation: Activation function to use
            output_dim: Output dimension (1 for binary classification)
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.d_model = d_model
        
        # Input embedding layer (projects from input_dim to d_model)
        self.embedding = nn.Linear(input_dim, d_model)
        
        # Positional encoding for sequence data
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=dim_feedforward, 
            dropout=dropout, 
            activation=activation
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        
        # Output projection (for classification)
        self.output_layer = nn.Linear(d_model, output_dim)
        
        # Initialize weights
        self._init_weights()
        
        logger.info(f"Initialized TransformerModel with {input_dim} input features and {d_model} embedding dimension")
    
    def _init_weights(self):
        """Initialize weights for better training"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x: torch.Tensor, return_embeddings: bool = False) -> torch.Tensor:
        """
        Forward pass through the model.
        
        Args:
            x: Input tensor of shape [batch_size, seq_len, input_dim]
            return_embeddings: If True, return embeddings instead of classification output
            
        Returns:
            If return_embeddings is False:
                Model output tensor of shape [batch_size, output_dim]
            If return_embeddings is True:
                Embeddings tensor of shape [batch_size, d_model]
        """
        # Reshape input: [batch_size, seq_len, input_dim] -> [seq_len, batch_size, input_dim]
        x = x.permute(1, 0, 2)
        
        # Project to embedding dimension
        x = self.embedding(x)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Pass through transformer encoder
        transformer_output = self.transformer_encoder(x)
        
        # Get embeddings from the last time step
        embeddings = transformer_output[-1]
        
        # Return embeddings if requested
        if return_embeddings:
            return embeddings
        
        # Otherwise, pass through output layer for classification
        output = self.output_layer(embeddings)
        return torch.sigmoid(output)  # Apply sigmoid for binary classification

class PositionalEncoding(nn.Module):
    """
    Positional encoding for the transformer model.
    """
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        """
        Initialize positional encoding.
        
        Args:
            d_model: Size of embeddings
            dropout: Dropout rate
            max_len: Maximum length of input sequences
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(1)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input.
        
        Args:
            x: Input tensor of shape [seq_len, batch_size, d_model]
            
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class TransformerAgent:
    """
    Agent responsible for training and using the Transformer model.
    """
    def __init__(self, 
                 input_dim: int = 5, 
                 d_model: int = 64, 
                 nhead: int = 4, 
                 num_encoder_layers: int = 2, 
                 dim_feedforward: int = 256, 
                 dropout: float = 0.1,
                 lr: float = 0.001,
                 weight_decay: float = 1e-5,
                 model_dir: str = "./models"):
        """
        Initialize the TransformerAgent.
        
        Args:
            input_dim: Number of input features
            d_model: Size of embeddings
            nhead: Number of attention heads
            num_encoder_layers: Number of transformer encoder layers
            dim_feedforward: Dimension of feedforward network
            dropout: Dropout rate
            lr: Learning rate for optimizer
            weight_decay: Weight decay for optimizer
            model_dir: Directory to save models
        """
        self.input_dim = input_dim
        self.d_model = d_model
        self.model_dir = model_dir
        self.lr = lr
        self.weight_decay = weight_decay
        
        # Initialize model
        self.model = TransformerModel(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            output_dim=1  # Binary classification
        )
        
        # Initialize optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay
        )
        
        # Loss function for binary classification
        self.criterion = nn.BCELoss()
        
        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.info(f"TransformerAgent initialized with model on {self.device}")
    
    def train(self, 
              train_windows: np.ndarray, 
              train_labels: np.ndarray, 
              val_windows: np.ndarray, 
              val_labels: np.ndarray, 
              batch_size: int = 32,
              epochs: int = 50, 
              patience: int = 10,
              model_name: str = "transformer_model") -> Dict[str, List[float]]:
        """
        Train the transformer model.
        
        Args:
            train_windows: Training windows of shape [n_samples, window_size, n_features]
            train_labels: Training labels of shape [n_samples]
            val_windows: Validation windows
            val_labels: Validation labels
            batch_size: Batch size for training
            epochs: Maximum number of epochs
            patience: Number of epochs to wait for improvement before early stopping
            model_name: Name for saving the model
            
        Returns:
            Dictionary with training history (loss, accuracy, val_loss, val_accuracy)
        """
        logger.info(f"Starting training with {len(train_windows)} samples, batch_size={batch_size}, epochs={epochs}")
        
        # Convert to PyTorch tensors
        X_train = torch.FloatTensor(train_windows)
        y_train = torch.FloatTensor(train_labels).unsqueeze(1)
        X_val = torch.FloatTensor(val_windows)
        y_val = torch.FloatTensor(val_labels).unsqueeze(1)
        
        # Data loaders
        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True
        )
        
        # Training history
        history = {
            'loss': [], 
            'accuracy': [], 
            'val_loss': [], 
            'val_accuracy': []
        }
        
        # Early stopping variables
        best_val_loss = float('inf')
        best_epoch = 0
        
        # Training loop
        for epoch in range(epochs):
            # Training
            self.model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            
            for batch_idx, (inputs, targets) in enumerate(train_loader):
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                # Zero the parameter gradients
                self.optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                # Backward pass and optimize
                loss.backward()
                self.optimizer.step()
                
                # Statistics
                running_loss += loss.item()
                predicted = (outputs > 0.5).float()
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
                
                if batch_idx % 10 == 0:
                    logger.info(f'Epoch: {epoch+1}/{epochs} | Batch: {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}')
            
            # Calculate epoch metrics
            train_loss = running_loss / len(train_loader)
            train_acc = correct / total
            
            # Validation
            val_loss, val_acc = self.evaluate(X_val, y_val)
            
            # Log epoch results
            logger.info(f'Epoch: {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}')
            
            # Update history
            history['loss'].append(train_loss)
            history['accuracy'].append(train_acc)
            history['val_loss'].append(val_loss)
            history['val_accuracy'].append(val_acc)
            
            # Save model if validation loss improved
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_epoch = epoch
                
                # Save model
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = os.path.join(self.model_dir, f"{model_name}_{timestamp}.pt")
                self.save_model(model_path)
                logger.info(f"Model saved to {model_path}")
            
            # Early stopping
            if epoch - best_epoch >= patience:
                logger.info(f"Early stopping at epoch {epoch+1} as validation loss hasn't improved for {patience} epochs")
                break
        
        # Plot training history
        self._plot_history(history, model_name)
        
        return history
    
    def evaluate(self, X: torch.Tensor, y: torch.Tensor) -> Tuple[float, float]:
        """
        Evaluate the model on given data.
        
        Args:
            X: Input data
            y: Target labels
            
        Returns:
            Tuple of (loss, accuracy)
        """
        self.model.eval()
        X, y = X.to(self.device), y.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(X)
            loss = self.criterion(outputs, y)
            predicted = (outputs > 0.5).float()
            accuracy = (predicted == y).float().mean().item()
        
        return loss.item(), accuracy
    
    def get_embeddings(self, windows: np.ndarray) -> np.ndarray:
        """
        Extract embeddings from the model for given windows.
        
        Args:
            windows: Input windows of shape [n_samples, window_size, n_features]
            
        Returns:
            Embeddings array of shape [n_samples, d_model]
        """
        logger.info(f"Extracting embeddings for {len(windows)} windows")
        
        # Convert to PyTorch tensor
        X = torch.FloatTensor(windows).to(self.device)
        
        # Set model to evaluation mode
        self.model.eval()
        
        # Extract embeddings
        with torch.no_grad():
            embeddings = self.model(X, return_embeddings=True)
            embeddings = embeddings.cpu().numpy()
        
        logger.info(f"Extracted embeddings with shape {embeddings.shape}")
        return embeddings
    
    def predict(self, windows: np.ndarray) -> np.ndarray:
        """
        Make predictions for given windows.
        
        Args:
            windows: Input windows of shape [n_samples, window_size, n_features]
            
        Returns:
            Predictions array of shape [n_samples, 1]
        """
        logger.info(f"Making predictions for {len(windows)} windows")
        
        # Convert to PyTorch tensor
        X = torch.FloatTensor(windows).to(self.device)
        
        # Set model to evaluation mode
        self.model.eval()
        
        # Make predictions
        with torch.no_grad():
            predictions = self.model(X)
            predictions = predictions.cpu().numpy()
        
        logger.info(f"Made predictions with shape {predictions.shape}")
        return predictions
    
    def save_model(self, path: str) -> None:
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model state dict
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'input_dim': self.input_dim,
            'd_model': self.d_model,
        }, path)
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """
        Load the model from a file.
        
        Args:
            path: Path to load the model from
        """
        if not os.path.exists(path):
            logger.error(f"Model file not found: {path}")
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Load checkpoint
        checkpoint = torch.load(path, map_location=self.device)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Load optimizer state if available
        if 'optimizer_state_dict' in checkpoint:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        logger.info(f"Model loaded from {path}")
    
    def _plot_history(self, history: Dict[str, List[float]], model_name: str) -> None:
        """
        Plot training history.
        
        Args:
            history: Dictionary with training history
            model_name: Name for the plot file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.figure(figsize=(12, 5))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(history['loss'], label='Train Loss')
        plt.plot(history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot accuracy
        plt.subplot(1, 2, 2)
        plt.plot(history['accuracy'], label='Train Accuracy')
        plt.plot(history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        # Save the figure
        os.makedirs(os.path.join(self.model_dir, 'plots'), exist_ok=True)
        plot_path = os.path.join(self.model_dir, 'plots', f"{model_name}_history_{timestamp}.png")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        
        logger.info(f"Training history plot saved to {plot_path}")
