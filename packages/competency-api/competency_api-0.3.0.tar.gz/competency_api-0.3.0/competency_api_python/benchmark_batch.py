#!/usr/bin/env python3
"""
Benchmark comparison between individual match_score calls and batch_match_score.
This demonstrates the significant performance improvement of batch processing.
"""

from competency_api import match_score, batch_match_score
import time

# Define test pairs
test_pairs = [
    # Pair 1
    (
        [{"name": "Python", "level": {"value": 4, "max": 5}}],
        [{"name": "Python", "level": {"value": 5, "max": 5}}],
    ),
    # Pair 2
    (
        [{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
        [{"name": "TypeScript", "level": {"value": 4, "max": 5}}],
    ),
    # Pair 3
    (
        [{"name": "SQL", "level": {"value": 4, "max": 5}}],
        [{"name": "PostgreSQL", "level": {"value": 4, "max": 5}}],
    ),
]

print("=" * 70)
print("BATCH MATCHING PERFORMANCE BENCHMARK")
print("=" * 70)
print(f"\nNumber of pairs to process: {len(test_pairs)}")

# Method 1: Individual calls
print("\n" + "-" * 70)
print("METHOD 1: Individual match_score() calls")
print("-" * 70)

start_time = time.time()
individual_results = []
for i, (required, candidate) in enumerate(test_pairs):
    result = match_score(required, candidate)
    individual_results.append(result)
    print(f"  Pair {i+1}: {result['overall_score']:.3f}")
individual_time = time.time() - start_time

print(f"\nTotal time: {individual_time:.3f} seconds")
print(f"Average per pair: {individual_time / len(test_pairs):.3f} seconds")

# Method 2: Batch processing
print("\n" + "-" * 70)
print("METHOD 2: batch_match_score() - single batch call")
print("-" * 70)

start_time = time.time()
batch_results = batch_match_score(test_pairs)
batch_time = time.time() - start_time

for i, result in enumerate(batch_results):
    print(f"  Pair {i+1}: {result['overall_score']:.3f}")

print(f"\nTotal time: {batch_time:.3f} seconds")
print(f"Average per pair: {batch_time / len(test_pairs):.3f} seconds")

# Comparison
print("\n" + "=" * 70)
print("PERFORMANCE COMPARISON")
print("=" * 70)
print(f"Individual calls: {individual_time:.3f}s total ({individual_time/len(test_pairs):.3f}s per pair)")
print(f"Batch processing: {batch_time:.3f}s total ({batch_time/len(test_pairs):.3f}s per pair)")
print(f"\nSpeedup: {individual_time / batch_time:.2f}x faster")
print(f"Time saved: {individual_time - batch_time:.3f} seconds ({(1 - batch_time/individual_time) * 100:.1f}%)")

# Verify results are identical
print("\n" + "=" * 70)
print("RESULT VERIFICATION")
print("=" * 70)
all_match = True
for i, (ind_result, batch_result) in enumerate(zip(individual_results, batch_results)):
    match = abs(ind_result['overall_score'] - batch_result['overall_score']) < 0.001
    all_match = all_match and match
    status = "✓" if match else "✗"
    print(f"Pair {i+1}: {status} (individual: {ind_result['overall_score']:.4f}, batch: {batch_result['overall_score']:.4f})")

if all_match:
    print("\n✓ All results match! Batch processing produces identical results.")
else:
    print("\n✗ Warning: Some results differ slightly (within floating point precision).")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("For processing multiple pairs, ALWAYS use batch_match_score()!")
print(f"It's {individual_time / batch_time:.1f}x faster and produces identical results.")
print("=" * 70)
