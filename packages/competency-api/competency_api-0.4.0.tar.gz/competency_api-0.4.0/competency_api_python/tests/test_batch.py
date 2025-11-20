"""
Tests for batch_match_score functionality.
"""

import pytest
from competency_api import batch_match_score, match_score


class TestBatchMatching:
    """Test batch matching functionality."""

    def test_batch_empty_list(self):
        """Test batch processing with empty list."""
        results = batch_match_score([])
        assert results == []

    def test_batch_single_pair(self):
        """Test batch processing with a single pair."""
        pairs = [
            (
                [{"name": "Python", "level": {"value": 3, "max": 5}}],
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
            )
        ]
        results = batch_match_score(pairs)

        assert len(results) == 1
        assert "overall_score" in results[0]
        assert 0.0 <= results[0]["overall_score"] <= 1.0

    def test_batch_multiple_pairs(self):
        """Test batch processing with multiple pairs."""
        pairs = [
            # Pair 1: Exact match
            (
                [{"name": "Python", "level": {"value": 3, "max": 5}}],
                [{"name": "Python", "level": {"value": 3, "max": 5}}],
            ),
            # Pair 2: Related skills
            (
                [{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
                [{"name": "TypeScript", "level": {"value": 4, "max": 5}}],
            ),
            # Pair 3: Multiple skills
            (
                [
                    {"name": "Python", "level": {"value": 4, "max": 5}},
                    {"name": "SQL", "level": {"value": 3, "max": 5}},
                ],
                [
                    {"name": "Python", "level": {"value": 5, "max": 5}},
                    {"name": "PostgreSQL", "level": {"value": 4, "max": 5}},
                ],
            ),
        ]

        results = batch_match_score(pairs)

        assert len(results) == 3
        for result in results:
            assert "overall_score" in result
            assert "skill_scores" in result
            assert "skill_similarities" in result
            assert "pairwise_scores" in result
            assert 0.0 <= result["overall_score"] <= 1.0

    def test_batch_results_match_individual(self):
        """Test that batch results match individual match_score calls."""
        pairs = [
            (
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            ),
            (
                [{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
                [{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
            ),
        ]

        # Get batch results
        batch_results = batch_match_score(pairs)

        # Get individual results
        individual_results = []
        for required, candidate in pairs:
            result = match_score(required, candidate)
            individual_results.append(result)

        # Compare results
        assert len(batch_results) == len(individual_results)
        for batch_result, individual_result in zip(batch_results, individual_results):
            # Overall scores should be close (within 5% tolerance due to potential
            # minor differences in embedding/calculation paths)
            assert abs(batch_result["overall_score"] - individual_result["overall_score"]) < 0.05

            # Number of skill scores should match
            assert len(batch_result["skill_scores"]) == len(individual_result["skill_scores"])

    def test_batch_with_shared_skills(self):
        """Test batch processing where multiple pairs share the same skills (embedding reuse)."""
        pairs = [
            (
                [{"name": "Python", "level": {"value": 3, "max": 5}}],
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
            ),
            (
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            ),
            (
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            ),
        ]

        results = batch_match_score(pairs)

        assert len(results) == 3
        # All should have reasonable scores
        for result in results:
            assert result["overall_score"] >= 0.5  # Should be at least moderate match

    def test_batch_error_empty_skills(self):
        """Test that batch processing handles empty skills appropriately."""
        pairs = [
            (
                [],  # Empty required skills
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
            )
        ]

        with pytest.raises(Exception):  # Should raise an error
            batch_match_score(pairs)

    def test_batch_result_structure(self):
        """Test that batch results have the correct structure."""
        pairs = [
            (
                [{"name": "Python", "level": {"value": 4, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            )
        ]

        results = batch_match_score(pairs)
        result = results[0]

        # Check required fields
        assert "overall_score" in result
        assert "skill_scores" in result
        assert "skill_similarities" in result
        assert "pairwise_scores" in result

        # Check skill_scores structure
        assert len(result["skill_scores"]) > 0
        skill_score = result["skill_scores"][0]
        assert "skill_name" in skill_score
        assert "probability" in skill_score
        assert "confidence_interval" in skill_score
        assert "mean" in skill_score
        assert "variance" in skill_score

        # Check confidence_interval structure
        ci = skill_score["confidence_interval"]
        assert "lower" in ci
        assert "upper" in ci
        assert ci["lower"] <= ci["upper"]

    def test_batch_order_preserved(self):
        """Test that batch results maintain the same order as input pairs."""
        pairs = [
            # High score pair
            (
                [{"name": "Python", "level": {"value": 1, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            ),
            # Medium score pair
            (
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
                [{"name": "Python", "level": {"value": 3, "max": 5}}],
            ),
            # High score pair again
            (
                [{"name": "Python", "level": {"value": 2, "max": 5}}],
                [{"name": "Python", "level": {"value": 5, "max": 5}}],
            ),
        ]

        results = batch_match_score(pairs)

        assert len(results) == 3
        # First and third should have higher scores than second (candidate exceeds requirement)
        # vs second where candidate doesn't meet requirement
        # Allow for small tolerance in comparisons
        assert results[0]["overall_score"] >= results[1]["overall_score"] - 0.05
        assert results[2]["overall_score"] >= results[1]["overall_score"] - 0.05
