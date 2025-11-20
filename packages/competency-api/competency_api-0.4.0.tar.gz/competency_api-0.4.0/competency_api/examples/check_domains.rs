use competency_api::SkillDomain;

fn main() {
    let test_skills = vec![
        "React",
        "Node.js", 
        "JavaScript",
        "Frontend Development",
        "Web Development",
        "Machine Learning",
        "Data Science",
        "Python",
        "PostgreSQL",
        "SQL",
        "TypeScript",
    ];
    
    println!("Skill Domain Classifications:");
    println!("{}", "=".repeat(60));
    for skill in test_skills {
        let domain = SkillDomain::classify_skill(skill);
        println!("{:30} -> {:?}", skill, domain);
    }
    
    println!("\n{}", "=".repeat(60));
    println!("Cross-Domain Penalties:");
    println!("{}", "=".repeat(60));
    
    // Check penalties for problematic pairs
    let pairs = vec![
        ("React", "Frontend Development"),
        ("JavaScript", "Web Development"),
        ("Machine Learning", "Data Science"),
        ("PostgreSQL", "SQL"),
    ];
    
    for (skill1, skill2) in pairs {
        let domain1 = SkillDomain::classify_skill(skill1);
        let domain2 = SkillDomain::classify_skill(skill2);
        let penalty = domain1.cross_domain_penalty(&domain2);
        println!("{:20} ({:?}) -> {:25} ({:?}): penalty = {:.2}", 
                 skill1, domain1, skill2, domain2, penalty);
    }
}
