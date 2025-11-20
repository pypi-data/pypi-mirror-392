use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use competency_api::*;
use std::time::Duration;
use std::collections::HashSet;

/// Create a pool of unique skill names
fn create_skill_pool(size: usize) -> Vec<String> {
    (0..size)
        .map(|i| format!("Skill_{}", i))
        .collect()
}

/// Create skills with a specific overlap percentage
/// overlap_pct: 0.0 = no overlap, 1.0 = complete overlap
fn create_skills_with_overlap(
    candidate_count: usize,
    required_count: usize,
    overlap_pct: f64,
) -> (Vec<Skill>, Vec<Skill>) {
    let pool_size = ((candidate_count + required_count) as f64 * (1.0 - overlap_pct * 0.5)) as usize;
    let pool = create_skill_pool(pool_size.max(candidate_count + required_count));

    let overlap_count = (required_count as f64 * overlap_pct) as usize;
    let unique_required = required_count - overlap_count;

    // Create candidate skills (first N from pool)
    let candidate_skills: Vec<Skill> = (0..candidate_count)
        .map(|i| Skill {
            name: pool[i % pool.len()].clone(),
            level: ProficiencyLevel {
                value: (i % 5) as u32 + 1,
                max: 5
            },
        })
        .collect();

    // Create required skills with controlled overlap
    let mut required_skills = Vec::with_capacity(required_count);

    // Add overlapping skills (from candidate pool)
    for i in 0..overlap_count {
        required_skills.push(Skill {
            name: pool[i % candidate_count].clone(),
            level: ProficiencyLevel {
                value: ((i + 2) % 5) as u32 + 1,
                max: 5
            },
        });
    }

    // Add unique required skills (from end of pool)
    for i in 0..unique_required {
        let idx = pool.len() - unique_required + i;
        required_skills.push(Skill {
            name: pool[idx].clone(),
            level: ProficiencyLevel {
                value: ((i + 3) % 5) as u32 + 1,
                max: 5
            },
        });
    }

    (candidate_skills, required_skills)
}

/// Count actual unique skills in both lists combined
fn count_unique_skills(candidates: &[Skill], required: &[Skill]) -> usize {
    let mut unique_names = HashSet::new();
    for skill in candidates {
        unique_names.insert(&skill.name);
    }
    for skill in required {
        unique_names.insert(&skill.name);
    }
    unique_names.len()
}

/// Benchmark using standard batch embedding (processes all skills twice)
fn bench_batch_separate(c: &mut Criterion) {
    let mut group = c.benchmark_group("batch_separate");
    group.measurement_time(Duration::from_secs(15));

    for overlap_pct in [0.0, 0.25, 0.5, 0.75, 0.9].iter() {
        let (candidate_skills, required_skills) =
            create_skills_with_overlap(50, 25, *overlap_pct);
        let unique_count = count_unique_skills(&candidate_skills, &required_skills);

        group.bench_with_input(
            BenchmarkId::new(
                "50_candidates_25_required",
                format!("{}%_overlap_{}_unique", (overlap_pct * 100.0) as u32, unique_count)
            ),
            overlap_pct,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    // Embed candidates and required separately (potential duplicate work)
                    let candidates = embedder.embed_skills(black_box(&candidate_skills)).unwrap();
                    let required = embedder.embed_skills(black_box(&required_skills)).unwrap();
                    black_box((candidates, required));
                });
            },
        );
    }

    group.finish();
}

/// Benchmark using unique embedding approach (deduplicates first)
fn bench_unique_combined(c: &mut Criterion) {
    let mut group = c.benchmark_group("unique_combined");
    group.measurement_time(Duration::from_secs(15));

    for overlap_pct in [0.0, 0.25, 0.5, 0.75, 0.9].iter() {
        let (candidate_skills, required_skills) =
            create_skills_with_overlap(50, 25, *overlap_pct);
        let unique_count = count_unique_skills(&candidate_skills, &required_skills);

        group.bench_with_input(
            BenchmarkId::new(
                "50_candidates_25_required",
                format!("{}%_overlap_{}_unique", (overlap_pct * 100.0) as u32, unique_count)
            ),
            overlap_pct,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    // Collect all unique skills
                    let mut all_skills: Vec<&Skill> = Vec::new();
                    let mut seen = HashSet::new();

                    for skill in &candidate_skills {
                        if seen.insert(&skill.name) {
                            all_skills.push(skill);
                        }
                    }
                    for skill in &required_skills {
                        if seen.insert(&skill.name) {
                            all_skills.push(skill);
                        }
                    }

                    // Embed unique skills once (returns HashMap)
                    let embedding_map = embedder.embed_unique_skills(black_box(&all_skills)).unwrap();
                    black_box(embedding_map);
                });
            },
        );
    }

    group.finish();
}

