//! Scoring strategies for skill matching.
//!
//! This module contains different approaches to calculating match scores
//! based on skill distances and proficiency levels.

use crate::traits::{ScoringStrategy, ConfidenceCalculator};
use crate::types::{SkillWithDistribution, SkillScore, ConfidenceInterval};
use crate::config::SkillMatcherConfig;
use crate::error::Result;
use crate::distribution::{BetaMixture, calculate_confidence_interval};
use tracing::info;

/// Default scoring strategy that implements the current algorithm.
///
/// This strategy provides a balance between exact matches, semantic similarity,
/// and proficiency levels with configurable penalties for distant skills.
pub struct DefaultScoringStrategy;

impl ScoringStrategy for DefaultScoringStrategy {
    fn calculate_skill_score(
        &self,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>],
        skill_index: usize,
        config: &SkillMatcherConfig,
    ) -> Result<SkillScore> {
        let threshold = req_skill.level.to_ratio();

        info!(
            "Calculating score for required skill '{}' (threshold: {:.2})",
            req_skill.name, threshold
        );

        // Always use semantic similarity matching - it handles exact matches well
        let normalized_weights = self.calculate_normalized_weights(similarities, skill_index, candidate_skills);

        // Log similarity scores for debugging  
        for (skill, similarity) in candidate_skills.iter().zip(similarities.iter()) {
            info!(
                "Similarity between '{}' and '{}': {:.3}",
                req_skill.name, skill.name, similarity[skill_index]
            );
        }

        // Calculate similarity threshold
        let max_similarity = similarities.iter()
            .map(|row| row[skill_index])
            .fold(f64::NEG_INFINITY, f64::max);

        // Apply penalty if skills are too dissimilar
        if max_similarity < config.penalty_config.similarity_threshold {
            return self.calculate_similarity_penalty_score(req_skill, candidate_skills, max_similarity, config);
        }

        // For similar skills, calculate score based on similarity and proficiency
        let mixture = self.create_skill_mixture(candidate_skills, &normalized_weights)?;
        let exceed_prob = 1.0 - mixture.cdf(threshold);
        let direct_ratio = self.calculate_direct_ratio(candidate_skills, &normalized_weights, threshold);
        
        let combined_score = self.combine_scores(
            direct_ratio,
            exceed_prob,
            &mixture,
            threshold,
            max_similarity,
            config,
            req_skill,
            candidate_skills,
            &normalized_weights,
        );

        info!(
            "Final score for '{}': {:.3} (exceed_prob: {:.3}, direct_ratio: {:.3})",
            req_skill.name, combined_score, exceed_prob, direct_ratio
        );
        
        Ok(SkillScore {
            skill_name: req_skill.name.clone(),
            probability: combined_score,
            confidence_interval: calculate_confidence_interval(&mixture, 0.95),
            mean: mixture.mean(),
            variance: mixture.variance(),
        })
    }

    fn calculate_overall_score(&self, skill_scores: &[SkillScore]) -> f64 {
        skill_scores.iter()
            .map(|score| score.probability)
            .sum::<f64>() / skill_scores.len() as f64
    }
}

impl DefaultScoringStrategy {
    fn normalize_skill_name(name: &str) -> String {
        name.to_lowercase()
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
    }


