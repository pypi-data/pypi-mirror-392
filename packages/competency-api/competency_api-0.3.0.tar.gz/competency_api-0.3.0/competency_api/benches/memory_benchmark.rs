use criterion::{black_box, criterion_group, criterion_main, Criterion};
use competency_api::*;
use std::time::Duration;

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

fn bench_skill_matching_memory(c: &mut Criterion) {
    let mut group = c.benchmark_group("memory_usage");
    group.measurement_time(Duration::from_secs(10));
    
    // Test with different sizes to understand scaling
    for size in [10, 50, 100, 200].iter() {
        let candidate_skills = create_test_skills(*size);
        let required_skills = create_test_skills(*size / 2);
        
        group.bench_function(
            format!("match_skills_{}_candidates_{}_required", size, size / 2),
            |b| {
                b.iter(|| {
                    let mut matcher = SkillMatcher::new().unwrap();
                    let result = matcher.calculate_match_score(
                        black_box(candidate_skills.clone()),
                        black_box(required_skills.clone()),
                    );
                    black_box(result.unwrap());
                });
            },
        );
    }
    
    group.finish();
}

fn bench_embedding_memory(c: &mut Criterion) {
    let mut group = c.benchmark_group("embedding_memory");
    group.measurement_time(Duration::from_secs(10));
    
    for size in [10, 50, 100].iter() {
        let skills = create_test_skills(*size);
        
        group.bench_function(
            format!("embed_skills_{}", size),
            |b| {
                b.iter(|| {
                    let mut embedder = SkillEmbedder::new().unwrap();
                    let result = embedder.embed_skills(black_box(&skills));
                    black_box(result.unwrap());
                });
            },
        );
    }
    
    group.finish();
}

fn bench_similarity_calculation_memory(c: &mut Criterion) {
    let mut group = c.benchmark_group("similarity_memory");
    group.measurement_time(Duration::from_secs(10));
    
    for size in [10, 50, 100].iter() {
        let mut embedder = SkillEmbedder::new().unwrap();
        let candidate_skills = create_test_skills(*size);
        let required_skills = create_test_skills(*size / 2);
        
        let candidate_skills_dist = embedder.embed_skills(&candidate_skills).unwrap();
        let required_skills_dist = embedder.embed_skills(&required_skills).unwrap();
        
        group.bench_function(
            format!("calculate_similarities_{}x{}", size, size / 2),
            |b| {
                b.iter(|| {
                    let similarities = SkillSimilarityCalculator::calculate_similarities(
                        black_box(&candidate_skills_dist),
                        black_box(&required_skills_dist),
                    );
                    black_box(similarities);
                });
            },
        );
    }
    
    group.finish();
}

criterion_group!(
    benches,
    bench_skill_matching_memory,
    bench_embedding_memory,
    bench_similarity_calculation_memory
);
criterion_main!(benches);