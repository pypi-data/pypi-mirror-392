//! Module for handling probability distributions in skill proficiency modeling.
//! 
//! This module provides functionality for working with Beta distributions and mixtures
//! of Beta distributions to model skill proficiency levels and their uncertainties.
//! It implements methods for computing probability densities, cumulative distributions,
//! and confidence intervals.

use statrs::distribution::{Beta, ContinuousCDF, Continuous};
use statrs::statistics::Distribution;
use crate::ProficiencyLevel;
use crate::types::ConfidenceInterval;
use crate::error::{Result, SkillMatcherError};
use crate::config::DistributionConfig;

/// Represents a weighted mixture of Beta distributions.
/// 
/// A beta mixture model combines multiple Beta distributions with associated weights
/// to create a more flexible probability distribution. This is particularly useful
/// for modeling skill proficiencies where there may be multiple possible proficiency
/// levels or uncertainty in the assessment.
/// 
/// The weights of all components must sum to 1.0.
/// 
/// # Example
/// 
/// Create a mixture by providing weighted Beta distribution components that sum to 1.0.
#[derive(Debug)]
pub struct BetaMixture {
    /// Vector of (weight, distribution) pairs that make up the mixture.
    /// Each weight represents the relative importance of its associated distribution.
    components: Vec<(f64, Beta)>,
}

impl BetaMixture {
    /// Creates a new mixture of Beta distributions.
    /// 
    /// # Arguments
    /// 
    /// * `components` - Vector of (weight, Beta) pairs. Weights must sum to 1.0
    ///                 within a small numerical tolerance.
    /// 
    /// # Returns
    /// 
    /// Returns a Result containing the new BetaMixture if the weights are valid.
    /// 
    /// # Errors
    /// 
    /// Returns a `SkillMatcherError::InvalidDistributionParameters` if the weights
    /// don't sum to 1.0 within tolerance.
    /// 
    /// # Example
    /// 
    /// Create weighted components where each weight represents the relative importance of its distribution.
    pub fn new(components: Vec<(f64, Beta)>) -> Result<Self> {
        // Validate that weights sum to 1
        let weight_sum: f64 = components.iter().map(|(w, _)| w).sum();
        if (weight_sum - 1.0).abs() > 1e-6 {
            return Err(SkillMatcherError::InvalidSkillData(
                "Mixture weights must sum to 1".to_string()
            ));
        }
        Ok(BetaMixture { components })
    }

    /// Calculates the probability density function (PDF) at a given point.
    /// 
    /// The PDF value represents the relative likelihood of the skill level being
    /// at the specified point.
    /// 
    /// # Arguments
    /// 
    /// * `x` - The point at which to evaluate the PDF (between 0 and 1)
    /// 
    /// # Returns
    /// 
    /// The weighted sum of component PDFs at the specified point.
    /// 
    /// # Example
    /// 
    /// Example: `mixture.pdf(0.7)` evaluates density at 70% proficiency.
    #[allow(dead_code)]
    pub fn pdf(&self, x: f64) -> f64 {
        self.components.iter()
            .map(|(w, beta)| w * beta.pdf(x))
            .sum()
    }

    /// Calculates the cumulative distribution function (CDF) at a given point.
    /// 
    /// The CDF value represents the probability that the skill level is less than
    /// or equal to the specified point.
    /// 
    /// # Arguments
    /// 
    /// * `x` - The point at which to evaluate the CDF (between 0 and 1)
    /// 
    /// # Returns
    /// 
    /// The weighted sum of component CDFs at the specified point.
    pub fn cdf(&self, x: f64) -> f64 {
        self.components.iter()
            .map(|(w, beta)| w * beta.cdf(x))
            .sum()
    }

    /// Calculates the mean (expected value) of the mixture distribution.
    /// 
    /// # Returns
    /// 
    /// The weighted average of component means.
    pub fn mean(&self) -> f64 {
        self.components.iter()
            .map(|(w, beta)| w * beta.mean().unwrap_or(0.))
            .sum()
    }

