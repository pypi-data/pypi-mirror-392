# Memory Profiling Guide

This guide shows how to profile memory usage in the competency API before and after optimizations.

## Quick Start

### 1. Run Basic Memory Tests
```bash
# Run memory tests without detailed profiling
cargo test memory_tests

# Run with memory profiling enabled
cargo test --features memory-profiling memory_tests
```

### 2. Run Memory Benchmarks
```bash
# Run criterion benchmarks
cargo bench

# Run with memory profiling for detailed analysis
cargo bench --features memory-profiling
```

### 3. Generate Detailed Memory Reports
```bash
# Run DHAT profiling example
cargo run --example memory_profile --features memory-profiling

# View the generated report
dh_view.py dhat-heap.json
```

## Profiling Tools

### 1. Peak Memory Tracking (`peak_alloc`)
- Tracks peak memory usage during execution
- Lightweight overhead
- Good for high-level memory usage tracking

### 2. DHAT Profiling (`dhat`)
- Detailed heap allocation analysis
- Shows allocation patterns, call stacks, and memory hotspots
- Higher overhead, use for detailed analysis

### 3. Criterion Benchmarks
- Performance benchmarking with memory statistics
- Generates HTML reports with trends
- Good for before/after comparisons

## Running Specific Profiles

### Baseline Memory Usage
```bash
# Get baseline measurements
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture
```

Expected output:
```
Memory usage for 10 candidates, 5 required: 2MB
Memory usage for 50 candidates, 25 required: 15MB  
Memory usage for 100 candidates, 50 required: 45MB
```

### Component-Specific Profiling

#### Embedding Memory
```bash
cargo test --features memory-profiling test_embedding_memory_usage -- --nocapture
```

#### Similarity Calculation Memory
```bash
cargo test --features memory-profiling test_similarity_calculation_memory -- --nocapture
```

#### Memory Growth Patterns
```bash
cargo test --features memory-profiling test_memory_growth_patterns -- --nocapture
```

## Detailed DHAT Analysis

### 1. Generate DHAT Report
```bash
cargo run --example memory_profile --features memory-profiling
```

### 2. View Report
```bash
# Install dhat viewer if not already installed
pip install dhat

# View the report
dh_view.py dhat-heap.json
```

### 3. Key Metrics to Watch
- **Total allocations**: Number of heap allocations
- **Total bytes allocated**: Total memory allocated during execution
- **Peak heap usage**: Maximum memory used at any point
- **Allocation hotspots**: Functions that allocate the most memory

## Benchmarking Before/After Optimizations

### 1. Record Baseline
```bash
# Generate baseline benchmark
cargo bench --features memory-profiling > baseline_results.txt
```

### 2. Apply Optimizations
- Implement memory optimizations
- Ensure tests still pass: `cargo test`

### 3. Compare Results
```bash
# Generate new benchmark
cargo bench --features memory-profiling > optimized_results.txt

# Compare results
diff baseline_results.txt optimized_results.txt
```

## Key Metrics to Track

### Memory Usage Metrics
- **Peak memory usage** (MB)
- **Total allocations** (count)
- **Average allocation size** (bytes)
- **Memory per skill processed** (MB/skill)

### Performance Metrics
- **Time per operation** (μs/ns)
- **Memory allocations per operation**
- **Cache efficiency** (cache misses/hits)

## Common Memory Optimization Targets

### High-Impact Areas
1. **Vec allocations without capacity hints**
   - Look for: `Vec::new()` in hot paths
   - Optimize: Use `Vec::with_capacity()`

2. **HashMap allocations**
   - Look for: `HashMap::new()` in loops
   - Optimize: Use `HashMap::with_capacity()`

3. **String cloning**
   - Look for: `.clone()` on strings in loops
   - Optimize: Use references or `Cow<str>`

### Memory Profiling Commands Summary

```bash
# Quick memory test
cargo test memory_tests

# Detailed profiling
cargo test --features memory-profiling memory_tests -- --nocapture

# Benchmark with memory tracking
cargo bench --features memory-profiling

# DHAT detailed analysis
cargo run --example memory_profile --features memory-profiling

# View DHAT report
dh_view.py dhat-heap.json
```

## Expected Results

### Before Optimization (Baseline)
- Small dataset (10/5): ~2MB peak
- Medium dataset (50/25): ~15MB peak  
- Large dataset (100/50): ~45MB peak
- Allocation pattern: O(n²) for similarity matrix

### After Optimization (Target)
- 20-30% reduction in peak memory usage
- 40-50% fewer total allocations
- Better memory locality and cache performance
- More predictable memory usage patterns

## Troubleshooting

### DHAT Not Working
- Ensure you have Python and `dhat` package installed: `pip install dhat`
- Check that `memory-profiling` feature is enabled
- Verify `dhat-heap.json` file is generated

### Peak Allocator Issues
- Only one global allocator can be active
- Comment out other allocators if conflicts occur
- Use `#[cfg(feature = "memory-profiling")]` guards

### Test Failures
- Some tests may fail with memory profiling due to allocator overhead
- Run tests without profiling first to ensure basic functionality
- Use larger tolerances in memory-sensitive tests