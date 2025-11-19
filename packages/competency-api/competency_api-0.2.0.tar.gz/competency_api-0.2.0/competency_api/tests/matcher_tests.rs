use std::collections::HashMap;
use competency_api::{
    Skill,
    ProficiencyLevel,
    SkillMatcher,
    Result,
};

#[cfg(test)]
mod tests {

    use super::*;

    // Test helper functions
    fn create_skill(name: &str, value: u32, max: u32) -> Skill {
        Skill {
            name: name.to_string(),
            level: ProficiencyLevel { value, max },
        }
    }

    fn setup_matcher() -> Result<SkillMatcher> {
        SkillMatcher::new()
    }

    #[test]
    fn test_exact_skill_matches() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            create_skill("Python", 4, 5),
            create_skill("Java", 3, 5),
            create_skill("SQL", 5, 5),
        ];
        
        let required_skills = vec![
            create_skill("Python", 5, 5),
            create_skill("Java", 3, 5),
            create_skill("SQL", 5, 5),
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        // Overall score should be high since candidate meets or exceeds all requirements
        assert!(result.overall_score > 0.9);
        
        // Check individual skill scores
        let skill_map: HashMap<_, _> = result.skill_scores.iter()
            .map(|s| (s.skill_name.as_str(), s))
            .collect();
        // Python: Candidate exceeds requirement
        assert!(skill_map["Python"].probability > 0.7);
        // Java: Candidate matches exactly
        assert!(skill_map["Java"].probability > 0.90);
        // SQL: Candidate exceeds requirement
        assert!(skill_map["SQL"].probability > 0.95);
        
        Ok(())
    }

    #[test]
    fn test_overqualified() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            create_skill("Python", 5, 5),
            create_skill("Java", 3, 5),
            create_skill("SQL", 4, 5),
        ];
        
        let required_skills = vec![
            create_skill("Python", 4, 5),
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        // Overall score should be high since candidate meets or exceeds all requirements
        assert!(result.overall_score > 0.9);
        
        Ok(())
    }

    #[test]
    fn test_related_skill_matches() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            create_skill("JavaScript", 5, 5),
            create_skill("PostgreSQL", 4, 5),
            create_skill("Machine Learning", 4, 5),
        ];
        
        let required_skills = vec![
            create_skill("TypeScript", 3, 5),      // Related to JavaScript
            create_skill("SQL", 3, 5),             // Related to PostgreSQL
            create_skill("Deep Learning", 3, 5),    // Related to Machine Learning
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        
        // Check that related skills are recognized
        let skill_map: HashMap<_, _> = result.skill_scores.iter()
            .map(|s| (s.skill_name.as_str(), s))
            .collect();
        
        // TypeScript should have some probability due to JavaScript expertise
        assert!(skill_map["TypeScript"].probability > 0.2);
        // SQL should have high probability due to PostgreSQL expertise
        assert!(skill_map["SQL"].probability > 0.8);
        // Deep Learning should have high probability due to ML expertise
        assert!(skill_map["Deep Learning"].probability > 0.8);
        
        Ok(())
    }

    #[test]
    fn test_skill_gaps() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            create_skill("Python", 2, 5),
            create_skill("Data Analysis", 2, 5),
        ];
        
        let required_skills = vec![
            create_skill("Python", 3, 5),
            create_skill("Data Science", 4, 5),
            create_skill("Statistics", 3, 5),
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        // Overall score should be lower due to gaps
        assert!(result.overall_score < 0.7);
        
        let skill_map: HashMap<_, _> = result.skill_scores.iter()
            .map(|s| (s.skill_name.as_str(), s))
            .collect();
        
        // Python: Candidate below requirement
        assert!(skill_map["Python"].probability < 0.7);
        // Data Science: Partial match through Data Analysis
        assert!(skill_map["Data Science"].probability < 0.7);
        // Statistics: No direct match, but some transfer from Data Analysis
        assert!(skill_map["Statistics"].probability < 0.6);
        
        Ok(())
    }

    #[test]
    fn test_confidence_intervals() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            create_skill("Software Engineering", 5, 5),
            create_skill("System Design", 4, 5),
        ];
        
        let required_skills = vec![
            create_skill("Software Development", 4, 5),
            create_skill("Distributed Systems", 4, 5),
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        
        for score in &result.skill_scores {
            // Verify confidence intervals are valid
            assert!(score.confidence_interval.lower <= score.mean);
            assert!(score.confidence_interval.upper >= score.mean);
            assert!(score.confidence_interval.lower >= 0.0);
            assert!(score.confidence_interval.upper <= 1.0);
            
            // Check variance is reasonable
            assert!(score.variance >= 0.0);
            assert!(score.variance <= 1.0);
        }
        
        Ok(())
    }

    #[test]
    fn test_diverse_skill_set() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let candidate_skills = vec![
            // Technical skills
            create_skill("Rust", 5, 5),
            create_skill("Systems Programming", 4, 5),
            // Data skills
            create_skill("Data Mining", 4, 5),
            create_skill("Statistical Analysis", 3, 5),
            // Soft skills
            create_skill("Project Management", 4, 5),
            create_skill("Team Leadership", 5, 5),
        ];
        
        let required_skills = vec![
            // Technical requirements
            create_skill("Low Level Programming", 4, 5),
            create_skill("C++", 3, 5),
            // Data requirements
            create_skill("Data Science", 3, 5),
            create_skill("Machine Learning", 3, 5),
            // Management requirements
            create_skill("Team Management", 4, 5),
            create_skill("Agile Methodologies", 3, 5),
        ];
        
        let result = matcher.calculate_match_score(candidate_skills, required_skills)?;
        let skill_map: HashMap<_, _> = result.skill_scores.iter()
            .map(|s| (s.skill_name.as_str(), s))
            .collect();
        
        // Technical skill transfer
        assert!(skill_map["Low Level Programming"].probability > 0.5); // Strong match from Rust + Systems
        assert!(skill_map["C++"].probability > 0.35);  // Good transfer from Rust
        
        // Data skill transfer
        assert!(skill_map["Data Science"].probability > 0.8); // Good match from Data Mining + Stats
        assert!(skill_map["Machine Learning"].probability > 0.35); // Moderate transfer
        
        // Management skill transfer
        assert!(skill_map["Team Management"].probability > 0.8); // Strong match from Leadership
        assert!(skill_map["Agile Methodologies"].probability > 0.5); // Some transfer from Project Management
        
        Ok(())
    }

    #[test]
    fn test_edge_cases() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        // Test single skill match
        let result = matcher.calculate_match_score(
            vec![create_skill("Python", 5, 5)],
            vec![create_skill("Python", 5, 5)],
        )?;
        assert!(result.overall_score > 0.95);
        
        // Test max level differences
        let result = matcher.calculate_match_score(
            vec![create_skill("Skill", 3, 3)], // Different max level
            vec![create_skill("Skill", 4, 5)],
        )?;
        assert!(result.overall_score > 0.9); // Should handle different scales
        
        Ok(())
    }

    #[test]
    fn test_debuf_cases() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        // Test single skill match
        let result = matcher.calculate_match_score(
            vec![create_skill("Project Management", 5, 5)],
            vec![create_skill("Customer Focus", 3, 5)],
        )?;
        println!("{:?}", result);
        
        Ok(())
    }

    #[test]
    fn test_comprehensive_semantic_similarity() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let test_cases = vec![
            // Very high similarity - should score >0.8
            (vec![create_skill("PostgreSQL", 5, 5)], vec![create_skill("SQL", 4, 5)], 0.8, "PostgreSQL is SQL"),
            (vec![create_skill("JavaScript", 5, 5)], vec![create_skill("TypeScript", 3, 5)], 0.8, "JS/TS very similar"),
            (vec![create_skill("Machine Learning", 5, 5)], vec![create_skill("Data Science", 4, 5)], 0.8, "ML is core to DS"),
            
            // High similarity - should score >0.6  
            (vec![create_skill("Python", 5, 5)], vec![create_skill("Programming", 4, 5)], 0.6, "Python is programming"),
            (vec![create_skill("Statistics", 4, 5)], vec![create_skill("Data Analysis", 3, 5)], 0.6, "Stats core to analysis"),
            
            // Moderate similarity - should score >0.5
            (vec![create_skill("MySQL", 4, 5)], vec![create_skill("Database", 3, 5)], 0.5, "MySQL is database"),
        ];
        
        for (candidate, required, expected_min, description) in test_cases {
            let candidate_name = candidate[0].name.clone();
            let required_name = required[0].name.clone();
            let result = matcher.calculate_match_score(candidate, required)?;
            assert!(
                result.overall_score >= expected_min, 
                "{}: {} -> {} scored {:.3}, expected >= {:.1}", 
                description, candidate_name, required_name, result.overall_score, expected_min
            );
        }
        
        Ok(())
    }

    #[test]
    fn test_perfect_matches_high_score() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let result = matcher.calculate_match_score(
            vec![create_skill("Python", 5, 5)],
            vec![create_skill("Python", 4, 5)],  // Candidate exceeds requirement
        )?;
        
        assert!(result.overall_score > 0.95);  // Should be near perfect
        Ok(())
    }

    #[test]
    fn test_tech_stack_similarity() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let result = matcher.calculate_match_score(
            vec![
                create_skill("React", 5, 5),
                create_skill("Node.js", 4, 5),
                create_skill("JavaScript", 5, 5),
            ],
            vec![
                create_skill("Frontend Development", 4, 5),
                create_skill("Web Development", 3, 5),
            ],
        )?;
        
        assert!(result.overall_score > 0.6);  // Related tech stack should score reasonably
        Ok(())
    }

    #[test]
    fn test_domain_expertise_transfer() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let test_cases = vec![
            // Finance domain
            (
                vec![create_skill("Investment Banking", 5, 5), create_skill("Risk Management", 4, 5)],
                vec![create_skill("Financial Analysis", 3, 5)]
            ),
            // Healthcare domain  
            (
                vec![create_skill("Clinical Research", 5, 5), create_skill("Medical Devices", 4, 5)],
                vec![create_skill("Healthcare", 3, 5)]
            ),
        ];
        
        for (candidate, required) in test_cases {
            let result = matcher.calculate_match_score(candidate, required)?;
            assert!(result.overall_score > 0.4, "Domain expertise should show some transfer");
        }
        
        Ok(())
    }

    #[test]
    fn test_skill_level_scaling() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        // Test different scales but same relative proficiency
        let result = matcher.calculate_match_score(
            vec![create_skill("Python", 8, 10)],    // 80% proficiency
            vec![create_skill("Python", 4, 5)],     // 80% proficiency
        )?;
        
        assert!(result.overall_score > 0.95);  // Same relative level should score very high
        Ok(())
    }

    #[test]
    fn test_perfect_match_different_scales() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let result = matcher.calculate_match_score(
            vec![create_skill("Data Analysis", 10, 10)],  // 100% on 10-point scale
            vec![create_skill("Data Analysis", 3, 3)],    // 100% on 3-point scale  
        )?;
        
        assert!(result.overall_score > 0.98);  // Perfect relative match
        Ok(())
    }

    #[test]
    fn test_overqualified_multiple_skills() -> Result<()> {
        let mut matcher = setup_matcher()?;
        
        let result = matcher.calculate_match_score(
            vec![
                create_skill("Senior Software Engineer", 5, 5),
                create_skill("System Architecture", 5, 5),
                create_skill("Team Leadership", 4, 5),
            ],
            vec![
                create_skill("Software Development", 3, 5),
            ],
        )?;
        
        assert!(result.overall_score > 0.8);  // Overqualified should score very high
        Ok(())
    }
}