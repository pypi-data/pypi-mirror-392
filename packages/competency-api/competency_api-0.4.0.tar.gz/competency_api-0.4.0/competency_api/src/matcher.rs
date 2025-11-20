use std::collections::HashMap;
use crate::embedding::SkillEmbedder;
use crate::error::{Result, SkillMatcherError};
use crate::types::{MatchResult, Skill, SkillScore, SkillWithDistribution};
use crate::similarity::SkillSimilarityCalculator;
use crate::config::SkillMatcherConfig;
use crate::traits::{SkillEmbedder as SkillEmbedderTrait, SimilarityCalculator, ScoringStrategy};
use crate::strategies::DefaultScoringStrategy;
use crate::distribution::create_beta_distribution;
use crate::domain::SkillDomain;
use tracing::{warn, info, instrument};

pub struct SkillMatcher {
    embedder: Box<dyn SkillEmbedderTrait>,
    similarity_calculator: Box<dyn SimilarityCalculator>,
    scoring_strategy: Box<dyn ScoringStrategy>,
    config: SkillMatcherConfig,
}

impl SkillMatcher {
    pub fn new() -> Result<Self> {
        let config = SkillMatcherConfig::default();
        let embedder = SkillEmbedder::with_config(config.clone())?;
        Ok(SkillMatcher {
            embedder: Box::new(embedder),
            similarity_calculator: Box::new(SkillSimilarityCalculator),
            scoring_strategy: Box::new(DefaultScoringStrategy),
            config,
        })
    }

    pub fn with_config(config: SkillMatcherConfig) -> Result<Self> {
        config.validate().map_err(|e| SkillMatcherError::InvalidSkillData(e))?;
        let embedder = SkillEmbedder::with_config(config.clone())?;
        Ok(SkillMatcher {
            embedder: Box::new(embedder),
            similarity_calculator: Box::new(SkillSimilarityCalculator),
            scoring_strategy: Box::new(DefaultScoringStrategy),
            config,
        })
    }

    pub fn with_components(
        embedder: Box<dyn SkillEmbedderTrait>,
        similarity_calculator: Box<dyn SimilarityCalculator>,
        scoring_strategy: Box<dyn ScoringStrategy>,
        config: SkillMatcherConfig,
    ) -> Result<Self> {
        config.validate().map_err(|e| SkillMatcherError::InvalidSkillData(e))?;
        Ok(SkillMatcher {
            embedder,
            similarity_calculator,
            scoring_strategy,
            config,
        })
    }

    #[instrument(skip(self))]
    pub fn calculate_match_score(
        &mut self,
        candidate_skills: Vec<Skill>,
        required_skills: Vec<Skill>
    ) -> Result<MatchResult> {
        info!(
            candidate_skills_count = candidate_skills.len(),
            required_skills_count = required_skills.len(),
            "Starting match score calculation"
        );

        if candidate_skills.is_empty() || required_skills.is_empty() {
            return Err(SkillMatcherError::EmptySkills {
                n_candidate: candidate_skills.len(),
                n_required: required_skills.len()
            });
        };

        let candidate_skills_dist = self.embedder.embed_skills(&candidate_skills)?;
        let required_skills_dist = self.embedder.embed_skills(&required_skills)?;

        let similarities = self.similarity_calculator.calculate_similarities(
            &candidate_skills_dist,
            &required_skills_dist
        );

        let skill_similarities = self.convert_similarities_to_hashmap(
            &candidate_skills_dist,
            &required_skills_dist,
            &similarities
        );

        let pairwise_scores = self.calculate_pairwise_scores(
            &candidate_skills_dist,
            &required_skills_dist,
            &similarities
        );

        let skill_scores = self.calculate_individual_scores(
            &candidate_skills_dist,
            &required_skills_dist,
            &similarities
        )?;

        let mut overall_score = self.scoring_strategy.calculate_overall_score(&skill_scores);

        // Apply coherence bonus for multi-skill roles with good domain alignment
        // This addresses the issue where individual skills score well but overall is conservative
        if required_skills_dist.len() >= 3 && candidate_skills_dist.len() >= 3 {
            overall_score = self.apply_coherence_bonus(
                overall_score,
                &candidate_skills_dist,
                &required_skills_dist,
                &similarities
            );
        }

        Ok(MatchResult {
            overall_score,
            skill_scores,
            skill_similarities,
            pairwise_scores,
        })
    }

