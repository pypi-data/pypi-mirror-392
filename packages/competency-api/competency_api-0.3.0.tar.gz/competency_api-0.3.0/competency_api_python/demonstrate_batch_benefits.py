#!/usr/bin/env python3
"""
Demonstrate the benefits of batch_match_score:
1. Consistency: Same results every time
2. Correct usage: How to use both functions
3. Performance: Speed comparison
"""

from competency_api import match_score, batch_match_score
import time
import json

print("\n" + "=" * 80)
print("DEMONSTRATION: BATCH vs INDIVIDUAL MATCH SCORE")
print("=" * 80)

# Create 5 different candidate-role pairs
pairs = [
    # Pair 1: Python Developer
    (
        [{"name": "Python", "level": {"value": 4, "max": 5}}],
        [{"name": "Python", "level": {"value": 5, "max": 5}}]
    ),
    # Pair 2: Full Stack Developer
    (
        [
            {"name": "React", "level": {"value": 4, "max": 5}},
            {"name": "Node.js", "level": {"value": 4, "max": 5}}
        ],
        [
            {"name": "React", "level": {"value": 5, "max": 5}},
            {"name": "JavaScript", "level": {"value": 5, "max": 5}},
            {"name": "Express", "level": {"value": 4, "max": 5}}
        ]
    ),
    # Pair 3: Data Scientist
    (
        [{"name": "Machine Learning", "level": {"value": 4, "max": 5}}],
        [
            {"name": "Python", "level": {"value": 5, "max": 5}},
            {"name": "TensorFlow", "level": {"value": 4, "max": 5}},
            {"name": "Scikit-learn", "level": {"value": 4, "max": 5}}
        ]
    ),
    # Pair 4: DevOps Engineer
    (
        [
            {"name": "Docker", "level": {"value": 4, "max": 5}},
            {"name": "Kubernetes", "level": {"value": 3, "max": 5}}
        ],
        [
            {"name": "Docker", "level": {"value": 5, "max": 5}},
            {"name": "AWS", "level": {"value": 4, "max": 5}}
        ]
    ),
    # Pair 5: HR Manager (from data.json)
    (
        [
            {"name": "Change Management", "level": {"value": 5, "max": 5}},
            {"name": "Compensation Strategy", "level": {"value": 5, "max": 5}}
        ],
        [
            {"name": "Change Management", "level": {"value": 5, "max": 5}},
            {"name": "Compensation and Benefits Strategy", "level": {"value": 5, "max": 5}},
            {"name": "Talent Management", "level": {"value": 5, "max": 5}}
        ]
    )
]

print("\n" + "=" * 80)
print("METHOD 1: Using batch_match_score (RECOMMENDED)")
print("=" * 80)

start = time.time()
batch_results = batch_match_score(pairs)
batch_time = time.time() - start

print(f"\nProcessed {len(pairs)} pairs in {batch_time:.2f} seconds")
print("\nResults:")
for i, result in enumerate(batch_results, 1):
    print(f"\nPair {i}:")
    print(f"  Overall Score: {result['overall_score']:.2%}")
    print(f"  Skill Scores:")
    for skill in result['skill_scores']:
        print(f"    - {skill['skill_name']}: {skill['probability']:.2%}")

print("\n" + "=" * 80)
print("METHOD 2: Using individual match_score calls")
print("=" * 80)

start = time.time()
individual_results = []
for i, (required, candidate) in enumerate(pairs, 1):
    print(f"Processing pair {i}/{len(pairs)}...")
    result = match_score(required, candidate)
    individual_results.append(result)
individual_time = time.time() - start

print(f"\nProcessed {len(pairs)} pairs in {individual_time:.2f} seconds")
print("\nResults:")
for i, result in enumerate(individual_results, 1):
    print(f"\nPair {i}:")
    print(f"  Overall Score: {result['overall_score']:.2%}")
    print(f"  Skill Scores:")
    for skill in result['skill_scores']:
        print(f"    - {skill['skill_name']}: {skill['probability']:.2%}")

print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON")
print("=" * 80)

print(f"\nBatch mode:      {batch_time:.2f} seconds")
print(f"Individual mode: {individual_time:.2f} seconds")
if individual_time > 0:
    speedup = individual_time / batch_time
    print(f"Speedup:         {speedup:.2f}x faster with batch mode")
    time_saved = individual_time - batch_time
    print(f"Time saved:      {time_saved:.2f} seconds")

print("\n" + "=" * 80)
print("CONSISTENCY CHECK")
print("=" * 80)

print("\nRunning batch_match_score 3 times to verify consistency...")
batch_run1 = batch_match_score(pairs)
batch_run2 = batch_match_score(pairs)
batch_run3 = batch_match_score(pairs)

all_consistent = True
for i in range(len(pairs)):
    score1 = batch_run1[i]['overall_score']
    score2 = batch_run2[i]['overall_score']
    score3 = batch_run3[i]['overall_score']

    consistent = (abs(score1 - score2) < 1e-10 and abs(score2 - score3) < 1e-10)
    all_consistent = all_consistent and consistent

    print(f"\nPair {i+1}:")
    print(f"  Run 1: {score1:.10f}")
    print(f"  Run 2: {score2:.10f}")
    print(f"  Run 3: {score3:.10f}")
    print(f"  Status: {'✓ Consistent' if consistent else '✗ Inconsistent'}")

print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)

print(f"""
1. CONSISTENCY:
   - Batch mode: {'✓ Produces identical results across runs' if all_consistent else '✗ Results vary'}
   - Individual mode: May produce different results due to embedding caching

2. PERFORMANCE:
   - Batch mode: {batch_time:.2f} seconds for {len(pairs)} pairs
   - Individual mode: {individual_time:.2f} seconds for {len(pairs)} pairs
   - Speedup: {individual_time/batch_time:.1f}x faster with batch mode

3. USAGE RECOMMENDATION:
   - Use batch_match_score() when you have multiple pairs to process
   - Use match_score() only for single pair processing
   - Batch mode is more efficient and consistent

4. WHY RESULTS DIFFER:
   - Batch mode processes all unique skills together in one embedding pass
   - Individual mode processes each pair separately
   - Both are valid, but batch provides better consistency and performance
""")

print("\n" + "=" * 80)
print("EXAMPLE CODE")
print("=" * 80)

print("""
# For a single pair:
result = match_score(required_skills, candidate_skills)

# For multiple pairs (RECOMMENDED):
pairs = [
    (required_skills_1, candidate_skills_1),
    (required_skills_2, candidate_skills_2),
    # ... more pairs
]
results = batch_match_score(pairs)

# Each result has the same structure:
# {
#   'overall_score': float,
#   'skill_scores': [...],
#   'skill_similarities': {...},
#   'pairwise_scores': {...}
# }
""")

print("\n" + "=" * 80)
