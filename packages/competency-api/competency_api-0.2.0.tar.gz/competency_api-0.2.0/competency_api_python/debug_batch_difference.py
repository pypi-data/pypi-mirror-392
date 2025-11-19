#!/usr/bin/env python3
"""Debug script to understand why batch and individual results differ."""

from competency_api import batch_match_score, match_score
import json

# Test pair
required = [{"name": "Python", "level": {"value": 4, "max": 5}}]
candidate = [{"name": "Python", "level": {"value": 5, "max": 5}}]

# Individual call
print("=" * 70)
print("INDIVIDUAL CALL")
print("=" * 70)
result_individual = match_score(required, candidate)
print(f"Overall Score: {result_individual['overall_score']}")
print(f"Skill Scores: {json.dumps(result_individual['skill_scores'], indent=2)}")

# Batch call
print("\n" + "=" * 70)
print("BATCH CALL (single pair)")
print("=" * 70)
result_batch = batch_match_score([(required, candidate)])[0]
print(f"Overall Score: {result_batch['overall_score']}")
print(f"Skill Scores: {json.dumps(result_batch['skill_scores'], indent=2)}")

# Compare
print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)
print(f"Overall Score Difference: {abs(result_individual['overall_score'] - result_batch['overall_score'])}")
print(f"Individual: {result_individual['overall_score']}")
print(f"Batch: {result_batch['overall_score']}")

# Try multiple individual calls to see if there's variance
print("\n" + "=" * 70)
print("MULTIPLE INDIVIDUAL CALLS")
print("=" * 70)
scores = []
for i in range(3):
    result = match_score(required, candidate)
    scores.append(result['overall_score'])
    print(f"Call {i+1}: {result['overall_score']}")

if len(set(scores)) > 1:
    print("\n⚠️  Individual calls produce different results!")
else:
    print("\n✓ Individual calls are consistent")
