use ::competency_api::{init_tracing, MatchResult, Skill, SkillMatcher, SkillMatcherConfig};
use pyo3::prelude::*;
use pythonize::{depythonize, pythonize};
use std::path::PathBuf;

/// Initialize tracing/logging for the competency API
#[pyfunction]
fn init_logging() -> PyResult<()> {
    init_tracing();
    Ok(())
}

/// Calculate match score between required skills and candidate skills
///
/// Args:
///     required_skills: List of required skills with proficiency levels
///     candidate_skills: List of candidate's acquired skills with proficiency levels
///
/// Returns:
///     MatchResult containing overall_score, skill_scores, and similarity matrices
///
/// Environment Variables:
///     FASTEMBED_CACHE_PATH: Optional path to cache embedding models
#[pyfunction]
fn match_score(py: Python, required_skills: &PyAny, candidate_skills: &PyAny) -> PyResult<PyObject> {
    // Convert Python objects to Rust types using pythonize
    let required: Vec<Skill> = depythonize(required_skills)?;
    let candidate: Vec<Skill> = depythonize(candidate_skills)?;

    // Check for custom cache directory from environment
    let config = if let Ok(cache_path) = std::env::var("FASTEMBED_CACHE_PATH") {
        SkillMatcherConfig::builder()
            .cache_dir(PathBuf::from(cache_path))
            .build()
    } else {
        SkillMatcherConfig::default()
    };

    // Create matcher and calculate score
    let mut matcher = SkillMatcher::with_config(config)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    let result: MatchResult = matcher
        .calculate_match_score(candidate, required)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    // Convert result back to Python object
    pythonize(py, &result).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Calculate match scores for multiple pairs in a batch (much faster than individual calls)
///
/// Args:
///     pairs: List of tuples, where each tuple contains (required_skills, candidate_skills)
///
/// Returns:
///     List of MatchResult objects, one for each pair in the same order
///
/// Environment Variables:
///     FASTEMBED_CACHE_PATH: Optional path to cache embedding models
///
/// Example:
///     pairs = [
///         (required_skills_1, candidate_skills_1),
///         (required_skills_2, candidate_skills_2),
///         (required_skills_3, candidate_skills_3),
///     ]
///     results = batch_match_score(pairs)
#[pyfunction]
fn batch_match_score(py: Python, pairs: &PyAny) -> PyResult<PyObject> {
    // Convert Python list of tuples to Rust Vec of tuples
    let pairs_vec: Vec<(Vec<Skill>, Vec<Skill>)> = depythonize(pairs)?;

    // Check for custom cache directory from environment
    let config = if let Ok(cache_path) = std::env::var("FASTEMBED_CACHE_PATH") {
        SkillMatcherConfig::builder()
            .cache_dir(PathBuf::from(cache_path))
            .build()
    } else {
        SkillMatcherConfig::default()
    };

    // Create matcher and calculate batch scores
    let mut matcher = SkillMatcher::with_config(config)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    // Convert the pairs format from (required, candidate) to (candidate, required) for the Rust API
    let rust_pairs: Vec<(Vec<Skill>, Vec<Skill>)> = pairs_vec
        .into_iter()
        .map(|(required, candidate)| (candidate, required))
        .collect();

    let results: Vec<MatchResult> = matcher
        .calculate_batch_match_scores(rust_pairs)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    // Convert results back to Python objects
    pythonize(py, &results).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Python module definition
#[pymodule]
fn competency_api(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_logging, m)?)?;
    m.add_function(wrap_pyfunction!(match_score, m)?)?;
    m.add_function(wrap_pyfunction!(batch_match_score, m)?)?;
    Ok(())
}
