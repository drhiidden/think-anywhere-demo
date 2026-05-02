"""
Structured prompt engineering for dynamic reasoning.

Provides templates and utilities for constructing prompts that guide LLMs
to use <THINK> blocks only when encountering high uncertainty.

Also includes alternative prompting strategies (CoT, Interleaved) for
benchmarking and comparison.
"""

import re
from typing import List, Optional, Dict
from enum import Enum


class ReasoningMode(Enum):
    """Available reasoning strategies."""
    THINK_ANYWHERE = "think_anywhere"  # Dynamic, entropy-based
    CHAIN_OF_THOUGHT = "cot"           # Upfront reasoning
    INTERLEAVED = "interleaved"        # Fixed-interval reasoning
    NO_REASONING = "baseline"          # Direct generation


class PromptBuilder:
    """
    Constructs structured prompts for different reasoning modes.
    
    Provides templates for Think Anywhere (dynamic reasoning) and baseline
    approaches (CoT, Interleaved) for experimental comparison.
    
    Example:
        >>> builder = PromptBuilder()
        >>> prompt = "Implement quicksort in Python"
        >>> structured = builder.build(prompt, ReasoningMode.THINK_ANYWHERE)
        >>> print(structured)
    """
    
    THINK_ANYWHERE_TEMPLATE = """
{original_prompt}

REASONING INSTRUCTIONS:
- Use <THINK>reasoning</THINK> blocks for complex decisions or ambiguities
- Keep reasoning brief and focused on the specific decision point
- Only reason when genuinely uncertain - not for trivial code
- After reasoning, continue with implementation

EXAMPLE:
```python
def example():
    # Simple assignment - no reasoning needed
    x = 5
    
    # <THINK>
    # Complex decision: Choose between Algorithm A (O(n log n)) and B (O(n²))
    # For n > 1000, Algorithm A is more efficient despite higher constant factors
    # Choose A for scalability
    # </THINK>
    
    # Implementation follows reasoning
    result = algorithm_a(x)
```

NOW IMPLEMENT:
"""

    COT_TEMPLATE = """
{original_prompt}

Before implementing, please think through the problem step by step:
1. Analyze the requirements
2. Identify key decisions and trade-offs
3. Design your approach
4. Consider edge cases

Show your complete reasoning first, then implement.
"""

    INTERLEAVED_TEMPLATE = """
{original_prompt}

Implement using alternating reasoning and code blocks:
[REASONING] → [CODE] → [REASONING] → [CODE]

Use this format:
```
REASONING: First, I need to...
CODE: <implementation>

REASONING: Next, I should consider...
CODE: <implementation>
```
"""
    
    def build(
        self,
        prompt: str,
        mode: ReasoningMode = ReasoningMode.THINK_ANYWHERE,
        custom_template: Optional[str] = None
    ) -> str:
        """
        Build a structured prompt for the given reasoning mode.
        
        Args:
            prompt: Original user prompt
            mode: Reasoning strategy to use
            custom_template: Optional custom template (overrides mode)
            
        Returns:
            Structured prompt with reasoning instructions
        """
        if custom_template:
            return custom_template.format(original_prompt=prompt)
        
        if mode == ReasoningMode.THINK_ANYWHERE:
            return self.THINK_ANYWHERE_TEMPLATE.format(original_prompt=prompt)
        elif mode == ReasoningMode.CHAIN_OF_THOUGHT:
            return self.COT_TEMPLATE.format(original_prompt=prompt)
        elif mode == ReasoningMode.INTERLEAVED:
            return self.INTERLEAVED_TEMPLATE.format(original_prompt=prompt)
        else:  # NO_REASONING
            return prompt
    
    def extract_think_blocks(self, text: str) -> List[str]:
        """
        Extract all <THINK> blocks from generated text.
        
        Args:
            text: Generated output potentially containing <THINK> blocks
            
        Returns:
            List of reasoning strings (content between tags)
            
        Example:
            >>> text = "x = 5\\n<THINK>Choose pivot</THINK>\\npivot = x"
            >>> builder.extract_think_blocks(text)
            ['Choose pivot']
        """
        pattern = r'<THINK>(.*?)</THINK>'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return [m.strip() for m in matches]
    
    def create_think_block(self, reasoning: str) -> str:
        """
        Format reasoning as a <THINK> block.
        
        Args:
            reasoning: Reasoning text
            
        Returns:
            Formatted <THINK> block
        """
        return f"<THINK>\n{reasoning.strip()}\n</THINK>"
    
    def remove_think_blocks(self, text: str) -> str:
        """
        Remove all <THINK> blocks, keeping only implementation.
        
        Args:
            text: Generated output with <THINK> blocks
            
        Returns:
            Clean code without reasoning blocks
        """
        pattern = r'<THINK>.*?</THINK>'
        return re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE).strip()
    
    def compare_modes(self, prompt: str) -> Dict[ReasoningMode, str]:
        """
        Generate prompts for all reasoning modes for comparison.
        
        Useful for benchmarking different reasoning strategies.
        
        Args:
            prompt: Original user prompt
            
        Returns:
            Dictionary mapping each mode to its structured prompt
        """
        return {
            mode: self.build(prompt, mode)
            for mode in ReasoningMode
        }
    
    def validate_think_block_syntax(self, text: str) -> bool:
        """
        Check if all <THINK> blocks are properly closed.
        
        Args:
            text: Generated text to validate
            
        Returns:
            True if syntax is valid (all blocks closed)
        """
        open_count = text.count('<THINK>')
        close_count = text.count('</THINK>')
        return open_count == close_count
