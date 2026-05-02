# Entropy Analysis

**Level**: Intermediate | **Time**: 2 hours  
**Prerequisites**: [Introduction to Think Anywhere](tutorial-basic.md), NumPy basics, probability theory

---

## Shannon Entropy: The Math

### Definition

For a discrete probability distribution `p = [p₁, p₂, ..., pₙ]`:

```
H(p) = -Σ pᵢ · log₂(pᵢ)
         i
```

### Normalized Entropy

To compare across distributions of different sizes, normalize by the maximum possible entropy:

```
H_norm(p) = H(p) / log₂(n)
```

This gives `H_norm ∈ [0, 1]`:
- **0** → perfect certainty (one token has p ≈ 1)
- **1** → maximum uncertainty (uniform distribution)

### Worked Examples

```python
import numpy as np

def normalized_entropy(probs):
    probs = np.clip(probs, 1e-10, 1.0)
    H = -np.sum(probs * np.log2(probs))
    return H / np.log2(len(probs))

# Case 1: Certain
p1 = [0.95, 0.03, 0.02]
print(f"Certain:   H = {normalized_entropy(p1):.3f}")  # ≈ 0.22

# Case 2: Two competing options
p2 = [0.5, 0.4, 0.1]
print(f"Competing: H = {normalized_entropy(p2):.3f}")  # ≈ 0.85

# Case 3: Uniform (maximum uncertainty)
p3 = [0.33, 0.33, 0.34]
print(f"Uniform:   H = {normalized_entropy(p3):.3f}")  # ≈ 1.00
```

---

## Why Entropy Works as a Reasoning Trigger

When a model assigns nearly equal probability to multiple completions, it is genuinely undecided. Any choice would be somewhat arbitrary — exactly the moment where explicit reasoning helps.

Empirical observation across 1000 code generation runs:

| Entropy Range | % of Tokens | Interpretation |
|---------------|-------------|----------------|
| `[0.0, 0.3)` | ~65% | Syntactic/obvious tokens (`def`, `return`, `:`) |
| `[0.3, 0.7)` | ~25% | Moderate choices (variable names, operators) |
| `[0.7, 1.0]` | ~10% | Genuine forks: algorithm choice, data structure, naming |

Think Anywhere acts only on the **10% of tokens** where reasoning truly matters.

---

## Visualizing Entropy During Generation

```python
from think_anywhere import ThinkingAgent, EntropyDetector
import matplotlib.pyplot as plt

detector = EntropyDetector(threshold=0.7)

# Simulate a sequence of token distributions
# (in production these come from model logprobs)
token_sequence = [
    {"token": "def",        "probs": [0.92, 0.04, 0.04]},
    {"token": "quicksort",  "probs": [0.41, 0.30, 0.29]},  # ← HIGH
    {"token": "(",          "probs": [0.98, 0.01, 0.01]},
    {"token": "arr",        "probs": [0.55, 0.30, 0.15]},
    {"token": "pivot",      "probs": [0.38, 0.35, 0.27]},  # ← HIGH
    {"token": "=",          "probs": [0.96, 0.02, 0.02]},
]

entropies = [
    detector.calculate_entropy(item["probs"])
    for item in token_sequence
]
tokens = [item["token"] for item in token_sequence]

plt.figure(figsize=(10, 4))
colors = ["#ff6b6b" if e >= 0.7 else "#6bcf7f" for e in entropies]
bars = plt.bar(tokens, entropies, color=colors, edgecolor="black")
plt.axhline(y=0.7, color="red", linestyle="--", label="Threshold (0.7)")
plt.ylim(0, 1.1)
plt.ylabel("Normalized Entropy")
plt.title("Token-Level Entropy During Code Generation")
plt.legend()
plt.tight_layout()
plt.savefig("entropy_analysis.png", dpi=150)
print("Saved to entropy_analysis.png")
```

**Red bars** are where `<THINK>` blocks would be activated.

---

## Threshold Selection

The threshold controls how often reasoning activates. There is a fundamental trade-off:

| Threshold | Reasoning Frequency | Token Cost | Risk |
|-----------|--------------------|-----------:|------|
| 0.3 | Very frequent | High | Over-thinking simple code |
| 0.5 | Balanced | Medium | — |
| **0.7** | Selective | **Low** | **Recommended** |
| 0.9 | Rare | Very low | Missing important decisions |

### Adaptive Threshold Strategy

```python
def adaptive_threshold(task_complexity):
    """
    Adjust threshold based on task type.
    Higher complexity → lower threshold (reason more often).
    """
    if task_complexity == "algorithm_design":
        return 0.5   # Reason more — many design choices
    elif task_complexity == "boilerplate":
        return 0.85  # Reason less — few real decisions
    else:
        return 0.7   # Default
```

---

## Entropy Statistics Over Multiple Generations

```python
from think_anywhere import ThinkingAgent

agent = ThinkingAgent(entropy_threshold=0.7)

prompts = [
    "Implement quicksort",
    "Implement binary search",
    "Design a REST API",
    "Write a hash table",
    "Create a caching layer",
]

for prompt in prompts:
    result = agent.generate(prompt)

stats = agent.get_statistics()
print(stats.summary())
```

**Example output**:
```
Think Anywhere Statistics:
  Total generations: 5
  Total reasoning blocks: 8
  Avg reasoning/generation: 1.60
  Avg entropy at reasoning: 0.776
  Entropy range: [0.721, 0.831]
  High-entropy events: 8
  Token efficiency: 37.8%
```

---

## Key Insight: Information Theory and Code

The reason entropy-based reasoning works for code generation specifically is that code has a **bimodal uncertainty structure**:

1. **Low uncertainty** — syntactic tokens (keywords, punctuation, obvious names): the model is near-certain
2. **High uncertainty** — semantic decisions (algorithm choice, data structure, naming strategy): multiple valid options with similar probability

Think Anywhere exploits this structure. Chain-of-Thought reasons about the low-uncertainty parts too — wasting tokens. Think Anywhere reasons *only* at the semantic decision points.

---

## Next Steps

- **Advanced**: [Custom Training](tutorial-advanced.md) — build a model that activates reasoning natively, without prompting

---

**Original Paper**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [YouTube Presentation](https://www.youtube.com/watch?v=wXGUiMfgL18)
