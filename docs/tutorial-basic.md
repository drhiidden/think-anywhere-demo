# Introduction to Think Anywhere

**Level**: Beginner | **Time**: 30 minutes  
**Prerequisites**: Basic Python, familiarity with LLMs

---

## What is Think Anywhere?

When an LLM generates code, it predicts tokens one by one. At each step, the model assigns probabilities to every possible next token. Most of the time, one option is clearly dominant — **low uncertainty, low entropy**. But sometimes the model genuinely doesn't know which path to take — **high uncertainty, high entropy**.

**Think Anywhere** uses this signal to activate reasoning *only at those critical moments*, instead of thinking upfront (Chain-of-Thought) or at fixed intervals (Interleaved Thinking).

---

## Core Concepts

### Entropy as Uncertainty

Shannon entropy measures how spread out a probability distribution is:

```
H(X) = -Σ p(x) · log₂(p(x))
```

**Example**:

```python
# Certain: one obvious choice
probs_certain = [0.95, 0.03, 0.02]
# H ≈ 0.24  → Low entropy → Keep going

# Uncertain: competing options
probs_uncertain = [0.35, 0.35, 0.30]
# H ≈ 0.99  → High entropy → THINK
```

### The THINK Block

When high entropy is detected, the model inserts a structured reasoning block:

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr

    # <THINK>
    # Pivot strategy affects worst-case performance.
    # First element → O(n²) on sorted input.
    # Middle element → balanced for common cases.
    # Choose middle for simplicity.
    # </THINK>

    pivot = arr[len(arr) // 2]
    ...
```

The reasoning is **embedded in the code**, not separated from it.

---

## Your First Experiment

### Step 1: Install

```bash
git clone https://github.com/drhiidden/think-anywhere-demo.git
cd think-anywhere-demo
pip install -e .
```

### Step 2: Run the quicksort example

```bash
python examples/01_quicksort.py
```

**Expected output**:
```
Generated code:
def quicksort(arr):
    ...
    # <THINK>
    # Pivot selection is critical...
    # </THINK>
    pivot = arr[len(arr) // 2]
    ...

Reasoning blocks:
  💭 Pivot selection is critical for performance...

Tokens used: 280
Efficiency: 37.5% vs CoT
```

### Step 3: Explore the threshold

Change the `entropy_threshold` and observe the difference:

```python
from think_anywhere import ThinkingAgent

# Conservative: reason only when very uncertain
agent_high = ThinkingAgent(entropy_threshold=0.9)

# Aggressive: reason more frequently
agent_low = ThinkingAgent(entropy_threshold=0.4)

prompt = "Implement binary search"

result_high = agent_high.generate(prompt)
result_low = agent_low.generate(prompt)

print(f"High threshold — reasoning blocks: {len(result_high.thoughts)}")
print(f"Low threshold  — reasoning blocks: {len(result_low.thoughts)}")
```

---

## Comparing with Chain-of-Thought

Run the comparison example to see all three strategies side by side:

```bash
python examples/02_comparison.py
```

| Method | Reasoning | Tokens | When |
|--------|-----------|--------|------|
| No reasoning | None | 150 | Never |
| CoT | All upfront | 450 | Always |
| Interleaved | Fixed intervals | 380 | Periodically |
| **Think Anywhere** | **Adaptive** | **280** | **When needed** |

---

## Key Takeaways

- **Entropy** measures model uncertainty token by token
- **Think Anywhere** only activates reasoning when `H ≥ threshold`
- **Result**: fewer tokens used, better reasoning quality
- The threshold is configurable — tune it for your use case

---

## Next Steps

- **Intermediate**: [Entropy Analysis](tutorial-entropy.md) — understand the math and visualize entropy patterns
- **Advanced**: [Custom Training](tutorial-advanced.md) — LoRA fine-tuning and GRPO

---

**Original Paper**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [YouTube Presentation](https://www.youtube.com/watch?v=wXGUiMfgL18)
