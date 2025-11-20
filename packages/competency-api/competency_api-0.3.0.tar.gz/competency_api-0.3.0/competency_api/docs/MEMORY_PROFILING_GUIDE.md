# Memory Profiling & Optimization Guide

A comprehensive guide for profiling and optimizing memory usage in the Competency API.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Setup & Configuration](#setup--configuration)
4. [Profiling Tools](#profiling-tools)
5. [Usage Examples](#usage-examples)
6. [Optimization Workflow](#optimization-workflow)
7. [Benchmarking](#benchmarking)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Overview

This guide covers memory profiling and optimization for the Competency API, which implements sophisticated skill matching using:
- Neural embeddings (fastembed)
- SIMD-accelerated similarity calculations (simsimd) 
- Beta distribution modeling (statrs)
- Parallel processing (rayon)

### Memory Optimization Goals
- **Reduce peak memory usage** by 20-30%
- **Minimize allocations** by 40-50% 
- **Improve cache locality** and performance
- **Enable predictable memory scaling**

## Quick Start

### 1. Install Prerequisites
```bash
# Install DHAT viewer (optional, for detailed analysis)
pip install dhat
```

### 2. Run Basic Memory Tests
```bash
# Test memory profiling functionality
cargo test --features memory-profiling profiling -- --nocapture

# Test without embedding model downloads (fast)
cargo test test_memory_without_profiling -- --nocapture
```

### 3. Generate Baseline Measurements
```bash
# Get baseline memory usage
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture
```

### 4. Run Detailed Analysis
```bash
# Generate DHAT heap profile
cargo run --example memory_profile --features memory-profiling

# View detailed report
dh_view.py dhat-heap.json
```

## Setup & Configuration

### Cargo.toml Dependencies

The project includes these memory profiling dependencies:

```toml
[dependencies]
# Optional memory profiling dependencies
dhat = { version = "0.3", optional = true }
peak_alloc = { version = "0.2", optional = true }
jemallocator = { version = "0.5", optional = true }

[dev-dependencies]
# Benchmarking dependencies
criterion = { version = "0.5", features = ["html_reports"] }

[features]
default = []
memory-profiling = ["dhat", "peak_alloc"]
jemalloc = ["jemallocator"]

[[bench]]
name = "memory_benchmark"
harness = false
```

### Feature Flags

- **`memory-profiling`**: Enables DHAT and peak_alloc for detailed analysis
- **`jemalloc`**: Uses jemalloc allocator (alternative to system allocator)

### Project Structure

```
competency_api/
├── src/
│   ├── profiling.rs          # Memory profiling utilities
│   └── lib.rs                # Main library with profiling module
├── benches/
│   └── memory_benchmark.rs   # Criterion benchmarks with memory tracking
├── tests/
│   └── memory_tests.rs       # Memory usage tests
├── examples/
│   └── memory_profile.rs     # DHAT profiling example
└── docs/
    ├── MEMORY_PROFILING_GUIDE.md  # This guide
    └── QUICK_START.md              # Quick reference
```

## Profiling Tools

### 1. Peak Memory Tracker (`peak_alloc`)

**Purpose**: Lightweight peak memory usage tracking
**Overhead**: Very low
**Use Case**: High-level memory usage monitoring

```rust
use competency_api::profiling::{MemoryProfiler, MemorySnapshot};

let profiler = MemoryProfiler::new();
// ... perform operations ...
println!("Current: {}MB, Peak: {}MB", 
         profiler.current_usage_mb(), 
         profiler.peak_usage_mb());
```

### 2. DHAT Heap Profiler (`dhat`)

**Purpose**: Detailed heap allocation analysis
**Overhead**: Moderate
**Use Case**: Finding allocation hotspots and patterns

```rust
#[cfg(feature = "memory-profiling")]
use dhat::{Dhat, DhatAlloc};

#[cfg(feature = "memory-profiling")]
#[global_allocator]
static ALLOCATOR: DhatAlloc = DhatAlloc;

fn main() {
    #[cfg(feature = "memory-profiling")]
    let _dhat = Dhat::start_heap_profiling();
    
    // Your code here
    
    // Report written to dhat-heap.json
}
```

### 3. Criterion Benchmarks

**Purpose**: Performance benchmarking with memory statistics
**Overhead**: Controlled
**Use Case**: Before/after optimization comparisons

```bash
# Run benchmarks with memory profiling
cargo bench --features memory-profiling

# View HTML reports
open target/criterion/reports/index.html
```

## Usage Examples

### Basic Memory Measurement

```rust
use competency_api::profiling::{profile_memory_usage, MemorySnapshot};

let (result, before, after) = profile_memory_usage("skill_matching", || {
    let mut matcher = SkillMatcher::new().unwrap();
    matcher.calculate_match_score(candidate_skills, required_skills)
});

println!("Before: {}", before);
println!("After: {}", after);
println!("Memory used: {}MB", after.peak_mb - before.peak_mb);
```

### Component-Specific Profiling

```rust
// Profile embedding operations
let (embedded_skills, before, after) = profile_memory_usage("embedding", || {
    let mut embedder = SkillEmbedder::new().unwrap();
    embedder.embed_skills(&skills)
});

// Profile similarity calculations
let (similarities, before, after) = profile_memory_usage("similarity", || {
    SkillSimilarityCalculator::calculate_similarities(&candidate_skills, &required_skills)
});
```

### Scaling Analysis

```rust
fn analyze_memory_scaling() {
    let sizes = vec![10, 50, 100, 200, 500];
    
    for size in sizes {
        let skills = create_test_skills(size);
        let (_, before, after) = profile_memory_usage(&format!("size_{}", size), || {
            // Your operation here
        });
        
        let memory_per_skill = (after.peak_mb - before.peak_mb) as f64 / size as f64;
        println!("Size {}: {}MB total, {:.2}MB per skill", 
                 size, after.peak_mb - before.peak_mb, memory_per_skill);
    }
}
```

## Optimization Workflow

### Step 1: Establish Baseline

```bash
# Record current memory usage
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > baseline.txt

# Run detailed profiling
cargo run --example memory_profile --features memory-profiling
cp dhat-heap.json baseline-dhat.json
```

### Step 2: Identify Optimization Targets

Based on our analysis, focus on these high-impact areas:

1. **Vec allocations without capacity hints**
   - Location: `similarity.rs:13`, `strategies.rs:161-175`
   - Impact: 20-30% allocation reduction

2. **HashMap allocations in loops**
   - Location: `similarity.rs:37-40`, `matcher.rs:110-113`
   - Impact: 15-25% memory reduction

3. **String cloning in hot paths**
   - Location: Multiple files in loop iterations
   - Impact: 10-20% fewer allocations

4. **Temporary Vec collections**
   - Location: `strategies.rs:184-186`, `embedding.rs:62-64`
   - Impact: 5-15% memory efficiency

### Step 3: Apply Optimizations

#### 3.1 Add Capacity Hints

```rust
// Before
let mut similarities = vec![vec![0.0; required_skills.len()]; candidate_skills.len()];

// After
let mut similarities = Vec::with_capacity(candidate_skills.len());
for _ in 0..candidate_skills.len() {
    similarities.push(Vec::with_capacity(required_skills.len()));
}
```

#### 3.2 Pre-allocate HashMaps

```rust
// Before
let mut result = HashMap::new();

// After
let mut result = HashMap::with_capacity(required_skills.len());
```

#### 3.3 Reduce String Cloning

```rust
// Before
skill_map.insert(cand_skill.name.clone(), similarity);

// After - use references where possible
skill_map.insert(&cand_skill.name, similarity);

// Or use Cow for conditional cloning
use std::borrow::Cow;
pub struct OptimizedSkill<'a> {
    name: Cow<'a, str>,
    // ... other fields
}
```

#### 3.4 Optimize Iterator Chains

```rust
// Before - creates intermediate Vec
let scores: Vec<f64> = skill_scores.iter()
    .map(|score| score.probability)
    .collect();
let max_score = scores.iter().fold(0.0f64, |a, &b| a.max(b));

// After - direct fold operation
let max_score = skill_scores.iter()
    .map(|score| score.probability)
    .fold(0.0f64, |a, b| a.max(b));
```

### Step 4: Measure Improvements

```bash
# Test optimized version
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture > optimized.txt

# Compare results
diff baseline.txt optimized.txt

# Generate new DHAT profile
cargo run --example memory_profile --features memory-profiling
cp dhat-heap.json optimized-dhat.json

# Compare DHAT reports
dh_view.py baseline-dhat.json
dh_view.py optimized-dhat.json
```

### Step 5: Validate Performance

```bash
# Run benchmarks to ensure no performance regression
cargo bench --features memory-profiling

# Run all tests to ensure correctness
cargo test --features memory-profiling
```

## Benchmarking

### Running Benchmarks

```bash
# Basic benchmarks
cargo bench

# With memory profiling
cargo bench --features memory-profiling

# Specific benchmark
cargo bench memory_usage

# Save results for comparison
cargo bench --features memory-profiling -- --save-baseline before_optimization
# ... apply optimizations ...
cargo bench --features memory-profiling -- --baseline before_optimization
```

### Benchmark Categories

1. **Memory Usage Benchmarks**
   - `bench_skill_matching_memory`: End-to-end memory usage
   - `bench_embedding_memory`: Embedding operation memory
   - `bench_similarity_calculation_memory`: Similarity computation memory

2. **Scaling Benchmarks**
   - Tests with 10, 50, 100, 200 skills
   - Memory usage vs. dataset size analysis

3. **Component Benchmarks**
   - Individual component memory profiles
   - Hot path allocation analysis

### Expected Results

#### Before Optimization (Baseline)
```
Memory usage for 10 candidates, 5 required: 2MB
Memory usage for 50 candidates, 25 required: 15MB  
Memory usage for 100 candidates, 50 required: 45MB
Total allocations: ~1000 per operation
```

#### After Optimization (Target)
```
Memory usage for 10 candidates, 5 required: 1.4MB (-30%)
Memory usage for 50 candidates, 25 required: 10.5MB (-30%)
Memory usage for 100 candidates, 50 required: 31.5MB (-30%)
Total allocations: ~500 per operation (-50%)
```

## Troubleshooting

### Common Issues

#### 1. DHAT Not Working
```bash
# Symptoms: No dhat-heap.json file generated
# Solutions:
pip install dhat  # Install DHAT viewer
cargo clean && cargo run --example memory_profile --features memory-profiling
```

#### 2. Peak Allocator Conflicts
```bash
# Symptoms: "Cannot set global allocator" error
# Solutions:
# Comment out other global allocators in your code
# Use feature flags to conditionally enable allocators
```

#### 3. Tests Timeout
```bash
# Symptoms: Memory tests take too long
# Solutions:
# Run without embedding model: cargo test test_memory_without_profiling
# Use smaller test datasets
# Run with internet connection for model downloads
```

#### 4. Type Conversion Errors
```bash
# Symptoms: f32/usize conversion errors
# Solutions:
# Use `as usize` for peak_alloc conversions
# Check feature flag guards are correct
```

### Debug Commands

```bash
# Check feature flags
cargo check --features memory-profiling

# Verbose test output
cargo test --features memory-profiling -- --nocapture

# Debug build with profiling
cargo build --features memory-profiling

# List available benchmarks
cargo bench --list
```

## Best Practices

### 1. Profiling Strategy

- **Start with peak_alloc** for quick measurements
- **Use DHAT for detailed analysis** of allocation patterns
- **Profile representative workloads** that match production usage
- **Test multiple dataset sizes** to understand scaling behavior

### 2. Optimization Priorities

1. **High-frequency allocations** in hot paths
2. **Large temporary allocations** that can be avoided
3. **Redundant string operations** and cloning
4. **HashMap/Vec capacity hints** for known sizes

### 3. Testing Approach

- **Always test before and after** optimizations
- **Verify correctness** before measuring performance
- **Use consistent test conditions** (same machine, same dataset)
- **Multiple runs** to account for variance

### 4. Documentation

- **Record baseline measurements** before starting
- **Document optimization rationale** and trade-offs
- **Update benchmarks** with new optimization targets
- **Maintain profiling examples** for future reference

### 5. Monitoring

- **Set up CI benchmarks** to catch regressions
- **Profile regularly** during development
- **Monitor production metrics** if applicable
- **Track memory usage trends** over time

## Advanced Topics

### Custom Allocators

```rust
// Using jemalloc for better performance
#[cfg(feature = "jemalloc")]
use jemallocator::Jemalloc;

#[cfg(feature = "jemalloc")]
#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;
```

### Memory Pools

```rust
use std::sync::Mutex;

pub struct MemoryPool<T> {
    pool: Mutex<Vec<Vec<T>>>,
}

impl<T> MemoryPool<T> {
    pub fn get_or_create(&self, capacity: usize) -> Vec<T> {
        let mut pool = self.pool.lock().unwrap();
        if let Some(mut vec) = pool.pop() {
            vec.clear();
            vec.reserve(capacity);
            vec
        } else {
            Vec::with_capacity(capacity)
        }
    }
    
    pub fn return_to_pool(&self, vec: Vec<T>) {
        let mut pool = self.pool.lock().unwrap();
        pool.push(vec);
    }
}
```

### Arena Allocation

```rust
// Using bumpalo for temporary allocations
use bumpalo::Bump;

pub struct TemporaryAllocator {
    arena: Bump,
}

impl TemporaryAllocator {
    pub fn allocate_vec<T>(&self, capacity: usize) -> bumpalo::collections::Vec<T> {
        bumpalo::collections::Vec::with_capacity_in(capacity, &self.arena)
    }
}
```

This comprehensive guide provides everything needed to profile, optimize, and monitor memory usage in the Competency API effectively.