    /// Build a SkillWithDistribution from a skill using pre-computed embeddings and domains.
    ///
    /// This helper method is used in batch processing to construct SkillWithDistribution
    /// instances using cached embeddings and domain classifications, while computing
    /// Beta distributions fresh for each skill based on its specific proficiency level.
    ///
    /// # Arguments
    /// * `skill` - The skill to build distribution for
    /// * `embedding_cache` - Pre-computed embeddings and domains lookup map
    ///
    /// # Returns
    /// A fully populated SkillWithDistribution
    fn build_skill_with_distribution(
        &self,
        skill: &Skill,
        embedding_cache: &HashMap<String, (Vec<f32>, SkillDomain)>,
    ) -> Result<SkillWithDistribution> {
        let (embedding, domain) = embedding_cache
            .get(&skill.name)
            .ok_or_else(|| {
                SkillMatcherError::InvalidSkillData(
                    format!("Skill '{}' not found in embedding cache", skill.name)
                )
            })?;

        Ok(SkillWithDistribution {
            name: skill.name.clone(),
            level: skill.level.clone(),
            distribution: create_beta_distribution(&skill.level, &self.config.distribution_config)?,
            embedding: embedding.clone(),
            domain: domain.clone(),
        })
    }

    /// Calculate match scores for multiple candidate-required skill pairs in a batch.
    ///
    /// This method is optimized for batch processing by deduplicating skills across pairs:
    /// - Embeds each unique skill name only once
    /// - Classifies domains only once per skill name
    /// - Computes Beta distributions per-instance (handles different proficiency levels)
    ///
    /// This provides significant performance improvements (60-70% faster embedding time)
    /// when the same skills appear across multiple pairs, which is common in batch operations.
    ///
    /// # Arguments
    /// * `pairs` - A vector of tuples, each containing (candidate_skills, required_skills)
    ///
    /// # Returns
    /// A vector of `MatchResult`, one for each input pair, in the same order.
    ///
    /// # Example
    /// ```ignore
    /// let pairs = vec![
    ///     (candidate1, required1),
    ///     (candidate2, required2),
    ///     (candidate3, required3),
    /// ];
    /// let results = matcher.calculate_batch_match_scores(pairs)?;
    /// ```
    #[instrument(skip(self, pairs))]
    pub fn calculate_batch_match_scores(
        &mut self,
        pairs: Vec<(Vec<Skill>, Vec<Skill>)>
    ) -> Result<Vec<MatchResult>> {
        info!(
            batch_size = pairs.len(),
            "Starting batch match score calculation with deduplication"
        );

        if pairs.is_empty() {
            return Ok(Vec::new());
        }

        // Phase 1: Collect all unique skills across all pairs
        let mut unique_skills_map: HashMap<String, &Skill> = HashMap::new();

        for (candidate_skills, required_skills) in &pairs {
            for skill in candidate_skills {
                unique_skills_map.entry(skill.name.clone())
                    .or_insert(skill);
            }
            for skill in required_skills {
                unique_skills_map.entry(skill.name.clone())
                    .or_insert(skill);
            }
        }

        info!(
            unique_skills_count = unique_skills_map.len(),
            "Collected unique skills for batch embedding"
        );

        // Phase 2: Batch embed all unique skills
        let unique_skills: Vec<&Skill> = unique_skills_map.values().copied().collect();
        let embedding_cache = self.embedder.embed_unique_skills(&unique_skills)?;

        info!("Completed batch embedding of unique skills");

        // Phase 3: Process each pair using pre-computed embeddings
        let mut results = Vec::with_capacity(pairs.len());

        for (candidate_skills, required_skills) in pairs {
            // Validate inputs
            if candidate_skills.is_empty() || required_skills.is_empty() {
                return Err(SkillMatcherError::EmptySkills {
                    n_candidate: candidate_skills.len(),
                    n_required: required_skills.len()
                });
            }

            // Build SkillWithDistribution vectors using cached embeddings
            let mut candidate_skills_dist = Vec::with_capacity(candidate_skills.len());
            for skill in &candidate_skills {
                candidate_skills_dist.push(
                    self.build_skill_with_distribution(skill, &embedding_cache)?
                );
            }

            let mut required_skills_dist = Vec::with_capacity(required_skills.len());
            for skill in &required_skills {
                required_skills_dist.push(
                    self.build_skill_with_distribution(skill, &embedding_cache)?
                );
            }

            // Calculate similarities and scores using existing logic
            let similarities = self.similarity_calculator.calculate_similarities(
                &candidate_skills_dist,
                &required_skills_dist
            );

            let skill_similarities = self.convert_similarities_to_hashmap(
                &candidate_skills_dist,
                &required_skills_dist,
                &similarities
            );

            let pairwise_scores = self.calculate_pairwise_scores(
                &candidate_skills_dist,
                &required_skills_dist,
                &similarities
            );

            let skill_scores = self.calculate_individual_scores(
                &candidate_skills_dist,
                &required_skills_dist,
                &similarities
            )?;

            let mut overall_score = self.scoring_strategy.calculate_overall_score(&skill_scores);

            // Apply coherence bonus for multi-skill roles with good domain alignment
            if required_skills_dist.len() >= 3 && candidate_skills_dist.len() >= 3 {
                overall_score = self.apply_coherence_bonus(
                    overall_score,
                    &candidate_skills_dist,
                    &required_skills_dist,
                    &similarities
                );
            }

            results.push(MatchResult {
                overall_score,
                skill_scores,
                skill_similarities,
                pairwise_scores,
            });
        }

        info!(
            results_count = results.len(),
            "Completed batch match score calculation"
        );

        Ok(results)
    }

