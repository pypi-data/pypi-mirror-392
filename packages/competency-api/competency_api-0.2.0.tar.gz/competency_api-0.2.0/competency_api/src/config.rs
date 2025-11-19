//! Configuration management for the skill matching library.
//!
//! This module provides configurable parameters for all aspects of skill matching,
//! including embedding models, similarity calculations, and scoring strategies.

use std::path::PathBuf;
use fastembed::EmbeddingModel;
use serde::{Deserialize, Serialize};

/// Configuration for penalty factors in skill matching.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PenaltyConfig {
    /// Similarity threshold below which penalties apply (0.0 - 1.0)
    pub similarity_threshold: f64,
    /// Penalty factor for moderately dissimilar skills (0.0 - 1.0)
    pub moderate_penalty: f64,
    /// Penalty factor for very dissimilar skills (0.0 - 1.0)
    pub severe_penalty: f64,
    /// Similarity threshold for severe penalties (0.0 - 1.0)
    pub severe_threshold: f64,
}

impl Default for PenaltyConfig {
    fn default() -> Self {
        Self {
            similarity_threshold: 0.30,  // Penalty applies if max similarity < 0.30
            moderate_penalty: 0.15,
            severe_penalty: 0.05,
            severe_threshold: 0.20,  // Severe penalty if max similarity < 0.20
        }
    }
}

/// Configuration for scoring weights and thresholds.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoringConfig {
    /// Weight for direct ratio scoring when candidate meets threshold
    pub ratio_weight_meets: f64,
    /// Weight for direct ratio scoring when candidate below threshold
    pub ratio_weight_below: f64,
    /// Distance boost for very similar skills (distance < 0.3)
    pub very_similar_boost: f64,
    /// Distance boost for moderately similar skills (distance < 0.5)
    pub moderately_similar_boost: f64,
    /// Maximum confidence weight adjustment
    pub max_confidence_weight: f64,
    /// Dampening factor for high scores
    pub high_score_dampening: f64,
}

impl Default for ScoringConfig {
    fn default() -> Self {
        Self {
            ratio_weight_meets: 0.5,
            ratio_weight_below: 0.3,
            very_similar_boost: 1.05,
            moderately_similar_boost: 1.02,
            max_confidence_weight: 0.7,
            high_score_dampening: 0.5,
        }
    }
}

/// Configuration for Beta distribution parameters.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DistributionConfig {
    /// Desired variance for Beta distributions
    pub desired_variance: f64,
    /// Safety factor for maximum variance (0.0 - 1.0)
    pub max_variance_factor: f64,
    /// Alpha parameter for zero proficiency cases
    pub zero_proficiency_alpha: f64,
    /// Beta parameter for zero proficiency cases
    pub zero_proficiency_beta: f64,
    /// Alpha parameter for perfect proficiency cases
    pub perfect_proficiency_alpha: f64,
    /// Beta parameter for perfect proficiency cases
    pub perfect_proficiency_beta: f64,
}

impl Default for DistributionConfig {
    fn default() -> Self {
        Self {
            desired_variance: 0.05,
            max_variance_factor: 0.9,
            zero_proficiency_alpha: 1.0,
            zero_proficiency_beta: 10.0,
            perfect_proficiency_alpha: 10.0,
            perfect_proficiency_beta: 1.0,
        }
    }
}

/// Main configuration struct for the skill matching system.
#[derive(Debug, Clone)]
pub struct SkillMatcherConfig {
    /// Embedding model to use for skill vectors
    pub embedding_model: EmbeddingModel,
    /// Custom cache directory for embeddings (None for auto-generated)
    pub cache_dir: Option<PathBuf>,
    /// Whether to show download progress for embedding models
    pub show_download_progress: bool,
    /// Penalty configuration for distant skills
    pub penalty_config: PenaltyConfig,
    /// Scoring configuration for match calculations
    pub scoring_config: ScoringConfig,
    /// Distribution configuration for Beta distributions
    pub distribution_config: DistributionConfig,
}

impl Default for SkillMatcherConfig {
    fn default() -> Self {
        Self {
            embedding_model: EmbeddingModel::ParaphraseMLMpnetBaseV2,
            cache_dir: None,
            show_download_progress: true,
            penalty_config: PenaltyConfig::default(),
            scoring_config: ScoringConfig::default(),
            distribution_config: DistributionConfig::default(),
        }
    }
}

