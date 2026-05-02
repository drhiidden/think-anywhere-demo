# Think Anywhere

Research implementation of entropy-based dynamic reasoning for Large Language Models.

## Quick Start

```bash
# Install
pip install -e .

# Run examples
python examples/01_quicksort.py
python examples/02_comparison.py

# Run tests
pytest tests/ -v
```

## Documentation

See [README.md](README.md) for full documentation.

## Project Structure

```
think-anywhere/
├── think_anywhere/      # Core library
│   ├── agent.py        # Main agent
│   ├── entropy.py      # Entropy detection
│   ├── prompts.py      # Prompt engineering
│   └── models.py       # Data models
├── examples/           # Usage examples
├── tests/              # Unit tests
└── docs/               # Additional documentation
```

## Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Test
pytest

# Format
black think_anywhere/ examples/ tests/

# Type check
mypy think_anywhere/
```

## License

MIT - See [LICENSE](LICENSE)
