# Memory Profiling Troubleshooting Guide

Common issues and solutions when using memory profiling tools in the Competency API.

## Table of Contents

1. [Setup Issues](#setup-issues)
2. [Compilation Errors](#compilation-errors)
3. [Runtime Issues](#runtime-issues)
4. [DHAT Profiling Issues](#dhat-profiling-issues)
5. [Benchmark Issues](#benchmark-issues)
6. [Performance Issues](#performance-issues)
7. [Platform-Specific Issues](#platform-specific-issues)

## Setup Issues

### Issue 1: Cargo Feature Resolution Error

**Error:**
```
error: failed to parse manifest at `Cargo.toml`
Caused by:
  feature `jemalloc` includes `jemallocator`, but `jemallocator` is not an optional dependency
```

**Solution:**
Ensure all profiling dependencies are marked as optional:

```toml
[dependencies]
dhat = { version = "0.3", optional = true }
peak_alloc = { version = "0.2", optional = true }
jemallocator = { version = "0.5", optional = true }

[features]
memory-profiling = ["dhat", "peak_alloc"]
jemalloc = ["jemallocator"]
```

**Verification:**
```bash
cargo check --features memory-profiling
```

### Issue 2: Missing DHAT Viewer

**Error:**
```bash
dh_view.py: command not found
```

**Solution:**
Install the DHAT viewer:

```bash
# Using pip
pip install dhat

# Using conda
conda install -c conda-forge dhat

# Using pip3 (if pip points to Python 2)
pip3 install dhat
```

**Verification:**
```bash
dh_view.py --help
```

### Issue 3: Python/DHAT Installation Issues

**Error:**
```
ModuleNotFoundError: No module named 'dhat'
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.7+
   python3 --version
   ```

2. **Install with specific Python version:**
   ```bash
   python3 -m pip install dhat
   ```

3. **Use virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install dhat
   ```

4. **Check installation:**
   ```bash
   python3 -c "import dhat; print('DHAT installed successfully')"
   ```

## Compilation Errors

### Issue 4: Type Conversion Errors

**Error:**
```
error[E0308]: mismatched types
expected `usize`, found `f32`
```

**Cause:** `peak_alloc` returns `f32` but code expects `usize`.

**Solution:**
Add explicit type conversions:

```rust
// Correct implementation
pub fn current_usage_mb(&self) -> usize {
    #[cfg(feature = "peak_alloc")]
    return PEAK_ALLOC.current_usage_as_mb() as usize;
    #[cfg(not(feature = "peak_alloc"))]
    return 0;
}
```

**Prevention:**
Always use type annotations when working with memory profiling APIs:

```rust
let memory_usage: usize = PEAK_ALLOC.current_usage_as_mb() as usize;
```

### Issue 5: Global Allocator Conflicts

**Error:**
```
error: cannot have more than one global allocator
```

**Cause:** Multiple global allocators defined.

**Solution:**
Use feature flags to conditionally enable allocators:

```rust
#[cfg(feature = "memory-profiling")]
use dhat::DhatAlloc;

#[cfg(feature = "memory-profiling")]
#[global_allocator]
static ALLOCATOR: DhatAlloc = DhatAlloc;

#[cfg(feature = "jemalloc")]
use jemallocator::Jemalloc;

#[cfg(feature = "jemalloc")]
#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;
```

**Best Practice:**
Only enable one allocator feature at a time:

```bash
# Good
cargo test --features memory-profiling

# Good
cargo test --features jemalloc

# Bad - may conflict
cargo test --features memory-profiling,jemalloc
```

### Issue 6: Feature Flag Dependencies

**Error:**
```
error[E0432]: unresolved import `dhat`
use of undeclared crate or module `dhat`
```

**Cause:** Code tries to use `dhat` without the feature enabled.

**Solution:**
Properly guard imports with feature flags:

```rust
// Correct
#[cfg(feature = "dhat")]
use dhat::{Dhat, DhatAlloc};

// Also correct with combined feature
#[cfg(feature = "memory-profiling")]
use dhat::{Dhat, DhatAlloc};
```

**Verification:**
```bash
cargo check  # Should work without features
cargo check --features memory-profiling  # Should work with features
```

## Runtime Issues

### Issue 7: Tests Timeout

**Error:**
```
test has been running for over 60 seconds
```

**Causes and Solutions:**

1. **Embedding model download:**
   ```bash
   # Run tests that don't require embeddings
   cargo test test_memory_without_profiling
   
   # Or ensure internet connection for model download
   export RUST_TEST_TIMEOUT=300  # 5 minutes
   ```

2. **Large dataset processing:**
   ```rust
   // Use smaller test datasets
   fn create_small_test_skills(n: usize) -> Vec<Skill> {
       (0..n.min(10)).map(|i| /* ... */).collect()
   }
   ```

3. **Slow profiling overhead:**
   ```bash
   # Run without DHAT for faster tests
   cargo test --features peak_alloc profiling
   ```

### Issue 8: Memory Usage Not Tracked

**Symptoms:**
- All memory measurements return 0
- No memory differences detected

**Debugging Steps:**

1. **Check feature flags:**
   ```bash
   cargo test --features memory-profiling profiling -- --nocapture
   ```

2. **Verify allocator is active:**
   ```rust
   #[test]
   fn test_allocator_working() {
       let before = std::alloc::System.alloc_bytes();
       let _data = vec![0u8; 1024 * 1024]; // 1MB
       let after = std::alloc::System.alloc_bytes();
       assert!(after > before);
   }
   ```

3. **Check compilation flags:**
   ```bash
   cargo test --features memory-profiling -v  # Verbose output
   ```

### Issue 9: Inconsistent Memory Measurements

**Symptoms:**
- Memory usage varies significantly between runs
- Negative memory differences

**Solutions:**

1. **Reset peak tracking:**
   ```rust
   profiler.reset_peak();
   // Perform operation
   let memory_used = profiler.peak_since_creation();
   ```

2. **Use multiple measurements:**
   ```rust
   let mut measurements = Vec::new();
   for _ in 0..5 {
       let (_, before, after) = profile_memory_usage("test", || {
           // Your operation
       });
       measurements.push(after.peak_mb - before.peak_mb);
   }
   let avg_memory = measurements.iter().sum::<usize>() / measurements.len();
   ```

3. **Control for background allocations:**
   ```rust
   // Warm up allocators
   let _warmup = vec![0u8; 1024];
   std::thread::sleep(Duration::from_millis(10));
   
   // Now measure
   let (_, before, after) = profile_memory_usage("actual_test", || {
       // Your operation
   });
   ```

## DHAT Profiling Issues

### Issue 10: No dhat-heap.json Generated

**Debugging Steps:**

1. **Check feature flag:**
   ```bash
   cargo run --example memory_profile --features memory-profiling
   ```

2. **Verify DHAT initialization:**
   ```rust
   fn main() {
       #[cfg(feature = "memory-profiling")]
       let _dhat = dhat::Dhat::start_heap_profiling();
       
       println!("DHAT initialized"); // Should print
       
       // Your code here
       
       println!("Exiting"); // Should print before file generation
   }
   ```

3. **Check file permissions:**
   ```bash
   ls -la dhat-heap.json
   pwd  # Check current directory
   ```

4. **Manual verification:**
   ```rust
   #[cfg(feature = "memory-profiling")]
   {
       use dhat::Dhat;
       let _dhat = Dhat::start_heap_profiling();
       let _data = vec![0u8; 1024 * 1024]; // Force allocation
   } // DHAT should write file when _dhat drops
   ```

### Issue 11: DHAT Report Shows No Data

**Symptoms:**
- `dhat-heap.json` exists but contains minimal data
- DHAT viewer shows "No heap blocks"

**Solutions:**

1. **Ensure allocations occur within DHAT scope:**
   ```rust
   let _dhat = dhat::Dhat::start_heap_profiling();
   
   // These allocations will be tracked
   let data = vec![0u8; 1024 * 1024];
   
   // DHAT stops tracking when _dhat drops
   ```

2. **Force heap allocations:**
   ```rust
   // Stack allocation - not tracked
   let array = [0u8; 1024];
   
   // Heap allocation - tracked by DHAT
   let vec = vec![0u8; 1024];
   let boxed = Box::new([0u8; 1024]);
   ```

3. **Check debug vs release mode:**
   ```bash
   # Debug mode (more allocations)
   cargo run --example memory_profile --features memory-profiling
   
   # Release mode (optimized, fewer allocations)
   cargo run --release --example memory_profile --features memory-profiling
   ```

### Issue 12: DHAT Viewer Won't Open

**Error:**
```
Error opening dhat-heap.json: File not found or corrupted
```

**Solutions:**

1. **Validate JSON file:**
   ```bash
   # Check file exists and has content
   ls -la dhat-heap.json
   
   # Validate JSON syntax
   python3 -m json.tool dhat-heap.json > /dev/null
   ```

2. **Check file path:**
   ```bash
   # DHAT creates file in current working directory
   pwd
   find . -name "dhat-heap.json" -type f
   ```

3. **Use absolute path:**
   ```bash
   dh_view.py /full/path/to/dhat-heap.json
   ```

4. **Alternative viewers:**
   ```bash
   # View raw JSON
   cat dhat-heap.json | jq .
   
   # Python script to validate
   python3 -c "
   import json
   with open('dhat-heap.json') as f:
       data = json.load(f)
       print(f'DHAT data loaded: {len(data)} entries')
   "
   ```

## Benchmark Issues

### Issue 13: Criterion Benchmarks Fail

**Error:**
```
error: bench target in package `competency_api` requires `Cargo.toml` to have a [package.metadata.docs.rs] section
```

**Solution:**
Ensure proper benchmark configuration:

```toml
[[bench]]
name = "memory_benchmark"
harness = false

[package.metadata.docs.rs]
all-features = true
```

### Issue 14: Benchmark Results Inconsistent

**Symptoms:**
- High variance in benchmark results
- Memory measurements fluctuate wildly

**Solutions:**

1. **Stabilize system conditions:**
   ```bash
   # Close other applications
   # Disable CPU frequency scaling (Linux)
   sudo cpupower frequency-set --governor performance
   
   # Run benchmarks
   cargo bench --features memory-profiling
   
   # Restore CPU scaling
   sudo cpupower frequency-set --governor powersave
   ```

2. **Increase benchmark sample size:**
   ```rust
   group.sample_size(100);  // More samples
   group.measurement_time(Duration::from_secs(30));  // Longer measurement
   ```

3. **Warm up before measurement:**
   ```rust
   group.bench_function("test", |b| {
       // Warm up
       for _ in 0..3 {
           black_box(test_function());
       }
       
       b.iter(|| {
           black_box(test_function())
       });
   });
   ```

## Performance Issues

### Issue 15: Profiling Causes Significant Slowdown

**Symptoms:**
- Tests take much longer with profiling enabled
- Normal operations become very slow

**Solutions:**

1. **Use lighter profiling for development:**
   ```bash
   # Use only peak_alloc, not DHAT
   cargo test --features peak_alloc
   ```

2. **Conditional profiling:**
   ```rust
   #[cfg(debug_assertions)]
   let _dhat = dhat::Dhat::start_heap_profiling();
   ```

3. **Profile specific operations only:**
   ```rust
   // Profile only critical sections
   let (result, _, _) = profile_memory_usage("critical_section", || {
       expensive_operation()
   });
   ```

### Issue 16: High Memory Overhead from Profiling

**Symptoms:**
- Memory usage much higher with profiling
- Out of memory errors during profiling

**Solutions:**

1. **Reduce dataset size for profiling:**
   ```rust
   #[cfg(feature = "memory-profiling")]
   const TEST_SIZE: usize = 100;
   #[cfg(not(feature = "memory-profiling"))]
   const TEST_SIZE: usize = 10000;
   ```

2. **Use sampling:**
   ```rust
   // Profile every 10th operation
   if operation_count % 10 == 0 {
       profile_memory_usage("sampled", || operation());
   }
   ```

3. **Alternative allocators:**
   ```bash
   # Try jemalloc for lower overhead
   cargo test --features jemalloc
   ```

## Platform-Specific Issues

### Issue 17: macOS Code Signing Issues

**Error:**
```
error: failed to execute process: Operation not permitted
```

**Solutions:**

1. **Disable SIP for development (not recommended for production):**
   - Reboot holding Cmd+R
   - Open Terminal in Recovery Mode
   - Run: `csrutil disable`
   - Reboot normally

2. **Use alternative approaches:**
   ```bash
   # Use instruments instead of custom profiling
   instruments -t "Allocations" target/debug/examples/memory_profile
   ```

3. **Codesign the binary:**
   ```bash
   codesign -s - target/debug/examples/memory_profile
   ```

### Issue 18: Windows Linker Issues

**Error:**
```
link.exe: error LNK2019: unresolved external symbol
```

**Solutions:**

1. **Install Visual Studio Build Tools**
2. **Use GNU toolchain:**
   ```bash
   rustup toolchain install stable-x86_64-pc-windows-gnu
   rustup default stable-x86_64-pc-windows-gnu
   ```

3. **Check dependency versions:**
   ```toml
   [target.'cfg(windows)'.dependencies]
   dhat = { version = "0.3", optional = true }
   ```

### Issue 19: Linux Permissions Issues

**Error:**
```
Permission denied (os error 13)
```

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la dhat-heap.json
   chmod 644 dhat-heap.json
   ```

2. **Run with appropriate permissions:**
   ```bash
   # Don't use sudo unless necessary
   cargo test --features memory-profiling
   ```

3. **Check disk space:**
   ```bash
   df -h .
   ```

## Diagnostic Commands

### General Diagnostics

```bash
# Check Rust version
rustc --version

# Check Cargo features
cargo check --features memory-profiling -v

# Check dependencies
cargo tree --features memory-profiling

# Test compilation
cargo build --features memory-profiling

# Test basic functionality
cargo test test_memory_without_profiling
```

### DHAT Diagnostics

```bash
# Check DHAT installation
python3 -c "import dhat; print(dhat.__version__)"

# Validate DHAT file
python3 -m json.tool dhat-heap.json > /dev/null && echo "Valid JSON"

# Check DHAT file size
ls -lh dhat-heap.json
```

### Memory Profiling Diagnostics

```bash
# Test profiling utilities
cargo test --features memory-profiling profiling -- --nocapture

# Check allocator
echo 'fn main() { let _v = vec![0u8; 1024]; }' | rustc --test --features memory-profiling -
```

### Environment Diagnostics

```bash
# Check environment variables
env | grep -i rust
env | grep -i cargo

# Check available memory
free -h  # Linux
vm_stat  # macOS
```

This troubleshooting guide covers the most common issues encountered when setting up and using memory profiling in the Competency API. For additional help, check the error logs and use the diagnostic commands provided.