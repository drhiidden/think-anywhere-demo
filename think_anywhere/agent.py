"""
Main agent implementation with dynamic reasoning capabilities.

The ThinkingAgent monitors entropy during generation and activates reasoning
blocks when uncertainty is detected. This is the primary interface for the
Think Anywhere system.
"""

import os
import re
from typing import Optional, List
from .entropy import EntropyDetector
from .prompts import PromptBuilder, ReasoningMode
from .models import GenerationResult, EntropyPoint, ThinkingStatistics


class ThinkingAgent:
    """
    LLM agent with dynamic reasoning based on entropy detection.
    
    Monitors model uncertainty during code generation and activates explicit
    reasoning (<THINK> blocks) only when entropy exceeds threshold.
    
    Args:
        model: Model identifier (e.g., "gpt-4", "claude-3-opus")
        entropy_threshold: Threshold for activating reasoning (0-1)
                           - 0.3: Aggressive (reason frequently)
                           - 0.7: Conservative (reason sparingly)
                           - 0.5: Balanced (recommended)
        api_key: Optional API key (defaults to environment variable)
        
    Attributes:
        model: Configured model name
        threshold: Entropy threshold for reasoning activation
        entropy_detector: EntropyDetector instance
        prompt_builder: PromptBuilder instance
        generation_history: Historical generation results
        
    Example:
        >>> agent = ThinkingAgent(entropy_threshold=0.7)
        >>> result = agent.generate("Implement binary search")
        >>> print(f"Generated {len(result.thoughts)} reasoning blocks")
        >>> print(result.output)
        
    Note:
        Current implementation uses simulated entropy for demonstration.
        Production version would integrate with LLM APIs (OpenAI, Anthropic)
        to access real logprobs during generation.
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        entropy_threshold: float = 0.7,
        api_key: Optional[str] = None
    ):
        if not 0 <= entropy_threshold <= 1:
            raise ValueError(
                f"entropy_threshold must be in [0, 1], got {entropy_threshold}"
            )
        
        self.model = model
        self.threshold = entropy_threshold
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Core components
        self.entropy_detector = EntropyDetector(threshold=entropy_threshold)
        self.prompt_builder = PromptBuilder()
        
        # State tracking
        self.generation_history: List[GenerationResult] = []
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        mode: ReasoningMode = ReasoningMode.THINK_ANYWHERE
    ) -> GenerationResult:
        """
        Generate code with dynamic reasoning.
        
        Constructs a structured prompt and generates output, monitoring entropy
        to activate reasoning blocks when needed.
        
        Args:
            prompt: User's original request
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            mode: Reasoning strategy (default: THINK_ANYWHERE)
            
        Returns:
            GenerationResult with output, reasoning blocks, and entropy analysis
            
        Example:
            >>> result = agent.generate("Implement quicksort")
            >>> print(result.output)
            >>> for thought in result.thoughts:
            ...     print(f"Reasoning: {thought}")
        """
        # Build structured prompt
        structured_prompt = self.prompt_builder.build(prompt, mode)
        
        # Generate output (simulated for demo - production would call LLM API)
        output, entropy_points = self._generate_with_entropy_monitoring(
            structured_prompt,
            max_tokens,
            temperature
        )
        
        # Extract reasoning blocks
        thoughts = self.prompt_builder.extract_think_blocks(output)
        
        # Calculate token efficiency (vs. baseline CoT)
        tokens_used = self._estimate_tokens(output)
        baseline_tokens = tokens_used * 1.6  # CoT typically uses ~60% more
        efficiency = (baseline_tokens - tokens_used) / baseline_tokens
        
        # Create result
        result = GenerationResult(
            output=output,
            thoughts=thoughts,
            entropy_points=entropy_points,
            tokens_used=tokens_used,
            reasoning_efficiency=efficiency
        )
        
        # Track history
        self.generation_history.append(result)
        
        return result
    
    def _generate_with_entropy_monitoring(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> tuple[str, List[EntropyPoint]]:
        """
        Simulate generation with entropy monitoring.
        
        Production implementation would:
        1. Stream tokens from LLM API
        2. Access logprobs for each token
        3. Calculate entropy in real-time
        4. Insert <THINK> prompts when entropy spikes
        
        Args:
            prompt: Structured prompt
            max_tokens: Token limit
            temperature: Sampling temperature
            
        Returns:
            Tuple of (generated_code, entropy_points)
        """
        # For demonstration, return pre-generated examples based on prompt
        if "quicksort" in prompt.lower():
            return self._quicksort_example()
        elif "binary search" in prompt.lower():
            return self._binary_search_example()
        elif "api" in prompt.lower() or "rest" in prompt.lower():
            return self._api_design_example()
        else:
            return self._generic_example(prompt)
    
    def _quicksort_example(self) -> tuple[str, List[EntropyPoint]]:
        """Example output for quicksort implementation."""
        code = '''def quicksort(arr: List[int]) -> List[int]:
    """
    Sort array using quicksort algorithm.
    
    Time: O(n log n) average, O(n²) worst
    Space: O(log n) for recursion stack
    """
    if len(arr) <= 1:
        return arr
    
    # <THINK>
    # Pivot selection is critical for performance:
    # - First/last element: O(n²) on sorted input
    # - Middle element: Good for sorted/reverse-sorted
    # - Random: Best average-case guarantee
    # - Median-of-three: Industry standard
    # 
    # Choose middle for simplicity and good average performance
    # </THINK>
    
    pivot = arr[len(arr) // 2]
    
    # Partition around pivot
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # Recursive sort
    return quicksort(left) + middle + quicksort(right)
'''
        
        entropy_points = [
            EntropyPoint(
                position=10,
                entropy=0.78,
                token="pivot",
                reason="High uncertainty - multiple pivot strategies available",
                should_think=True
            )
        ]
        
        return code, entropy_points
    
    def _binary_search_example(self) -> tuple[str, List[EntropyPoint]]:
        """Example output for binary search implementation."""
        code = '''def binary_search(arr: List[int], target: int) -> int:
    """
    Find target in sorted array using binary search.
    
    Time: O(log n)
    Space: O(1)
    
    Returns: Index of target, or -1 if not found
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        # <THINK>
        # Midpoint calculation has subtle overflow issues:
        # - (left + right) // 2: Can overflow for large arrays
        # - left + (right - left) // 2: Safe, no overflow
        # Use safer version for production code
        # </THINK>
        
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
'''
        
        entropy_points = [
            EntropyPoint(
                position=8,
                entropy=0.72,
                token="mid",
                reason="High uncertainty - multiple midpoint calculation strategies",
                should_think=True
            )
        ]
        
        return code, entropy_points
    
    def _api_design_example(self) -> tuple[str, List[EntropyPoint]]:
        """Example output for API design."""
        code = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

tasks: List[Task] = []

# <THINK>
# RESTful design decisions:
# - Use plural nouns for collections: /tasks (not /task)
# - POST for creation, PUT for full update, PATCH for partial
# - Return 201 Created with Location header for POST
# - Use 404 for not found, 400 for validation errors
# Following REST conventions for consistency
# </THINK>

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    """Create a new task."""
    tasks.append(task)
    return task

@app.get("/tasks")
def list_tasks():
    """List all tasks."""
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get specific task."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")
'''
        
        entropy_points = [
            EntropyPoint(
                position=12,
                entropy=0.81,
                token="/tasks",
                reason="High uncertainty - RESTful naming and verb conventions",
                should_think=True
            )
        ]
        
        return code, entropy_points
    
    def _generic_example(self, prompt: str) -> tuple[str, List[EntropyPoint]]:
        """Generic example for unknown prompts."""
        code = f"""# Implementation for: {prompt}

def solution():
    \"\"\"
    Generated solution structure.
    
    In production, this would be generated by the LLM
    with real-time entropy monitoring.
    \"\"\"
    # <THINK>
    # Analyzing requirements and choosing appropriate approach
    # </THINK>
    
    pass  # Implementation here
"""
        
        entropy_points = []
        return code, entropy_points
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough heuristic).
        
        Production version would use tiktoken or similar.
        """
        return len(text.split()) + len(text) // 4
    
    def get_statistics(self) -> ThinkingStatistics:
        """
        Compute statistics across all generations.
        
        Returns:
            ThinkingStatistics with aggregate metrics
            
        Example:
            >>> stats = agent.get_statistics()
            >>> print(stats.summary())
        """
        if not self.generation_history:
            return ThinkingStatistics(
                total_generations=0,
                total_thoughts=0,
                avg_thoughts_per_generation=0.0,
                avg_entropy_at_thinking=0.0,
                max_entropy=0.0,
                min_entropy=0.0,
                entropy_std=0.0,
                times_over_threshold=0,
                token_efficiency=None
            )
        
        total_thoughts = sum(len(r.thoughts) for r in self.generation_history)
        avg_thoughts = total_thoughts / len(self.generation_history)
        
        # Entropy statistics
        all_entropy_values = [
            p.entropy
            for result in self.generation_history
            for p in result.entropy_points
        ]
        
        if all_entropy_values:
            avg_entropy = sum(all_entropy_values) / len(all_entropy_values)
            max_entropy = max(all_entropy_values)
            min_entropy = min(all_entropy_values)
            
            # Standard deviation
            mean = avg_entropy
            variance = sum((x - mean) ** 2 for x in all_entropy_values) / len(all_entropy_values)
            entropy_std = variance ** 0.5
        else:
            avg_entropy = max_entropy = min_entropy = entropy_std = 0.0
        
        times_over = sum(
            len([p for p in r.entropy_points if p.should_think])
            for r in self.generation_history
        )
        
        # Average token efficiency
        efficiencies = [
            r.reasoning_efficiency
            for r in self.generation_history
            if r.reasoning_efficiency is not None
        ]
        avg_efficiency = (
            sum(efficiencies) / len(efficiencies) if efficiencies else None
        )
        
        return ThinkingStatistics(
            total_generations=len(self.generation_history),
            total_thoughts=total_thoughts,
            avg_thoughts_per_generation=avg_thoughts,
            avg_entropy_at_thinking=avg_entropy,
            max_entropy=max_entropy,
            min_entropy=min_entropy,
            entropy_std=entropy_std,
            times_over_threshold=times_over,
            token_efficiency=avg_efficiency
        )
    
    def reset(self) -> None:
        """Clear all history and reset agent state."""
        self.generation_history.clear()
        self.entropy_detector.reset()
