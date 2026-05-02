"""
Basic unit tests for Think Anywhere components.

Run with: pytest tests/
"""

import pytest
from think_anywhere import ThinkingAgent, EntropyDetector, PromptBuilder
from think_anywhere.prompts import ReasoningMode
from think_anywhere.models import EntropyPoint, GenerationResult


class TestEntropyDetector:
    """Test entropy calculation and uncertainty detection."""
    
    def test_entropy_calculation_uniform(self):
        """Uniform distribution should have high entropy."""
        detector = EntropyDetector(threshold=0.5)
        probs = [0.25, 0.25, 0.25, 0.25]
        
        entropy = detector.calculate_entropy(probs)
        
        assert 0.99 < entropy <= 1.0  # Should be near maximum
    
    def test_entropy_calculation_certain(self):
        """Certain distribution should have low entropy."""
        detector = EntropyDetector(threshold=0.5)
        probs = [0.95, 0.03, 0.01, 0.01]
        
        entropy = detector.calculate_entropy(probs)
        
        assert 0.0 <= entropy < 0.3  # Should be low
    
    def test_should_think_threshold(self):
        """Test threshold-based reasoning activation."""
        detector = EntropyDetector(threshold=0.7)
        
        assert detector.should_think(0.8) is True
        assert detector.should_think(0.6) is False
        assert detector.should_think(0.7) is True
    
    def test_invalid_threshold(self):
        """Invalid threshold should raise ValueError."""
        with pytest.raises(ValueError):
            EntropyDetector(threshold=1.5)
        
        with pytest.raises(ValueError):
            EntropyDetector(threshold=-0.1)
    
    def test_statistics_calculation(self):
        """Test entropy statistics computation."""
        detector = EntropyDetector(threshold=0.5)
        
        # Generate some entropy values
        detector.calculate_entropy([0.8, 0.2])  # Low entropy
        detector.calculate_entropy([0.5, 0.5])  # High entropy
        detector.calculate_entropy([0.6, 0.4])  # Medium entropy
        
        stats = detector.get_statistics()
        
        assert stats['count'] == 3
        assert 0 < stats['mean'] < 1
        assert stats['times_over_threshold'] >= 0


class TestPromptBuilder:
    """Test prompt engineering utilities."""
    
    def test_build_think_anywhere_prompt(self):
        """Test Think Anywhere prompt construction."""
        builder = PromptBuilder()
        prompt = "Implement quicksort"
        
        result = builder.build(prompt, ReasoningMode.THINK_ANYWHERE)
        
        assert "Implement quicksort" in result
        assert "<THINK>" in result
        assert "REASONING INSTRUCTIONS" in result
    
    def test_build_cot_prompt(self):
        """Test Chain-of-Thought prompt construction."""
        builder = PromptBuilder()
        prompt = "Implement quicksort"
        
        result = builder.build(prompt, ReasoningMode.CHAIN_OF_THOUGHT)
        
        assert "Implement quicksort" in result
        assert "step by step" in result.lower()
    
    def test_extract_think_blocks(self):
        """Test extraction of reasoning blocks."""
        builder = PromptBuilder()
        text = """
        x = 5
        <THINK>
        Choose pivot strategy
        </THINK>
        pivot = x
        <THINK>
        Partition array
        </THINK>
        """
        
        thoughts = builder.extract_think_blocks(text)
        
        assert len(thoughts) == 2
        assert "Choose pivot strategy" in thoughts[0]
        assert "Partition array" in thoughts[1]
    
    def test_remove_think_blocks(self):
        """Test removal of reasoning blocks."""
        builder = PromptBuilder()
        text = "x = 5\n<THINK>reasoning</THINK>\ny = 10"
        
        clean = builder.remove_think_blocks(text)
        
        assert "<THINK>" not in clean
        assert "x = 5" in clean
        assert "y = 10" in clean
    
    def test_validate_syntax(self):
        """Test <THINK> block syntax validation."""
        builder = PromptBuilder()
        
        valid = "<THINK>reason</THINK>"
        invalid = "<THINK>reason"
        
        assert builder.validate_think_block_syntax(valid) is True
        assert builder.validate_think_block_syntax(invalid) is False


class TestThinkingAgent:
    """Test main agent functionality."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ThinkingAgent(entropy_threshold=0.7)
        
        assert agent.threshold == 0.7
        assert agent.model == "gpt-4"
        assert len(agent.generation_history) == 0
    
    def test_invalid_threshold(self):
        """Invalid threshold should raise ValueError."""
        with pytest.raises(ValueError):
            ThinkingAgent(entropy_threshold=1.5)
    
    def test_generate_quicksort(self):
        """Test generation for quicksort example."""
        agent = ThinkingAgent(entropy_threshold=0.7)
        
        result = agent.generate("Implement quicksort")
        
        assert result.output is not None
        assert "quicksort" in result.output.lower()
        assert len(result.thoughts) > 0  # Should have reasoning
        assert result.tokens_used > 0
    
    def test_generation_tracks_history(self):
        """Test that generation results are tracked."""
        agent = ThinkingAgent()
        
        agent.generate("Implement quicksort")
        agent.generate("Implement binary search")
        
        assert len(agent.generation_history) == 2
    
    def test_get_statistics(self):
        """Test statistics computation."""
        agent = ThinkingAgent()
        
        agent.generate("Implement quicksort")
        stats = agent.get_statistics()
        
        assert stats.total_generations == 1
        assert stats.total_thoughts >= 0
        assert 0 <= stats.avg_entropy_at_thinking <= 1
    
    def test_reset(self):
        """Test agent reset."""
        agent = ThinkingAgent()
        
        agent.generate("Implement quicksort")
        assert len(agent.generation_history) > 0
        
        agent.reset()
        assert len(agent.generation_history) == 0


class TestModels:
    """Test data models."""
    
    def test_entropy_point_validation(self):
        """Test EntropyPoint entropy validation."""
        # Valid entropy
        point = EntropyPoint(
            position=0,
            entropy=0.5,
            token="test",
            reason="testing"
        )
        assert point.entropy == 0.5
        
        # Invalid entropy
        with pytest.raises(ValueError):
            EntropyPoint(
                position=0,
                entropy=1.5,
                token="test",
                reason="testing"
            )
    
    def test_generation_result_properties(self):
        """Test GenerationResult computed properties."""
        result = GenerationResult(
            output="code",
            thoughts=["thought1", "thought2"],
            entropy_points=[],
            tokens_used=100
        )
        
        assert result.has_reasoning is True
        assert result.num_reasoning_points == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
