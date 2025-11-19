#!/usr/bin/env python3
"""Debug script to check embeddings and similarities."""

from competency_api import batch_match_score, match_score
import json

# Test pair - exact same skill name
required = [{"name": "Python", "level": {"value": 4, "max": 5}}]
candidate = [{"name": "Python", "level": {"value": 5, "max": 5}}]

# Individual call
result_individual = match_score(required, candidate)
print("INDIVIDUAL - Similarities:")
print(json.dumps(result_individual['skill_similarities'], indent=2))
print(f"\nINDIVIDUAL - Pairwise Scores:")
print(json.dumps(result_individual['pairwise_scores'], indent=2))

# Batch call
result_batch = batch_match_score([(required, candidate)])[0]
print("\n" + "=" * 70)
print("BATCH - Similarities:")
print(json.dumps(result_batch['skill_similarities'], indent=2))
print(f"\nBATCH - Pairwise Scores:")
print(json.dumps(result_batch['pairwise_scores'], indent=2))