    fn calculate_similarity_penalty_score(
        &self,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        max_similarity: f64,
        config: &SkillMatcherConfig,
    ) -> Result<SkillScore> {
        let base_penalty_factor = if max_similarity < config.penalty_config.severe_threshold {
            config.penalty_config.severe_penalty
        } else {
            config.penalty_config.moderate_penalty + 
            (max_similarity - config.penalty_config.severe_threshold) / 
            (config.penalty_config.similarity_threshold - config.penalty_config.severe_threshold) * 
            (config.penalty_config.severe_penalty - config.penalty_config.moderate_penalty)
        };

        // Apply proficiency boost even for low similarity skills
        let best_candidate_proficiency = candidate_skills.iter()
            .map(|skill| skill.level.to_ratio())
            .fold(0.0f64, f64::max);
        
        let proficiency_boost = 1.0 + (best_candidate_proficiency * 0.3); // Up to 30% boost
        let penalty_factor = (base_penalty_factor * proficiency_boost).min(1.0);

        info!(
            "Similarity penalty applied for '{}' (max similarity: {:.3}, penalty: {:.3})",
            req_skill.name, max_similarity, penalty_factor
        );
        
        Ok(SkillScore {
            skill_name: req_skill.name.clone(),
            probability: penalty_factor,
            confidence_interval: ConfidenceInterval {
                lower: 0.0,
                upper: penalty_factor + 0.1,
            },
            mean: penalty_factor,
            variance: 0.1,
        })
    }

    fn calculate_normalized_weights(
        &self, 
        similarities: &[Vec<f64>], 
        skill_index: usize,
        candidate_skills: &[SkillWithDistribution]
    ) -> Vec<f64> {
        let raw_similarities: Vec<f64> = similarities.iter()
            .map(|row| row[skill_index])
            .collect();
        
        // Use similarities as weights with proficiency factor (higher similarity + proficiency = higher weight)
        let weights: Vec<f64> = raw_similarities.iter()
            .zip(candidate_skills.iter())
            .map(|(&similarity, skill)| {
                let proficiency_factor = 1.0 + (skill.level.to_ratio() * 0.5); // 1.0-1.5x multiplier
                (similarity * proficiency_factor).max(0.01)  // Ensure positive weights, minimum 0.01
            })
            .collect();
        
        let weight_sum: f64 = weights.iter().sum();
        if weight_sum == 0.0 {
            return vec![1.0 / weights.len() as f64; weights.len()];
        }
        
        weights.iter()
            .map(|&w| w / weight_sum)
            .collect()
    }

    fn create_skill_mixture(
        &self,
        candidate_skills: &[SkillWithDistribution],
        normalized_weights: &[f64],
    ) -> Result<BetaMixture> {
        let components: Vec<(f64, statrs::distribution::Beta)> = candidate_skills.iter()
            .zip(normalized_weights)
            .map(|(skill, &weight)| (weight, skill.distribution))
            .collect();
        
        BetaMixture::new(components)
    }

    fn calculate_direct_ratio(
        &self,
        candidate_skills: &[SkillWithDistribution],
        normalized_weights: &[f64],
        threshold: f64,
    ) -> f64 {
        candidate_skills.iter()
            .zip(normalized_weights)
            .map(|(skill, &weight)| {
                let candidate_ratio = skill.level.to_ratio();
                weight * match candidate_ratio.partial_cmp(&threshold) {
                    Some(std::cmp::Ordering::Less) => candidate_ratio / threshold,
                    _ => 1.0
                }
            })
            .sum()
    }

