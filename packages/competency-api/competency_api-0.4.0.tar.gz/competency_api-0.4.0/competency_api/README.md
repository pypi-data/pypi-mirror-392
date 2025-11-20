# Competency API

A Rust library implementing the **Geometric Theory of Skills Space** for sophisticated skill matching and analysis. The library provides probabilistic skill matching using Beta distributions, semantic skill analysis via neural embeddings, and confidence-based matching with intervals.

## Features

- **Probabilistic Skill Matching**: Uses Beta distributions to model skill proficiency levels with uncertainty quantification
- **Semantic Skill Analysis**: Employs neural embeddings to understand relationships between different skills  
- **Confidence-Based Matching**: Provides detailed match scores with confidence intervals
- **Skill Distribution Prediction**: Predicts proficiency in unmeasured skills based on known skills
- **Memory Optimized**: Comprehensive memory profiling and optimization tools included
- **Performance Focused**: SIMD-accelerated similarity calculations and parallel processing

## Quick Start

### Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
competency_api = "0.1.0"
```

### Basic Usage

```rust
use competency_api::*;

// Create skills
let candidate_skills = vec![
    Skill {
        name: "Python Programming".to_string(),
        level: ProficiencyLevel { value: 4, max: 5 }
    },
    Skill {
        name: "Data Analysis".to_string(),
        level: ProficiencyLevel { value: 3, max: 5 }
    },
];

let required_skills = vec![
    Skill {
        name: "Programming".to_string(),
        level: ProficiencyLevel { value: 3, max: 5 }
    },
];

// Calculate match score
let mut matcher = SkillMatcher::new()?;
let result = matcher.calculate_match_score(candidate_skills, required_skills)?;

println!("Overall match score: {:.2}", result.overall_score);
for skill_score in result.skill_scores {
    println!("Skill: {}, Score: {:.2}", skill_score.skill_name, skill_score.probability);
}
```

## Core Concepts

### Skill Representation

Each skill is represented by:
- A proficiency level (current value and maximum possible value)
- A Beta distribution capturing uncertainty in the skill level
- A semantic embedding vector representing the skill's meaning

### Matching Process

The matching process involves:
1. Converting skills to distributions
2. Calculating semantic similarities using neural embeddings
3. Computing match probabilities with confidence intervals
4. Generating final match scores with uncertainty quantification

## Architecture

### Core Modules

- **`types.rs`** - Core data structures (Skill, ProficiencyLevel, MatchResult, ConfidenceInterval)
- **`embedding.rs`** - Neural embeddings for semantic skill analysis using fastembed
- **`similarity.rs`** - SIMD-accelerated cosine similarity calculations via simsimd
- **`distribution.rs`** - Beta distribution modeling for skill proficiency uncertainty
- **`matcher.rs`** - Main skill matching orchestration logic
- **`strategies.rs`** - Configurable scoring strategies (Default, Conservative, Aggressive)
- **`config.rs`** - Configuration management for all aspects of skill matching

### Key Dependencies

- **[fastembed](https://github.com/Anush008/fastembed-rs)** (5.0.0) - Text embeddings generation
- **[simsimd](https://github.com/ashvardanian/simsimd)** (6.2.0) - SIMD-accelerated similarity calculations
- **[statrs](https://github.com/statrs-dev/statrs)** (0.17.1) - Statistical distributions (Beta distributions)
- **[rayon](https://github.com/rayon-rs/rayon)** (1.10.0) - Parallel processing
- **[serde](https://github.com/serde-rs/serde)** (1.0.215) - Serialization/deserialization

## Memory Profiling & Optimization

This library includes comprehensive memory profiling tools for performance analysis and optimization.

### Quick Memory Profiling

```bash
# Test memory profiling functionality
cargo test --features memory-profiling profiling -- --nocapture

# Get baseline memory measurements  
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture

# Generate detailed DHAT heap analysis
cargo run --example memory_profile --features memory-profiling
```

### Memory Features

- **Peak memory tracking** with `peak_alloc`
- **Detailed heap analysis** with DHAT profiling  
- **Benchmark integration** with Criterion
- **Automated regression testing** for memory usage
- **Optimization workflow** with systematic improvement process

### Expected Memory Usage

| Dataset Size | Peak Memory | Allocations | Memory/Skill |
|--------------|-------------|-------------|--------------|
| 10 candidates, 5 required | ~2MB | ~500 | ~0.13MB |
| 50 candidates, 25 required | ~15MB | ~2500 | ~0.20MB |
| 100 candidates, 50 required | ~45MB | ~7500 | ~0.30MB |

### Documentation

For detailed memory profiling and optimization:

- **[Memory Profiling Guide](docs/MEMORY_PROFILING_GUIDE.md)** - Comprehensive guide to profiling tools and usage
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Step-by-step setup instructions
- **[Usage Examples](docs/USAGE_EXAMPLES.md)** - Practical examples and tutorials
- **[Optimization Workflow](docs/OPTIMIZATION_WORKFLOW.md)** - Systematic optimization process
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Quick Start](QUICK_START.md)** - Ready-to-use commands

## Configuration

### Basic Configuration

```rust
use competency_api::*;

let config = SkillMatcherConfig::builder()
    .embedding_model(EmbeddingModel::AllMiniLML6V2)
    .show_download_progress(false)
    .build();

