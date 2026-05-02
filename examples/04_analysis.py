"""
Example 4: Entropy Analysis and Visualization

Advanced example showing entropy patterns and reasoning activation points.
Useful for research and tuning threshold values.
"""

from think_anywhere import ThinkingAgent, EntropyDetector
import matplotlib.pyplot as plt


def analyze_entropy_patterns():
    """Analyze entropy patterns across multiple generations."""
    
    agent = ThinkingAgent(entropy_threshold=0.7)
    
    test_prompts = [
        "Implement bubble sort",
        "Implement quicksort",
        "Design a REST API for users",
        "Write a binary search tree",
        "Create a caching layer"
    ]
    
    print("=" * 70)
    print("Entropy Pattern Analysis")
    print("=" * 70)
    print()
    
    all_entropy_values = []
    all_labels = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"{i}. Testing: {prompt}")
        
        result = agent.generate(prompt)
        
        print(f"   Reasoning blocks: {len(result.thoughts)}")
        print(f"   High-entropy points: {len(result.entropy_points)}")
        
        for point in result.entropy_points:
            all_entropy_values.append(point.entropy)
            all_labels.append(f"Q{i}")
        
        print()
    
    # Statistics
    stats = agent.get_statistics()
    print("AGGREGATE STATISTICS:")
    print("-" * 70)
    print(stats.summary())
    print()
    
    # Visualization (if matplotlib available)
    try:
        plt.figure(figsize=(10, 6))
        
        # Entropy distribution
        plt.subplot(2, 1, 1)
        plt.hist(all_entropy_values, bins=20, edgecolor='black', alpha=0.7)
        plt.axvline(0.7, color='red', linestyle='--', label='Threshold')
        plt.xlabel('Entropy')
        plt.ylabel('Frequency')
        plt.title('Entropy Distribution Across Generations')
        plt.legend()
        
        # Entropy by question
        plt.subplot(2, 1, 2)
        plt.scatter(range(len(all_entropy_values)), all_entropy_values, alpha=0.6)
        plt.axhline(0.7, color='red', linestyle='--', label='Threshold')
        plt.xlabel('Generation Point')
        plt.ylabel('Entropy')
        plt.title('Entropy Over Time')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('entropy_analysis.png', dpi=150)
        print("✓ Visualization saved to 'entropy_analysis.png'")
        
    except ImportError:
        print("⚠ matplotlib not available - skipping visualization")


def tune_threshold():
    """Experiment with different threshold values."""
    
    print("\n" + "=" * 70)
    print("Threshold Tuning Experiment")
    print("=" * 70)
    print()
    
    prompt = "Implement a hash table with collision resolution"
    thresholds = [0.3, 0.5, 0.7, 0.9]
    
    print(f"Testing prompt: {prompt}\n")
    print(f"{'Threshold':>10} | {'Reasoning Blocks':>17} | {'Entropy Points':>15} | {'Tokens':>7}")
    print("-" * 70)
    
    for threshold in thresholds:
        agent = ThinkingAgent(entropy_threshold=threshold)
        result = agent.generate(prompt)
        
        print(f"{threshold:>10.1f} | {len(result.thoughts):>17} | {len(result.entropy_points):>15} | {result.tokens_used:>7}")
    
    print()
    print("Observations:")
    print("• Lower threshold (0.3) = More reasoning blocks (may be excessive)")
    print("• Higher threshold (0.9) = Fewer reasoning blocks (may miss important decisions)")
    print("• Recommended: 0.6-0.7 for balanced reasoning")


if __name__ == "__main__":
    analyze_entropy_patterns()
    tune_threshold()
