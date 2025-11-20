#!/usr/bin/env python3
"""
Test the competency matching API with data from data.json and output as JSON
"""

from competency_api import match_score
import json

# Load data from data.json
with open('data.json', 'r') as f:
    data = json.load(f)

required_skills = data['requiredSkills']
candidate_skills = data['candidateSkills']

# Calculate match score
result = match_score(required_skills, candidate_skills)

# Print the full result as pretty-printed JSON
print(json.dumps(result, indent=2))
