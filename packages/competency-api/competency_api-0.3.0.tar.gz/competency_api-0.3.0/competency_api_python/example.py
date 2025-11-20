#!/usr/bin/env python3
"""
Example usage of the competency-api Python binding.

This demonstrates various scenarios:
1. No penalty for exceeding expectations
2. Proficiency penalties
3. Related skills matching
"""

from competency_api import match_score, init_logging
import json


def print_result(title, result):
    """Pretty print a result with a title."""
    print(f"\n{title}")
    print("=" * len(title))
    print(json.dumps(result, indent=2))
    print()


# Initialize logging (optional)
init_logging()

# Scenario 1: No penalty for exceeding expectation
print("\n" + "=" * 60)
print("SCENARIO 1: No Penalty for Exceeding Expectation")
print("=" * 60)
candidate_skills_1 = [
    {"name": "Python", "level": {"value": 4, "max": 5}},
]

required_skills_1 = [
    {"name": "Python", "level": {"value": 1, "max": 5}},
]

result_1 = match_score(required_skills_1, candidate_skills_1)
print_result("Result", result_1)

# Scenario 2: Proficiency Penalty 1
print("=" * 60)
print("SCENARIO 2: Proficiency Penalty 1")
print("=" * 60)
candidate_skills_2 = [
    {"name": "Python", "level": {"value": 4, "max": 5}},
]

required_skills_2 = [
    {"name": "Python", "level": {"value": 5, "max": 5}},
]

result_2 = match_score(required_skills_2, candidate_skills_2)
print_result("Result", result_2)

# Scenario 3: Proficiency Penalty 2
print("=" * 60)
print("SCENARIO 3: Proficiency Penalty 2")
print("=" * 60)
candidate_skills_3 = [
    {"name": "Python", "level": {"value": 3, "max": 5}},
]

required_skills_3 = [
    {"name": "Python", "level": {"value": 5, "max": 5}},
]

result_3 = match_score(required_skills_3, candidate_skills_3)
print_result("Result", result_3)

# Scenario 4: Related Skills
print("=" * 60)
print("SCENARIO 4: Related Skills")
print("=" * 60)
candidate_skills_4 = [
    {"name": "CSS", "level": {"value": 4, "max": 5}},
    {"name": "Typescript", "level": {"value": 4, "max": 5}},
    {"name": "Javascript", "level": {"value": 4, "max": 5}},
    {"name": "HTML", "level": {"value": 4, "max": 5}},
]

required_skills_4 = [
    {"name": "Web development", "level": {"value": 4, "max": 5}},
]

result_4 = match_score(required_skills_4, candidate_skills_4)
print_result("Result", result_4)

print("\n" + "=" * 60)
print("All examples completed successfully!")
print("=" * 60)