/// Builder for SkillMatcherConfig to enable fluent configuration.
#[derive(Debug, Clone)]
pub struct SkillMatcherConfigBuilder {
    config: SkillMatcherConfig,
}

impl SkillMatcherConfigBuilder {
    /// Create a new builder with default configuration.
    pub fn new() -> Self {
        Self {
            config: SkillMatcherConfig::default(),
        }
    }

    /// Set the embedding model to use.
    pub fn embedding_model(mut self, model: EmbeddingModel) -> Self {
        self.config.embedding_model = model;
        self
    }

    /// Set a custom cache directory for embeddings.
    pub fn cache_dir<P: Into<PathBuf>>(mut self, path: P) -> Self {
        self.config.cache_dir = Some(path.into());
        self
    }

    /// Set whether to show download progress.
    pub fn show_download_progress(mut self, show: bool) -> Self {
        self.config.show_download_progress = show;
        self
    }

    /// Set penalty configuration.
    pub fn penalty_config(mut self, config: PenaltyConfig) -> Self {
        self.config.penalty_config = config;
        self
    }

    /// Set scoring configuration.
    pub fn scoring_config(mut self, config: ScoringConfig) -> Self {
        self.config.scoring_config = config;
        self
    }

    /// Set distribution configuration.
    pub fn distribution_config(mut self, config: DistributionConfig) -> Self {
        self.config.distribution_config = config;
        self
    }

    /// Build the final configuration.
    pub fn build(self) -> SkillMatcherConfig {
        self.config
    }
}

impl Default for SkillMatcherConfigBuilder {
    fn default() -> Self {
        Self::new()
    }
}

impl SkillMatcherConfig {
    /// Create a new builder for this configuration.
    pub fn builder() -> SkillMatcherConfigBuilder {
        SkillMatcherConfigBuilder::new()
    }

    /// Validate the configuration parameters.
    pub fn validate(&self) -> Result<(), String> {
        // Validate penalty config
        if self.penalty_config.similarity_threshold < 0.0 || self.penalty_config.similarity_threshold > 1.0 {
            return Err("similarity_threshold must be between 0.0 and 1.0".to_string());
        }
        if self.penalty_config.moderate_penalty < 0.0 || self.penalty_config.moderate_penalty > 1.0 {
            return Err("moderate_penalty must be between 0.0 and 1.0".to_string());
        }
        if self.penalty_config.severe_penalty < 0.0 || self.penalty_config.severe_penalty > 1.0 {
            return Err("severe_penalty must be between 0.0 and 1.0".to_string());
        }
        if self.penalty_config.severe_threshold < 0.0 || self.penalty_config.severe_threshold > 1.0 {
            return Err("severe_threshold must be between 0.0 and 1.0".to_string());
        }

        // Validate scoring config
        if self.scoring_config.ratio_weight_meets < 0.0 || self.scoring_config.ratio_weight_meets > 1.0 {
            return Err("ratio_weight_meets must be between 0.0 and 1.0".to_string());
        }
        if self.scoring_config.ratio_weight_below < 0.0 || self.scoring_config.ratio_weight_below > 1.0 {
            return Err("ratio_weight_below must be between 0.0 and 1.0".to_string());
        }

        // Validate distribution config
        if self.distribution_config.desired_variance < 0.0 {
            return Err("desired_variance must be non-negative".to_string());
        }
        if self.distribution_config.max_variance_factor < 0.0 || self.distribution_config.max_variance_factor > 1.0 {
            return Err("max_variance_factor must be between 0.0 and 1.0".to_string());
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = SkillMatcherConfig::default();
        assert!(config.validate().is_ok());
    }

    #[test]
    fn test_builder_pattern() {
        let config = SkillMatcherConfig::builder()
            .embedding_model(EmbeddingModel::AllMiniLML6V2)
            .show_download_progress(false)
            .build();
        
        assert_eq!(config.embedding_model, EmbeddingModel::AllMiniLML6V2);
        assert!(!config.show_download_progress);
        assert!(config.validate().is_ok());
    }

    #[test]
    fn test_config_validation() {
        let mut config = SkillMatcherConfig::default();
        
        // Test invalid similarity threshold
        config.penalty_config.similarity_threshold = 1.5;
        assert!(config.validate().is_err());
        
        // Reset and test invalid penalty
        config.penalty_config.similarity_threshold = 0.7;
        config.penalty_config.moderate_penalty = -0.1;
        assert!(config.validate().is_err());
    }

}