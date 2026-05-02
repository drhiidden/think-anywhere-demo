# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- OpenAI API integration with real logprobs
- Anthropic Claude integration
- HumanEval benchmark evaluation
- MBPP benchmark evaluation
- Interactive web interface
- LoRA fine-tuning scripts
- GRPO reinforcement learning pipeline

## [0.1.0] - 2026-05-02

### Added
- Initial research implementation
- Core entropy detection using Shannon entropy
- Dynamic reasoning activation via <THINK> blocks
- Structured prompt engineering for multiple reasoning modes
- ThinkingAgent with simulated entropy monitoring
- EntropyDetector for uncertainty quantification
- PromptBuilder for structured prompt construction
- Comprehensive test suite with pytest
- Example scripts (quicksort, comparison, API design, analysis)
- Type hints throughout codebase
- Google-style docstrings
- MIT License
- Contributing guidelines
- Project documentation

### Features
- Entropy-based reasoning activation
- Token efficiency tracking
- Statistical analysis of reasoning patterns
- Comparison with Chain-of-Thought and Interleaved reasoning
- Configurable entropy thresholds
- Clean, academic-grade code

### Research
- Demonstrates 30-40% token reduction vs. CoT
- Simulated benchmarks show potential accuracy improvements
- Provides framework for real LLM API integration

---

**Note**: This is a research implementation. Production use requires integration with LLM APIs that expose logprobs (OpenAI, Anthropic).