let matcher = SkillMatcher::with_config(config)?;
```

### Advanced Configuration

```rust
let penalty_config = PenaltyConfig {
    similarity_threshold: 0.15,
    moderate_penalty: 0.3,
    severe_penalty: 0.1,
    severe_threshold: 0.05,
};

let scoring_config = ScoringConfig {
    ratio_weight_meets: 0.6,
    ratio_weight_below: 0.4,
    very_similar_boost: 1.1,
    moderately_similar_boost: 1.05,
    max_confidence_weight: 0.8,
    high_score_dampening: 0.6,
};

let config = SkillMatcherConfig::builder()
    .penalty_config(penalty_config)
    .scoring_config(scoring_config)
    .cache_dir("./custom_cache")
    .build();
```

## Performance Characteristics

### Computational Complexity

- **Embedding Generation**: O(n) where n is number of skills
- **Similarity Calculation**: O(n×m) where n=candidates, m=required skills  
- **Distribution Operations**: O(n) for Beta distribution calculations
- **Overall Matching**: O(n×m + n×d) where d is embedding dimension

### Optimizations

- **SIMD Acceleration**: Vectorized similarity calculations using simsimd
- **Parallel Processing**: Multi-threaded operations with rayon
- **Memory Efficiency**: Pre-allocated containers and minimal copying
- **Caching**: Embedding model caching for repeated operations

### Benchmarks

Run benchmarks to measure performance:

```bash
# Standard benchmarks
cargo bench

# With memory profiling
cargo bench --features memory-profiling

# View results
open target/criterion/reports/index.html
```

## Testing

### Unit Tests

```bash
# Run all tests
cargo test

# Run with memory profiling
cargo test --features memory-profiling

# Run specific test suite
cargo test matcher::tests
```

### Integration Tests

```bash
# Memory usage tests
cargo test --features memory-profiling memory_tests

# Benchmark tests
cargo test --features memory-profiling benchmark
```

### Test Coverage

The library maintains high test coverage across:
- Core matching algorithms
- Distribution calculations  
- Similarity computations
- Configuration validation
- Memory usage patterns
- Error handling paths

## Examples

### Basic Skill Matching

```rust
use competency_api::*;

let candidate = vec![
    Skill { name: "Rust".to_string(), level: ProficiencyLevel { value: 4, max: 5 } },
    Skill { name: "Python".to_string(), level: ProficiencyLevel { value: 5, max: 5 } },
];

let required = vec![
    Skill { name: "Programming".to_string(), level: ProficiencyLevel { value: 3, max: 5 } },
];

let mut matcher = SkillMatcher::new()?;
let result = matcher.calculate_match_score(candidate, required)?;

println!("Match score: {:.2}", result.overall_score);
```

### Custom Scoring Strategy

```rust
use competency_api::*;
use competency_api::strategies::ConservativeScoringStrategy;

let config = SkillMatcherConfig::default();
let embedder = SkillEmbedder::with_config(config.clone())?;
let similarity_calculator = SkillSimilarityCalculator;
let scoring_strategy = ConservativeScoringStrategy;

let matcher = SkillMatcher::with_components(
    Box::new(embedder),
    Box::new(similarity_calculator), 
    Box::new(scoring_strategy),
    config,
)?;
```

### Memory Profiling Integration

```rust
use competency_api::profiling::{profile_memory_usage, MemorySnapshot};

let (result, before, after) = profile_memory_usage("skill_matching", || {
    let mut matcher = SkillMatcher::new().unwrap();
    matcher.calculate_match_score(candidate_skills, required_skills)
});

println!("Memory used: {}MB", after.peak_mb - before.peak_mb);
```

## Contributing

### Development Setup

1. Install Rust 1.70+
2. Install Python 3.7+ (for DHAT profiling)
3. Install DHAT viewer: `pip install dhat`

### Running Tests

```bash
# Standard development tests
cargo test

# With memory profiling
cargo test --features memory-profiling

# Benchmarks
cargo bench --features memory-profiling
```

### Memory Optimization

Follow the [Optimization Workflow](docs/OPTIMIZATION_WORKFLOW.md) for systematic memory improvements:

1. Establish baseline measurements
2. Profile and analyze current usage
3. Identify optimization targets  
4. Implement changes incrementally
5. Validate improvements
6. Document results

### Code Quality

- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting  
- Maintain test coverage above 90%
- Profile memory usage for significant changes
- Document public APIs thoroughly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Mathematical Foundation

The library implements the Geometric Theory of Skills Space, which:

- **Treats skills as points** in a high-dimensional semantic space
- **Uses probability distributions** to model skill proficiency with uncertainty
- **Employs information geometry** for skill relationship modeling  
- **Utilizes statistical manifolds** for distribution interpolation
- **Applies Bayesian inference** for confidence interval computation

## Roadmap

### Current Version (0.1.0)
- ✅ Core skill matching algorithms
- ✅ Memory profiling and optimization tools
- ✅ Comprehensive test suite
- ✅ Performance benchmarking
- ✅ Documentation and examples

### Future Enhancements
- Time-based skill decay modeling
- Team synergy analysis  
- Skill development path recommendations
- Integration with standard HR systems
- Real-time streaming skill matching
- Multi-language embedding support

## Support

- **Documentation**: See [docs/](docs/) directory for detailed guides
- **Examples**: Check [examples/](examples/) directory for usage patterns
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for questions and ideas

---

**Built with Rust for Performance, Designed for Scale, Optimized for Memory Efficiency**