    /// Calculates the variance of the mixture distribution.
    /// 
    /// The variance represents the spread or dispersion of the distribution around
    /// its mean. It accounts for both the individual component variances and the
    /// distances between component means.
    /// 
    /// # Returns
    /// 
    /// The total variance of the mixture.
    pub fn variance(&self) -> f64 {
        let mean = self.mean();
        let e_x2: f64 = self.components.iter()
            .map(|(w, beta)| {
                w * (beta.variance().unwrap_or(0.1) + beta.mean().unwrap_or(0.).powi(2))
            })
            .sum();
        e_x2 - mean.powi(2)
    }

    /// Calculates the inverse CDF (quantile function) using numerical methods.
    /// 
    /// This function finds the value x where CDF(x) = p using binary search.
    /// It's useful for finding confidence intervals and percentiles.
    /// 
    /// # Arguments
    /// 
    /// * `p` - The probability value (between 0 and 1)
    /// 
    /// # Returns
    /// 
    /// The value x where CDF(x) = p
    pub fn inverse_cdf(&self, p: f64) -> f64 {
        if p <= 0.0 { return 0.0; }
        if p >= 1.0 { return 1.0; }

        let mut left = 0.0;
        let mut right = 1.0;
        let tolerance = 1e-6;
        
        while right - left > tolerance {
            let mid = (left + right) / 2.0;
            let cdf = self.cdf(mid);
            
            if cdf < p {
                left = mid;
            } else {
                right = mid;
            }
        }
        
        (left + right) / 2.0
    }
}

/// Calculates a confidence interval for a given mixture distribution.
/// 
/// # Arguments
/// 
/// * `dist` - The beta mixture distribution
/// * `confidence` - The confidence level (e.g., 0.95 for 95% confidence)
/// 
/// # Returns
/// 
/// A `ConfidenceInterval` containing the lower and upper bounds.
/// 
/// # Example
/// 
/// Example: `calculate_confidence_interval(&mixture, 0.95)` returns the 95% confidence interval.
pub fn calculate_confidence_interval(dist: &BetaMixture, confidence: f64) -> ConfidenceInterval {
    let alpha = (1.0 - confidence) / 2.0;
    ConfidenceInterval {
        lower: dist.inverse_cdf(alpha),
        upper: dist.inverse_cdf(1.0 - alpha),
    }
}

