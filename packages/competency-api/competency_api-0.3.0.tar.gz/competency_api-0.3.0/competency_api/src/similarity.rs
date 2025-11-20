use std::collections::HashMap;
use crate::types::SkillWithDistribution;
use simsimd::SpatialSimilarity;
use crate::traits::SimilarityCalculator as SimilarityCalculatorTrait;
use rayon::prelude::*;

pub struct SkillSimilarityCalculator;

impl SkillSimilarityCalculator {
    pub fn calculate_similarities(
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution]
    ) -> Vec<Vec<f64>> {
        let num_candidates = candidate_skills.len();
        let num_required = required_skills.len();
        
        // Use parallel processing for large datasets
        if num_candidates * num_required > 1000 {
            // Parallel implementation for large datasets
            candidate_skills.par_iter().enumerate().map(|(_i, candidate_skill)| {
                let mut row = Vec::with_capacity(num_required);
                for required_skill in required_skills.iter() {
                    let distance = f32::cosine(
                        &candidate_skill.embedding,
                        &required_skill.embedding
                    ).unwrap_or(1.0) as f64;
                    row.push(1.0 - distance);
                }
                row
            }).collect()
        } else {
            // Sequential implementation for smaller datasets (avoid parallelization overhead)
            let mut similarities = Vec::with_capacity(num_candidates);
            
            for candidate_skill in candidate_skills.iter() {
                let mut row = Vec::with_capacity(num_required);
                for required_skill in required_skills.iter() {
                    let distance = f32::cosine(
                        &candidate_skill.embedding,
                        &required_skill.embedding
                    ).unwrap_or(1.0) as f64;
                    row.push(1.0 - distance);
                }
                similarities.push(row);
            }
            
            similarities
        }
    }

    pub fn distances_to_hashmap(
        distances: &[Vec<f32>],
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution]
    ) -> HashMap<String, HashMap<String, f32>> {
        // Pre-allocate HashMap with capacity hints
        let mut result: HashMap<String, HashMap<String, f32>> = HashMap::with_capacity(required_skills.len());

        for (req_idx, req_skill) in required_skills.iter().enumerate() {
            let mut candidate_distances = HashMap::with_capacity(candidate_skills.len());
            
            for (cand_idx, cand_skill) in candidate_skills.iter().enumerate() {
                candidate_distances.insert(
                    cand_skill.name.clone(),
                    distances[cand_idx][req_idx]
                );
            }
            
            result.insert(req_skill.name.clone(), candidate_distances);
        }

        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::ProficiencyLevel;
    use statrs::distribution::Beta;

    #[test]
    fn test_cosine_similarity_behavior() {
        // Test that f32::cosine returns similarity, not distance
        
        // Identical vectors should return ~0.0 distance, ~1.0 similarity
        let vec1 = vec![1.0_f32, 2.0, 3.0];
        let vec2 = vec![1.0_f32, 2.0, 3.0];
        let distance = f32::cosine(&vec1, &vec2).unwrap();
        let similarity = 1.0 - distance as f64;
        println!("Identical vectors cosine distance: {}, similarity: {}", distance, similarity);
        assert!(similarity > 0.999, "Identical vectors should have cosine similarity ~1.0");
        
        // Orthogonal vectors should return ~1.0 distance, ~0.0 similarity
        let vec3 = vec![1.0_f32, 0.0, 0.0];
        let vec4 = vec![0.0_f32, 1.0, 0.0];
        let distance2 = f32::cosine(&vec3, &vec4).unwrap();
        let similarity2 = 1.0 - distance2 as f64;
        println!("Orthogonal vectors cosine distance: {}, similarity: {}", distance2, similarity2);
        assert!(similarity2.abs() < 0.01, "Orthogonal vectors should have cosine similarity ~0.0");
        
        // Opposite vectors should return ~2.0 distance, ~-1.0 similarity
        let vec5 = vec![1.0_f32, 2.0, 3.0];
        let vec6 = vec![-1.0_f32, -2.0, -3.0];
        let distance3 = f32::cosine(&vec5, &vec6).unwrap();
        let similarity3 = 1.0 - distance3 as f64;
        println!("Opposite vectors cosine distance: {}, similarity: {}", distance3, similarity3);
        assert!((similarity3 - (-1.0)).abs() < 0.01, "Opposite vectors should have cosine similarity ~-1.0");
    }

    #[test]
    fn test_distances_to_hashmap() {
        use crate::domain::SkillDomain;

        // Create test skills
        let create_test_skill = |name: &str| SkillWithDistribution {
            name: name.to_string(),
            level: ProficiencyLevel { value: 1, max: 5 },
            distribution: Beta::new(2.0, 2.0).unwrap(),
            embedding: vec![1.0, 0.0],
            domain: SkillDomain::General,
        };

        let candidate_skills = vec![
            create_test_skill("Python"),
            create_test_skill("Java"),
        ];

        let required_skills = vec![
            create_test_skill("Programming"),
            create_test_skill("Coding"),
        ];

        let distances = vec![
            vec![0.9, 0.8],
            vec![0.7, 0.6],
        ];

        let result = SkillSimilarityCalculator::distances_to_hashmap(
            &distances,
            &candidate_skills,
            &required_skills
        );

        // Verify structure and values
        assert_eq!(result["Programming"]["Python"], 0.9);
        assert_eq!(result["Programming"]["Java"], 0.7);
        assert_eq!(result["Coding"]["Python"], 0.8);
        assert_eq!(result["Coding"]["Java"], 0.6);
    }
}

impl SimilarityCalculatorTrait for SkillSimilarityCalculator {
    fn calculate_similarities(
        &self,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
    ) -> Vec<Vec<f64>> {
        Self::calculate_similarities(candidate_skills, required_skills)
    }
}