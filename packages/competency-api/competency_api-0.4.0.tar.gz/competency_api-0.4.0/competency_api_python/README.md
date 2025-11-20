# Competency API - Python Binding

Python binding for the competency matching API, built with PyO3 and Rust for high performance.

## Overview

This library provides intelligent matching between required skills and candidate skills using:
- **Semantic similarity** via neural text embeddings (FastEmbed)
- **Proficiency modeling** using Beta distributions for uncertainty quantification
- **Domain-aware matching** with cross-domain penalties and coherence bonuses
- **SIMD-accelerated** similarity calculations for performance

## Installation

### From Source (Development)

Requirements:
- Python 3.8 or higher
- Rust toolchain (install from [rustup.rs](https://rustup.rs))
- Maturin (`pip install maturin`)

```bash
# Install in development mode
cd competency_api_python
maturin develop

# Or for release build (faster)
maturin develop --release
```

### From Wheel (Future)

```bash
pip install competency-api
```

## Quick Start

### Single Match

```python
from competency_api import match_score, init_logging

# Optional: Enable logging
init_logging()

# Define required skills for a role
required_skills = [
    {"name": "Python", "level": {"value": 4, "max": 5}},
    {"name": "Machine Learning", "level": {"value": 3, "max": 5}},
]

# Define candidate's skills
candidate_skills = [
    {"name": "Python", "level": {"value": 5, "max": 5}},
    {"name": "Deep Learning", "level": {"value": 3, "max": 5}},
    {"name": "TensorFlow", "level": {"value": 4, "max": 5}},
]

# Calculate match score
result = match_score(required_skills, candidate_skills)

print(f"Overall Score: {result['overall_score']:.2%}")
for skill_score in result['skill_scores']:
    print(f"  {skill_score['skill_name']}: {skill_score['probability']:.2%}")
```

### Batch Matching (Recommended for Multiple Pairs)

For processing multiple candidate-requirement pairs, use `batch_match_score()` which is **8-10x faster**:

```python
from competency_api import batch_match_score

# Define multiple pairs to evaluate
pairs = [
    # Pair 1: Senior Python Developer
    (
        [{"name": "Python", "level": {"value": 5, "max": 5}}],  # required
        [{"name": "Python", "level": {"value": 4, "max": 5}}],  # candidate
    ),
    # Pair 2: Full-Stack Web Developer
    (
        [
            {"name": "React", "level": {"value": 4, "max": 5}},
            {"name": "Node.js", "level": {"value": 4, "max": 5}},
        ],  # required
        [
            {"name": "React", "level": {"value": 5, "max": 5}},
            {"name": "JavaScript", "level": {"value": 5, "max": 5}},
            {"name": "Express", "level": {"value": 4, "max": 5}},
        ],  # candidate
    ),
    # Pair 3: Data Scientist
    (
        [{"name": "Machine Learning", "level": {"value": 4, "max": 5}}],  # required
        [
            {"name": "Python", "level": {"value": 5, "max": 5}},
            {"name": "TensorFlow", "level": {"value": 4, "max": 5}},
            {"name": "Scikit-learn", "level": {"value": 4, "max": 5}},
        ],  # candidate
    ),
]

# Process all pairs in a single batch (much faster!)
results = batch_match_score(pairs)

# Display results
for i, result in enumerate(results, 1):
    print(f"Pair {i}: {result['overall_score']:.2%}")
    for skill_score in result['skill_scores']:
        print(f"  - {skill_score['skill_name']}: {skill_score['probability']:.2%}")
```

**Performance:** Batch processing is 8-10x faster than individual calls when processing multiple pairs.

## API Reference

### `match_score(required_skills, candidate_skills) -> dict`

Calculate the match score between required skills and candidate skills.

**Note:** For processing multiple candidate-requirement pairs, use `batch_match_score()` instead for much better performance.

**Parameters:**
- `required_skills` (list): List of required skills with proficiency levels
- `candidate_skills` (list): List of candidate's skills with proficiency levels

Each skill is a dictionary with:
- `name` (str): Skill name
- `level` (dict): Proficiency level with:
  - `value` (int): Current proficiency (0-max)
  - `max` (int): Maximum proficiency scale

**Returns:**
A dictionary containing:
- `overall_score` (float): Overall match score (0.0-1.0)
- `skill_scores` (list): Individual skill scores with:
  - `skill_name` (str): Name of the required skill
  - `probability` (float): Match probability (0.0-1.0)
  - `mean` (float): Mean of the score distribution
  - `variance` (float): Variance of the score distribution
  - `confidence_interval` (dict): 95% confidence interval with `lower` and `upper` bounds
- `skill_similarities` (dict): Semantic similarity matrix between all skills
- `pairwise_scores` (dict): Pairwise proficiency scores

**Example:**
```python
result = match_score(
    required_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}],
    candidate_skills=[{"name": "Python", "level": {"value": 4, "max": 5}}]
)
# Returns: {'overall_score': 0.98, 'skill_scores': [...], ...}
```

### `batch_match_score(pairs) -> list[dict]`

Calculate match scores for multiple candidate-requirement pairs in a single batch operation. This is **much faster** than calling `match_score()` multiple times because it:
- Initializes the embedding model only once
- Embeds all unique skills across all pairs in one batch
- Reuses embeddings efficiently across all pairs

**Parameters:**
- `pairs` (list): List of tuples, where each tuple contains `(required_skills, candidate_skills)`

**Returns:**
A list of `MatchResult` dictionaries (same structure as `match_score()`), one for each input pair in the same order.

**Example:**
```python
from competency_api import batch_match_score

pairs = [
    # Pair 1: Python developer
    (
        [{"name": "Python", "level": {"value": 4, "max": 5}}],  # required
        [{"name": "Python", "level": {"value": 5, "max": 5}}],  # candidate
    ),
    # Pair 2: Web developer
    (
        [{"name": "Web Development", "level": {"value": 4, "max": 5}}],  # required
        [
            {"name": "HTML", "level": {"value": 4, "max": 5}},
            {"name": "CSS", "level": {"value": 4, "max": 5}},
            {"name": "JavaScript", "level": {"value": 4, "max": 5}},
        ],  # candidate
    ),
]

results = batch_match_score(pairs)

for i, result in enumerate(results):
    print(f"Pair {i+1}: {result['overall_score']:.2%}")
```

**Performance:**
- **5 pairs**: ~2.8 seconds total (~0.56 seconds per pair)
- **Individual calls**: Would take ~4-5 seconds per pair due to repeated model initialization
- **Speedup**: Up to **8-10x faster** for large batches

See `batch_example.py` for a complete example.

### `init_logging() -> None`

Initialize tracing/logging for the competency API. Call this once at the start of your application to enable debug output.

**Example:**
```python
from competency_api import init_logging

init_logging()
```

## Configuration

### Cache Directory

The library downloads and caches embedding models (~100MB) on first use. By default, models are cached in `~/.cache/fastembed/`. You can customize this location:

```python
import os
os.environ["FASTEMBED_CACHE_PATH"] = "/custom/cache/path"

from competency_api import match_score
# Now will use custom cache directory
```

## Performance

### Single Match Performance

Typical performance characteristics for `match_score()`:
- **Model initialization**: ~1.3s (one-time, cached globally)
- **Small dataset** (10 candidate / 5 required skills): ~1.16s
- **Medium dataset** (50 candidate / 25 required skills): ~1.29s
- **Large dataset** (100 candidate / 50 required skills): ~1.64s

### Batch Match Performance

Performance for `batch_match_score()` is significantly better:

| Number of Pairs | Individual Calls | Batch Processing | Speedup |
|----------------|------------------|------------------|---------|
| 3 pairs        | ~12-15s          | ~2.5s            | ~5-6x   |
| 5 pairs        | ~20-25s          | ~2.8s            | ~8-10x  |
| 10 pairs       | ~40-50s          | ~3.5s            | ~12-15x |

**Why is batch faster?**
- **Single model initialization** - Only loads the embedding model once
- **Embedding reuse** - Skills appearing in multiple pairs are embedded once and cached
- **Reduced overhead** - Eliminates repeated setup/teardown for each pair

**Recommendation:** Always use `batch_match_score()` when processing more than 1 pair.

### Technical Details

The library uses:
- Global model caching to avoid re-initialization
- SIMD-accelerated similarity calculations (~0.2μs per comparison)
- Batch embedding processing for optimal throughput

## Examples

### Basic Exact Match

```python
from competency_api import match_score

result = match_score(
    required_skills=[{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
    candidate_skills=[{"name": "JavaScript", "level": {"value": 3, "max": 5}}]
)
print(f"Score: {result['overall_score']:.2%}")  # ~98-100%
```

### Proficiency Penalty

```python
result = match_score(
    required_skills=[{"name": "Python", "level": {"value": 5, "max": 5}}],
    candidate_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}]
)
print(f"Score: {result['overall_score']:.2%}")  # Lower due to proficiency gap
```

### Related Skills

```python
result = match_score(
    required_skills=[{"name": "Web Development", "level": {"value": 4, "max": 5}}],
    candidate_skills=[
        {"name": "HTML", "level": {"value": 4, "max": 5}},
        {"name": "CSS", "level": {"value": 4, "max": 5}},
        {"name": "JavaScript", "level": {"value": 4, "max": 5}},
    ]
)
print(f"Score: {result['overall_score']:.2%}")  # High due to related skills
```

### Batch Processing Example

```python
from competency_api import batch_match_score

# Evaluate multiple candidates against different roles
pairs = [
    ([{"name": "Python", "level": {"value": 4, "max": 5}}],
     [{"name": "Python", "level": {"value": 5, "max": 5}}]),

    ([{"name": "JavaScript", "level": {"value": 3, "max": 5}}],
     [{"name": "TypeScript", "level": {"value": 4, "max": 5}}]),

    ([{"name": "Database", "level": {"value": 4, "max": 5}}],
     [{"name": "PostgreSQL", "level": {"value": 4, "max": 5}}]),
]

results = batch_match_score(pairs)
for i, result in enumerate(results, 1):
    print(f"Match {i}: {result['overall_score']:.2%}")
```

### Full Examples

See the example scripts for complete demonstrations:
- `example.py` - Single match scenarios with various skill combinations
- `batch_example.py` - Batch matching with 5 diverse candidate-role pairs
- `benchmark_batch.py` - Performance comparison between individual and batch processing

## Testing

Run the test suite with pytest:

```bash
# Install test dependencies
pip install pytest

# Run tests
cd competency_api_python
pytest tests/ -v

# Or run tests with coverage
pip install pytest-cov
pytest tests/ --cov=competency_api --cov-report=html
```

## How It Works

1. **Semantic Embeddings**: Skills are converted to dense vector representations using a neural embedding model
2. **Similarity Calculation**: SIMD-accelerated cosine similarity between skill vectors
3. **Domain Classification**: Skills are classified into 14 domains (Finance, Tech, Marketing, etc.)
4. **Proficiency Modeling**: Beta distributions model uncertainty in proficiency levels
5. **Score Aggregation**:
   - Base score from semantic similarity and proficiency match
   - Cross-domain penalty for unrelated skills
   - Coherence bonus for multi-skill roles with aligned domains
6. **Confidence Intervals**: 95% confidence intervals quantify uncertainty

## Troubleshooting

### Model Download Issues

If model downloads fail:
1. Check internet connection
2. Verify disk space (~100MB needed)
3. Check cache directory permissions
4. Try setting a custom cache path (see Configuration)

### Import Errors

If you get "cannot import name 'match_score'":
1. Ensure you've built the package: `maturin develop`
2. Check you're in the correct Python environment
3. Verify Rust toolchain is installed: `rustc --version`

### Performance Issues

For slow performance:
1. Use `maturin develop --release` for optimized builds
2. First run is slower due to model download and initialization
3. Subsequent runs use cached models and are much faster

## License

This package is part of the competency matching workspace. See the root LICENSE file for details.

## Related

- **Core Library**: `../competency_api/` - Rust implementation
- **Node.js Binding**: `../competency_api_node_binding/` - Node.js/JavaScript binding
