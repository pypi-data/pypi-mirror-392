use thiserror::Error;

#[derive(Error, Debug)]
pub enum SkillMatcherError {
    #[error("Failed to initialize embedding model: {0}")]
    EmbeddingInitError(String),
    
    #[error("Failed to generate embeddings: {0}")]
    EmbeddingError(String),
    
    #[error("Failed to create beta distribution: {0}")]
    BetaDistributionError(String),
    
    #[error("Invalid skill data: {0}")]
    InvalidSkillData(String),

    #[error("No skills provided: candidate_skills={n_candidate}, required_skills={n_required}")]
    EmptySkills {
        n_candidate: usize,
        n_required: usize
    }
}

pub type Result<T> = std::result::Result<T, SkillMatcherError>;