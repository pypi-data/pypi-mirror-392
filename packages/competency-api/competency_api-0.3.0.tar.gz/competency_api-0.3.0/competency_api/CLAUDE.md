# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Rust library implementing the **Geometric Theory of Skills Space** for sophisticated skill matching and analysis. The library provides probabilistic skill matching using Beta distributions, semantic skill analysis via neural embeddings, and confidence-based matching with intervals.

## Code Architecture

### Core Modules
- `types.rs` - Core data structures (Skill, ProficiencyLevel, MatchResult, ConfidenceInterval)
- `error.rs` - Custom error handling with SkillMatcherError
- `distribution.rs` - Beta distribution modeling for skill proficiency uncertainty
- `embedding.rs` - Neural embeddings for semantic skill analysis using fastembed
- `similarity.rs` - SIMD-accelerated cosine similarity calculations via simsimd
- `matcher.rs` - Main skill matching orchestration logic
- `profiling.rs` - Memory profiling utilities for optimization (when `memory-profiling` feature enabled)

### Key Dependencies
- **fastembed** (5.0.0) - Text embeddings generation
- **simsimd** (6.2.0) - SIMD-accelerated similarity calculations
- **statrs** (0.17.1) - Statistical distributions (Beta distributions)
- **rayon** (1.10.0) - Parallel processing
- **serde** (1.0.215) - Serialization/deserialization

### Memory Profiling Dependencies (Optional)
- **dhat** (0.3.3) - Heap allocation analysis (feature: `dhat`)
- **criterion** (0.5) - Performance benchmarking
- **jemallocator** (0.5) - Alternative allocator for testing (feature: `jemalloc`)

## Performance Characteristics

### Baseline Performance (as of 2025-01-10)
- **Small dataset (10/5 skills)**: ~1.16 seconds
- **Medium dataset (50/25 skills)**: ~1.29 seconds  
- **Large dataset (100/50 skills)**: ~1.64 seconds
- **Similarity calculations**: ~0.2μs per comparison (SIMD-optimized)

### Known Bottlenecks
1. **Embedding model initialization**: ~1.3s (one-time cost)
2. **Embedding generation**: ~2ms per skill (after init)
3. **Memory allocations**: Vec/HashMap without capacity hints

### Optimization Opportunities
1. **Embedding model caching** (HIGH IMPACT - eliminate 1.3s init cost)
2. **Memory pre-allocation** (MEDIUM IMPACT - reduce allocation overhead)
3. **Batch embedding processing** (MEDIUM IMPACT - reduce per-skill overhead)

## Memory Profiling Setup

### Available Commands
```bash
# Test memory profiling functionality
cargo test profiling --features memory-profiling

# Run performance benchmarks  
cargo bench --features memory-profiling

# Generate DHAT heap analysis
cargo run --example memory_profile --features dhat

# Get baseline memory measurements
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture
```

### Feature Flags
- `memory-profiling` - Enables DHAT profiling and memory utilities
- `dhat` - Enables detailed heap allocation analysis
- `jemalloc` - Uses jemalloc allocator instead of system allocator

### Documentation
Complete memory profiling documentation available in `docs/`:
- `MEMORY_PROFILING_GUIDE.md` - Comprehensive profiling guide
- `SETUP_GUIDE.md` - Setup and configuration instructions
- `USAGE_EXAMPLES.md` - Practical profiling examples
- `OPTIMIZATION_WORKFLOW.md` - Systematic optimization process
- `BASELINE_RESULTS.md` - Current performance measurements
- `TROUBLESHOOTING.md` - Solutions to common issues

## Development Guidelines

### When Making Performance Changes
1. **Run benchmarks before and after**: `cargo bench --features memory-profiling`
2. **Test memory usage**: Use DHAT profiling to analyze allocation patterns
3. **Check for regressions**: Ensure no >5% performance degradation
4. **Update baselines**: Document new performance characteristics

### Memory Optimization Best Practices
1. **Use capacity hints**: `Vec::with_capacity()`, `HashMap::with_capacity()`
2. **Avoid unnecessary cloning**: Use references where possible
3. **Pre-allocate known sizes**: Especially for similarity matrices
4. **Profile before optimizing**: Use DHAT to identify actual bottlenecks

### Testing Requirements
- All tests must pass: `cargo test`
- Memory tests must pass: `cargo test --features memory-profiling`
- Benchmarks should show no significant regression
- New optimizations should include regression tests

## Workspace Context

This project is part of a larger workspace (ds-colab) that includes Node.js bindings in `competency_api_node_binding/`. When making API changes, consider compatibility with the Node.js bindings.

## Known Issues & Workarounds

### Fixed Issues (Resolved 2025-01-10)
- ✅ Compilation errors with DHAT imports
- ✅ Global allocator conflicts between profiling tools  
- ✅ Feature flag configuration for optional dependencies
- ✅ Unused import warnings in test modules

### Current Limitations
- Memory profiling utilities use mock values (due to global allocator constraints)
- DHAT profiling requires separate feature flag (`dhat`) to avoid conflicts
- Embedding model downloads can be slow on first run

### Performance Notes
- First run requires embedding model download (~100MB)
- Model initialization dominates initial performance (1.3s)
- Similarity calculations are highly optimized with SIMD
- Memory usage scales linearly with dataset size