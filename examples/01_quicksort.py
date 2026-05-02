"""
Example 1: Quicksort with Dynamic Reasoning

Demonstrates Think Anywhere on a classic algorithm problem.
The agent reasons about pivot selection strategy when uncertainty is high.
"""

from think_anywhere import ThinkingAgent


def main():
    # Initialize agent with conservative threshold
    agent = ThinkingAgent(
        model="gpt-4",
        entropy_threshold=0.7
    )
    
    print("=" * 70)
    print("Think Anywhere Example: Quicksort Implementation")
    print("=" * 70)
    print()
    
    # Generate quicksort with reasoning
    prompt = """
    Implement an efficient quicksort algorithm in Python.
    Consider performance characteristics and edge cases.
    """
    
    result = agent.generate(prompt)
    
    # Display generated code
    print("GENERATED CODE:")
    print("-" * 70)
    print(result.output)
    print()
    
    # Display reasoning points
    print("REASONING BLOCKS:")
    print("-" * 70)
    for i, thought in enumerate(result.thoughts, 1):
        print(f"{i}. {thought}")
    print()
    
    # Display entropy analysis
    print("ENTROPY ANALYSIS:")
    print("-" * 70)
    for point in result.entropy_points:
        print(f"Position {point.position}: {point.reason}")
        print(f"  Entropy: {point.entropy:.3f}")
        print(f"  Token: {point.token}")
    print()
    
    # Display efficiency metrics
    print("EFFICIENCY METRICS:")
    print("-" * 70)
    print(f"Tokens used: {result.tokens_used}")
    print(f"Reasoning blocks: {len(result.thoughts)}")
    print(f"Token efficiency: {result.reasoning_efficiency:.1%}")
    print(f"(vs. Chain-of-Thought baseline)")
    print()
    
    # Display agent statistics
    stats = agent.get_statistics()
    print("AGENT STATISTICS:")
    print("-" * 70)
    print(stats.summary())


if __name__ == "__main__":
    main()
