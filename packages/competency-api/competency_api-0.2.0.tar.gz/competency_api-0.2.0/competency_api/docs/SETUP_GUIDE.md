# Memory Profiling Setup Guide

Step-by-step instructions for setting up memory profiling in the Competency API.

## Prerequisites

### System Requirements
- Rust 1.70+ (for latest criterion and memory profiling features)
- Python 3.7+ (for DHAT viewer, optional)
- Internet connection (for initial embedding model download)

### Install DHAT Viewer (Optional but Recommended)
```bash
pip install dhat
```

Or using conda:
```bash
conda install -c conda-forge dhat
```

## Configuration Files

### 1. Cargo.toml Configuration

The project is already configured with the necessary dependencies:

```toml
[dependencies]
# Core dependencies
fastembed = "5.0.0"
simsimd = "6.2.0"
# ... other deps ...

# Optional memory profiling dependencies
dhat = { version = "0.3", optional = true }
peak_alloc = { version = "0.2", optional = true }
jemallocator = { version = "0.5", optional = true }

[dev-dependencies]
# Benchmarking
criterion = { version = "0.5", features = ["html_reports"] }
# ... other dev deps ...

[features]
default = []
memory-profiling = ["dhat", "peak_alloc"]
jemalloc = ["jemallocator"]

[[bench]]
name = "memory_benchmark"
harness = false
```

### 2. Feature Flags Explained

| Feature | Purpose | Dependencies | Use Case |
|---------|---------|--------------|----------|
| `default` | Standard functionality | Core deps only | Normal usage |
| `memory-profiling` | Memory analysis | `dhat`, `peak_alloc` | Development, optimization |
| `jemalloc` | Alternative allocator | `jemallocator` | Performance testing |

## Project Structure

```
competency_api/
├── Cargo.toml                          # Dependencies and features
├── src/
│   ├── lib.rs                          # Main library
│   ├── profiling.rs                    # Memory profiling utilities
│   ├── embedding.rs                    # Embedding operations
│   ├── similarity.rs                   # Similarity calculations
│   ├── matcher.rs                      # Main matching logic
│   └── ...                             # Other modules
├── benches/
│   └── memory_benchmark.rs             # Criterion benchmarks
├── tests/
│   └── memory_tests.rs                 # Memory usage tests
├── examples/
│   └── memory_profile.rs               # DHAT profiling example
└── docs/
    ├── MEMORY_PROFILING_GUIDE.md       # Complete guide
    ├── SETUP_GUIDE.md                  # This file
    └── QUICK_START.md                  # Quick reference
```

## Verification Steps

### 1. Test Basic Compilation
```bash
# Test without profiling features
cargo check

# Test with memory profiling
cargo check --features memory-profiling

# Test with jemalloc
cargo check --features jemalloc
```

### 2. Verify Profiling Module
```bash
# Test memory profiling utilities
cargo test --features memory-profiling profiling -- --nocapture
```

Expected output:
```
test profiling::tests::test_memory_profiling ... ok
test profiling::tests::test_memory_snapshot ... ok
test profiling::tests::test_profile_memory_usage ... ok
```

### 3. Test Simple Memory Measurement
```bash
# Test without embedding models (fast)
cargo test test_memory_without_profiling -- --nocapture
```

Expected output:
```
test test_memory_without_profiling ... ok
```

### 4. Test DHAT Integration
```bash
# Generate DHAT profile
cargo run --example memory_profile --features memory-profiling
```

This should create a `dhat-heap.json` file in the project root.

### 5. View DHAT Report
```bash
# View the generated profile
dh_view.py dhat-heap.json
```

This opens a web interface showing heap allocation details.

### 6. Test Benchmarks
```bash
# Run memory benchmarks
cargo bench --features memory-profiling
```

Expected output:
```
memory_usage/match_skills_10_candidates_5_required
                        time:   [X.XXX ms X.XXX ms X.XXX ms]
memory_usage/embed_skills_10
                        time:   [X.XXX ms X.XXX ms X.XXX ms]
...
```

## Environment Setup

### 1. Environment Variables

Set these for consistent profiling:

```bash
# Disable embedding model download progress (for cleaner output)
export FASTEMBED_SHOW_DOWNLOAD_PROGRESS=false

# Set cache directory (optional)
export FASTEMBED_CACHE_DIR="./cache"

# Rust logging level
export RUST_LOG=info
```

### 2. Development Environment

Add to your `.bashrc` or `.zshrc`:

