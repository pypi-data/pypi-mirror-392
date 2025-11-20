#!/usr/bin/env python3
"""
Load data from data.json, run match_score, and save result to a new JSON file
"""

from competency_api import match_score
import json

# Load data from data.json
print("Loading data from data.json...")
with open('data.json', 'r') as f:
    data = json.load(f)

required_skills = data['requiredSkills']
candidate_skills = data['candidateSkills']

print(f"Required Skills: {len(required_skills)}")
print(f"Candidate Skills: {len(candidate_skills)}")

# Calculate match score
print("\nCalculating match score...")
result = match_score(required_skills, candidate_skills)

print(f"Overall Match Score: {result['overall_score']:.2%}")

# Save result to JSON file
output_file = 'match_result.json'
print(f"\nSaving result to {output_file}...")

with open(output_file, 'w') as f:
    json.dump(result, indent=2, fp=f)

print(f"✓ Successfully saved result to {output_file}")

# Print summary
print("\nResult Summary:")
print(f"  Overall Score: {result['overall_score']:.2%}")
print(f"  Number of Skill Scores: {len(result['skill_scores'])}")
print(f"  Top 3 Matching Skills:")
sorted_skills = sorted(result['skill_scores'], key=lambda x: x['probability'], reverse=True)
for i, skill in enumerate(sorted_skills[:3], 1):
    print(f"    {i}. {skill['skill_name']}: {skill['probability']:.2%}")