    fn combine_scores(
        &self,
        direct_ratio: f64,
        exceed_prob: f64,
        mixture: &BetaMixture,
        threshold: f64,
        max_similarity: f64,
        config: &SkillMatcherConfig,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        normalized_weights: &[f64],
    ) -> f64 {
        // Check if this is essentially the same skill with minor variations
        let req_normalized = Self::normalize_skill_name(&req_skill.name);
        let has_normalized_match = candidate_skills.iter()
            .any(|s| Self::normalize_skill_name(&s.name) == req_normalized);
        
        let mean_skill = mixture.mean();
        
        if has_normalized_match || max_similarity > 0.9 {
            // Same skill or nearly identical - use linear interpolation based on proficiency
            // Score ranges from 0.6 to 1.0 based on how well proficiency matches
            let proficiency_ratio = (mean_skill / threshold).min(1.0);
            return 0.6 + (0.4 * proficiency_ratio);
        }
        
        let confidence = 1.0 - mixture.variance();
        
        // Apply similarity boost for semantically similar skills
        let similarity_boost = if max_similarity > 0.7 {
            1.05  // Boost excellent matches
        } else if max_similarity > 0.5 {
            0.9 + (max_similarity * 0.3)  // 0.9-1.05 range
        } else if max_similarity > 0.3 {
            0.6 + (max_similarity * 0.8)  // 0.6-0.8 range
        } else {
            0.3 + (max_similarity * 1.0)  // 0.3-0.6 range, no floor
        };
        
        // Apply generous weights for semantic matching
        let ratio_weight = if mean_skill >= threshold {
            ((config.scoring_config.ratio_weight_meets + (0.2 * confidence)) * similarity_boost)
                .min(config.scoring_config.max_confidence_weight)
        } else {
            ((config.scoring_config.ratio_weight_below + (0.3 * confidence)) * similarity_boost)
                .min(0.8)
        };
        
        let prob_weight = 1.0 - ratio_weight;
        let raw_score = (ratio_weight * direct_ratio) + (prob_weight * exceed_prob);

        // Apply similarity-based final adjustment with graduated bonuses
        let similarity_bonus = if max_similarity > 0.7 {
            1.0  // Perfect
        } else if max_similarity > 0.5 {
            0.75 + (max_similarity - 0.5) * 1.25  // 0.75-1.0
        } else if max_similarity > 0.3 {
            0.45 + (max_similarity - 0.3) * 1.5   // 0.45-0.75
        } else {
            // Exponential penalty: 0% → 0%, 10% → 3%, 20% → 12%, 30% → 27%
            (max_similarity * max_similarity * 3.0).min(0.45)
        }.min(1.0);

        // Apply domain-based penalty for cross-domain mismatches
        // BUT: preserve high semantic similarity matches (likely synonyms)
        let domain_factor = if max_similarity > 0.75 {
            // Very high semantic similarity - likely synonyms or equivalent terms
            // Apply minimal or no domain penalty
            1.0
        } else if max_similarity > 0.65 {
            // High semantic similarity - related concepts
            // Apply small penalty even for cross-domain (10% max)
            let best_candidate_domain = if candidate_skills.len() == 1 {
                &candidate_skills[0].domain
            } else {
                let domain_weights: std::collections::HashMap<_, f64> = candidate_skills.iter()
                    .zip(normalized_weights.iter())
                    .fold(std::collections::HashMap::new(), |mut acc, (skill, &weight)| {
                        *acc.entry(&skill.domain).or_insert(0.0) += weight;
                        acc
                    });

                domain_weights.iter()
                    .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
                    .map(|(domain, _)| *domain)
                    .unwrap_or(&candidate_skills[0].domain)
            };

            let base_penalty = req_skill.domain.cross_domain_penalty(best_candidate_domain);
            // Reduce penalty for high semantic similarity (cap at 10%)
            let reduced_penalty = (base_penalty * 0.2).min(0.10);
            1.0 - reduced_penalty
        } else if max_similarity > 0.50 {
            // Moderate semantic similarity
            // Apply partial domain penalty (50% of full penalty)
            let best_candidate_domain = if candidate_skills.len() == 1 {
                &candidate_skills[0].domain
            } else {
                let domain_weights: std::collections::HashMap<_, f64> = candidate_skills.iter()
                    .zip(normalized_weights.iter())
                    .fold(std::collections::HashMap::new(), |mut acc, (skill, &weight)| {
                        *acc.entry(&skill.domain).or_insert(0.0) += weight;
                        acc
                    });

                domain_weights.iter()
                    .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
                    .map(|(domain, _)| *domain)
                    .unwrap_or(&candidate_skills[0].domain)
            };

            let base_penalty = req_skill.domain.cross_domain_penalty(best_candidate_domain);
            let reduced_penalty = base_penalty * 0.5;
            1.0 - reduced_penalty
        } else {
            // Low semantic similarity - apply full domain penalty
            let best_candidate_domain = if candidate_skills.len() == 1 {
                &candidate_skills[0].domain
            } else {
                let domain_weights: std::collections::HashMap<_, f64> = candidate_skills.iter()
                    .zip(normalized_weights.iter())
                    .fold(std::collections::HashMap::new(), |mut acc, (skill, &weight)| {
                        *acc.entry(&skill.domain).or_insert(0.0) += weight;
                        acc
                    });

                domain_weights.iter()
                    .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
                    .map(|(domain, _)| *domain)
                    .unwrap_or(&candidate_skills[0].domain)
            };

            let domain_penalty = req_skill.domain.cross_domain_penalty(best_candidate_domain);
            1.0 - domain_penalty
        };

        let final_score = raw_score * similarity_bonus * domain_factor;

        info!(
            "Combining scores: direct_ratio={:.3}, exceed_prob={:.3}, ratio_weight={:.3}, raw={:.3}, final={:.3}",
            direct_ratio, exceed_prob, ratio_weight, raw_score, final_score
        );

        final_score
    }
}

