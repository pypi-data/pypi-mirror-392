use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use statrs::distribution::Beta;

use crate::domain::SkillDomain;

/// Represents a skill proficiency level with a current value and maximum possible value.
/// 
/// The proficiency level is represented as a ratio between the current value and maximum value,
/// allowing for standardized comparison across different scaling systems.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProficiencyLevel {
    /// Current proficiency value
    pub value: u32,
    /// Maximum possible proficiency value
    pub max: u32,
}

impl ProficiencyLevel {
    /// Creates a new ProficiencyLevel with the given value and maximum.
    ///
    /// # Arguments
    /// * `value` - Current proficiency value
    /// * `max` - Maximum possible proficiency value
    ///
    /// # Returns
    /// * `Some(ProficiencyLevel)` if value <= max
    /// * `None` if value > max
    pub fn new(value: u32, max: u32) -> Option<Self> {
        if value <= max {
            Some(Self { value, max })
        } else {
            None
        }
    }

    /// Converts the proficiency level to a ratio between 0.0 and 1.0
    ///
    /// # Returns
    /// A float representing the ratio of current value to maximum value
    pub fn to_ratio(&self) -> f64 {
        self.value as f64 / self.max as f64
    }
}

/// Represents a named skill with an associated proficiency level.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Skill {
    /// Name of the skill
    pub name: String,
    /// Proficiency level for this skill
    pub level: ProficiencyLevel,
}

impl Skill {
    /// Creates a new Skill with the given name and proficiency level.
    ///
    /// # Arguments
    /// * `name` - Name of the skill
    /// * `level` - Proficiency level for the skill
    pub fn new(name: impl Into<String>, level: ProficiencyLevel) -> Self {
        Self {
            name: name.into(),
            level,
        }
    }
}

/// Represents a skill with its statistical distribution and semantic embedding.
#[derive(Debug, Clone)]
pub struct SkillWithDistribution {
    /// Name of the skill
    pub name: String,
    /// Proficiency level for this skill
    pub level: ProficiencyLevel,
    /// Beta distribution representing the uncertainty in skill level
    pub distribution: Beta,
    /// Vector embedding representing the semantic meaning of the skill
    pub embedding: Vec<f32>,
    /// Skill domain classification for cross-domain penalty calculation
    pub domain: SkillDomain,
}

/// Represents a confidence interval with lower and upper bounds.
#[derive(Debug, Clone, serde::Serialize)]
pub struct ConfidenceInterval {
    /// Lower bound of the confidence interval
    pub lower: f64,
    /// Upper bound of the confidence interval
    pub upper: f64,
}

impl ConfidenceInterval {
    /// Creates a new ConfidenceInterval with the given bounds.
    ///
    /// # Arguments
    /// * `lower` - Lower bound of the interval
    /// * `upper` - Upper bound of the interval
    ///
    /// # Returns
    /// * `Some(ConfidenceInterval)` if lower <= upper
    /// * `None` if lower > upper
    pub fn new(lower: f64, upper: f64) -> Option<Self> {
        if lower <= upper {
            Some(Self { lower, upper })
        } else {
            None
        }
    }

    /// Returns the width of the confidence interval
    pub fn width(&self) -> f64 {
        self.upper - self.lower
    }
}

/// Represents the matching score for a single skill.
#[derive(Debug, serde::Serialize)]
pub struct SkillScore {
    /// Name of the skill being scored
    pub skill_name: String,
    /// Probability of meeting or exceeding the required proficiency level
    pub probability: f64,
    /// Confidence interval for the probability estimate
    pub confidence_interval: ConfidenceInterval,
    /// Mean of the probability distribution
    pub mean: f64,
    /// Variance of the probability distribution
    pub variance: f64,
}

/// Represents the overall result of matching a candidate's skills against requirements.
#[derive(Debug, serde::Serialize)]
pub struct MatchResult {
    /// Overall match score between 0.0 and 1.0
    pub overall_score: f64,
    /// Individual scores for each required skill
    pub skill_scores: Vec<SkillScore>,
    /// Pairwise semantic similarities between required and candidate skills (1.0 = identical, 0.0 = completely different)
    pub skill_similarities: HashMap<String, HashMap<String, f64>>,
    /// Pairwise scores combining semantic similarity and proficiency level (required -> candidate -> combined score)
    pub pairwise_scores: HashMap<String, HashMap<String, f64>>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_proficiency_level_creation() {
        assert!(ProficiencyLevel::new(3, 5).is_some());
        assert!(ProficiencyLevel::new(5, 5).is_some());
        assert!(ProficiencyLevel::new(6, 5).is_none());
    }

    #[test]
    fn test_proficiency_level_ratio() {
        let level = ProficiencyLevel::new(3, 5).unwrap();
        assert_eq!(level.to_ratio(), 0.6);

        let level = ProficiencyLevel::new(5, 5).unwrap();
        assert_eq!(level.to_ratio(), 1.0);
    }

    #[test]
    fn test_skill_creation() {
        let level = ProficiencyLevel::new(3, 5).unwrap();
        let skill = Skill::new("Python", level);
        
        assert_eq!(skill.name, "Python");
        assert_eq!(skill.level.value, 3);
        assert_eq!(skill.level.max, 5);
    }

    #[test]
    fn test_confidence_interval_creation() {
        assert!(ConfidenceInterval::new(0.2, 0.8).is_some());
        assert!(ConfidenceInterval::new(0.8, 0.2).is_none());
    }

    #[test]
    fn test_confidence_interval_width() {
        let ci = ConfidenceInterval::new(0.2, 0.8).unwrap();
        approx::assert_abs_diff_eq!(ci.width(), 0.6, epsilon = 1e-10);
    }

    #[test]
    fn test_skill_serialization() {
        let level = ProficiencyLevel::new(3, 5).unwrap();
        let skill = Skill::new("Python", level);
        
        let serialized = serde_json::to_string(&skill).unwrap();
        let deserialized: Skill = serde_json::from_str(&serialized).unwrap();
        
        assert_eq!(skill.name, deserialized.name);
        assert_eq!(skill.level.value, deserialized.level.value);
        assert_eq!(skill.level.max, deserialized.level.max);
    }
}