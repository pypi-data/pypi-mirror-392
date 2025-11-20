use competency_api::*;

#[cfg(feature = "dhat")]
use dhat::{Dhat, DhatAlloc};

#[cfg(feature = "dhat")]
#[global_allocator]
static ALLOCATOR: DhatAlloc = DhatAlloc;

fn main() {
    #[cfg(feature = "dhat")]
    let _dhat = Dhat::start_heap_profiling();
    
    println!("Starting memory profiling of competency API...");
    
    // Create test data
    let candidate_skills = (0..100).map(|i| Skill {
        name: format!("Skill_{}", i),
        level: ProficiencyLevel { 
            value: (i % 5) as u32 + 1, 
            max: 5 
        },
    }).collect::<Vec<_>>();
    
    let required_skills = (0..50).map(|i| Skill {
        name: format!("Required_{}", i),
        level: ProficiencyLevel { 
            value: (i % 5) as u32 + 1, 
            max: 5 
        },
    }).collect::<Vec<_>>();
    
    println!("Created {} candidate skills and {} required skills", 
             candidate_skills.len(), required_skills.len());
    
    // Profile the main matching operation
    let mut matcher = SkillMatcher::new().unwrap();
    println!("Created matcher");
    
    let result = matcher.calculate_match_score(candidate_skills, required_skills).unwrap();
    println!("Match completed with overall score: {:.3}", result.overall_score);
    
    // Profile individual components
    println!("\nProfiling individual components...");
    
    // Test embedding
    let test_skills = (0..20).map(|i| Skill {
        name: format!("Test_{}", i),
        level: ProficiencyLevel { value: 3, max: 5 },
    }).collect::<Vec<_>>();
    
    let mut embedder = SkillEmbedder::new().unwrap();
    let embedded_skills = embedder.embed_skills(&test_skills).unwrap();
    println!("Embedded {} skills", embedded_skills.len());
    
    // Test similarity calculation
    let similarities = SkillSimilarityCalculator::calculate_similarities(
        &embedded_skills[0..10],
        &embedded_skills[10..20],
    );
    println!("Calculated similarities: {}x{}", similarities.len(), similarities[0].len());
    
    println!("Memory profiling complete!");
    
    #[cfg(feature = "dhat")]
    {
        println!("\nDHAT profiling data will be written to dhat-heap.json");
        println!("View with: dh_view.py dhat-heap.json");
    }
}