#![allow(dead_code)]
#![allow(unused_imports)]

use std::collections::HashMap;
use approx::assert_relative_eq;

use competency_api::{
    SkillEmbedder,
    create_beta_distribution,
    Skill,
    ProficiencyLevel,
    SkillMatcher,
    Result,
};

fn create_skill(name: &str, value: u32, max: u32) -> Skill {
    Skill {
        name: name.to_string(),
        level: ProficiencyLevel { value, max },
    }
}

fn main() -> Result<()>{
    //let matcher = SkillMatcher::new()?;
    let p = create_beta_distribution(&ProficiencyLevel::new(4,5).unwrap())?;
    print!("{:?}", p);
    Ok(())

}