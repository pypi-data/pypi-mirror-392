# Memory Optimization Workflow

A systematic approach to identifying, implementing, and validating memory optimizations in the Competency API.

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Baseline Establishment](#phase-1-baseline-establishment)
3. [Phase 2: Profiling & Analysis](#phase-2-profiling--analysis)
4. [Phase 3: Optimization Planning](#phase-3-optimization-planning)
5. [Phase 4: Implementation](#phase-4-implementation)
6. [Phase 5: Validation](#phase-5-validation)
7. [Phase 6: Documentation & Monitoring](#phase-6-documentation--monitoring)
8. [Optimization Strategies](#optimization-strategies)
9. [Automation & CI/CD](#automation--cicd)

## Overview

This workflow provides a structured approach to memory optimization that ensures:
- **Measurable improvements** with concrete metrics
- **No performance regressions** through comprehensive testing
- **Maintainable code** with clear documentation
- **Repeatable process** for future optimizations

### Expected Outcomes
- 20-30% reduction in peak memory usage
- 40-50% fewer memory allocations
- Improved cache locality and performance
- More predictable memory scaling

## Phase 1: Baseline Establishment

### 1.1 Environment Setup

```bash
# Ensure clean environment
cargo clean

# Install profiling tools
pip install dhat

# Verify setup
cargo test --features memory-profiling profiling -- --nocapture
```

### 1.2 Capture Baseline Metrics

```bash
# Create baseline directory
mkdir -p profiling_results/baseline
cd profiling_results/baseline

# Run comprehensive baseline tests
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > memory_baseline.txt

# Generate DHAT profile
cargo run --example memory_profile --features memory-profiling
cp ../../dhat-heap.json ./baseline_dhat.json

# Run benchmarks
cargo bench --features memory-profiling > benchmark_baseline.txt
```

### 1.3 Document Current State

Create `profiling_results/baseline/BASELINE_REPORT.md`:

```markdown
# Baseline Memory Profile - [Date]

## Test Environment
- Rust version: [version]
- Platform: [platform]
- Hardware: [specs]

## Memory Usage Results
- Small dataset (10/5): XMB
- Medium dataset (50/25): XMB  
- Large dataset (100/50): XMB

## Key Metrics
- Peak memory usage: XMB
- Total allocations: X
- Average allocation size: X bytes
- Memory per skill: X MB/skill

## Performance Baseline
- Average operation time: X ms
- Throughput: X operations/sec

## Identified Issues
- [List memory allocation hotspots]
- [Note scaling patterns]
- [Document any concerning trends]
```

## Phase 2: Profiling & Analysis

### 2.1 Detailed DHAT Analysis

```bash
# Generate detailed heap profile
dh_view.py baseline_dhat.json

# Key areas to analyze:
# 1. Total heap allocations
# 2. Peak heap usage
# 3. Allocation hotspots
# 4. Call stacks with highest allocation
```

### 2.2 Component-Specific Analysis

Run focused profiling on each component:

```bash
# Embedding component
cargo test --features memory-profiling test_embedding_memory_usage -- --nocapture

# Similarity calculation
cargo test --features memory-profiling test_similarity_calculation_memory -- --nocapture

# Matching logic
cargo test --features memory-profiling test_memory_growth_patterns -- --nocapture
```

### 2.3 Code Analysis

Use tools to identify optimization opportunities:

```bash
# Find Vec::new() without capacity hints
grep -r "Vec::new()" src/ --include="*.rs"

# Find HashMap::new() without capacity hints  
grep -r "HashMap::new()" src/ --include="*.rs"

# Find string cloning in loops
grep -r "\.clone()" src/ --include="*.rs" -A 2 -B 2

# Find unnecessary allocations
grep -r "collect()" src/ --include="*.rs" -A 2 -B 2
```

### 2.4 Create Analysis Report

Document findings in `profiling_results/ANALYSIS_REPORT.md`:

```markdown
# Memory Analysis Report

## High-Impact Optimization Targets

### 1. Vec Allocations (Priority: High)
- **Location**: similarity.rs:13
- **Issue**: Nested Vec creation without capacity hints
- **Impact**: 25-30% of allocations
- **Estimated Savings**: 5-8MB

### 2. HashMap Growth (Priority: High)  
- **Location**: matcher.rs:110, similarity.rs:37
- **Issue**: HashMap resizing during population
- **Impact**: 15-20% of allocations
- **Estimated Savings**: 3-5MB

### 3. String Cloning (Priority: Medium)
- **Location**: Multiple files in loops
- **Issue**: Unnecessary string clones
- **Impact**: 10-15% of allocations
- **Estimated Savings**: 2-3MB

## Optimization Plan
[Prioritized list of optimizations to implement]
```

## Phase 3: Optimization Planning

### 3.1 Prioritize Optimizations

Create optimization backlog with estimated impact:

| Priority | Optimization | Location | Estimated Impact | Effort | Risk |
|----------|-------------|----------|------------------|--------|------|
| P1 | Vec capacity hints | similarity.rs:13 | High (5-8MB) | Low | Low |
| P1 | HashMap capacity | matcher.rs:110 | High (3-5MB) | Low | Low |
| P2 | String cloning | Multiple | Medium (2-3MB) | Medium | Low |
| P3 | Iterator optimization | strategies.rs | Low (1-2MB) | High | Medium |

### 3.2 Create Implementation Plan

For each optimization, document:

```markdown
## Optimization: Vec Capacity Hints

### Current Code
```rust
let mut similarities = vec![vec![0.0; required_skills.len()]; candidate_skills.len()];
```

### Optimized Code
```rust
let mut similarities = Vec::with_capacity(candidate_skills.len());
for _ in 0..candidate_skills.len() {
    similarities.push(Vec::with_capacity(required_skills.len()));
}
```

### Expected Impact
- Memory savings: 5-8MB
- Allocation reduction: 30%
- Performance: No regression expected

### Testing Strategy
- Unit tests: Verify correctness
- Memory tests: Measure improvement
- Benchmarks: Ensure no performance loss

### Rollback Plan
- Keep original implementation in git history
- Feature flag for easy rollback if needed
```

### 3.3 Create Feature Branches

```bash
# Create optimization branches
git checkout -b optimization/vec-capacity-hints
git checkout -b optimization/hashmap-preallocation
git checkout -b optimization/string-cloning
```

## Phase 4: Implementation

### 4.1 Implement Optimizations Incrementally

#### Example: Vec Capacity Optimization

```bash
git checkout optimization/vec-capacity-hints

# Edit the file
```

```rust
// In src/similarity.rs
impl SkillSimilarityCalculator {
    pub fn calculate_similarities(
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution]
    ) -> Vec<Vec<f64>> {
        // OLD: let mut similarities = vec![vec![0.0; required_skills.len()]; candidate_skills.len()];
        
        // NEW: Pre-allocate with capacity
        let mut similarities = Vec::with_capacity(candidate_skills.len());
        for _ in 0..candidate_skills.len() {
            similarities.push(Vec::with_capacity(required_skills.len()));
        }
        
        // Rest of the implementation remains the same
        for (i, candidate_skill) in candidate_skills.iter().enumerate() {
            for (j, required_skill) in required_skills.iter().enumerate() {
                let distance = f32::cosine(
                    &candidate_skill.embedding,
                    &required_skill.embedding
                ).unwrap_or(1.0) as f64;
                
                similarities[i].push(1.0 - distance);
            }
        }
        
        similarities
    }
}
```

### 4.2 Test Each Optimization

```bash
# Run tests to ensure correctness
cargo test

# Run memory tests to measure improvement
cargo test --features memory-profiling test_similarity_calculation_memory -- --nocapture

# Run benchmarks
cargo bench --features memory-profiling
```

### 4.3 Measure Incremental Improvements

```bash
# Create results directory for this optimization
mkdir -p profiling_results/optimization_vec_capacity

# Measure memory usage
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > profiling_results/optimization_vec_capacity/memory_results.txt

# Generate new DHAT profile
cargo run --example memory_profile --features memory-profiling
cp dhat-heap.json profiling_results/optimization_vec_capacity/optimized_dhat.json

# Compare with baseline
echo "=== BASELINE ===" > profiling_results/optimization_vec_capacity/comparison.txt
cat profiling_results/baseline/memory_baseline.txt >> profiling_results/optimization_vec_capacity/comparison.txt
echo "=== OPTIMIZED ===" >> profiling_results/optimization_vec_capacity/comparison.txt
cat profiling_results/optimization_vec_capacity/memory_results.txt >> profiling_results/optimization_vec_capacity/comparison.txt
```

### 4.4 Document Changes

Create `OPTIMIZATION_LOG.md`:

```markdown
# Optimization Implementation Log

## Vec Capacity Hints - [Date]

### Changes Made
- Modified `similarity.rs:13` to use `Vec::with_capacity()`
- Pre-allocate nested vectors with known size

### Results
- Memory usage: Before XMB → After YMB (Z% reduction)
- Allocations: Before X → After Y (Z% reduction)
- Performance: No regression (±X%)

### Validation
- ✅ All tests pass
- ✅ Memory usage reduced
- ✅ No performance regression
- ✅ Code review completed

### Files Modified
- src/similarity.rs
- tests/memory_tests.rs (updated expected values)
```

## Phase 5: Validation

### 5.1 Comprehensive Testing

```bash
# Run all tests
cargo test --features memory-profiling

# Run performance tests
cargo bench --features memory-profiling

# Test without profiling features (production mode)
cargo test
cargo bench

# Test with different allocators
cargo test --features jemalloc
```

### 5.2 Memory Regression Testing

Create automated test to prevent regressions:

```rust
// In tests/memory_regression_tests.rs
#[test]
#[cfg(feature = "memory-profiling")]
fn test_memory_regression_vec_capacity() {
    use competency_api::profiling::profile_memory_usage;
    
    let candidate_skills = create_test_skills(100);
    let required_skills = create_test_skills(50);
    
    let (_, before, after) = profile_memory_usage("similarity_calc", || {
        SkillSimilarityCalculator::calculate_similarities(&candidate_skills, &required_skills)
    });
    
    let memory_used = after.peak_mb - before.peak_mb;
    
    // Assert memory usage is below threshold (with some tolerance)
    assert!(memory_used <= 8, "Memory usage {} exceeds threshold of 8MB", memory_used);
    
    // Log for monitoring
    println!("Similarity calculation memory usage: {}MB", memory_used);
}
```

### 5.3 Performance Validation

```bash
# Run extended benchmarks
cargo bench --features memory-profiling -- --warm-up-time 5 --measurement-time 30

# Compare with baseline
# Look for:
# - No >5% performance regression
# - Memory usage reduction
# - Allocation count reduction
```

### 5.4 Integration Testing

```bash
# Test real-world scenarios
cargo run --example memory_profile --features memory-profiling

# Test scaling behavior
cargo test --features memory-profiling test_memory_growth_patterns -- --nocapture

# Test edge cases
cargo test --features memory-profiling -- --nocapture | grep -E "(MB|allocations)"
```

## Phase 6: Documentation & Monitoring

### 6.1 Update Documentation

```bash
# Update CLAUDE.md with optimization notes
# Update README.md with performance characteristics
# Update API documentation with memory considerations
```

### 6.2 Create Monitoring Dashboard

```markdown
# Memory Performance Dashboard

## Current Metrics (Post-Optimization)
- Small dataset (10/5): XMB (was YMB, -Z%)
- Medium dataset (50/25): XMB (was YMB, -Z%)
- Large dataset (100/50): XMB (was YMB, -Z%)

## Thresholds & Alerts
- Small dataset: Alert if >2MB
- Medium dataset: Alert if >12MB
- Large dataset: Alert if >35MB

## Optimization History
- [Date]: Vec capacity hints (-30% allocations)
- [Date]: HashMap preallocation (-20% memory)
- [Date]: String cloning reduction (-15% allocations)
```

### 6.3 Set Up Continuous Monitoring

```yaml
# .github/workflows/memory_monitoring.yml
name: Memory Performance Monitoring

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  memory-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
        
    - name: Run memory tests
      run: |
        cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > memory_results.txt
        
    - name: Check memory thresholds
      run: |
        python3 scripts/check_memory_thresholds.py memory_results.txt
        
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: memory-results
        path: memory_results.txt
```

## Optimization Strategies

### Strategy 1: Allocation Elimination

**Goal**: Remove unnecessary allocations

**Techniques**:
- Use iterators instead of collecting to Vec
- Pass references instead of cloning
- Use `Cow<str>` for conditional cloning
- Stack allocation for small, fixed-size data

**Example**:
```rust
// Before: Creates temporary Vec
let max_score = skill_scores.iter()
    .map(|score| score.probability)
    .collect::<Vec<_>>()
    .iter()
    .fold(0.0, |a, &b| a.max(b));

// After: Direct fold, no allocation
let max_score = skill_scores.iter()
    .map(|score| score.probability)
    .fold(0.0, |a, b| a.max(b));
```

### Strategy 2: Pre-allocation

**Goal**: Allocate with known capacity to avoid growth

**Techniques**:
- `Vec::with_capacity()` for known sizes
- `HashMap::with_capacity()` for known sizes
- `String::with_capacity()` for string building

**Example**:
```rust
// Before: HashMap grows as needed
let mut result = HashMap::new();
for (key, value) in data {
    result.insert(key, value);
}

// After: Pre-allocate capacity
let mut result = HashMap::with_capacity(data.len());
for (key, value) in data {
    result.insert(key, value);
}
```

### Strategy 3: Memory Pooling

**Goal**: Reuse allocations across operations

**Implementation**:
```rust
pub struct MemoryPool<T> {
    pool: Mutex<Vec<Vec<T>>>,
}

impl<T> MemoryPool<T> {
    pub fn borrow(&self, capacity: usize) -> PooledVec<T> {
        let mut pool = self.pool.lock().unwrap();
        let mut vec = pool.pop().unwrap_or_default();
        vec.clear();
        vec.reserve(capacity);
        PooledVec { vec, pool: &self.pool }
    }
}
```

### Strategy 4: Data Structure Optimization

**Goal**: Use more memory-efficient data structures

**Techniques**:
- Flat vectors instead of nested Vec<Vec<T>>
- SOA (Structure of Arrays) instead of AOS
- Packed data structures for better cache usage

**Example**:
```rust
// Before: Vec<Vec<f64>> - scattered memory
type SimilarityMatrix = Vec<Vec<f64>>;

// After: Flat Vec with indexing - contiguous memory
pub struct FlatMatrix {
    data: Vec<f64>,
    rows: usize,
    cols: usize,
}

impl FlatMatrix {
    fn get(&self, row: usize, col: usize) -> f64 {
        self.data[row * self.cols + col]
    }
}
```

## Automation & CI/CD

### Automated Optimization Detection

```python
# scripts/detect_optimizations.py
import re
import sys

def find_optimization_opportunities(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Find Vec::new() without capacity
    vec_new_pattern = r'Vec::new\(\)'
    for match in re.finditer(vec_new_pattern, content):
        issues.append(f"Vec::new() at position {match.start()}")
    
    # Find HashMap::new() without capacity  
    hashmap_new_pattern = r'HashMap::new\(\)'
    for match in re.finditer(hashmap_new_pattern, content):
        issues.append(f"HashMap::new() at position {match.start()}")
    
    return issues

if __name__ == "__main__":
    for file_path in sys.argv[1:]:
        issues = find_optimization_opportunities(file_path)
        if issues:
            print(f"Optimization opportunities in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
```

### Performance Regression Detection

```bash
#!/bin/bash
# scripts/check_memory_regression.sh

# Run memory tests and capture results
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > current_results.txt

# Compare with stored baseline
python3 scripts/compare_memory_results.py baseline_results.txt current_results.txt

if [ $? -ne 0 ]; then
    echo "Memory regression detected!"
    exit 1
fi

echo "Memory performance within acceptable bounds"
```

This workflow provides a systematic approach to memory optimization that ensures improvements are measurable, sustainable, and don't introduce regressions.