//! Trait definitions for core components of the skill matching system.
//!
//! This module defines the key traits that enable dependency injection and
//! pluggable implementations for different aspects of skill matching.

use crate::types::{Skill, SkillWithDistribution, SkillScore, ConfidenceInterval};
use crate::error::Result;
use crate::config::SkillMatcherConfig;

/// Trait for components that can embed skills into vector representations.
///
/// This trait allows for different embedding models and strategies to be used
/// interchangeably in the skill matching system.
pub trait SkillEmbedder {
    /// Embed a collection of skills into their vector representations.
    ///
    /// # Arguments
    /// * `skills` - The skills to embed
    ///
    /// # Returns
    /// A vector of skills with their embeddings and distributions
    fn embed_skills(&mut self, skills: &[Skill]) -> Result<Vec<SkillWithDistribution>>;
}

/// Trait for components that calculate similarities between skill embeddings.
///
/// This trait enables different similarity calculation algorithms to be used,
/// such as cosine similarity, dot product, or more sophisticated metrics.
pub trait SimilarityCalculator {
    /// Calculate pairwise similarities between candidate and required skills.
    ///
    /// # Arguments
    /// * `candidate_skills` - Skills from the candidate
    /// * `required_skills` - Skills required for the position
    ///
    /// # Returns
    /// A matrix where similarities[i][j] is the similarity between candidate skill i and required skill j
    fn calculate_similarities(
        &self,
        candidate_skills: &[SkillWithDistribution],
        required_skills: &[SkillWithDistribution],
    ) -> Vec<Vec<f64>>;
}

/// Trait for components that implement scoring strategies.
///
/// This trait allows for different approaches to calculating match scores based on
/// skill similarities and proficiency levels.
pub trait ScoringStrategy {
    /// Calculate the score for a single required skill.
    ///
    /// # Arguments
    /// * `req_skill` - The required skill to score
    /// * `candidate_skills` - All candidate skills
    /// * `similarities` - Similarity matrix between candidate and required skills
    /// * `skill_index` - Index of the required skill in the similarity matrix
    /// * `config` - Configuration for scoring parameters
    ///
    /// # Returns
    /// A SkillScore containing the probability and confidence information
    fn calculate_skill_score(
        &self,
        req_skill: &SkillWithDistribution,
        candidate_skills: &[SkillWithDistribution],
        similarities: &[Vec<f64>],
        skill_index: usize,
        config: &SkillMatcherConfig,
    ) -> Result<SkillScore>;

    /// Calculate the overall match score from individual skill scores.
    ///
    /// # Arguments
    /// * `skill_scores` - Individual scores for each required skill
    ///
    /// # Returns
    /// An overall score between 0.0 and 1.0
    fn calculate_overall_score(&self, skill_scores: &[SkillScore]) -> f64;
}

/// Trait for components that can create confidence intervals.
///
/// This trait allows for different statistical approaches to uncertainty quantification.
pub trait ConfidenceCalculator {
    /// Calculate a confidence interval for a given distribution.
    ///
    /// # Arguments
    /// * `mean` - Mean of the distribution
    /// * `variance` - Variance of the distribution  
    /// * `confidence_level` - Desired confidence level (e.g., 0.95 for 95%)
    ///
    /// # Returns
    /// A confidence interval with lower and upper bounds
    fn calculate_confidence_interval(
        &self,
        mean: f64,
        variance: f64,
        confidence_level: f64,
    ) -> ConfidenceInterval;
}