/// Direct comparison of both approaches at different overlap levels
fn bench_overlap_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("overlap_comparison");
    group.measurement_time(Duration::from_secs(20));

    for overlap_pct in [0.0, 0.5, 0.9].iter() {
        let (candidate_skills, required_skills) =
            create_skills_with_overlap(50, 25, *overlap_pct);
        let unique_count = count_unique_skills(&candidate_skills, &required_skills);

        // Batch approach
        group.bench_with_input(
            BenchmarkId::new(
                "batch",
                format!("{}%_overlap_{}_unique", (overlap_pct * 100.0) as u32, unique_count)
            ),
            overlap_pct,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let candidates = embedder.embed_skills(black_box(&candidate_skills)).unwrap();
                    let required = embedder.embed_skills(black_box(&required_skills)).unwrap();
                    black_box((candidates, required));
                });
            },
        );

        // Unique approach
        group.bench_with_input(
            BenchmarkId::new(
                "unique",
                format!("{}%_overlap_{}_unique", (overlap_pct * 100.0) as u32, unique_count)
            ),
            overlap_pct,
            |b, _| {
                let mut embedder = SkillEmbedder::new().unwrap();
                b.iter(|| {
                    let mut all_skills: Vec<&Skill> = Vec::new();
                    let mut seen = HashSet::new();

                    for skill in &candidate_skills {
                        if seen.insert(&skill.name) {
                            all_skills.push(skill);
                        }
                    }
                    for skill in &required_skills {
                        if seen.insert(&skill.name) {
                            all_skills.push(skill);
                        }
                    }

                    let embedding_map = embedder.embed_unique_skills(black_box(&all_skills)).unwrap();
                    black_box(embedding_map);
                });
            },
        );
    }

    group.finish();
}

/// Test with larger datasets to see scaling behavior
fn bench_large_overlap(c: &mut Criterion) {
    let mut group = c.benchmark_group("large_overlap");
    group.measurement_time(Duration::from_secs(20));

    for size in [100, 200].iter() {
        for overlap_pct in [0.0, 0.5, 0.9].iter() {
            let (candidate_skills, required_skills) =
                create_skills_with_overlap(*size, size / 2, *overlap_pct);
            let unique_count = count_unique_skills(&candidate_skills, &required_skills);

            // Batch approach
            group.bench_with_input(
                BenchmarkId::new(
                    "batch",
                    format!("{}_skills_{}%_overlap_{}_unique", size, (overlap_pct * 100.0) as u32, unique_count)
                ),
                &(size, overlap_pct),
                |b, _| {
                    let mut embedder = SkillEmbedder::new().unwrap();
                    b.iter(|| {
                        let candidates = embedder.embed_skills(black_box(&candidate_skills)).unwrap();
                        let required = embedder.embed_skills(black_box(&required_skills)).unwrap();
                        black_box((candidates, required));
                    });
                },
            );

            // Unique approach
            group.bench_with_input(
                BenchmarkId::new(
                    "unique",
                    format!("{}_skills_{}%_overlap_{}_unique", size, (overlap_pct * 100.0) as u32, unique_count)
                ),
                &(size, overlap_pct),
                |b, _| {
                    let mut embedder = SkillEmbedder::new().unwrap();
                    b.iter(|| {
                        let mut all_skills: Vec<&Skill> = Vec::new();
                        let mut seen = HashSet::new();

                        for skill in &candidate_skills {
                            if seen.insert(&skill.name) {
                                all_skills.push(skill);
                            }
                        }
                        for skill in &required_skills {
                            if seen.insert(&skill.name) {
                                all_skills.push(skill);
                            }
                        }

                        let embedding_map = embedder.embed_unique_skills(black_box(&all_skills)).unwrap();
                        black_box(embedding_map);
                    });
                },
            );
        }
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_batch_separate,
    bench_unique_combined,
    bench_overlap_comparison,
    bench_large_overlap
);
criterion_main!(benches);
