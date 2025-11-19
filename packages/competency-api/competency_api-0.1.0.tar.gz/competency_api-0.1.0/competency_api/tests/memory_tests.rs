use competency_api::*;
use std::collections::HashMap;

#[cfg(feature = "memory-profiling")]
use competency_api::profiling::{MemoryProfiler, MemorySnapshot, profile_memory_usage};

fn create_test_skills(n: usize) -> Vec<Skill> {
    (0..n)
        .map(|i| Skill {
            name: format!("Skill_{}", i),
            level: ProficiencyLevel { 
                value: (i % 5) as u32 + 1, 
                max: 5 
            },
        })
        .collect()
}

#[test]
#[cfg(feature = "memory-profiling")]
fn test_baseline_memory_usage() {
    let profiler = MemoryProfiler::new();
    
    // Test different scales
    let test_cases = vec![
        (10, 5),   // Small: 10 candidates, 5 required
        (50, 25),  // Medium: 50 candidates, 25 required  
        (100, 50), // Large: 100 candidates, 50 required
    ];
    
    let mut results = HashMap::new();
    
    for (candidates, required) in test_cases {
        let candidate_skills = create_test_skills(candidates);
        let required_skills = create_test_skills(required);
        
        let (result, before, after) = profile_memory_usage(
            &format!("match_{}_{}", candidates, required),
            || {
                let mut matcher = SkillMatcher::new().unwrap();
                matcher.calculate_match_score(candidate_skills, required_skills)
            }
        );
        
        assert!(result.is_ok());
        
        let memory_used = after.peak_mb.saturating_sub(before.peak_mb);
        results.insert((candidates, required), memory_used);
        
        println!("Memory usage for {} candidates, {} required: {}MB", 
                 candidates, required, memory_used);
    }
    
    // Store baseline results
    println!("\nBaseline Memory Usage:");
    for ((candidates, required), memory_mb) in results {
        println!("  {},{}: {}MB", candidates, required, memory_mb);
    }
}

#[test]
#[cfg(feature = "memory-profiling")]
fn test_embedding_memory_usage() {
    let test_cases = vec![10, 50, 100, 200];
    
    for size in test_cases {
        let skills = create_test_skills(size);
        
        let (result, before, after) = profile_memory_usage(
            &format!("embed_{}", size),
            || {
                let mut embedder = SkillEmbedder::new().unwrap();
                embedder.embed_skills(&skills)
            }
        );
        
        assert!(result.is_ok());
        
        let memory_used = after.peak_mb.saturating_sub(before.peak_mb);
        println!("Embedding {} skills: {}MB", size, memory_used);
    }
}

#[test]
#[cfg(feature = "memory-profiling")]
fn test_similarity_calculation_memory() {
    let mut embedder = SkillEmbedder::new().unwrap();
    
    let test_cases = vec![
        (10, 5),
        (50, 25),
        (100, 50),
    ];
    
    for (candidates, required) in test_cases {
        let candidate_skills = create_test_skills(candidates);
        let required_skills = create_test_skills(required);
        
        let candidate_skills_dist = embedder.embed_skills(&candidate_skills).unwrap();
        let required_skills_dist = embedder.embed_skills(&required_skills).unwrap();
        
        let (result, before, after) = profile_memory_usage(
            &format!("similarity_{}_{}", candidates, required),
            || {
                SkillSimilarityCalculator::calculate_similarities(
                    &candidate_skills_dist,
                    &required_skills_dist,
                )
            }
        );
        
        let memory_used = after.peak_mb.saturating_sub(before.peak_mb);
        println!("Similarity calculation for {}x{}: {}MB", candidates, required, memory_used);
        
        // Verify results
        assert_eq!(result.len(), candidates);
        assert_eq!(result[0].len(), required);
    }
}

#[test]
#[cfg(feature = "memory-profiling")]
fn test_memory_growth_patterns() {
    let profiler = MemoryProfiler::new();
    
    // Test memory growth as we scale up
    let sizes = vec![10, 20, 50, 100];
    let mut previous_usage = 0;
    
    for size in sizes {
        let candidate_skills = create_test_skills(size);
        let required_skills = create_test_skills(size / 2);
        
        profiler.reset_peak();
        let before = MemorySnapshot::take("before");
        
        let mut matcher = SkillMatcher::new().unwrap();
        let _result = matcher.calculate_match_score(candidate_skills, required_skills).unwrap();
        
        let after = MemorySnapshot::take("after");
        let current_usage = after.peak_mb.saturating_sub(before.peak_mb);
        
        println!("Size {}: {}MB (growth: {}MB)", 
                 size, current_usage, current_usage.saturating_sub(previous_usage));
        
        previous_usage = current_usage;
    }
}

#[test]
fn test_memory_without_profiling() {
    // This test can run without the memory-profiling feature
    // It performs basic functionality tests to ensure the code works
    
    let candidate_skills = create_test_skills(10);
    let required_skills = create_test_skills(5);
    
    let mut matcher = SkillMatcher::new().unwrap();
    let result = matcher.calculate_match_score(candidate_skills, required_skills);
    
    assert!(result.is_ok());
    let match_result = result.unwrap();
    assert_eq!(match_result.skill_scores.len(), 5);
    assert!(match_result.overall_score >= 0.0);
    assert!(match_result.overall_score <= 1.0);
}