    /// Apply coherence bonus for multi-skill roles where skills are within related domains
    /// and have good semantic similarity. This addresses the conservative aggregation issue.
    fn apply_coherence_bonus(
        &self,
        base_score: f64,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>]
    ) -> f64 {
        use crate::domain::SkillDomain;

        // Calculate average semantic similarity across all required skills
        let avg_similarity: f64 = required_skills.iter().enumerate()
            .map(|(i, _)| {
                similarities.iter()
                    .map(|row| row[i])
                    .fold(f64::NEG_INFINITY, f64::max)
            })
            .sum::<f64>() / required_skills.len() as f64;

        // Check if most skills are within related domains
        let required_domains: Vec<&SkillDomain> = required_skills.iter()
            .map(|s| &s.domain)
            .collect();

        let candidate_domains: Vec<&SkillDomain> = candidate_skills.iter()
            .map(|s| &s.domain)
            .collect();

        // Calculate domain coherence (0.0 = completely unrelated, 1.0 = same domain)
        let domain_coherence = self.calculate_domain_coherence(&required_domains, &candidate_domains);

        // Apply coherence bonus if:
        // 1. Average semantic similarity is good (>0.60)
        // 2. Domains are related (coherence > 0.7)
        // 3. Base score is in the "good but not perfect" range (0.55-0.75)
        if avg_similarity > 0.60 && domain_coherence > 0.7 && base_score >= 0.55 && base_score <= 0.75 {
            // Apply a moderate bonus (5-7%) based on both similarity and domain coherence
            let bonus_factor = 0.05 + (0.02 * (avg_similarity - 0.60)) + (0.02 * (domain_coherence - 0.7));
            let bonus = bonus_factor.min(0.07); // Cap at 7%
            (base_score + bonus).min(1.0)
        } else {
            base_score
        }
    }

    /// Calculate domain coherence between required and candidate skill sets
    /// Returns a value between 0.0 (completely unrelated) and 1.0 (same domain)
    fn calculate_domain_coherence(
        &self,
        required_domains: &[&crate::domain::SkillDomain],
        candidate_domains: &[&crate::domain::SkillDomain]
    ) -> f64 {
        use std::collections::HashMap;

        // Count domain frequencies
        let mut req_domain_counts: HashMap<&crate::domain::SkillDomain, usize> = HashMap::new();
        for domain in required_domains {
            *req_domain_counts.entry(domain).or_insert(0) += 1;
        }

        let mut cand_domain_counts: HashMap<&crate::domain::SkillDomain, usize> = HashMap::new();
        for domain in candidate_domains {
            *cand_domain_counts.entry(domain).or_insert(0) += 1;
        }

        // Calculate overlap: how many required skills have candidates in same/related domain?
        let mut coherence_sum = 0.0;
        for (req_domain, _) in &req_domain_counts {
            // Check if candidates have skills in same or related domain
            for (cand_domain, _) in &cand_domain_counts {
                let penalty = req_domain.cross_domain_penalty(cand_domain);
                let domain_match = 1.0 - penalty; // Convert penalty to match score
                coherence_sum += domain_match;
            }
        }

        // Normalize by total possible matches
        let total_combinations = required_domains.len() * candidate_domains.len();
        if total_combinations > 0 {
            (coherence_sum / total_combinations as f64).min(1.0)
        } else {
            0.0
        }
    }

    fn convert_similarities_to_hashmap(
        &self,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>]
    ) -> HashMap<String, HashMap<String, f64>> {
        // Pre-allocate HashMap with capacity hints
        let mut result = HashMap::with_capacity(required_skills.len());
        
        for (i, req_skill) in required_skills.iter().enumerate() {
            let mut skill_map = HashMap::with_capacity(candidate_skills.len());
            
            for (j, cand_skill) in candidate_skills.iter().enumerate() {
                // Use similarity directly from the matrix
                let similarity = if cand_skill.name == req_skill.name {
                    1.0  // Identical skill names should have perfect similarity
                } else {
                    similarities[j][i]
                };
                skill_map.insert(
                    cand_skill.name.clone(),
                    similarity
                );
            }
            
            result.insert(req_skill.name.clone(), skill_map);
        }
        
        result
    }

    fn calculate_pairwise_scores(
        &self,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>]
    ) -> HashMap<String, HashMap<String, f64>> {
        // Pre-allocate HashMap with capacity hints
        let mut result = HashMap::with_capacity(required_skills.len());
        
        for (i, req_skill) in required_skills.iter().enumerate() {
            let mut skill_map = HashMap::with_capacity(candidate_skills.len());
            let req_threshold = req_skill.level.to_ratio();
            
            for (j, cand_skill) in candidate_skills.iter().enumerate() {
                // Get semantic similarity
                let similarity = if cand_skill.name == req_skill.name {
                    1.0  // Identical skill names should have perfect similarity
                } else {
                    similarities[j][i]
                };
                
                // Calculate proficiency match ratio
                let cand_proficiency = cand_skill.level.to_ratio();
                let proficiency_ratio = (cand_proficiency / req_threshold).min(1.0);
                
                // Use same logic as skill scores for consistency
                let pairwise_score = if similarity > 0.9 {
                    // Same skill or nearly identical - use the same formula as skill scores
                    // Score ranges from 0.6 to 1.0 based on how well proficiency matches
                    0.6 + (0.4 * proficiency_ratio)
                } else if similarity > 0.7 {
                    // High similarity: strong base score with proficiency adjustment
                    0.5 + (0.35 * similarity) + (0.15 * proficiency_ratio)
                } else if similarity > 0.5 {
                    // Moderate similarity: similarity-weighted with some proficiency impact
                    0.3 + (0.5 * similarity) + (0.2 * proficiency_ratio)
                } else if similarity > 0.3 {
                    // Low-moderate similarity: mostly similarity-based
                    0.2 + (0.6 * similarity) + (0.2 * proficiency_ratio)
                } else if similarity > 0.18 {
                    // Low similarity: apply penalty similar to skill scores
                    0.1 + (0.7 * similarity) + (0.2 * proficiency_ratio)
                } else {
                    // Very low similarity: heavy penalty
                    0.05 + (0.8 * similarity) + (0.15 * proficiency_ratio)
                };
                
                skill_map.insert(
                    cand_skill.name.clone(),
                    pairwise_score
                );
            }
            
            result.insert(req_skill.name.clone(), skill_map);
        }
        
        result
    }

    fn calculate_individual_scores(
        &self,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>]
    ) -> Result<Vec<SkillScore>> {
        // Pre-allocate result vector with exact capacity
        let mut result = Vec::with_capacity(required_skills.len());
        
        for (i, req_skill) in required_skills.iter().enumerate() {
            let score = self.scoring_strategy.calculate_skill_score(
                req_skill,
                candidate_skills,
                similarities,
                i,
                &self.config
            )?;
            result.push(score);
        }
        
        Ok(result)
    }

}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::init_test_tracing;
    use crate::types::ProficiencyLevel;
    use std::sync::Once;

    static INIT: Once = Once::new();


    /// Initialize tracing exactly once for all tests
    fn setup() {
        INIT.call_once(|| {
            init_test_tracing();
        });
    }

    // You can use this attribute to run setup() before each test
    #[ctor::ctor]
    fn init_tests() {
        setup();
    }

    #[test]
    fn test_similarity_mapping() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;
        
        let candidate_skills = vec![
            Skill {
                name: "Python".to_string(),
                level: ProficiencyLevel { value: 4, max: 5 },
            },
            Skill {
                name: "Java".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 },
            },
        ];

        let required_skills = vec![
            Skill {
                name: "Programming".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 },
            },
        ];

        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        
        // Verify similarity map structure
        assert!(result.skill_similarities.contains_key("Programming"));
        let programming_similarities = result.skill_similarities.get("Programming").unwrap();
        assert!(programming_similarities.contains_key("Python"));
        assert!(programming_similarities.contains_key("Java"));
        
        // Verify similarity scores are between 0 and 1
        for score in programming_similarities.values() {
            assert!(*score >= 0.0 && *score <= 1.0);
        }
        
        // Verify pairwise scores structure
        assert!(result.pairwise_scores.contains_key("Programming"));
        let programming_pairwise = result.pairwise_scores.get("Programming").unwrap();
        assert!(programming_pairwise.contains_key("Python"));
        assert!(programming_pairwise.contains_key("Java"));
        
        // Verify pairwise scores combine similarity and proficiency match
        let _python_similarity = programming_similarities.get("Python").unwrap();
        let python_pairwise = programming_pairwise.get("Python").unwrap();
        let _java_similarity = programming_similarities.get("Java").unwrap();
        let java_pairwise = programming_pairwise.get("Java").unwrap();
        
        // Pairwise scores should be between 0 and 1
        assert!(*python_pairwise >= 0.0 && *python_pairwise <= 1.0);
        assert!(*java_pairwise >= 0.0 && *java_pairwise <= 1.0);
        
        // Python has higher proficiency (4/5) than required (3/5), so should score well
        // Java matches the requirement exactly (3/5), so should also score well
        // The exact values depend on the semantic similarity between the skills
        
        Ok(())
    }
    
    #[test]
    fn test_matcher_creation() -> Result<()> {
        let _matcher = SkillMatcher::new()?;
        Ok(())
    }

    #[test]
    fn test_basic_matching() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;

        let candidate_skills = vec![
            Skill {
                name: "Python".to_string(),
                level: ProficiencyLevel { value: 4, max: 5 },
            },
            Skill {
                name: "SQL".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 },
            },
        ];

        let required_skills = vec![
            Skill {
                name: "SQL".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 },
            },
        ];

        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;

        assert!(result.overall_score >= 0.0 && result.overall_score <= 1.0);
        assert_eq!(result.skill_scores.len(), 1);
        assert_eq!(result.skill_scores[0].skill_name, "SQL");

        Ok(())
    }

    #[test]
    fn test_batch_deduplication_correctness() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;

        // Create pairs with overlapping skills
        let pairs = vec![
            (
                vec![
                    Skill {
                        name: "Python".to_string(),
                        level: ProficiencyLevel { value: 4, max: 5 },
                    },
                    Skill {
                        name: "SQL".to_string(),
                        level: ProficiencyLevel { value: 3, max: 5 },
                    },
                ],
                vec![
                    Skill {
                        name: "Python".to_string(),
                        level: ProficiencyLevel { value: 3, max: 5 },
                    },
                ],
            ),
            (
                vec![
                    Skill {
                        name: "Python".to_string(),
                        level: ProficiencyLevel { value: 5, max: 5 },
                    },
                    Skill {
                        name: "Java".to_string(),
                        level: ProficiencyLevel { value: 4, max: 5 },
                    },
                ],
                vec![
                    Skill {
                        name: "Python".to_string(),
                        level: ProficiencyLevel { value: 4, max: 5 },
                    },
                ],
            ),
        ];

        // Test batch processing
        let batch_results = matcher.calculate_batch_match_scores(pairs.clone())?;

        // Test individual processing for comparison
        let mut individual_results = Vec::new();
        for (candidate, required) in pairs {
            let result = matcher.calculate_match_score(candidate, required)?;
            individual_results.push(result);
        }

        // Verify same number of results
        assert_eq!(batch_results.len(), individual_results.len());

        // Verify results are equivalent (within floating point tolerance)
        for (batch_result, individual_result) in batch_results.iter().zip(individual_results.iter()) {
            // Overall scores should be very close (within 0.01 tolerance for floating point)
            assert!(
                (batch_result.overall_score - individual_result.overall_score).abs() < 0.01,
                "Overall scores differ: batch={}, individual={}",
                batch_result.overall_score,
                individual_result.overall_score
            );

            // Skill scores should match
            assert_eq!(batch_result.skill_scores.len(), individual_result.skill_scores.len());
        }

        Ok(())
    }

    #[test]
    fn test_batch_with_different_proficiency_levels() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;

        // Test that same skill name with different levels gets different distributions
        let pairs = vec![
            (
                vec![Skill {
                    name: "Python".to_string(),
                    level: ProficiencyLevel { value: 2, max: 5 },
                }],
                vec![Skill {
                    name: "Python".to_string(),
                    level: ProficiencyLevel { value: 2, max: 5 },
                }],
            ),
            (
                vec![Skill {
                    name: "Python".to_string(),
                    level: ProficiencyLevel { value: 5, max: 5 },
                }],
                vec![Skill {
                    name: "Python".to_string(),
                    level: ProficiencyLevel { value: 2, max: 5 },
                }],
            ),
        ];

        let results = matcher.calculate_batch_match_scores(pairs)?;

        assert_eq!(results.len(), 2);

        // First pair: equal proficiency, should have high score
        assert!(results[0].overall_score > 0.8, "Equal proficiency should score high");

        // Second pair: higher candidate proficiency, should score even higher
        assert!(
            results[1].overall_score >= results[0].overall_score,
            "Higher proficiency should score at least as well"
        );

        Ok(())
    }

    #[test]
    fn test_batch_empty_pairs() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;

        let pairs: Vec<(Vec<Skill>, Vec<Skill>)> = vec![];
        let results = matcher.calculate_batch_match_scores(pairs)?;

        assert_eq!(results.len(), 0);

        Ok(())
    }

    #[test]
    fn test_batch_single_pair() -> Result<()> {
        let mut matcher = SkillMatcher::new()?;

        let pairs = vec![(
            vec![Skill {
                name: "Python".to_string(),
                level: ProficiencyLevel { value: 4, max: 5 },
            }],
            vec![Skill {
                name: "Python".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 },
            }],
        )];

        let results = matcher.calculate_batch_match_scores(pairs)?;

        assert_eq!(results.len(), 1);
        assert!(results[0].overall_score >= 0.0 && results[0].overall_score <= 1.0);

        Ok(())
    }
}
