//! # Skill Space Matcher
//! 
//! `skill_space_matcher` is a Rust library that implements the Geometric Theory of Skills Space,
//! providing sophisticated skill matching and analysis capabilities for HR systems,
//! recruitment platforms, and career development tools.
//! 
//! ## Key Features
//! 
//! - **Probabilistic Skill Matching**: Uses Beta distributions to model skill proficiency levels
//!   with uncertainty quantification.
//! - **Semantic Skill Analysis**: Employs neural embeddings to understand relationships between
//!   different skills.
//! - **Confidence-Based Matching**: Provides detailed match scores with confidence intervals.
//! - **Skill Distribution Prediction**: Predicts proficiency in unmeasured skills based on
//!   known skills.
//! 
//! ## Core Concepts
//! 
//! ### Skill Representation
//! 
//! Each skill is represented by:
//! - A proficiency level (current value and maximum possible value)
//! - A Beta distribution capturing uncertainty in the skill level
//! - A semantic embedding vector representing the skill's meaning
//! 
//! Create skills by instantiating a `Skill` struct with a name and `ProficiencyLevel`.
//! 
//! ### Matching Process
//! 
//! The matching process involves:
//! 1. Converting skills to distributions
//! 2. Calculating semantic similarities
//! 3. Computing match probabilities
//! 4. Generating confidence intervals
//! 
//! Use the `SkillMatcher` to calculate match scores between candidate and required skills.
//! 
//! ## Mathematical Foundation
//! 
//! The library implements the Geometric Theory of Skills Space, which:
//! - Treats skills as points in a high-dimensional semantic space
//! - Uses probability distributions to model skill proficiency
//! - Employs information geometry for skill relationship modeling
//! - Utilizes statistical manifolds for distribution interpolation
//! 
//! ## Example Use Cases
//! 
//! ### Recruitment
//! For recruitment, create `SkillMatcher` instances and use `calculate_match_score` to evaluate how well candidate skills match job requirements.
//! 
//! ## Error Handling
//! 
//! The library uses a custom error type `SkillMatcherError` for comprehensive error handling.
//! All operations that might fail return a `Result<T, SkillMatcherError>`.
//! 
//! ## Performance Considerations
//! 
//! The library optimizes performance through:
//! - SIMD-accelerated similarity calculations via `simsimd`
//! - Efficient Beta distribution operations using `statrs`
//! - Cached embeddings for frequently used skills
//! 
//! ## Future Directions
//! 
//! Planned future enhancements include:
//! - Time-based skill decay modeling
//! - Team synergy analysis
//! - Skill development path recommendations
//! - Integration with standard HR systems
//! 
//! ## License
//! 
//! This project is licensed under the MIT License.

mod types;
mod error;
mod distribution;
mod embedding;
mod similarity;
mod matcher;
mod config;
mod traits;
mod strategies;
mod domain;

#[cfg(feature = "memory-profiling")]
pub mod profiling;

pub use types::{
    ProficiencyLevel,
    Skill,
    SkillScore,
    MatchResult,
    ConfidenceInterval,
};
pub use error::{SkillMatcherError, Result};
pub use matcher::SkillMatcher;
pub use similarity::SkillSimilarityCalculator;
pub use embedding::SkillEmbedder;
pub use distribution::create_beta_distribution_default as create_beta_distribution;
pub use config::{SkillMatcherConfig, SkillMatcherConfigBuilder, PenaltyConfig, ScoringConfig, DistributionConfig};
pub use traits::{SkillEmbedder as SkillEmbedderTrait, SimilarityCalculator, ScoringStrategy, ConfidenceCalculator};
pub use strategies::{DefaultScoringStrategy, ConservativeScoringStrategy, AggressiveScoringStrategy, SimpleConfidenceCalculator};
// Re-export commonly used traits
pub use simsimd::SpatialSimilarity;

pub fn init_tracing() {
    let env_filter = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));

    tracing_subscriber::fmt()
        .with_env_filter(env_filter)
        .with_target(false)
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_file(true)
        .with_line_number(true)
        .with_level(true)
        .init();
}

#[cfg(test)]
pub fn init_test_tracing() {
    use tracing_subscriber::fmt::format::FmtSpan;
    let subscriber = tracing_subscriber::fmt()
        .with_test_writer() // Write to stderr for tests
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_file(true)
        .with_line_number(true)
        .with_level(true)
        .with_span_events(FmtSpan::FULL) // Log enter/exit of spans
        .with_env_filter("info") // Set debug level for tests
        .try_init();

    // Ignore if already initialized
    if subscriber.is_err() {
        println!("Tracing already initialized");
    }
}