# Contributing to Think Anywhere

Thank you for your interest in contributing! This document provides guidelines for contributing to the Think Anywhere project.

## Code of Conduct

- Be respectful and inclusive
- Focus on technical merit
- Provide constructive feedback
- Welcome newcomers

## Development Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/drhidden/think-anywhere.git
   cd think-anywhere
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   pytest --cov=think_anywhere --cov-report=html
   ```

3. **Code quality**:
   ```bash
   # Format code
   black think_anywhere/ examples/ tests/
   isort think_anywhere/ examples/ tests/
   
   # Lint
   flake8 think_anywhere/
   mypy think_anywhere/
   ```

## Contribution Guidelines

### Reporting Issues

- Use GitHub Issues
- Include:
  - Clear description
  - Steps to reproduce
  - Expected vs. actual behavior
  - Environment details (Python version, OS)

### Pull Requests

1. **Branch from main**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Follow existing code style
   - Add tests for new features
   - Update documentation
   - Keep commits focused and atomic

3. **Test thoroughly**:
   ```bash
   pytest tests/ -v
   black think_anywhere/ examples/ tests/ --check
   mypy think_anywhere/
   ```

4. **Submit PR**:
   - Clear title and description
   - Reference related issues
   - Explain motivation and approach

### Code Style

- **Python**: Follow PEP 8
- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style
- **Type hints**: Required for public APIs
- **Imports**: Sorted with isort

Example:
```python
def calculate_entropy(probabilities: List[float]) -> float:
    """
    Calculate Shannon entropy from probability distribution.
    
    Args:
        probabilities: Token probability distribution
        
    Returns:
        Normalized entropy in [0, 1]
        
    Example:
        >>> calculate_entropy([0.5, 0.5])
        1.0
    """
    # Implementation...
```

### Testing

- Minimum 80% code coverage
- Test edge cases
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_entropy_calculation_uniform():
    """Uniform distribution should have high entropy."""
    # Arrange
    detector = EntropyDetector(threshold=0.5)
    probs = [0.25, 0.25, 0.25, 0.25]
    
    # Act
    entropy = detector.calculate_entropy(probs)
    
    # Assert
    assert 0.99 < entropy <= 1.0
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Include examples in docstrings
- Update CHANGELOG.md

## Areas for Contribution

### High Priority

1. **LLM API Integration**
   - OpenAI API with logprobs
   - Anthropic Claude integration
   - Real-time entropy monitoring

2. **Benchmarking**
   - HumanEval evaluation
   - MBPP evaluation
   - Performance metrics

3. **Visualization**
   - Entropy plots
   - Reasoning flow diagrams
   - Interactive dashboards

### Medium Priority

1. **Advanced Entropy Detection**
   - Multi-token lookahead
   - Context-aware thresholds
   - Adaptive threshold tuning

2. **Training Pipeline**
   - LoRA fine-tuning scripts
   - GRPO reinforcement learning
   - Custom token integration

3. **Examples and Tutorials**
   - More code generation examples
   - Debugging scenarios
   - Design pattern examples

### Low Priority

1. **CLI Tool**
   - Command-line interface
   - Configuration files
   - Batch processing

2. **Web Interface**
   - Simple web UI
   - Real-time entropy visualization
   - Interactive playground

## Research Contributions

If you're conducting research using Think Anywhere:

1. **Share findings**: Open issues or discussions
2. **Propose improvements**: Based on empirical results
3. **Contribute benchmarks**: New evaluation datasets
4. **Publish**: Please cite the project in papers

## Questions?

- Open a GitHub Discussion
- Comment on relevant issues
- Reach out via the blog: [drhidden.github.io](https://drhidden.github.io)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve Think Anywhere! 🚀
