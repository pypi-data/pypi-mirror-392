//! Module for handling skill embedding operations using text embeddings.
//! 
//! This module provides functionality to convert skill names into vector embeddings
//! using a pre-trained text embedding model. These embeddings enable semantic 
//! similarity calculations between skills.

use fastembed::{InitOptions, TextEmbedding};
use crate::types::{Skill, SkillWithDistribution};
use crate::error::{Result, SkillMatcherError};
use crate::distribution::create_beta_distribution;
use crate::traits::SkillEmbedder as SkillEmbedderTrait;
use crate::config::SkillMatcherConfig;
use crate::domain::SkillDomain;
use std::sync::{Arc, Mutex, OnceLock};
use std::collections::HashMap;

/// Global cache for embedding models to avoid repeated initialization
static MODEL_CACHE: OnceLock<Arc<Mutex<HashMap<String, Arc<Mutex<TextEmbedding>>>>>> = OnceLock::new();

/// Get or create a cached embedding model
fn get_or_create_model(config: &SkillMatcherConfig) -> Result<Arc<Mutex<TextEmbedding>>> {
    use std::env;
    
    let cache = MODEL_CACHE.get_or_init(|| {
        Arc::new(Mutex::new(HashMap::new()))
    });
    
    let cache_dir_str = config.cache_dir.as_ref()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| {
            env::current_dir()
                .unwrap_or_else(|_| std::path::PathBuf::from("."))
                .join(".fastembed_cache")
                .to_string_lossy()
                .to_string()
        });
    
    let cache_key = format!("{:?}{}", config.embedding_model, cache_dir_str);
    
    let mut cache_guard = cache.lock().unwrap();
    
    if let Some(model) = cache_guard.get(&cache_key) {
        return Ok(Arc::clone(model));
    }
    
    // Create new model if not cached
    let cache_dir = config.cache_dir.clone().unwrap_or_else(|| {
        env::current_dir()
            .unwrap_or_else(|_| std::path::PathBuf::from("."))
            .join(".fastembed_cache")
    });
    
    let model = TextEmbedding::try_new(
        InitOptions::new(config.embedding_model.clone())
            .with_cache_dir(cache_dir)
            .with_show_download_progress(config.show_download_progress)
    ).map_err(|e| SkillMatcherError::EmbeddingInitError(e.to_string()))?;
    
    let arc_model = Arc::new(Mutex::new(model));
    cache_guard.insert(cache_key, Arc::clone(&arc_model));
    
    Ok(arc_model)
}



pub struct SkillEmbedder {
    /// The underlying text embedding model used to generate skill vectors.
    model: Arc<Mutex<TextEmbedding>>,
    /// Configuration for distribution parameters.
    config: SkillMatcherConfig,
}

impl SkillEmbedder {

    ///
    /// Initializes the text embedding model with the ParaphraseMLMiniLML12V2Q
    /// configuration, which is well-suited for semantic similarity tasks.
    ///
    /// # Errors
    ///
    /// Returns a `SkillMatcherError::EmbeddingInitError` if the embedding model
    /// fails to initialize.
    ///
    /// # Example
    ///
    /// Example: Create a new embedder with `SkillEmbedder::new()`.
    pub fn new() -> Result<Self> {
        Self::with_config(SkillMatcherConfig::default())
    }

    pub fn with_config(config: SkillMatcherConfig) -> Result<Self> {
        let model = get_or_create_model(&config)?;
        Ok(SkillEmbedder { model, config })
    }

    pub fn embed_skills(&mut self, skills: &[Skill]) -> Result<Vec<SkillWithDistribution>> {
        // Pre-allocate collections with known capacity
        let mut texts = Vec::with_capacity(skills.len());
        let mut result = Vec::with_capacity(skills.len());
        
        // Extract skill names for batch embedding
        for skill in skills {
            texts.push(skill.name.as_str());
        }
        
        // Generate embeddings for all skill names using the cached model
        let embeddings = {
            let mut model_guard = self.model.lock().unwrap();
            model_guard.embed(texts, None)
                .map_err(|e| SkillMatcherError::EmbeddingError(e.to_string()))?
        };
        
        // Combine original skills with their embeddings and create distributions
        for (skill, embedding) in skills.iter().zip(embeddings) {
            result.push(SkillWithDistribution {
                name: skill.name.clone(),
                level: skill.level.clone(),
                distribution: create_beta_distribution(&skill.level, &self.config.distribution_config)?,
                embedding,
                domain: SkillDomain::classify_skill(&skill.name),
            });
        }
        
        Ok(result)
    }
}



#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::ProficiencyLevel;

    #[test]
    fn test_skill_embedding() -> Result<()> {
        let mut embedder = SkillEmbedder::new()?;
        let skills = vec![
            Skill {
                name: "Python Programming".to_string(),
                level: ProficiencyLevel { value: 4, max: 5 }
            },
            Skill {
                name: "Data Analysis".to_string(),
                level: ProficiencyLevel { value: 3, max: 5 }
            }
        ];

        let embedded_skills = embedder.embed_skills(&skills)?;

        // Basic validation
        assert_eq!(embedded_skills.len(), 2);
        assert_eq!(embedded_skills[0].name, "Python Programming");
        assert_eq!(embedded_skills[1].name, "Data Analysis");
        
        // Verify embeddings are non-empty
        assert!(!embedded_skills[0].embedding.is_empty());
        assert!(!embedded_skills[1].embedding.is_empty());

        Ok(())
    }
}

impl SkillEmbedderTrait for SkillEmbedder {
    fn embed_skills(&mut self, skills: &[Skill]) -> Result<Vec<SkillWithDistribution>> {
        self.embed_skills(skills)
    }
}