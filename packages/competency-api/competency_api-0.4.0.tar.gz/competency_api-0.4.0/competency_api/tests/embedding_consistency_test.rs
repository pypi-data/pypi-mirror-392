use competency_api::*;
use approx::assert_relative_eq;
use statrs::statistics::Distribution;

#[test]
fn test_batch_vs_single_embedding_consistency() {
    // Create test skills
    let skills = vec![
        Skill {
            name: "Python Programming".to_string(),
            level: ProficiencyLevel { value: 4, max: 5 }
        },
        Skill {
            name: "Data Analysis".to_string(),
            level: ProficiencyLevel { value: 3, max: 5 }
        },
        Skill {
            name: "Machine Learning".to_string(),
            level: ProficiencyLevel { value: 5, max: 5 }
        },
        Skill {
            name: "SQL".to_string(),
            level: ProficiencyLevel { value: 2, max: 5 }
        },
        Skill {
            name: "JavaScript".to_string(),
            level: ProficiencyLevel { value: 3, max: 5 }
        },
    ];

    // Batch embedding
    let mut embedder_batch = SkillEmbedder::new().unwrap();
    let batch_results = embedder_batch.embed_skills(&skills).unwrap();

    // Single embedding
    let mut embedder_single = SkillEmbedder::new().unwrap();
    let mut single_results = Vec::with_capacity(skills.len());
    for skill in &skills {
        let embedded = embedder_single.embed_skills(&[skill.clone()]).unwrap();
        single_results.extend(embedded);
    }

    // Verify we got the same number of results
    assert_eq!(batch_results.len(), single_results.len(),
        "Batch and single embedding should produce same number of results");

    // Verify each embedding is identical
    for (i, (batch_skill, single_skill)) in batch_results.iter().zip(single_results.iter()).enumerate() {
        // Check names match
        assert_eq!(batch_skill.name, single_skill.name,
            "Skill {} name mismatch", i);

        // Check domains match
        assert_eq!(batch_skill.domain, single_skill.domain,
            "Skill {} domain mismatch", i);

        // Check embedding dimensions match
        assert_eq!(batch_skill.embedding.len(), single_skill.embedding.len(),
            "Skill {} embedding dimension mismatch", i);

        // Check each embedding value is identical (or extremely close due to floating point)
        for (_j, (batch_val, single_val)) in batch_skill.embedding.iter()
            .zip(single_skill.embedding.iter())
            .enumerate()
        {
            assert_relative_eq!(
                batch_val,
                single_val,
                epsilon = 1e-6
            );
        }

        // Check distribution parameters match
        // Beta distributions should be identical since they're based on the same level
        let batch_mean = batch_skill.distribution.mean().unwrap();
        let single_mean = single_skill.distribution.mean().unwrap();
        assert_relative_eq!(
            batch_mean,
            single_mean,
            epsilon = 1e-10
        );
    }

    println!("✓ Batch and single embedding produce identical results!");
}

#[test]
fn test_unique_vs_batch_embedding_consistency() {
    // Create test skills with some duplicates
    let skills = vec![
        Skill {
            name: "Python Programming".to_string(),
            level: ProficiencyLevel { value: 4, max: 5 }
        },
        Skill {
            name: "Data Analysis".to_string(),
            level: ProficiencyLevel { value: 3, max: 5 }
        },
        Skill {
            name: "Python Programming".to_string(), // Duplicate with different level
            level: ProficiencyLevel { value: 5, max: 5 }
        },
    ];

    // Batch embedding
    let mut embedder_batch = SkillEmbedder::new().unwrap();
    let batch_results = embedder_batch.embed_skills(&skills).unwrap();

    // Unique embedding
    let unique_skills: Vec<&Skill> = skills.iter().collect();
    let mut embedder_unique = SkillEmbedder::new().unwrap();
    let unique_map = embedder_unique.embed_unique_skills(&unique_skills).unwrap();

    // Verify the unique map has the right number of unique skills (2, not 3)
    assert_eq!(unique_map.len(), 2,
        "Should have 2 unique skill names despite 3 total skills");

    // Verify embeddings from batch match those in the unique map
    for (i, batch_skill) in batch_results.iter().enumerate() {
        let (unique_embedding, unique_domain) = unique_map.get(&batch_skill.name)
            .expect(&format!("Skill {} '{}' not found in unique map", i, batch_skill.name));

        // Check domain matches
        assert_eq!(&batch_skill.domain, unique_domain,
            "Skill {} domain mismatch", i);

        // Check embedding dimensions match
        assert_eq!(batch_skill.embedding.len(), unique_embedding.len(),
            "Skill {} embedding dimension mismatch", i);

        // Check each embedding value is identical
        for (_j, (batch_val, unique_val)) in batch_skill.embedding.iter()
            .zip(unique_embedding.iter())
            .enumerate()
        {
            assert_relative_eq!(
                batch_val,
                unique_val,
                epsilon = 1e-6
            );
        }
    }

    println!("✓ Unique and batch embedding produce consistent embeddings!");
}

#[test]
fn test_embedding_determinism() {
    // Test that running the same embedding twice gives identical results
    let skills = vec![
        Skill {
            name: "Rust Programming".to_string(),
            level: ProficiencyLevel { value: 4, max: 5 }
        },
        Skill {
            name: "System Design".to_string(),
            level: ProficiencyLevel { value: 3, max: 5 }
        },
    ];

    // First run
    let mut embedder1 = SkillEmbedder::new().unwrap();
    let results1 = embedder1.embed_skills(&skills).unwrap();

    // Second run
    let mut embedder2 = SkillEmbedder::new().unwrap();
    let results2 = embedder2.embed_skills(&skills).unwrap();

    // Verify results are identical
    assert_eq!(results1.len(), results2.len());

    for (skill1, skill2) in results1.iter().zip(results2.iter()) {
        assert_eq!(skill1.name, skill2.name);
        assert_eq!(skill1.embedding.len(), skill2.embedding.len());

        for (val1, val2) in skill1.embedding.iter().zip(skill2.embedding.iter()) {
            assert_relative_eq!(
                val1,
                val2,
                epsilon = 1e-10
            );
        }
    }

    println!("✓ Embedding is deterministic!");
}
