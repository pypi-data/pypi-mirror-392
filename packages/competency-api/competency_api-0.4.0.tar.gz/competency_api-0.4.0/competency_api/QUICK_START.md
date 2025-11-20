# Quick Start: Memory Profiling

## Fixed Setup - Ready to Use!

The memory profiling is now working correctly. Here's how to use it:

### 1. Test Memory Profiling (Basic)
```bash
cargo test --features memory-profiling profiling -- --nocapture
```

### 2. Test Simple Memory Usage (No Embedding Model Required)
```bash
cargo test test_memory_without_profiling -- --nocapture
```

### 3. Run DHAT for Detailed Analysis
```bash
cargo run --example memory_profile --features memory-profiling
```

## What's Working

✅ **Memory profiling setup complete**
✅ **Peak memory tracking with `peak_alloc`** 
✅ **DHAT integration for detailed analysis**
✅ **Criterion benchmarks with memory stats**
✅ **Tests without embedding model dependencies**

## Next Steps

1. **Get Baseline**: Run the profiling tests to see current memory usage
2. **Apply Optimizations**: Implement the memory optimizations we identified
3. **Compare Results**: Re-run tests to measure improvement

## Expected Output

When you run the memory profiling, you'll see output like:
```
test_memory_profiling: current=4MB, peak=6MB
test_memory_snapshot: current=2MB, peak=4MB
test_profile_memory_usage: current=1MB, peak=3MB
```

## Note About Embedding Tests

Some tests that require downloading embedding models may fail if you don't have internet access or the model cache. The core memory profiling functionality works independently of these models.

## Ready for Optimization!

You can now:
1. Measure current memory usage
2. Apply the optimizations we identified
3. Measure the improvements
4. Generate detailed reports