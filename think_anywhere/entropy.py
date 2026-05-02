"""
Entropy detection for LLM uncertainty monitoring.

Calculates Shannon entropy from token probabilities to detect when the model
should activate reasoning. High entropy indicates uncertainty and multiple
competing options.

The core formula is:
    H(X) = -Σ p(x) * log₂(p(x))

Normalized to [0, 1] by dividing by log₂(n) where n is vocabulary size.
"""

import math
from typing import List, Dict, Optional
from .models import EntropyPoint


class EntropyDetector:
    """
    Detects points of high uncertainty in LLM generation.
    
    Monitors token-level probabilities and calculates Shannon entropy to identify
    when the model should activate explicit reasoning.
    
    Args:
        threshold: Entropy threshold for activating reasoning (0-1)
                   Typical values: 0.7 (conservative), 0.5 (balanced), 0.3 (aggressive)
        
    Attributes:
        threshold: Configured entropy threshold
        entropy_history: Historical entropy values from all analyses
        
    Example:
        >>> detector = EntropyDetector(threshold=0.7)
        >>> probs = [0.4, 0.3, 0.2, 0.1]  # Token probabilities
        >>> entropy = detector.calculate_entropy(probs)
        >>> if detector.should_think(entropy):
        ...     print("High uncertainty detected - activate reasoning")
    
    Raises:
        ValueError: If threshold is not in range [0, 1]
    """
    
    def __init__(self, threshold: float = 0.7):
        if not 0 <= threshold <= 1:
            raise ValueError(
                f"Threshold must be in [0, 1], got {threshold}"
            )
        
        self.threshold = threshold
        self.entropy_history: List[float] = []
    
    def calculate_entropy(self, probabilities: List[float]) -> float:
        """
        Calculate Shannon entropy from probability distribution.
        
        Computes normalized entropy H(X) = -Σ p(x) * log₂(p(x)) / log₂(n)
        
        Args:
            probabilities: Token probability distribution
            
        Returns:
            Normalized entropy in [0, 1] where:
                - 0 = certainty (one token has p ≈ 1)
                - 1 = maximum uncertainty (uniform distribution)
        
        Notes:
            - Probabilities below 1e-10 are filtered for numerical stability
            - Empty or invalid distributions return 0.0
            - Result is normalized by max possible entropy (log₂ of vocab size)
        """
        if not probabilities:
            return 0.0
        
        # Filter near-zero probabilities for numerical stability
        filtered_probs = [p for p in probabilities if p > 1e-10]
        
        if not filtered_probs:
            return 0.0
        
        # Calculate Shannon entropy
        entropy = -sum(p * math.log2(p) for p in filtered_probs)
        
        # Normalize by maximum possible entropy
        max_entropy = math.log2(len(filtered_probs))
        normalized = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # Track history for analysis
        self.entropy_history.append(normalized)
        
        return normalized
    
    def should_think(self, entropy: float) -> bool:
        """
        Determine if reasoning should be activated based on entropy.
        
        Args:
            entropy: Entropy value (0-1) from calculate_entropy()
            
        Returns:
            True if entropy exceeds threshold (model is uncertain)
        """
        return entropy >= self.threshold
    
    def analyze_token_sequence(
        self,
        tokens_with_probs: List[Dict[str, any]]
    ) -> List[EntropyPoint]:
        """
        Analyze a sequence of tokens and identify high-entropy points.
        
        Args:
            tokens_with_probs: List of dicts with keys:
                - 'token': str - generated token
                - 'probs': List[float] - probability distribution
                
        Returns:
            List of EntropyPoint objects for positions exceeding threshold
            
        Example:
            >>> sequence = [
            ...     {'token': 'def', 'probs': [0.9, 0.05, 0.05]},
            ...     {'token': 'quicksort', 'probs': [0.4, 0.3, 0.3]},  # High entropy
            ... ]
            >>> points = detector.analyze_token_sequence(sequence)
            >>> print(points[0].reason)
        """
        high_entropy_points = []
        
        for idx, item in enumerate(tokens_with_probs):
            entropy = self.calculate_entropy(item['probs'])
            
            if self.should_think(entropy):
                point = EntropyPoint(
                    position=idx,
                    entropy=entropy,
                    token=item['token'],
                    reason=self._explain_high_entropy(entropy),
                    should_think=True
                )
                high_entropy_points.append(point)
        
        return high_entropy_points
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Compute statistical summary of entropy history.
        
        Returns:
            Dictionary with keys:
                - count: Number of entropy measurements
                - mean: Average entropy
                - max: Maximum entropy observed
                - min: Minimum entropy observed
                - std: Standard deviation
                - threshold: Configured threshold
                - times_over_threshold: Count of high-entropy events
        """
        if not self.entropy_history:
            return {
                'count': 0,
                'mean': 0.0,
                'max': 0.0,
                'min': 0.0,
                'std': 0.0,
                'threshold': self.threshold,
                'times_over_threshold': 0
            }
        
        count = len(self.entropy_history)
        mean = sum(self.entropy_history) / count
        max_val = max(self.entropy_history)
        min_val = min(self.entropy_history)
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in self.entropy_history) / count
        std = math.sqrt(variance)
        
        return {
            'count': count,
            'mean': mean,
            'max': max_val,
            'min': min_val,
            'std': std,
            'threshold': self.threshold,
            'times_over_threshold': sum(
                1 for e in self.entropy_history if e >= self.threshold
            )
        }
    
    def reset(self) -> None:
        """Clear entropy history for fresh analysis."""
        self.entropy_history.clear()
    
    def _explain_high_entropy(self, entropy: float) -> str:
        """
        Generate human-readable explanation for high entropy.
        
        Args:
            entropy: Entropy value (0-1)
            
        Returns:
            Natural language explanation of uncertainty level
        """
        if entropy >= 0.9:
            return "Very high uncertainty - multiple options equally likely"
        elif entropy >= 0.7:
            return "High uncertainty - model unsure of best option"
        elif entropy >= 0.5:
            return "Moderate uncertainty - competing alternatives exist"
        else:
            return "Low uncertainty - model confident in choice"
