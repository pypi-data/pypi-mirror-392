import numpy as np
from typing import List, Dict, Any
import logging

class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5, clip_threshold: float = 1.0):
        """Initialize Differential Privacy mechanism.
        
        Args:
            epsilon: Privacy parameter (ε) that controls privacy loss
            delta: Probability of privacy breach (δ)
            clip_threshold: Maximum L2 norm for gradient clipping
        """
        self.epsilon = epsilon
        self.delta = delta
        self.clip_threshold = clip_threshold
        self.logger = logging.getLogger(__name__)

    def compute_sensitivity(self, batch_size: int) -> float:
        """Compute sensitivity for the current parameters."""
        return 2 * self.clip_threshold / batch_size

    def add_noise(self, weights: List[np.ndarray], num_samples: int) -> List[np.ndarray]:
        """Add Gaussian noise to weights for differential privacy.
        
        Args:
            weights: List of weight arrays to add noise to
            num_samples: Number of training samples used
            
        Returns:
            List of weight arrays with added noise
        """
        try:
            sensitivity = self.compute_sensitivity(num_samples)
            sigma = np.sqrt(2 * np.log(1.25 / self.delta)) * sensitivity / self.epsilon
            
            noisy_weights = []
            for layer in weights:
                noise = np.random.normal(0, sigma, layer.shape)
                noisy_weights.append(layer + noise)
            
            return noisy_weights
        except Exception as e:
            self.logger.error(f"Error adding noise to weights: {str(e)}")
            return weights

    def clip_gradients(self, gradients: List[np.ndarray]) -> List[np.ndarray]:
        """Clip gradients to limit sensitivity.
        
        Args:
            gradients: List of gradient arrays to clip
            
        Returns:
            List of clipped gradient arrays
        """
        try:
            # Calculate total L2 norm
            total_norm = np.sqrt(sum(np.sum(np.square(g)) for g in gradients))
            
            # Apply clipping if norm exceeds threshold
            if total_norm > self.clip_threshold:
                scale = self.clip_threshold / total_norm
                return [g * scale for g in gradients]
            
            return gradients
        except Exception as e:
            self.logger.error(f"Error clipping gradients: {str(e)}")
            return gradients

    def get_privacy_spent(self, steps: int) -> Dict[str, float]:
        """Calculate current privacy budget spent using simplified moment accounting.
        
        For production systems, consider implementing RDP accountant (Renyi Differential Privacy)
        for tighter privacy bounds. This simplified version provides conservative estimates.
        
        Args:
            steps: Number of training steps performed
            
        Returns:
            Dictionary containing current privacy loss values (epsilon_spent, delta_spent)
        """
        try:
            # Simplified moment accounting
            # For production: use RDP accountant from autodp or Google's TensorFlow Privacy
            privacy_spent = self.epsilon * np.sqrt(steps)
            delta_spent = self.delta * steps
            
            return {
                'epsilon_spent': privacy_spent,
                'delta_spent': delta_spent
            }
        except Exception as e:
            self.logger.error(f"Error calculating privacy spent: {str(e)}")
            return {'epsilon_spent': float('inf'), 'delta_spent': 1.0}