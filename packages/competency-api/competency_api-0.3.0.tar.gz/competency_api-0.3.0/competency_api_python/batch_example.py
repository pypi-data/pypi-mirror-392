#!/usr/bin/env python3
"""
Example usage of the batch_match_score function for efficient batch processing.

This demonstrates how to use the batch API which is much faster than calling
match_score multiple times, as it:
1. Initializes the embedding model only once
2. Embeds all unique skills across all pairs in one batch
3. Uses parallel processing for calculating individual match scores
"""

from competency_api import batch_match_score, init_logging
import json
import time


def print_result(title, result):
    """Pretty print a result with a title."""
    print(f"\n{title}")
    print("=" * len(title))
    print(json.dumps(result, indent=2))
    print()


# Initialize logging (optional)
init_logging()

print("\n" + "=" * 60)
print("BATCH MATCHING EXAMPLE")
print("=" * 60)

# Define multiple candidate-requirement pairs
pairs = [
    # Pair 1: Python developer vs Python requirement
    (
        [{"name": "Python", "level": {"value": 1, "max": 5}}],  # required
        [{"name": "Python", "level": {"value": 4, "max": 5}}],  # candidate
    ),
    # Pair 2: Web development skills vs Web development requirement
    (
        [{"name": "Web development", "level": {"value": 4, "max": 5}}],  # required
        [
            {"name": "CSS", "level": {"value": 4, "max": 5}},
            {"name": "Typescript", "level": {"value": 4, "max": 5}},
            {"name": "Javascript", "level": {"value": 4, "max": 5}},
            {"name": "HTML", "level": {"value": 4, "max": 5}},
        ],  # candidate
    ),
    # Pair 3: Data Science skills vs Machine Learning requirement
    (
        [{"name": "Machine Learning", "level": {"value": 4, "max": 5}}],  # required
        [
            {"name": "Python", "level": {"value": 5, "max": 5}},
            {"name": "TensorFlow", "level": {"value": 4, "max": 5}},
            {"name": "Scikit-learn", "level": {"value": 4, "max": 5}},
            {"name": "Pandas", "level": {"value": 5, "max": 5}},
        ],  # candidate
    ),
    # Pair 4: Backend development
    (
        [
            {"name": "Node.js", "level": {"value": 4, "max": 5}},
            {"name": "Database", "level": {"value": 3, "max": 5}},
        ],  # required
        [
            {"name": "Node.js", "level": {"value": 5, "max": 5}},
            {"name": "Express", "level": {"value": 4, "max": 5}},
            {"name": "PostgreSQL", "level": {"value": 4, "max": 5}},
            {"name": "MongoDB", "level": {"value": 3, "max": 5}},
        ],  # candidate
    ),
    # Pair 5: Mobile development
    (
        [
            {"name": "Mobile Development", "level": {"value": 4, "max": 5}},
            {"name": "React", "level": {"value": 3, "max": 5}},
        ],  # required
        [
            {"name": "React Native", "level": {"value": 4, "max": 5}},
            {"name": "iOS Development", "level": {"value": 3, "max": 5}},
            {"name": "Android Development", "level": {"value": 3, "max": 5}},
        ],  # candidate
    ),
]

print(f"\nProcessing {len(pairs)} candidate-requirement pairs in batch...")
print("-" * 60)

# Time the batch operation
start_time = time.time()
results = batch_match_score(pairs)
end_time = time.time()

print(f"\nBatch processing completed in {end_time - start_time:.3f} seconds")
print(f"Average time per pair: {(end_time - start_time) / len(pairs):.3f} seconds")
print("-" * 60)

# Print results for each pair
for i, result in enumerate(results):
    print(f"\nPair {i + 1} Results:")
    print(f"  Overall Score: {result['overall_score']:.3f}")
    print(f"  Number of skill scores: {len(result['skill_scores'])}")

    # Print individual skill scores
    for skill_score in result['skill_scores']:
        print(f"    - {skill_score['skill_name']}: {skill_score['probability']:.3f}")

print("\n" + "=" * 60)
print("Batch matching completed successfully!")
print("=" * 60)

# Example: Filter high-scoring matches
print("\n" + "=" * 60)
print("HIGH-SCORING MATCHES (score >= 0.75)")
print("=" * 60)

high_scoring = [
    (i, result) for i, result in enumerate(results)
    if result['overall_score'] >= 0.75
]

if high_scoring:
    for i, result in high_scoring:
        print(f"Pair {i + 1}: {result['overall_score']:.3f}")
else:
    print("No matches with score >= 0.75")

print()
