"""
Think Anywhere: Dynamic Reasoning in Large Language Models

A Python library implementing entropy-based dynamic reasoning for LLMs during
code generation. The system monitors model uncertainty and activates reasoning
only when needed.

Core components:
    - ThinkingAgent: Main agent with dynamic reasoning
    - EntropyDetector: Monitors model uncertainty
    - PromptBuilder: Constructs structured prompts

Example:
    >>> from think_anywhere import ThinkingAgent
    >>> agent = ThinkingAgent(entropy_threshold=0.7)
    >>> result = agent.generate("Implement quicksort")
    >>> print(result.output)
"""

__version__ = "0.1.0"
__author__ = "Dr. Hidden"
__license__ = "MIT"

from .agent import ThinkingAgent
from .entropy import EntropyDetector
from .prompts import PromptBuilder
from .models import GenerationResult, EntropyPoint, ThinkingStatistics

__all__ = [
    "ThinkingAgent",
    "EntropyDetector",
    "PromptBuilder",
    "GenerationResult",
    "EntropyPoint",
    "ThinkingStatistics",
]
