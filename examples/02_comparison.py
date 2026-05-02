"""
Example 2: Comparing Reasoning Strategies

Demonstrates the difference between Think Anywhere, Chain-of-Thought,
and Interleaved reasoning on the same problem.
"""

from think_anywhere import ThinkingAgent
from think_anywhere.prompts import ReasoningMode


def main():
    print("=" * 70)
    print("Comparing Reasoning Strategies: Binary Search")
    print("=" * 70)
    print()
    
    prompt = """
    Implement binary search in Python.
    Handle edge cases and ensure O(log n) complexity.
    """
    
    agent = ThinkingAgent(entropy_threshold=0.7)
    
    # Test all reasoning modes
    modes = [
        ReasoningMode.THINK_ANYWHERE,
        ReasoningMode.CHAIN_OF_THOUGHT,
        ReasoningMode.INTERLEAVED,
        ReasoningMode.NO_REASONING
    ]
    
    results = {}
    
    for mode in modes:
        print(f"\n{'=' * 70}")
        print(f"MODE: {mode.value.upper()}")
        print('=' * 70)
        
        result = agent.generate(prompt, mode=mode)
        results[mode] = result
        
        print(f"\nReasoning blocks: {len(result.thoughts)}")
        print(f"Tokens used: {result.tokens_used}")
        print(f"Entropy points: {len(result.entropy_points)}")
        
        if result.thoughts:
            print("\nFirst reasoning block:")
            print(result.thoughts[0][:200] + "..." if len(result.thoughts[0]) > 200 else result.thoughts[0])
    
    # Compare efficiency
    print(f"\n{'=' * 70}")
    print("EFFICIENCY COMPARISON")
    print('=' * 70)
    
    baseline = results[ReasoningMode.NO_REASONING].tokens_used
    
    for mode in modes:
        result = results[mode]
        overhead = ((result.tokens_used - baseline) / baseline * 100)
        print(f"{mode.value:20} | Tokens: {result.tokens_used:4} | Overhead: {overhead:+.1f}%")


if __name__ == "__main__":
    main()
