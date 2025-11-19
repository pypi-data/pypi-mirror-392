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

## API Reference

### `match_score(required_skills, candidate_skills) -> dict`

Calculate the match score between required skills and candidate skills.

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

Typical performance characteristics:
- **Model initialization**: ~1.3s (one-time, cached globally)
- **Small dataset** (10 candidate / 5 required skills): ~1.16s
- **Medium dataset** (50 candidate / 25 required skills): ~1.29s
- **Large dataset** (100 candidate / 50 required skills): ~1.64s

The library uses:
- Global model caching to avoid re-initialization
- SIMD-accelerated similarity calculations (~0.2μs per comparison)
- Parallel processing with Rayon for large datasets

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

### Full Example

See `example.py` for a complete demonstration with multiple scenarios.

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
