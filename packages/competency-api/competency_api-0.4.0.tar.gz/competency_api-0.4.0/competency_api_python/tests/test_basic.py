"""
Basic test suite for the competency-api Python binding.

Tests core functionality including:
- Exact skill matches
- Proficiency level differences
- Related skills matching
- Error handling
"""

import pytest
from competency_api import match_score, init_logging


class TestBasicFunctionality:
    """Test basic API functionality."""

    def test_init_logging(self):
        """Test that init_logging doesn't raise errors."""
        init_logging()  # Should not raise

    def test_exact_skill_match(self):
        """Test identical skill and proficiency level."""
        required = [{"name": "JavaScript", "level": {"value": 3, "max": 5}}]
        candidate = [{"name": "JavaScript", "level": {"value": 3, "max": 5}}]

        result = match_score(required, candidate)

        assert "overall_score" in result
        assert "skill_scores" in result
        assert len(result["skill_scores"]) == 1

        # Perfect match should score very high
        probability = result["skill_scores"][0]["probability"]
        assert probability >= 0.95, f"Expected score >= 0.95, got {probability}"

    def test_candidate_exceeds_requirement(self):
        """Test when candidate exceeds required proficiency."""
        required = [{"name": "Python", "level": {"value": 3, "max": 5}}]
        candidate = [{"name": "Python", "level": {"value": 5, "max": 5}}]

        result = match_score(required, candidate)

        # Exceeding requirements should score very high
        probability = result["skill_scores"][0]["probability"]
        assert probability >= 0.95, f"Expected score >= 0.95, got {probability}"

    def test_proficiency_penalty(self):
        """Test proficiency penalty when candidate falls short."""
        required = [{"name": "Python", "level": {"value": 5, "max": 5}}]
        candidate = [{"name": "Python", "level": {"value": 3, "max": 5}}]

        result = match_score(required, candidate)

        # Should have a penalty for lower proficiency
        probability = result["skill_scores"][0]["probability"]
        assert 0.5 <= probability < 0.95, f"Expected 0.5 <= score < 0.95, got {probability}"

    def test_similar_skills(self):
        """Test matching similar but not identical skills."""
        required = [{"name": "REST API", "level": {"value": 3, "max": 5}}]
        candidate = [{"name": "RESTful APIs", "level": {"value": 3, "max": 5}}]

        result = match_score(required, candidate)

        # Similar wording should score high
        probability = result["skill_scores"][0]["probability"]
        assert probability >= 0.85, f"Expected score >= 0.85, got {probability}"

    def test_related_skills_web_dev(self):
        """Test matching related skills (web development scenario)."""
        required = [{"name": "Web development", "level": {"value": 4, "max": 5}}]
        candidate = [
            {"name": "HTML", "level": {"value": 4, "max": 5}},
            {"name": "CSS", "level": {"value": 4, "max": 5}},
            {"name": "JavaScript", "level": {"value": 4, "max": 5}},
        ]

        result = match_score(required, candidate)

        # Related skills should provide reasonable match
        probability = result["skill_scores"][0]["probability"]
        assert probability >= 0.40, f"Expected score >= 0.40, got {probability}"


class TestResultStructure:
    """Test the structure of returned results."""

    def test_result_contains_all_fields(self):
        """Test that result contains all expected fields."""
        required = [{"name": "Python", "level": {"value": 3, "max": 5}}]
        candidate = [{"name": "Python", "level": {"value": 3, "max": 5}}]

        result = match_score(required, candidate)

        # Check top-level fields
        assert "overall_score" in result
        assert "skill_scores" in result
        assert "skill_similarities" in result
        assert "pairwise_scores" in result

        # Check skill_scores structure
        assert len(result["skill_scores"]) > 0
        skill_score = result["skill_scores"][0]
        assert "skill_name" in skill_score
        assert "probability" in skill_score
        assert "mean" in skill_score
        assert "variance" in skill_score
        assert "confidence_interval" in skill_score

        # Check confidence_interval structure
        ci = skill_score["confidence_interval"]
        assert "lower" in ci
        assert "upper" in ci

    def test_overall_score_range(self):
        """Test that overall_score is between 0 and 1."""
        required = [{"name": "Python", "level": {"value": 3, "max": 5}}]
        candidate = [{"name": "Python", "level": {"value": 3, "max": 5}}]

        result = match_score(required, candidate)

        assert 0.0 <= result["overall_score"] <= 1.0


class TestMultipleSkills:
    """Test scenarios with multiple skills."""

    def test_multiple_required_skills(self):
        """Test matching against multiple required skills."""
        required = [
            {"name": "Python", "level": {"value": 3, "max": 5}},
            {"name": "JavaScript", "level": {"value": 3, "max": 5}},
        ]
        candidate = [
            {"name": "Python", "level": {"value": 4, "max": 5}},
            {"name": "JavaScript", "level": {"value": 4, "max": 5}},
        ]

        result = match_score(required, candidate)

        assert len(result["skill_scores"]) == 2
        assert result["overall_score"] >= 0.90

    def test_partial_skill_coverage(self):
        """Test when candidate has some but not all required skills."""
        required = [
            {"name": "Python", "level": {"value": 3, "max": 5}},
            {"name": "Java", "level": {"value": 3, "max": 5}},
        ]
        candidate = [
            {"name": "Python", "level": {"value": 4, "max": 5}},
        ]

        result = match_score(required, candidate)

        # Should have scores for both required skills
        assert len(result["skill_scores"]) == 2

        # Python should score high
        python_score = next(s for s in result["skill_scores"] if s["skill_name"] == "Python")
        assert python_score["probability"] >= 0.90

        # Java should score lower (no direct match)
        java_score = next(s for s in result["skill_scores"] if s["skill_name"] == "Java")
        assert java_score["probability"] < python_score["probability"]


class TestErrorHandling:
    """Test error handling."""

    def test_empty_required_skills(self):
        """Test behavior with empty required skills."""
        with pytest.raises(RuntimeError):
            match_score([], [{"name": "Python", "level": {"value": 3, "max": 5}}])

    def test_empty_candidate_skills(self):
        """Test behavior with empty candidate skills."""
        with pytest.raises(RuntimeError):
            match_score([{"name": "Python", "level": {"value": 3, "max": 5}}], [])

    def test_invalid_skill_structure(self):
        """Test behavior with invalid skill structure."""
        with pytest.raises(Exception):  # Could be TypeError or RuntimeError
            match_score(
                [{"name": "Python"}],  # Missing level
                [{"name": "Python", "level": {"value": 3, "max": 5}}]
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
