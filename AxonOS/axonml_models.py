#!/usr/bin/env python3
"""
AxonML Neural Network Models
LSTM and Transformer models for BCI signal decoding
Production-ready implementation with strict typing
"""

import torch
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass
import math


@dataclass
class ModelConfig:
    """Configuration for neural network models"""
    input_size: int = 64
    hidden_size: int = 128
    num_layers: int = 2
    num_classes: int = 3
    dropout: float = 0.3
    bidirectional: bool = True
    d_model: int = 128
    nhead: int = 8
    max_seq_len: int = 1000


class AttentionMechanism(nn.Module):
    """
    Self-attention mechanism for LSTM outputs
    """
    
    def __init__(self, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        
        # Attention layers
        self.attention_weights = nn.Linear(hidden_size, 1, bias=False)
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, lstm_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply attention mechanism
        
        Args:
            lstm_output: LSTM output (batch, time, hidden_size)
            
        Returns:
            attended: Weighted sum of LSTM outputs (batch, hidden_size)
            weights: Attention weights (batch, time)
        """
        # Compute attention scores
        scores = self.attention_weights(lstm_output)  # (batch, time, 1)
        scores = scores.squeeze(-1)  # (batch, time)
        
        # Apply softmax to get weights
        weights = self.softmax(scores)  # (batch, time)
        
        # Apply attention weights
        weights_expanded = weights.unsqueeze(-1)  # (batch, time, 1)
        attended = torch.sum(lstm_output * weights_expanded, dim=1)  # (batch, hidden_size)
        
        return attended, weights


class LSTMDecoder(nn.Module):
    """
    LSTM-based decoder for BCI signals
    Processes time-series EEG data to predict motor imagery classes
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.config = config
        self.input_size = config.input_size
        self.hidden_size = config.hidden_size
        self.num_layers = config.num_layers
        self.num_classes = config.num_classes
        self.bidirectional = config.bidirectional
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=config.input_size,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0.0,
            bidirectional=config.bidirectional
        )
        
        # Attention mechanism
        self.attention = AttentionMechanism(
            hidden_size=config.hidden_size * (2 if config.bidirectional else 1)
        )
        
        # Classification head
        classifier_input = config.hidden_size * (2 if config.bidirectional else 1)
        self.classifier = nn.Sequential(
            nn.Linear(classifier_input, classifier_input // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(classifier_input // 2, config.num_classes)
        )
        
    def forward(self, x: torch.Tensor, lengths: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through LSTM decoder
        
        Args:
            x: Input tensor of shape (batch, time, features)
            lengths: Optional sequence lengths for variable-length inputs
            
        Returns:
            logits: Class logits (batch, num_classes)
            attention_weights: Attention weights (batch, time)
        """
        batch_size, seq_len, _ = x.size()
        
        # Pass through LSTM
        if lengths is not None:
            # Handle variable-length sequences
            x_packed = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
            lstm_out, (hidden, cell) = self.lstm(x_packed)
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)
        else:
            lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention mechanism
        attended, attention_weights = self.attention(lstm_out)
        
        # Classification
        logits = self.classifier(attended)
        
        return logits, attention_weights
    
    def get_attention_weights(self, x: torch.Tensor) -> np.ndarray:
        """Get attention weights for visualization"""
        self.eval()
        with torch.no_grad():
            _, attention_weights = self.forward(x)
            return attention_weights.cpu().numpy()


class PositionalEncoding(nn.Module):
    """
    Positional encoding for transformer models
    """
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input
        
        Args:
            x: Input tensor (batch, time, d_model)
            
        Returns:
            x: Output with positional encoding (batch, time, d_model)
        """
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class TransformerDecoder(nn.Module):
    """
    Transformer-based decoder for BCI signals
    Uses multi-head attention for temporal modeling
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.d_model = config.d_model
        self.input_size = config.input_size
        
        # Input projection
        self.input_projection = nn.Linear(config.input_size, config.d_model)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(config.d_model, config.max_seq_len, config.dropout)
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.d_model * 4,
            dropout=config.dropout,
            activation='relu',
            batch_first=True  # Critical for performance
        )
        
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=config.num_layers
        )
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_model // 2, config.num_classes)
        )
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(config.d_model)
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through transformer decoder
        
        Args:
            x: Input tensor (batch, time, features)
            mask: Optional attention mask
            
        Returns:
            logits: Class logits (batch, num_classes)
        """
        batch_size, seq_len, _ = x.size()
        
        # Project input to model dimension
        x = self.input_projection(x)  # (batch, time, d_model)
        
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Apply layer normalization
        x = self.layer_norm(x)
        
        # Pass through transformer
        x = self.transformer(x, src_key_padding_mask=mask)
        
        # Global average pooling over time dimension
        x = x.transpose(1, 2)  # (batch, d_model, time)
        x = self.global_pool(x)  # (batch, d_model, 1)
        x = x.squeeze(-1)  # (batch, d_model)
        
        # Classification
        logits = self.classifier(x)
        
        return logits


class ConvNetDecoder(nn.Module):
    """
    Convolutional neural network decoder
    Processes EEG signals as 1D time series
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.num_channels = config.input_size  # input_size = num_channels
        self.num_timepoints = config.max_seq_len
        
        # Spatial filtering (across channels) - expects (batch, 1, channels, time)
        self.spatial_conv = nn.Conv2d(1, 1, kernel_size=(config.input_size, 1))
        
        # Temporal convolution layers - applied after spatial filtering (1 channel input)
        self.conv1 = nn.Conv1d(1, 32, kernel_size=15, padding=7)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=15, padding=7)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=15, padding=7)
        
        # Pooling
        self.pool1 = nn.MaxPool1d(kernel_size=2, stride=2)
        self.pool2 = nn.MaxPool1d(kernel_size=2, stride=2)
        
        # Batch normalization
        self.bn1 = nn.BatchNorm1d(32)
        self.bn2 = nn.BatchNorm1d(64)
        self.bn3 = nn.BatchNorm1d(128)
        
        # Calculate output size after convolutions
        self.conv_output_size = self._get_conv_output_size(config.max_seq_len)
        
        # Classification head - dynamically created based on actual input size
        self.classifier = None
        self.dropout = config.dropout
        self.num_classes = config.num_classes
        
    def _get_conv_output_size(self, input_size: int) -> int:
        """Calculate output size after convolutions and pooling"""
        size = input_size
        size = size // 2  # After pool1
        size = size // 2  # After pool2
        return size
    
    def _create_classifier(self, input_size: int) -> nn.Sequential:
        """Create classifier with correct input size"""
        return nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(self.dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(self.dropout),
            nn.Linear(128, self.num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through ConvNet
        
        Args:
            x: Input tensor (batch, channels, time)
            
        Returns:
            logits: Class logits (batch, num_classes)
        """
        batch_size, channels, timepoints = x.size()
        
        # Apply spatial filtering first - reduces channels from num_channels to 1
        x_spatial = x.unsqueeze(1)  # (batch, 1, channels, time)
        x_spatial = self.spatial_conv(x_spatial)  # (batch, 1, 1, time)
        x_spatial = x_spatial.squeeze(1)  # (batch, 1, time)
        
        # Apply temporal convolutions to the spatially filtered signal
        # Note: conv1 expects (batch, in_channels, time) where in_channels=1
        x = F.relu(self.bn1(self.conv1(x_spatial)))
        x = self.pool1(x)
        
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        x = F.relu(self.bn3(self.conv3(x)))
        
        # Flatten for classification
        x = x.view(batch_size, -1)
        
        # Create classifier dynamically if needed (for different input sizes)
        if self.classifier is None or self.classifier[0].in_features != x.shape[1]:
            self.classifier = self._create_classifier(x.shape[1])
        
        # Classification
        logits = self.classifier(x)
        
        return logits


class EnsembleModel(nn.Module):
    """
    Ensemble of different models for robust predictions
    """
    
    def __init__(self, models: List[nn.Module], weights: Optional[List[float]] = None):
        super().__init__()
        
        self.models = nn.ModuleList(models)
        
        # Default to equal weights
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        
        self.register_buffer('weights', torch.tensor(weights))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through ensemble
        
        Args:
            x: Input tensor
            
        Returns:
            weighted_logits: Weighted average of model outputs
        """
        outputs = []
        
        for model in self.models:
            with torch.no_grad():
                output = model(x)
                # Handle models that return tuples (e.g., LSTM with attention)
                if isinstance(output, (list, tuple)):
                    output = output[0]  # Take first element (logits)
                outputs.append(output)
        
        # Stack outputs
        outputs = torch.stack(outputs, dim=0)  # (num_models, batch, num_classes)
        
        # Apply weights
        weights_expanded = self.weights.view(-1, 1, 1)
        weighted_outputs = outputs * weights_expanded
        
        # Sum across models
        ensemble_output = weighted_outputs.sum(dim=0)
        
        return ensemble_output
    
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict with uncertainty estimation
        
        Args:
            x: Input tensor
            
        Returns:
            mean_prediction: Mean prediction across models
            uncertainty: Prediction uncertainty
        """
        outputs = []
        
        for model in self.models:
            with torch.no_grad():
                output = model(x)
                # Handle models that return tuples (e.g., LSTM with attention)
                if isinstance(output, (list, tuple)):
                    output = output[0]  # Take first element (logits)
                output = torch.softmax(output, dim=1)
                outputs.append(output)
        
        outputs = torch.stack(outputs, dim=0)  # (num_models, batch, num_classes)
        
        # Mean prediction
        mean_prediction = outputs.mean(dim=0)
        
        # Uncertainty (variance across models)
        uncertainty = outputs.var(dim=0)
        
        return mean_prediction, uncertainty


class ModelFactory:
    """
    Factory for creating different model architectures
    """
    
    @staticmethod
    def create_lstm_model(
        input_size: int = 64,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 3,
        dropout: float = 0.3,
        bidirectional: bool = True
    ) -> LSTMDecoder:
        """Create LSTM model"""
        config = ModelConfig(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            num_classes=num_classes,
            dropout=dropout,
            bidirectional=bidirectional
        )
        return LSTMDecoder(config)
    
    @staticmethod
    def create_transformer_model(
        input_size: int = 64,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        num_classes: int = 3,
        dropout: float = 0.1,
        max_seq_len: int = 1000
    ) -> TransformerDecoder:
        """Create Transformer model"""
        config = ModelConfig(
            input_size=input_size,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            num_classes=num_classes,
            dropout=dropout,
            max_seq_len=max_seq_len
        )
        return TransformerDecoder(config)
    
    @staticmethod
    def create_convnet_model(
        num_channels: int = 64,
        num_timepoints: int = 1000,
        num_classes: int = 3,
        dropout: float = 0.3
    ) -> ConvNetDecoder:
        """Create ConvNet model"""
        config = ModelConfig(
            input_size=num_channels,
            max_seq_len=num_timepoints,
            num_classes=num_classes,
            dropout=dropout
        )
        return ConvNetDecoder(config)
    
    @staticmethod
    def create_ensemble(
        models: List[nn.Module],
        weights: Optional[List[float]] = None
    ) -> EnsembleModel:
        """Create ensemble model"""
        return EnsembleModel(models=models, weights=weights)


# Example usage
if __name__ == "__main__":
    print("Testing AxonML models...")
    
    factory = ModelFactory()
    
    # Test data
    batch_size, seq_len, features = 2, 100, 64
    dummy_input = torch.randn(batch_size, seq_len, features)
    conv_input = torch.randn(batch_size, features, seq_len)
    
    # Test LSTM
    print("\n1. Testing LSTM model...")
    lstm_model = factory.create_lstm_model()
    logits, attention = lstm_model(dummy_input)
    print(f"LSTM output shape: {logits.shape}")
    print(f"Attention shape: {attention.shape}")
    
    # Test Transformer
    print("\n2. Testing Transformer model...")
    transformer_model = factory.create_transformer_model()
    logits = transformer_model(dummy_input)
    print(f"Transformer output shape: {logits.shape}")
    
    # Test ConvNet
    print("\n3. Testing ConvNet model...")
    convnet_model = factory.create_convnet_model()
    logits = convnet_model(conv_input)
    print(f"ConvNet output shape: {logits.shape}")
    
    # Test ensemble
    print("\n4. Testing ensemble model...")
    models = [lstm_model, transformer_model]
    ensemble = factory.create_ensemble(models, weights=[0.5, 0.5])
    
    prediction, uncertainty = ensemble.predict_with_uncertainty(dummy_input)
    print(f"Ensemble prediction shape: {prediction.shape}")
    print(f"Uncertainty shape: {uncertainty.shape}")
    
    print("\n✅ All models working correctly!")


# Example usage
if __name__ == "__main__":
    print("Testing AxonML models...")
    
    factory = ModelFactory()
    
    # Test data
    batch_size, seq_len, features = 2, 100, 64
    dummy_input = torch.randn(batch_size, seq_len, features)
    conv_input = torch.randn(batch_size, features, seq_len)
    
    # Test LSTM
    print("\n1. Testing LSTM model...")
    lstm_model = factory.create_lstm_model()
    logits, attention = lstm_model(dummy_input)
    print(f"LSTM output shape: {logits.shape}")
    print(f"Attention shape: {attention.shape}")
    
    # Test Transformer
    print("\n2. Testing Transformer model...")
    transformer_model = factory.create_transformer_model()
    logits = transformer_model(dummy_input)
    print(f"Transformer output shape: {logits.shape}")
    
    # Test ConvNet
    print("\n3. Testing ConvNet model...")
    convnet_model = factory.create_convnet_model()
    logits = convnet_model(conv_input)
    print(f"ConvNet output shape: {logits.shape}")
    
    # Test ensemble
    print("\n4. Testing ensemble model...")
    models = [lstm_model, transformer_model]
    ensemble = factory.create_ensemble(models, weights=[0.5, 0.5])
    
    prediction, uncertainty = ensemble.predict_with_uncertainty(dummy_input)
    print(f"Ensemble prediction shape: {prediction.shape}")
    print(f"Uncertainty shape: {uncertainty.shape}")
    
    print("\n✅ All models working correctly!")
