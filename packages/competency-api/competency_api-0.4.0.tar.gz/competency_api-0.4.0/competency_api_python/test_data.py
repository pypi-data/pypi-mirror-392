#!/usr/bin/env python3
"""
Test the competency matching API with data from data.json
"""

from competency_api import match_score, init_logging
import json

# Initialize logging (optional)
init_logging()

# Load data from data.json
with open('data.json', 'r') as f:
    data = json.load(f)

required_skills = data['requiredSkills']
candidate_skills = data['candidateSkills']

print("\n" + "=" * 60)
print("COMPETENCY MATCHING TEST")
print("=" * 60)
print(f"Required Skills: {len(required_skills)}")
print(f"Candidate Skills: {len(candidate_skills)}")
print("=" * 60)

# Calculate match score
result = match_score(required_skills, candidate_skills)

# Print overall score
print(f"\nOverall Match Score: {result['overall_score']:.2%}")
print("\n" + "=" * 60)
print("Individual Skill Scores:")
print("=" * 60)

# Print individual skill scores
for skill_score in result['skill_scores']:
    print(f"\n{skill_score['skill_name']}:")
    print(f"  Probability: {skill_score['probability']:.2%}")
    print(f"  Mean: {skill_score['mean']:.4f}")
    print(f"  Variance: {skill_score['variance']:.6f}")
    print(f"  95% CI: [{skill_score['confidence_interval']['lower']:.4f}, {skill_score['confidence_interval']['upper']:.4f}]")

print("\n" + "=" * 60)
print("Full Result (JSON):")
print("=" * 60)
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