/// Creates a Beta distribution for a given proficiency level that models the uncertainty
/// in the skill assessment.
///
/// # Theory
/// The Beta distribution is used to model skill proficiency because:
/// - It's bounded between [0,1], matching normalized skill levels
/// - It can represent various shapes of uncertainty based on the mean
/// - Its parameters (α,β) have interpretable properties
///
/// # Mathematical Details
/// For a target mean μ and variance σ², the parameters are calculated as:
/// - α = ((1-μ)/σ² - 1/μ)μ²
/// - β = α(1/μ - 1)
///
/// To ensure valid parameters (α,β > 0), the variance must satisfy:
/// σ² < μ(1-μ)
///
/// The maximum possible variance for any mean is 0.25 (occurring at μ = 0.5).
///
/// # Arguments
/// * `level` - A ProficiencyLevel containing the skill value and maximum possible value
/// * `config` - Configuration for distribution parameters
///
/// # Returns
/// * `Result<Beta>` - A Beta distribution with parameters matching the desired mean and largest
///                    possible variance that ensures valid parameters
///
/// # Example
/// Example: A ProficiencyLevel with value 3 and max 5 creates a Beta distribution with mean ~0.6.
pub fn create_beta_distribution(level: &ProficiencyLevel, config: &DistributionConfig) -> Result<Beta> {
    let mean = level.to_ratio();
    
    // Handle edge cases for mean = 0.0 or 1.0
    if mean == 0.0 {
        // For zero proficiency, use parameters that concentrate probability mass near 0
        return Beta::new(config.zero_proficiency_alpha, config.zero_proficiency_beta)
            .map_err(|e| SkillMatcherError::BetaDistributionError(e.to_string()));
    } else if mean == 1.0 {
        // For perfect proficiency, use parameters that concentrate probability mass near 1
        return Beta::new(config.perfect_proficiency_alpha, config.perfect_proficiency_beta)
            .map_err(|e| SkillMatcherError::BetaDistributionError(e.to_string()));
    }

    // Calculate maximum allowable variance for this mean
    // The variance must be less than μ(1-μ) for valid alpha/beta parameters
    let max_variance = mean * (1.0 - mean);
    
    // Target variance - adjust if needed to ensure valid parameters
    let variance = if config.desired_variance >= max_variance {
        // Use configured safety factor of max variance to ensure we stay safely within bounds
        max_variance * config.max_variance_factor
    } else {
        config.desired_variance
    };

    // Calculate alpha using the formula: α = ((1-μ)/σ² - 1/μ)μ²
    let alpha = ((1.0 - mean) / variance - 1.0 / mean) * mean * mean;
    
    // Calculate beta using the formula: β = α(1/μ - 1)
    let beta = alpha * (1.0 / mean - 1.0);

    // Verify parameters are valid
    if alpha <= 0.0 || beta <= 0.0 {
        return Err(SkillMatcherError::BetaDistributionError(format!(
            "Invalid Beta parameters: α={}, β={}. Mean={}, variance={}", 
            alpha, beta, mean, variance
        )));
    }

    // Create the Beta distribution with calculated parameters
    Beta::new(alpha, beta)
        .map_err(|e| SkillMatcherError::BetaDistributionError(e.to_string()))
}

/// Backward compatibility wrapper for create_beta_distribution.
/// Uses default distribution configuration.
pub fn create_beta_distribution_default(level: &ProficiencyLevel) -> Result<Beta> {
    create_beta_distribution(level, &DistributionConfig::default())
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_beta_mixture_creation() -> Result<()> {
        // Valid mixture
        let components = vec![
            (0.6, Beta::new(2.0, 3.0).unwrap()),
            (0.4, Beta::new(3.0, 2.0).unwrap()),
        ];
        let mixture = BetaMixture::new(components)?;
        assert!(mixture.mean() >= 0.0 && mixture.mean() <= 1.0);

        // Invalid weights (don't sum to 1)
        let invalid_components = vec![
            (0.3, Beta::new(2.0, 3.0).unwrap()),
            (0.3, Beta::new(3.0, 2.0).unwrap()),
        ];
        assert!(BetaMixture::new(invalid_components).is_err());

        Ok(())
    }

    #[test]
    fn test_confidence_interval() -> Result<()> {
        let components = vec![
            (0.5, Beta::new(5.0, 2.0).unwrap()),
            (0.5, Beta::new(2.0, 5.0).unwrap()),
        ];
        let mixture = BetaMixture::new(components)?;
        
        let ci = calculate_confidence_interval(&mixture, 0.95);
        assert!(ci.lower < ci.upper);
        assert!(ci.lower >= 0.0 && ci.upper <= 1.0);

        Ok(())
    }

    #[test]
    fn test_distribution_properties() -> Result<()> {
        let components = vec![
            (0.7, Beta::new(4.0, 2.0).unwrap()),
            (0.3, Beta::new(2.0, 4.0).unwrap()),
        ];
        let mixture = BetaMixture::new(components)?;

        // Test PDF
        let pdf_sum = (0..100)
            .map(|i| mixture.pdf(i as f64 / 100.0) / 100.0)
            .sum::<f64>();
        assert!((pdf_sum - 1.0).abs() < 0.1);  // Approximate integration

        // Test CDF properties
        assert!((mixture.cdf(0.0) - 0.0).abs() < 1e-6);
        assert!((mixture.cdf(1.0) - 1.0).abs() < 1e-6);
        assert!(mixture.cdf(0.5) > 0.0 && mixture.cdf(0.5) < 1.0);

        Ok(())
    }
}