```bash
# Memory profiling aliases
alias profile-memory="cargo test --features memory-profiling profiling -- --nocapture"
alias profile-baseline="cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture"
alias profile-dhat="cargo run --example memory_profile --features memory-profiling"
alias profile-bench="cargo bench --features memory-profiling"
alias view-dhat="dh_view.py dhat-heap.json"
```

### 3. VS Code Configuration (Optional)

Add to `.vscode/settings.json`:

```json
{
    "rust-analyzer.cargo.features": ["memory-profiling"],
    "rust-analyzer.runnables.extraArgs": ["--features", "memory-profiling"],
    "rust-analyzer.check.extraArgs": ["--features", "memory-profiling"]
}
```

## Common Configuration Issues

### Issue 1: Optional Dependencies Error
```
error: feature `jemalloc` includes `jemallocator`, but `jemallocator` is not an optional dependency
```

**Solution**: Ensure dependencies are marked as optional:
```toml
jemallocator = { version = "0.5", optional = true }
```

### Issue 2: Type Conversion Errors
```
error[E0308]: mismatched types
expected `usize`, found `f32`
```

**Solution**: Use proper type conversions in profiling code:
```rust
initial_peak: PEAK_ALLOC.peak_usage_as_mb() as usize,
```

### Issue 3: Global Allocator Conflicts
```
error: cannot set global allocator
```

**Solution**: Use feature flags to conditionally enable allocators:
```rust
#[cfg(feature = "memory-profiling")]
#[global_allocator]
static ALLOCATOR: DhatAlloc = DhatAlloc;
```

### Issue 4: DHAT Not Working
```
No dhat-heap.json file generated
```

**Solutions**:
1. Ensure `memory-profiling` feature is enabled
2. Check Python and `dhat` package installation
3. Verify the example runs to completion

### Issue 5: Tests Timing Out
```
test has been running for over 60 seconds
```

**Solutions**:
1. Use tests that don't require embedding model downloads
2. Ensure internet connection for initial model download
3. Set up local model cache

## Advanced Configuration

### 1. Custom Allocator Setup

For performance comparison with different allocators:

```toml
[dependencies]
mimalloc = { version = "0.1", optional = true }

[features]
mimalloc-allocator = ["mimalloc"]
```

```rust
#[cfg(feature = "mimalloc-allocator")]
use mimalloc::MiMalloc;

#[cfg(feature = "mimalloc-allocator")]
#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;
```

### 2. CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Memory Profiling Tests
  run: |
    cargo test --features memory-profiling profiling
    cargo test test_memory_without_profiling

- name: Memory Benchmarks
  run: |
    cargo bench --features memory-profiling -- --output-format json | tee benchmark-results.json

- name: Upload Benchmark Results
  uses: actions/upload-artifact@v3
  with:
    name: benchmark-results
    path: benchmark-results.json
```

### 3. Docker Setup

For consistent profiling environment:

```dockerfile
FROM rust:1.75

# Install Python and DHAT
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install dhat

# Set working directory
WORKDIR /app

# Copy project
COPY . .

# Build with memory profiling
RUN cargo build --features memory-profiling

# Run profiling
CMD ["cargo", "test", "--features", "memory-profiling", "profiling", "--", "--nocapture"]
```

## Validation Checklist

- [ ] `cargo check` passes without features
- [ ] `cargo check --features memory-profiling` passes
- [ ] `cargo test profiling --features memory-profiling` passes
- [ ] `cargo test test_memory_without_profiling` passes
- [ ] `cargo run --example memory_profile --features memory-profiling` creates `dhat-heap.json`
- [ ] `dh_view.py dhat-heap.json` opens successfully (if DHAT installed)
- [ ] `cargo bench --features memory-profiling` runs successfully
- [ ] All tests pass with and without profiling features

## Next Steps

Once setup is complete:

1. **Read the [Memory Profiling Guide](MEMORY_PROFILING_GUIDE.md)** for detailed usage instructions
2. **Run baseline measurements** to establish current memory usage
3. **Identify optimization targets** using the profiling tools
4. **Apply optimizations** and measure improvements
5. **Set up continuous monitoring** for regression detection

## Support

If you encounter issues:

1. Check the [Troubleshooting section](MEMORY_PROFILING_GUIDE.md#troubleshooting) in the main guide
2. Verify your Rust version: `rustc --version`
3. Check feature flags: `cargo check --features memory-profiling`
4. Review error messages for dependency conflicts
5. Ensure all prerequisites are installed correctly