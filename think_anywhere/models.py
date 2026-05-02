"""
Data models for Think Anywhere.

Type-safe data structures for reasoning results, entropy analysis, and statistics.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EntropyPoint:
    """
    Represents a point of high entropy (uncertainty) during generation.
    
    Attributes:
        position: Token position or line number
        entropy: Normalized entropy value (0-1)
        token: Token or code snippet at this position
        reason: Human-readable explanation of why entropy is high
        should_think: Whether reasoning should be activated at this point
    """
    position: int
    entropy: float
    token: str
    reason: str
    should_think: bool = True
    
    def __post_init__(self):
        """Validate entropy value is in valid range."""
        if not 0 <= self.entropy <= 1:
            raise ValueError(f"Entropy must be in [0, 1], got {self.entropy}")


@dataclass
class GenerationResult:
    """
    Result of code generation with dynamic reasoning.
    
    Attributes:
        output: Generated code
        thoughts: List of reasoning blocks extracted from <THINK> tags
        entropy_points: Points where high entropy was detected
        tokens_used: Total tokens consumed
        reasoning_efficiency: Ratio of tokens saved vs. CoT
        metadata: Optional additional information
    """
    output: str
    thoughts: List[str]
    entropy_points: List[EntropyPoint]
    tokens_used: int
    reasoning_efficiency: Optional[float] = None
    metadata: dict = field(default_factory=dict)
    
    @property
    def has_reasoning(self) -> bool:
        """Check if generation included any reasoning blocks."""
        return len(self.thoughts) > 0
    
    @property
    def num_reasoning_points(self) -> int:
        """Count of reasoning activation points."""
        return len([p for p in self.entropy_points if p.should_think])
    
    def __repr__(self) -> str:
        """Concise representation for debugging."""
        return (
            f"GenerationResult("
            f"tokens={self.tokens_used}, "
            f"thoughts={len(self.thoughts)}, "
            f"entropy_points={len(self.entropy_points)})"
        )


@dataclass
class ThinkingStatistics:
    """
    Statistical analysis of reasoning behavior.
    
    Attributes:
        total_generations: Number of code generation runs
        total_thoughts: Total reasoning blocks produced
        avg_thoughts_per_generation: Average reasoning blocks per run
        avg_entropy_at_thinking: Mean entropy when reasoning activates
        max_entropy: Maximum entropy observed
        min_entropy: Minimum entropy observed
        entropy_std: Standard deviation of entropy values
        times_over_threshold: Count of high-entropy events
        token_efficiency: Token savings vs. baseline (e.g., CoT)
    """
    total_generations: int
    total_thoughts: int
    avg_thoughts_per_generation: float
    avg_entropy_at_thinking: float
    max_entropy: float
    min_entropy: float
    entropy_std: float
    times_over_threshold: int
    token_efficiency: Optional[float] = None
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Think Anywhere Statistics:",
            f"  Total generations: {self.total_generations}",
            f"  Total reasoning blocks: {self.total_thoughts}",
            f"  Avg reasoning/generation: {self.avg_thoughts_per_generation:.2f}",
            f"  Avg entropy at reasoning: {self.avg_entropy_at_thinking:.3f}",
            f"  Entropy range: [{self.min_entropy:.3f}, {self.max_entropy:.3f}]",
            f"  High-entropy events: {self.times_over_threshold}",
        ]
        
        if self.token_efficiency is not None:
            lines.append(f"  Token efficiency: {self.token_efficiency:.1%}")
        
        return "\n".join(lines)
