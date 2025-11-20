# Memory Profiling Usage Examples

Practical examples showing how to use the memory profiling tools in the Competency API.

## Table of Contents

1. [Basic Memory Measurement](#basic-memory-measurement)
2. [Component-Specific Profiling](#component-specific-profiling)
3. [Optimization Scenarios](#optimization-scenarios)
4. [Benchmarking Examples](#benchmarking-examples)
5. [Advanced Analysis](#advanced-analysis)
6. [Real-World Workflows](#real-world-workflows)

## Basic Memory Measurement

### Example 1: Simple Memory Snapshot

```rust
use competency_api::profiling::MemorySnapshot;

fn basic_memory_measurement() {
    // Take initial snapshot
    let before = MemorySnapshot::take("initial");
    println!("Before operation: {}", before);
    
    // Perform memory-intensive operation
    let data: Vec<u8> = vec![0; 1024 * 1024]; // 1MB allocation
    
    // Take final snapshot
    let after = MemorySnapshot::take("after_allocation");
    println!("After operation: {}", after);
    
    let memory_used = after.peak_mb.saturating_sub(before.peak_mb);
    println!("Memory used: {}MB", memory_used);
}
```

### Example 2: Memory Profiler Usage

```rust
use competency_api::profiling::MemoryProfiler;

fn profile_with_memory_profiler() {
    let profiler = MemoryProfiler::new();
    
    println!("Initial state:");
    println!("  Current: {}MB", profiler.current_usage_mb());
    println!("  Peak: {}MB", profiler.peak_usage_mb());
    
    // Reset peak tracking
    profiler.reset_peak();
    
    // Perform operations
    let mut data = Vec::new();
    for i in 0..1000 {
        data.push(vec![0u8; 1024]); // 1KB each
    }
    
    println!("After allocations:");
    println!("  Current: {}MB", profiler.current_usage_mb());
    println!("  Peak since reset: {}MB", profiler.peak_since_creation());
}
```

### Example 3: Profile Memory Usage Function

```rust
use competency_api::profiling::profile_memory_usage;

fn analyze_operation_memory() {
    let (result, before, after) = profile_memory_usage("vector_creation", || {
        // Create and manipulate a large vector
        let mut data = Vec::with_capacity(1_000_000);
        for i in 0..1_000_000 {
            data.push(i as f64);
        }
        data.iter().sum::<f64>()
    });
    
    println!("Operation result: {}", result);
    println!("Memory profile:");
    println!("  Before: {}", before);
    println!("  After: {}", after);
    
    let memory_delta = after.peak_mb.saturating_sub(before.peak_mb);
    println!("  Memory used: {}MB", memory_delta);
}
```

## Component-Specific Profiling

### Example 4: Embedding Memory Analysis

```rust
use competency_api::*;
use competency_api::profiling::profile_memory_usage;

fn profile_embedding_memory() {
    let skills = vec![
        Skill { name: "Python".to_string(), level: ProficiencyLevel { value: 4, max: 5 } },
        Skill { name: "Rust".to_string(), level: ProficiencyLevel { value: 3, max: 5 } },
        Skill { name: "Machine Learning".to_string(), level: ProficiencyLevel { value: 5, max: 5 } },
    ];
    
    let (embedded_skills, before, after) = profile_memory_usage("embedding", || {
        let mut embedder = SkillEmbedder::new().unwrap();
        embedder.embed_skills(&skills).unwrap()
    });
    
    println!("Embedding Analysis:");
    println!("  Skills processed: {}", skills.len());
    println!("  Memory before: {}", before);
    println!("  Memory after: {}", after);
    println!("  Memory per skill: {:.2}MB", 
             (after.peak_mb - before.peak_mb) as f64 / skills.len() as f64);
    
    // Verify embedding dimensions
    if let Some(first_skill) = embedded_skills.first() {
        println!("  Embedding dimension: {}", first_skill.embedding.len());
        println!("  Memory per embedding: {:.2}KB", 
                 first_skill.embedding.len() * 4 / 1024); // f32 = 4 bytes
    }
}
```

### Example 5: Similarity Calculation Profiling

```rust
use competency_api::similarity::SkillSimilarityCalculator;
use competency_api::profiling::profile_memory_usage;

fn profile_similarity_calculation() {
    // Create embedded skills (mock data for example)
    let mut embedder = SkillEmbedder::new().unwrap();
    let candidate_skills = create_test_skills(50);
    let required_skills = create_test_skills(25);
    
    let candidate_embedded = embedder.embed_skills(&candidate_skills).unwrap();
    let required_embedded = embedder.embed_skills(&required_skills).unwrap();
    
    let (similarities, before, after) = profile_memory_usage("similarity_calc", || {
        SkillSimilarityCalculator::calculate_similarities(&candidate_embedded, &required_embedded)
    });
    
    println!("Similarity Calculation Analysis:");
    println!("  Matrix size: {}x{}", similarities.len(), similarities[0].len());
    println!("  Memory before: {}", before);
    println!("  Memory after: {}", after);
    
    let total_comparisons = candidate_skills.len() * required_skills.len();
    let memory_per_comparison = (after.peak_mb - before.peak_mb) * 1024 * 1024 / total_comparisons;
    println!("  Memory per comparison: {}bytes", memory_per_comparison);
}

fn create_test_skills(count: usize) -> Vec<Skill> {
    (0..count).map(|i| Skill {
        name: format!("Skill_{}", i),
        level: ProficiencyLevel { value: (i % 5) as u32 + 1, max: 5 }
    }).collect()
}
```

### Example 6: End-to-End Matching Profiling

```rust
use competency_api::*;
use competency_api::profiling::profile_memory_usage;

fn profile_complete_matching() {
    let candidate_skills = vec![
        Skill { name: "Python Programming".to_string(), level: ProficiencyLevel { value: 4, max: 5 } },
        Skill { name: "Data Analysis".to_string(), level: ProficiencyLevel { value: 3, max: 5 } },
        Skill { name: "Machine Learning".to_string(), level: ProficiencyLevel { value: 5, max: 5 } },
    ];
    
    let required_skills = vec![
        Skill { name: "Programming".to_string(), level: ProficiencyLevel { value: 3, max: 5 } },
        Skill { name: "Data Science".to_string(), level: ProficiencyLevel { value: 4, max: 5 } },
    ];
    
    let (match_result, before, after) = profile_memory_usage("complete_matching", || {
        let mut matcher = SkillMatcher::new().unwrap();
        matcher.calculate_match_score(candidate_skills.clone(), required_skills.clone()).unwrap()
    });
    
    println!("Complete Matching Analysis:");
    println!("  Candidate skills: {}", candidate_skills.len());
    println!("  Required skills: {}", required_skills.len());
    println!("  Overall match score: {:.3}", match_result.overall_score);
    println!("  Memory before: {}", before);
    println!("  Memory after: {}", after);
    println!("  Total memory used: {}MB", after.peak_mb - before.peak_mb);
    
    // Analyze per-skill memory usage
    let total_skills = candidate_skills.len() + required_skills.len();
    let memory_per_skill = (after.peak_mb - before.peak_mb) as f64 / total_skills as f64;
    println!("  Memory per skill: {:.2}MB", memory_per_skill);
}
```

## Optimization Scenarios

### Example 7: Before/After Optimization Comparison

```rust
use competency_api::profiling::{profile_memory_usage, MemorySnapshot};
use std::collections::HashMap;

// Unoptimized version - creates HashMap without capacity hint
fn unoptimized_hashmap_creation(size: usize) -> HashMap<String, f64> {
    let mut map = HashMap::new(); // No capacity hint
    for i in 0..size {
        map.insert(format!("key_{}", i), i as f64);
    }
    map
}

// Optimized version - pre-allocates HashMap capacity
fn optimized_hashmap_creation(size: usize) -> HashMap<String, f64> {
    let mut map = HashMap::with_capacity(size); // Pre-allocate
    for i in 0..size {
        map.insert(format!("key_{}", i), i as f64);
    }
    map
}

fn compare_hashmap_optimization() {
    let size = 10_000;
    
    // Test unoptimized version
    let (_, before1, after1) = profile_memory_usage("unoptimized_hashmap", || {
        unoptimized_hashmap_creation(size)
    });
    
    // Test optimized version
    let (_, before2, after2) = profile_memory_usage("optimized_hashmap", || {
        optimized_hashmap_creation(size)
    });
    
    let unoptimized_memory = after1.peak_mb - before1.peak_mb;
    let optimized_memory = after2.peak_mb - before2.peak_mb;
    let improvement = unoptimized_memory.saturating_sub(optimized_memory);
    let percentage = if unoptimized_memory > 0 {
        (improvement as f64 / unoptimized_memory as f64) * 100.0
    } else { 0.0 };
    
    println!("HashMap Optimization Comparison:");
    println!("  Unoptimized memory: {}MB", unoptimized_memory);
    println!("  Optimized memory: {}MB", optimized_memory);
    println!("  Memory saved: {}MB ({:.1}%)", improvement, percentage);
}
```

### Example 8: Vector Capacity Optimization

```rust
use competency_api::profiling::profile_memory_usage;

// Unoptimized: Vec grows as needed
fn unoptimized_vec_creation(size: usize) -> Vec<f64> {
    let mut vec = Vec::new();
    for i in 0..size {
        vec.push(i as f64);
    }
    vec
}

// Optimized: Pre-allocate Vec capacity
fn optimized_vec_creation(size: usize) -> Vec<f64> {
    let mut vec = Vec::with_capacity(size);
    for i in 0..size {
        vec.push(i as f64);
    }
    vec
}

fn compare_vec_optimization() {
    let sizes = vec![1_000, 10_000, 100_000];
    
    for size in sizes {
        println!("\nTesting with {} elements:", size);
        
        let (_, before1, after1) = profile_memory_usage("unoptimized_vec", || {
            unoptimized_vec_creation(size)
        });
        
        let (_, before2, after2) = profile_memory_usage("optimized_vec", || {
            optimized_vec_creation(size)
        });
        
        let unopt_mem = after1.peak_mb - before1.peak_mb;
        let opt_mem = after2.peak_mb - before2.peak_mb;
        let savings = unopt_mem.saturating_sub(opt_mem);
        
        println!("  Unoptimized: {}MB", unopt_mem);
        println!("  Optimized: {}MB", opt_mem);
        println!("  Savings: {}MB", savings);
    }
}
```

### Example 9: String Cloning Optimization

```rust
use competency_api::profiling::profile_memory_usage;
use std::collections::HashMap;

// Unoptimized: Clones strings unnecessarily
fn unoptimized_string_processing(data: &[String]) -> HashMap<String, usize> {
    let mut map = HashMap::new();
    for item in data {
        let key = item.clone(); // Unnecessary clone
        map.insert(key, item.len());
    }
    map
}

// Optimized: Uses references where possible
fn optimized_string_processing(data: &[String]) -> HashMap<&str, usize> {
    let mut map = HashMap::with_capacity(data.len());
    for item in data {
        map.insert(item.as_str(), item.len()); // No clone needed
    }
    map
}

fn compare_string_optimization() {
    // Create test data
    let test_data: Vec<String> = (0..1000)
        .map(|i| format!("test_string_with_data_{}", i))
        .collect();
    
    let (_, before1, after1) = profile_memory_usage("unoptimized_strings", || {
        unoptimized_string_processing(&test_data)
    });
    
    let (_, before2, after2) = profile_memory_usage("optimized_strings", || {
        optimized_string_processing(&test_data)
    });
    
    let unopt_mem = after1.peak_mb - before1.peak_mb;
    let opt_mem = after2.peak_mb - before2.peak_mb;
    
    println!("String Processing Optimization:");
    println!("  Unoptimized (with cloning): {}MB", unopt_mem);
    println!("  Optimized (with references): {}MB", opt_mem);
    println!("  Memory saved: {}MB", unopt_mem.saturating_sub(opt_mem));
}
```

## Benchmarking Examples

### Example 10: Custom Benchmark

```rust
// This would go in benches/custom_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use competency_api::*;
use competency_api::profiling::profile_memory_usage;

fn benchmark_skill_matching(c: &mut Criterion) {
    let mut group = c.benchmark_group("skill_matching_memory");
    
    for size in [10, 50, 100].iter() {
        let candidate_skills = create_test_skills(*size);
        let required_skills = create_test_skills(*size / 2);
        
        group.bench_function(
            format!("skills_{}", size),
            |b| {
                b.iter(|| {
                    let (result, _, _) = profile_memory_usage("benchmark", || {
                        let mut matcher = SkillMatcher::new().unwrap();
                        matcher.calculate_match_score(
                            black_box(candidate_skills.clone()),
                            black_box(required_skills.clone()),
                        ).unwrap()
                    });
                    black_box(result);
                });
            },
        );
    }
    
    group.finish();
}

fn create_test_skills(n: usize) -> Vec<Skill> {
    (0..n).map(|i| Skill {
        name: format!("Skill_{}", i),
        level: ProficiencyLevel { value: (i % 5) as u32 + 1, max: 5 }
    }).collect()
}

criterion_group!(benches, benchmark_skill_matching);
criterion_main!(benches);
```

### Example 11: Memory Scaling Analysis

```rust
use competency_api::profiling::profile_memory_usage;

fn analyze_memory_scaling() {
    let sizes = vec![10, 25, 50, 100, 200, 500];
    let mut results = Vec::new();
    
    println!("Memory Scaling Analysis:");
    println!("Size\tMemory(MB)\tMB/Skill\tGrowth Rate");
    
    for (i, &size) in sizes.iter().enumerate() {
        let skills = create_test_skills(size);
        
        let (_, before, after) = profile_memory_usage(&format!("scale_{}", size), || {
            let mut matcher = SkillMatcher::new().unwrap();
            // Simulate processing
            let mut embedder = SkillEmbedder::new().unwrap();
            embedder.embed_skills(&skills).unwrap()
        });
        
        let memory_used = after.peak_mb - before.peak_mb;
        let memory_per_skill = memory_used as f64 / size as f64;
        
        let growth_rate = if i > 0 {
            let prev_memory = results[i-1].1;
            let prev_size = sizes[i-1];
            let size_ratio = size as f64 / prev_size as f64;
            let memory_ratio = memory_used as f64 / prev_memory as f64;
            memory_ratio / size_ratio
        } else {
            1.0
        };
        
        results.push((size, memory_used, memory_per_skill, growth_rate));
        
        println!("{}\t{}\t\t{:.2}\t\t{:.2}x", 
                 size, memory_used, memory_per_skill, growth_rate);
    }
    
    // Analyze scaling pattern
    let linear_threshold = 1.1; // Within 10% of linear scaling
    let scaling_pattern = if results.iter().skip(1).all(|(_, _, _, growth)| *growth < linear_threshold) {
        "Linear (O(n))"
    } else if results.iter().skip(1).all(|(_, _, _, growth)| *growth < 2.2) {
        "Quadratic (O(n²))"
    } else {
        "Exponential or worse"
    };
    
    println!("\nScaling pattern: {}", scaling_pattern);
}
```

## Advanced Analysis

### Example 12: Memory Leak Detection

```rust
use competency_api::profiling::MemoryProfiler;
use std::thread;
use std::time::Duration;

fn detect_memory_leaks() {
    let profiler = MemoryProfiler::new();
    
    println!("Memory Leak Detection Test");
    println!("Initial memory: {}MB", profiler.current_usage_mb());
    
    // Simulate multiple operations
    for iteration in 1..=10 {
        profiler.reset_peak();
        
        // Perform operation that might leak memory
        let _data = create_and_process_skills(100);
        
        // Force garbage collection (if applicable)
        thread::sleep(Duration::from_millis(100));
        
        let current_memory = profiler.current_usage_mb();
        let peak_memory = profiler.peak_usage_mb();
        
        println!("Iteration {}: Current={}MB, Peak={}MB", 
                 iteration, current_memory, peak_memory);
        
        // Check for increasing memory usage (potential leak)
        if iteration > 5 && current_memory > iteration * 2 {
            println!("WARNING: Potential memory leak detected!");
            println!("Memory usage growing faster than expected");
        }
    }
}

fn create_and_process_skills(count: usize) -> Vec<f64> {
    let skills = create_test_skills(count);
    // Simulate processing that should release memory
    skills.iter().map(|s| s.level.to_ratio()).collect()
}
```

### Example 13: Memory Fragmentation Analysis

```rust
use competency_api::profiling::{MemoryProfiler, profile_memory_usage};

fn analyze_memory_fragmentation() {
    let profiler = MemoryProfiler::new();
    
    println!("Memory Fragmentation Analysis");
    
    // Phase 1: Allocate many small objects
    let (small_objects, before1, after1) = profile_memory_usage("small_allocs", || {
        (0..10000).map(|i| vec![i as u8; 100]).collect::<Vec<_>>()
    });
    
    let small_alloc_memory = after1.peak_mb - before1.peak_mb;
    println!("Small allocations: {}MB", small_alloc_memory);
    
    // Phase 2: Free half the objects (simulate fragmentation)
    let (_, before2, after2) = profile_memory_usage("free_half", || {
        small_objects.into_iter().enumerate()
            .filter(|(i, _)| i % 2 == 0)
            .map(|(_, obj)| obj)
            .collect::<Vec<_>>()
    });
    
    let after_free_memory = after2.current_mb - before2.current_mb;
    println!("After freeing half: {}MB", after_free_memory);
    
    // Phase 3: Allocate large object
    let (_, before3, after3) = profile_memory_usage("large_alloc", || {
        vec![0u8; 1024 * 1024] // 1MB
    });
    
    let large_alloc_memory = after3.peak_mb - before3.peak_mb;
    println!("Large allocation: {}MB", large_alloc_memory);
    
    // Analyze fragmentation
    let expected_large_memory = 1; // 1MB
    if large_alloc_memory > expected_large_memory * 2 {
        println!("Possible fragmentation detected!");
        println!("Large allocation used more memory than expected");
    } else {
        println!("No significant fragmentation detected");
    }
}
```

## Real-World Workflows

### Example 14: Production Monitoring Simulation

```rust
use competency_api::profiling::{MemoryProfiler, MemorySnapshot};
use std::time::{Duration, Instant};

struct MemoryMonitor {
    profiler: MemoryProfiler,
    start_time: Instant,
    snapshots: Vec<(Duration, MemorySnapshot)>,
}

impl MemoryMonitor {
    fn new() -> Self {
        Self {
            profiler: MemoryProfiler::new(),
            start_time: Instant::now(),
            snapshots: Vec::new(),
        }
    }
    
    fn take_snapshot(&mut self, label: &str) {
        let elapsed = self.start_time.elapsed();
        let snapshot = MemorySnapshot::take(label);
        self.snapshots.push((elapsed, snapshot));
    }
    
    fn report(&self) {
        println!("Memory Monitoring Report:");
        println!("Time\t\tOperation\t\tCurrent(MB)\tPeak(MB)");
        
        for (duration, snapshot) in &self.snapshots {
            println!("{:.2}s\t\t{}\t\t{}\t\t{}", 
                     duration.as_secs_f64(),
                     snapshot.label,
                     snapshot.current_mb,
                     snapshot.peak_mb);
        }
        
        if let (Some(first), Some(last)) = (self.snapshots.first(), self.snapshots.last()) {
            let total_memory_growth = last.1.current_mb.saturating_sub(first.1.current_mb);
            let total_time = last.0.as_secs_f64() - first.0.as_secs_f64();
            
            println!("\nSummary:");
            println!("Total memory growth: {}MB", total_memory_growth);
            println!("Total time: {:.2}s", total_time);
            if total_time > 0.0 {
                println!("Memory growth rate: {:.2}MB/s", 
                         total_memory_growth as f64 / total_time);
            }
        }
    }
}

fn simulate_production_workflow() {
    let mut monitor = MemoryMonitor::new();
    
    monitor.take_snapshot("startup");
    
    // Simulate initialization
    std::thread::sleep(Duration::from_millis(100));
    monitor.take_snapshot("initialized");
    
    // Simulate processing batches
    for batch in 1..=5 {
        let skills = create_test_skills(50);
        let mut matcher = SkillMatcher::new().unwrap();
        let _result = matcher.calculate_match_score(
            skills.clone(), 
            skills[0..25].to_vec()
        ).unwrap();
        
        monitor.take_snapshot(&format!("batch_{}", batch));
        std::thread::sleep(Duration::from_millis(50));
    }
    
    monitor.take_snapshot("shutdown");
    monitor.report();
}
```

### Example 15: A/B Testing Memory Performance

```rust
use competency_api::profiling::profile_memory_usage;
use std::collections::HashMap;

struct PerformanceTest {
    name: String,
    memory_usage: usize,
    execution_time: std::time::Duration,
}

fn ab_test_implementations() {
    // Test different implementation approaches
    let test_size = 1000;
    let skills = create_test_skills(test_size);
    
    // Implementation A: Standard approach
    let test_a = {
        let start = std::time::Instant::now();
        let (result, before, after) = profile_memory_usage("impl_a", || {
            standard_similarity_calculation(&skills)
        });
        let duration = start.elapsed();
        
        PerformanceTest {
            name: "Standard Implementation".to_string(),
            memory_usage: after.peak_mb - before.peak_mb,
            execution_time: duration,
        }
    };
    
    // Implementation B: Optimized approach
    let test_b = {
        let start = std::time::Instant::now();
        let (result, before, after) = profile_memory_usage("impl_b", || {
            optimized_similarity_calculation(&skills)
        });
        let duration = start.elapsed();
        
        PerformanceTest {
            name: "Optimized Implementation".to_string(),
            memory_usage: after.peak_mb - before.peak_mb,
            execution_time: duration,
        }
    };
    
    // Compare results
    println!("A/B Testing Results:");
    println!("Implementation\t\tMemory(MB)\tTime(ms)");
    println!("{}\t{}\t\t{}", test_a.name, test_a.memory_usage, test_a.execution_time.as_millis());
    println!("{}\t{}\t\t{}", test_b.name, test_b.memory_usage, test_b.execution_time.as_millis());
    
    let memory_improvement = test_a.memory_usage.saturating_sub(test_b.memory_usage);
    let time_improvement = test_a.execution_time.saturating_sub(test_b.execution_time);
    
    println!("\nImprovement:");
    println!("Memory saved: {}MB", memory_improvement);
    println!("Time saved: {}ms", time_improvement.as_millis());
    
    if memory_improvement > 0 || time_improvement > std::time::Duration::from_millis(0) {
        println!("✅ Optimization successful!");
    } else {
        println!("❌ No significant improvement detected");
    }
}

// Mock implementations for testing
fn standard_similarity_calculation(skills: &[Skill]) -> Vec<Vec<f64>> {
    let mut result = Vec::new(); // No capacity hint
    for i in 0..skills.len() {
        let mut row = Vec::new(); // No capacity hint
        for j in 0..skills.len() {
            row.push((i as f64 + j as f64) / (skills.len() as f64));
        }
        result.push(row);
    }
    result
}

fn optimized_similarity_calculation(skills: &[Skill]) -> Vec<Vec<f64>> {
    let mut result = Vec::with_capacity(skills.len()); // Pre-allocated
    for i in 0..skills.len() {
        let mut row = Vec::with_capacity(skills.len()); // Pre-allocated
        for j in 0..skills.len() {
            row.push((i as f64 + j as f64) / (skills.len() as f64));
        }
        result.push(row);
    }
    result
}
```

These examples demonstrate practical usage patterns for memory profiling in the Competency API, from basic measurements to advanced optimization workflows.