#!/usr/bin/env python3
"""
Test the competency matching API with data from data.json (without logging)
"""

from competency_api import match_score
import json

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
print("Top 10 Individual Skill Scores:")
print("=" * 60)

# Sort skills by probability and print top 10
sorted_skills = sorted(result['skill_scores'], key=lambda x: x['probability'], reverse=True)
for i, skill_score in enumerate(sorted_skills[:10], 1):
    print(f"\n{i}. {skill_score['skill_name']}:")
    print(f"   Probability: {skill_score['probability']:.2%}")
    print(f"   Mean: {skill_score['mean']:.4f}")
    print(f"   95% CI: [{skill_score['confidence_interval']['lower']:.4f}, {skill_score['confidence_interval']['upper']:.4f}]")

print("\n" + "=" * 60)
print("Bottom 5 Individual Skill Scores:")
print("=" * 60)

# Print bottom 5
for i, skill_score in enumerate(sorted_skills[-5:], 1):
    print(f"\n{i}. {skill_score['skill_name']}:")
    print(f"   Probability: {skill_score['probability']:.2%}")
    print(f"   Mean: {skill_score['mean']:.4f}")
    print(f"   95% CI: [{skill_score['confidence_interval']['lower']:.4f}, {skill_score['confidence_interval']['upper']:.4f}]")

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
