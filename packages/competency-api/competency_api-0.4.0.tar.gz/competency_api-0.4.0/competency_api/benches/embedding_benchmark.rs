use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
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

/// Benchmark batch embedding using the existing embed_skills method
fn bench_batch_embedding(c: &mut Criterion) {
    let mut group = c.benchmark_group("batch_embedding");
    group.measurement_time(Duration::from_secs(15));

    for size in [10, 25, 50, 100, 200].iter() {
        let skills = create_test_skills(*size);

        group.bench_with_input(
            BenchmarkId::new("embed_skills_batch", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let result = embedder.embed_skills(black_box(&skills));
                    black_box(result.unwrap());
                });
            },
        );
    }

    group.finish();
}

/// Benchmark single embedding by calling embed on individual skills
fn bench_single_embedding(c: &mut Criterion) {
    let mut group = c.benchmark_group("single_embedding");
    group.measurement_time(Duration::from_secs(15));

    for size in [10, 25, 50, 100, 200].iter() {
        let skills = create_test_skills(*size);

        group.bench_with_input(
            BenchmarkId::new("embed_skills_single", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let mut result = Vec::with_capacity(skills.len());
                    for skill in black_box(&skills) {
                        let embedded = embedder.embed_skills(&[skill.clone()]).unwrap();
                        result.extend(embedded);
                    }
                    black_box(result);
                });
            },
        );
    }

    group.finish();
}

/// Benchmark the new embed_unique_skills method
fn bench_unique_embedding(c: &mut Criterion) {
    let mut group = c.benchmark_group("unique_embedding");
    group.measurement_time(Duration::from_secs(15));

    for size in [10, 25, 50, 100, 200].iter() {
        let skills = create_test_skills(*size);
        let skill_refs: Vec<&Skill> = skills.iter().collect();

        group.bench_with_input(
            BenchmarkId::new("embed_unique_skills", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let result = embedder.embed_unique_skills(black_box(&skill_refs));
                    black_box(result.unwrap());
                });
            },
        );
    }

    group.finish();
}

/// Comparison benchmark showing all three approaches side-by-side
fn bench_embedding_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("embedding_comparison");
    group.measurement_time(Duration::from_secs(20));

    for size in [10, 50, 100].iter() {
        let skills = create_test_skills(*size);
        let skill_refs: Vec<&Skill> = skills.iter().collect();

        // Batch embedding
        group.bench_with_input(
            BenchmarkId::new("batch", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let result = embedder.embed_skills(black_box(&skills));
                    black_box(result.unwrap());
                });
            },
        );

        // Single embedding
        group.bench_with_input(
            BenchmarkId::new("single", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let mut result = Vec::with_capacity(skills.len());
                    for skill in black_box(&skills) {
                        let embedded = embedder.embed_skills(&[skill.clone()]).unwrap();
                        result.extend(embedded);
                    }
                    black_box(result);
                });
            },
        );

        // Unique embedding
        group.bench_with_input(
            BenchmarkId::new("unique", size),
            size,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let result = embedder.embed_unique_skills(black_box(&skill_refs));
                    black_box(result.unwrap());
                });
            },
        );
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_batch_embedding,
    bench_single_embedding,
    bench_unique_embedding,
    bench_embedding_comparison
);
criterion_main!(benches);