/// Conservative scoring strategy that penalizes uncertainty more heavily.
///
/// This strategy is more cautious about assigning high scores when there's
/// significant uncertainty in the skill match.
pub struct ConservativeScoringStrategy;

impl ScoringStrategy for ConservativeScoringStrategy {
    fn calculate_skill_score(
        &self,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>],
        skill_index: usize,
        config: &SkillMatcherConfig,
    ) -> Result<SkillScore> {
        // Use default strategy but apply conservative adjustments
        let default_strategy = DefaultScoringStrategy;
        let mut score = default_strategy.calculate_skill_score(
            req_skill, candidate_skills, similarities, skill_index, config
        )?;
        
        // Apply conservative penalty based on variance
        let uncertainty_penalty = 1.0 - (score.variance * 0.5);
        score.probability *= uncertainty_penalty;
        
        Ok(score)
    }

    fn calculate_overall_score(&self, skill_scores: &[SkillScore]) -> f64 {
        // Conservative approach: use minimum score as a factor
        let avg_score = skill_scores.iter()
            .map(|score| score.probability)
            .sum::<f64>() / skill_scores.len() as f64;
        
        let min_score = skill_scores.iter()
            .map(|score| score.probability)
            .fold(f64::INFINITY, f64::min);
        
        // Blend average with minimum score
        0.7 * avg_score + 0.3 * min_score
    }
}

/// Aggressive scoring strategy that gives more credit for partial matches.
///
/// This strategy is more optimistic about skill transferability and gives
/// higher scores for semantically related skills.
pub struct AggressiveScoringStrategy;

impl ScoringStrategy for AggressiveScoringStrategy {
    fn calculate_skill_score(
        &self,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>],
        skill_index: usize,
        config: &SkillMatcherConfig,
    ) -> Result<SkillScore> {
        // Use default strategy but apply aggressive adjustments
        let default_strategy = DefaultScoringStrategy;
        let mut score = default_strategy.calculate_skill_score(
            req_skill, candidate_skills, similarities, skill_index, config
        )?;
        
        // Apply aggressive boost for any reasonable similarity
        let max_similarity = similarities.iter()
            .map(|row| row[skill_index])
            .fold(f64::NEG_INFINITY, f64::max);
        
        if max_similarity > 0.2 {
            let boost = 1.0 + (max_similarity - 0.2) * 0.3;
            score.probability = (score.probability * boost).min(1.0);
        }
        
        Ok(score)
    }

    fn calculate_overall_score(&self, skill_scores: &[SkillScore]) -> f64 {
        // Aggressive approach: weight higher scores more heavily
        let scores: Vec<f64> = skill_scores.iter()
            .map(|score| score.probability)
            .collect();
        
        let avg_score = scores.iter().sum::<f64>() / scores.len() as f64;
        let max_score = scores.iter().fold(0.0f64, |a, &b| a.max(b));
        
        // Blend average with maximum score
        0.6 * avg_score + 0.4 * max_score
    }
}

