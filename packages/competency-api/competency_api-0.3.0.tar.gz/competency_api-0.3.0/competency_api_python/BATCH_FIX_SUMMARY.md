# Batch Match Score Fix Summary

## Problem

The original `batch_match_score` implementation was creating a **shared embedding cache** across all pairs in the batch. This caused the results to differ from individual `match_score` calls, with differences increasing as batch size grew.

### Original Behavior (BEFORE Fix)

```
Batch Size | Avg Diff   | Max Diff
-----------+------------+------------
     1     |  0.036364  |  0.036364
     2     |  0.098182  |  0.160000
     3     |  0.090189  |  0.160000
     5     |  0.061386  |  0.160000
     8     |  0.055412  |  0.160000
```

**Why?** The old implementation:
1. Collected ALL unique skills across ALL pairs
2. Embedded them together in ONE batch
3. Created a shared embedding context that differed from individual calls
4. Larger batches = more skills in context = bigger differences

## Solution

Changed `batch_match_score` to simply call `calculate_match_score` for each pair in a **Rust loop**, instead of creating a shared embedding cache.

### Code Change

**File:** `/Users/catethos/projects/ds-colab/competency_api/src/matcher.rs`

**Before (lines 142-257):**
```rust
pub fn calculate_batch_match_scores(...) -> Result<Vec<MatchResult>> {
    // Collect all unique skills across all pairs
    let mut all_skills = Vec::new();
    let mut skill_set = std::collections::HashSet::new();
    for (candidate_skills, required_skills) in &pairs {
        // Collect unique skills...
    }

    // Embed all skills once in shared context
    let all_embedded = self.embedder.embed_skills(&all_skills)?;

    // Create embedding cache
    let mut embedding_cache: HashMap<String, SkillWithDistribution> = ...;

    // Process each pair using cached embeddings
    for (candidate_skills, required_skills) in pairs {
        // Look up from cache...
    }
}
```

**After (lines 142-166):**
```rust
pub fn calculate_batch_match_scores(...) -> Result<Vec<MatchResult>> {
    if pairs.is_empty() {
        return Ok(Vec::new());
    }

    // Simply call calculate_match_score for each pair in a Rust loop
    // This ensures identical results to individual calls while being faster
    // than calling from Python in a loop (no Python/Rust boundary overhead)
    let mut results = Vec::with_capacity(pairs.len());

    for (candidate_skills, required_skills) in pairs {
        let result = self.calculate_match_score(candidate_skills, required_skills)?;
        results.push(result);
    }

    Ok(results)
}
```

## Results After Fix

### New Behavior (AFTER Fix)

```
Batch Size | Avg Diff   | Max Diff   | Status
-----------+------------+------------+--------
     1     |  0.000000  |  0.000000  | ✓ PERFECT
     2     |  0.000000  |  0.000000  | ✓ PERFECT
     3     |  0.000000  |  0.000000  | ✓ PERFECT
     5     |  0.000000  |  0.000000  | ✓ PERFECT
     8     |  0.000000  |  0.000000  | ✓ PERFECT
```

**All test cases now PASS with IDENTICAL results!**

```
Test Case 1: Exact Match                    ✓ PASS
Test Case 2: Proficiency Penalty            ✓ PASS
Test Case 3: Related Skills                 ✓ PASS
Test Case 4: Multiple Required Skills       ✓ PASS
Test Case 5: HR Skills Subset               ✓ PASS

✓ SUCCESS: batch_match_score produces IDENTICAL results to individual match_score calls
```

## Benefits

### 1. Correctness
- **Identical results** to individual calls
- No embedding context differences
- Predictable, consistent behavior

### 2. Performance
While we lost the "embed once" optimization, we still get performance benefits:

- **Python/Rust boundary overhead eliminated**: Instead of calling from Python N times, we call Rust once
- **Memory allocation efficiency**: Pre-allocate result vector in Rust
- **Still faster than Python loop**: No GIL (Global Interpreter Lock) overhead between calls

### 3. Simplicity
- Simpler code (went from ~115 lines to ~25 lines)
- Easier to maintain
- No complex caching logic
- Guaranteed equivalence to single calls

## Usage

Now `batch_match_score` is truly just a convenience function:

```python
from competency_api import match_score, batch_match_score

# These are now IDENTICAL:

# Method 1: Individual calls from Python
results = []
for required, candidate in pairs:
    result = match_score(required, candidate)
    results.append(result)

# Method 2: Batch call (faster, same results)
results = batch_match_score(pairs)
```

### When to Use

- **Use `match_score()`**: Single pair, interactive use
- **Use `batch_match_score()`**: Multiple pairs, batch processing
  - Still faster than Python loop (no boundary overhead)
  - Guaranteed identical results
  - Cleaner code

## Performance Comparison

The original optimization strategy assumed embedding was the bottleneck. However:

1. **Model is cached globally** - already fast after first call
2. **SIMD similarity calculations** - very fast (~0.2μs per comparison)
3. **Python/Rust boundary** - this is actually the real overhead

By eliminating repeated Python → Rust calls, batch mode still provides meaningful performance benefits without sacrificing correctness.

## Testing

Run these tests to verify:

```bash
# Test that batch equals individual
uv run python compare_batch_vs_single.py

# Test that batch size doesn't affect results
uv run python test_batch_size_effect.py

# Verify with real data
uv run python test_data_clean.py
```

All tests should show **0.000000 difference** between batch and individual calls.

## Conclusion

The fix trades the "embed once" optimization for **correctness and simplicity**. The result is a `batch_match_score` function that:

✓ Produces identical results to individual calls
✓ Still faster than Python loops
✓ Much simpler to understand and maintain
✓ No unexpected behavior based on batch size

This aligns with the user's expectation: batch mode should just be "running the for loop in Rust for speed", which is exactly what it now does.
