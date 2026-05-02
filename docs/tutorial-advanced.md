# Custom Training

**Level**: Advanced | **Time**: Full day  
**Prerequisites**: [Entropy Analysis](tutorial-entropy.md), PyTorch, familiarity with LoRA and RLHF

---

## Overview

The current implementation uses **prompt engineering** to guide models toward dynamic reasoning. This works well but relies on the model following instructions — it is a behavioral overlay, not a model capability.

The original Think Anywhere paper proposes **training** the model to reason natively, without needing structured prompts. This tutorial describes the full three-stage training pipeline.

> ⚠️ **Note**: The training pipeline requires access to model weights. This tutorial describes the methodology for research purposes. The demo implementation uses prompt engineering only.

---

## Stage 1: Custom Tokens

### Why Custom Tokens?

Rather than using the text strings `<THINK>` and `</THINK>`, the paper introduces dedicated vocabulary tokens:

```
<THINK_ANYWHERE_START>
<THINK_ANYWHERE_END>
```

This separates reasoning markers from regular text, making them unambiguous for the model.

### Embedding Initialization

A key detail: these tokens are **not initialized randomly**. The paper uses a semantic initialization:

```python
# Conceptual implementation
embedding_think = (
    0.5 * mean_embedding(["think", "any", "where"])
    + 0.5 * embedding("<start_token>")
)
```

**Why**: Random initialization would require the model to learn what the token *means* from scratch. Semantic initialization gives the model a head start — it already knows these tokens are related to "thinking" and to structural boundaries.

---

## Stage 2: Supervised Fine-Tuning (SFT) with LoRA

### Generate Training Data

Use a strong teacher model (e.g., GPT-4) to produce ~5000 examples with the pattern:

```
code...
<THINK>
reasoning...
</THINK>
code continues...
```

The teacher should insert `<THINK>` blocks at genuinely complex decision points — algorithm selection, data structure choice, edge case handling — not at trivial steps.

### Apply LoRA

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

# Load base model
model = AutoModelForCausalLM.from_pretrained("your-base-model")

# Add new tokens
tokenizer.add_tokens(["<THINK_ANYWHERE_START>", "<THINK_ANYWHERE_END>"])
model.resize_token_embeddings(len(tokenizer))

# Initialize new token embeddings semantically
with torch.no_grad():
    think_words = ["think", "any", "where"]
    mean_emb = mean([model.get_input_embeddings()(
        tokenizer.encode(w, return_tensors="pt")
    ) for w in think_words])
    start_emb = model.get_input_embeddings()(
        tokenizer.encode("<s>", return_tensors="pt")
    )
    new_emb = 0.5 * mean_emb + 0.5 * start_emb
    model.get_input_embeddings().weight[-2] = new_emb  # START token

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Trainable: ~0.5% of parameters
```

### Train on SFT Data

```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./sft-think-anywhere",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=sft_dataset,  # Your generated examples
)

trainer.train()
```

**Result after SFT**: The model will insert `<THINK>` blocks, but not consistently at the right moments. SFT alone shows limited improvement — this is expected.

---

## Stage 3: Reinforcement Learning with GRPO

SFT teaches the *form* (how to write `<THINK>` blocks). GRPO teaches *when* to use them, by optimizing for correctness.

### Reward Function

The reward has two components:

```python
def compute_reward(generated_output, expected_output):
    """
    Reward = 0.1 * structure_score + 0.9 * correctness_score
    """
    structure_score = evaluate_structure(generated_output)
    correctness_score = evaluate_correctness(generated_output, expected_output)

    return 0.1 * structure_score + 0.9 * correctness_score


def evaluate_structure(output):
    """
    Check structural validity of THINK blocks.
    - Has at least one THINK block (0.33)
    - All THINK blocks properly closed (0.33)
    - At least one initial reasoning block (0.33)
    """
    score = 0.0
    has_think = "<THINK>" in output
    balanced = output.count("<THINK>") == output.count("</THINK>")
    has_intro_block = output.strip().startswith("<THINK>")

    if has_think:
        score += 0.33
    if balanced:
        score += 0.33
    if has_intro_block:
        score += 0.34

    return score


def evaluate_correctness(output, expected):
    """
    Run the generated code against test cases.
    Binary: passes all tests (1.0) or not (0.0).
    """
    code = extract_code(output)  # Strip THINK blocks
    return run_tests(code, expected)
```

### Why 10% / 90%?

The 90% weight on correctness ensures the model focuses on writing code that **works**. The 10% on structure prevents the model from learning to simply omit `<THINK>` blocks to maximize the 90%.

This is a critical design decision: without the structure term, GRPO would likely converge to never reasoning (simpler, often correct). With it, the model learns that reasoning is expected and rewarded when it leads to correct code.

---

## Expected Results

| Stage | HumanEval | MBPP | Token Efficiency |
|-------|-----------|------|------------------|
| Base model | 67.3% | 72.1% | baseline |
| + SFT | 71.2% | 75.8% | -5% |
| + GRPO | **79.7%** | **84.1%** | **-30%** |

The GRPO stage provides the largest improvement. SFT alone is insufficient — the model learns the format but not the judgment of *when* to reason.

---

## Evaluation: Reproducing Benchmarks

Once trained, evaluate against standard benchmarks:

```python
from think_anywhere.evaluation import HumanEvalRunner, MBPPRunner

runner = HumanEvalRunner(agent=trained_agent)
results = runner.run(n_problems=164, temperature=0.2)

print(f"Pass@1: {results.pass_at_1:.1%}")
print(f"Avg tokens: {results.avg_tokens:.0f}")
print(f"Avg THINK blocks: {results.avg_think_blocks:.2f}")
```

---

## Further Directions

1. **Entropy-gated GRPO**: Only compute `THINK` reward when logprob entropy was actually high at the insertion point — this tightens the training signal
2. **Multi-language evaluation**: Benchmark on Python, JavaScript, Rust to test generalization
3. **Reasoning compression**: Shorter `<THINK>` blocks with same or better correctness

---

## Related Work

- **GRPO** (Group Relative Policy Optimization): Used here for RL training
- **LoRA** (Hu et al., 2022): Low-rank adaptation for efficient fine-tuning
- **SFT → RLHF pipeline**: Standard pattern, here adapted for code correctness rather than human preferences

---

**Original Paper**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [YouTube Presentation](https://www.youtube.com/watch?v=wXGUiMfgL18)