/// Simple confidence calculator using normal approximation.
pub struct SimpleConfidenceCalculator;

impl ConfidenceCalculator for SimpleConfidenceCalculator {
    fn calculate_confidence_interval(
        &self,
        mean: f64,
        variance: f64,
        confidence_level: f64,
    ) -> ConfidenceInterval {
        let std_dev = variance.sqrt();
        let z_score = match confidence_level {
            0.90 => 1.645,
            0.95 => 1.96,
            0.99 => 2.576,
            _ => 1.96, // Default to 95%
        };
        
        let margin = z_score * std_dev;
        ConfidenceInterval {
            lower: (mean - margin).max(0.0),
            upper: (mean + margin).min(1.0),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{ProficiencyLevel, Skill};
    
    fn create_test_skill(name: &str, value: u32, max: u32) -> SkillWithDistribution {
        let skill = Skill {
            name: name.to_string(),
            level: ProficiencyLevel { value, max },
        };
        let distribution = crate::create_beta_distribution(&skill.level).unwrap();
        use crate::domain::SkillDomain;
        SkillWithDistribution {
            name: skill.name.clone(),
            level: skill.level,
            distribution,
            embedding: vec![1.0, 0.0, 0.0], // Dummy embedding
            domain: SkillDomain::classify_skill(name),
        }
    }

    #[test]
    fn test_default_scoring_strategy() {
        let strategy = DefaultScoringStrategy;
        let config = SkillMatcherConfig::default();

        let req_skill = create_test_skill("Python", 3, 5);
        let candidate_skills = vec![create_test_skill("Python", 4, 5)];
        let similarities = vec![vec![1.0]]; // Perfect similarity (1.0 = identical)

        let score = strategy.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        assert!(score.probability > 0.9); // Should be high for exact match
    }

    #[test]
    fn test_conservative_vs_aggressive() {
        let conservative = ConservativeScoringStrategy;
        let aggressive = AggressiveScoringStrategy;
        let config = SkillMatcherConfig::default();

        let req_skill = create_test_skill("Programming", 3, 5);
        let candidate_skills = vec![create_test_skill("Python", 4, 5)];
        let similarities = vec![vec![0.7]]; // Good similarity (was 0.3 which is now below threshold)

        let conservative_score = conservative.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        let aggressive_score = aggressive.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        // Aggressive should generally score higher for uncertain matches
        assert!(aggressive_score.probability >= conservative_score.probability);
    }

    #[test]
    fn test_confidence_calculator() {
        let calc = SimpleConfidenceCalculator;
        let ci = calc.calculate_confidence_interval(0.5, 0.1, 0.95);

        assert!(ci.lower < 0.5);
        assert!(ci.upper > 0.5);
        assert!(ci.lower >= 0.0);
        assert!(ci.upper <= 1.0);
    }

    /// Regression test for Phase 2: High semantic similarity should bypass domain penalty
    #[test]
    fn test_high_semantic_similarity_bypasses_domain_penalty() {
        let strategy = DefaultScoringStrategy;
        let config = SkillMatcherConfig::default();

        // "Team Leadership" gets classified as Leadership domain
        // "Team Management" gets classified as Leadership domain
        // But even if they're in different domains, high semantic similarity should preserve score
        let req_skill = create_test_skill("Team Leadership", 3, 5);
        let candidate_skills = vec![create_test_skill("Team Management", 4, 5)];

        // Simulate high semantic similarity (0.8 = very similar, likely synonyms)
        let similarities = vec![vec![0.85]];

        let score = strategy.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        // Should score high despite potential domain mismatch
        // Target: > 75% for clear synonyms
        assert!(
            score.probability > 0.70,
            "High semantic similarity (0.85) should preserve score even across domains. Got: {:.2}%",
            score.probability * 100.0
        );
    }

    /// Regression test for Phase 2: Cross-domain with low similarity should get penalized
    #[test]
    fn test_cross_domain_low_similarity_gets_penalized() {
        let strategy = DefaultScoringStrategy;
        let config = SkillMatcherConfig::default();

        // Marketing vs Finance - different domains
        let req_skill = create_test_skill("Marketing Strategy", 3, 5);
        let candidate_skills = vec![create_test_skill("Financial Analysis", 4, 5)];

        // Low semantic similarity (0.35 = somewhat similar due to business context)
        let similarities = vec![vec![0.35]];

        let score = strategy.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        // Should score low due to cross-domain penalty + low similarity
        // Target: < 30% for unrelated domains
        assert!(
            score.probability < 0.35,
            "Cross-domain with low similarity should be penalized. Got: {:.2}%",
            score.probability * 100.0
        );
    }

    /// Regression test for Phase 2: Moderate similarity with same domain
    #[test]
    fn test_moderate_similarity_same_domain() {
        let strategy = DefaultScoringStrategy;
        let config = SkillMatcherConfig::default();

        // Both in HR domain
        let req_skill = create_test_skill("Recruitment", 3, 5);
        let candidate_skills = vec![create_test_skill("Talent Acquisition", 4, 5)];

        // Moderate-high semantic similarity (0.70 = related concepts)
        let similarities = vec![vec![0.70]];

        let score = strategy.calculate_skill_score(
            &req_skill, &candidate_skills, &similarities, 0, &config
        ).unwrap();

        // Should score well - related skills in same domain
        // Target: > 65% for related skills
        assert!(
            score.probability > 0.60,
            "Related skills in same domain should score well. Got: {:.2}%",
            score.probability * 100.0
        );
    }

    /// Regression test for Phase 2: Domain penalty scaling with similarity
    #[test]
    fn test_domain_penalty_scales_with_similarity() {
        let strategy = DefaultScoringStrategy;
        let config = SkillMatcherConfig::default();

        // Marketing vs Finance - cross domain
        let req_skill = create_test_skill("Marketing Analysis", 3, 5);

        // Three candidates with different similarity levels
        let low_sim_candidate = create_test_skill("Financial Planning", 4, 5);
        let med_sim_candidate = create_test_skill("Business Analysis", 4, 5);
        let high_sim_candidate = create_test_skill("Market Analysis", 4, 5);

        // Test low similarity (0.30) - should get full domain penalty
        let score_low = strategy.calculate_skill_score(
            &req_skill,
            &[low_sim_candidate],
            &[vec![0.30]],
            0,
            &config
        ).unwrap();

        // Test moderate similarity (0.55) - should get partial domain penalty
        let score_med = strategy.calculate_skill_score(
            &req_skill,
            &[med_sim_candidate],
            &[vec![0.55]],
            0,
            &config
        ).unwrap();

        // Test high similarity (0.78) - should bypass domain penalty
        let score_high = strategy.calculate_skill_score(
            &req_skill,
            &[high_sim_candidate],
            &[vec![0.78]],
            0,
            &config
        ).unwrap();

        // Scores should increase with similarity
        assert!(
            score_low.probability < score_med.probability,
            "Medium similarity should score higher than low. Low: {:.2}%, Med: {:.2}%",
            score_low.probability * 100.0,
            score_med.probability * 100.0
        );

        assert!(
            score_med.probability < score_high.probability,
            "High similarity should score higher than medium. Med: {:.2}%, High: {:.2}%",
            score_med.probability * 100.0,
            score_high.probability * 100.0
        );

        // High similarity should be significantly higher
        assert!(
            score_high.probability > 0.70,
            "High similarity (0.78) should preserve score. Got: {:.2}%",
            score_high.probability * 100.0
        );
    }
}