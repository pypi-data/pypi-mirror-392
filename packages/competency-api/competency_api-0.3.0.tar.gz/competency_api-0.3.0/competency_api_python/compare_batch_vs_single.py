#!/usr/bin/env python3
"""
Compare batch_match_score vs individual match_score calls to verify they produce the same results
"""

from competency_api import match_score, batch_match_score
import json

# Define multiple test cases
test_cases = [
    # Test Case 1: Exact match
    {
        "name": "Exact Match",
        "required": [{"name": "Python", "level": {"value": 4, "max": 5}}],
        "candidate": [{"name": "Python", "level": {"value": 4, "max": 5}}]
    },
    # Test Case 2: Proficiency penalty
    {
        "name": "Proficiency Penalty",
        "required": [{"name": "JavaScript", "level": {"value": 5, "max": 5}}],
        "candidate": [{"name": "JavaScript", "level": {"value": 3, "max": 5}}]
    },
    # Test Case 3: Related skills
    {
        "name": "Related Skills",
        "required": [{"name": "Web Development", "level": {"value": 4, "max": 5}}],
        "candidate": [
            {"name": "HTML", "level": {"value": 4, "max": 5}},
            {"name": "CSS", "level": {"value": 4, "max": 5}},
            {"name": "JavaScript", "level": {"value": 4, "max": 5}}
        ]
    },
    # Test Case 4: Multiple required skills
    {
        "name": "Multiple Required Skills",
        "required": [
            {"name": "Python", "level": {"value": 4, "max": 5}},
            {"name": "Machine Learning", "level": {"value": 3, "max": 5}}
        ],
        "candidate": [
            {"name": "Python", "level": {"value": 5, "max": 5}},
            {"name": "Deep Learning", "level": {"value": 3, "max": 5}},
            {"name": "TensorFlow", "level": {"value": 4, "max": 5}}
        ]
    },
    # Test Case 5: From data.json (subset)
    {
        "name": "HR Skills Subset",
        "required": [
            {"name": "Change Management & Transformation", "level": {"value": 5, "max": 5}},
            {"name": "Compensation and Benefits Strategy", "level": {"value": 5, "max": 5}},
            {"name": "Performance management", "level": {"value": 4, "max": 5}}
        ],
        "candidate": [
            {"name": "Change Management", "level": {"value": 5, "max": 5}},
            {"name": "Compensation and Benefits Strategy", "level": {"value": 5, "max": 5}},
            {"name": "Performance Management", "level": {"value": 5, "max": 5}},
            {"name": "Talent Management", "level": {"value": 5, "max": 5}}
        ]
    }
]

print("\n" + "=" * 80)
print("COMPARING BATCH VS INDIVIDUAL MATCH SCORE")
print("=" * 80)

# Method 1: Individual calls
print("\n[1/2] Running individual match_score calls...")
individual_results = []
for i, test_case in enumerate(test_cases, 1):
    print(f"  - Processing test case {i}/{len(test_cases)}: {test_case['name']}")
    result = match_score(test_case['required'], test_case['candidate'])
    individual_results.append(result)

# Method 2: Batch call
print("\n[2/2] Running batch_match_score...")
pairs = [(tc['required'], tc['candidate']) for tc in test_cases]
batch_results = batch_match_score(pairs)

print("\n" + "=" * 80)
print("COMPARISON RESULTS")
print("=" * 80)

all_match = True
for i, test_case in enumerate(test_cases):
    individual = individual_results[i]
    batch = batch_results[i]

    print(f"\nTest Case {i+1}: {test_case['name']}")
    print("-" * 80)

    # Compare overall scores
    individual_score = individual['overall_score']
    batch_score = batch['overall_score']
    score_match = abs(individual_score - batch_score) < 1e-10

    print(f"Overall Score:")
    print(f"  Individual: {individual_score:.10f}")
    print(f"  Batch:      {batch_score:.10f}")
    print(f"  Match:      {'✓ YES' if score_match else '✗ NO'}")

    # Compare number of skill scores
    num_skills_match = len(individual['skill_scores']) == len(batch['skill_scores'])
    print(f"\nNumber of Skill Scores:")
    print(f"  Individual: {len(individual['skill_scores'])}")
    print(f"  Batch:      {len(batch['skill_scores'])}")
    print(f"  Match:      {'✓ YES' if num_skills_match else '✗ NO'}")

    # Compare individual skill scores
    skill_scores_match = True
    if num_skills_match:
        for j, (ind_skill, batch_skill) in enumerate(zip(individual['skill_scores'], batch['skill_scores'])):
            name_match = ind_skill['skill_name'] == batch_skill['skill_name']
            prob_match = abs(ind_skill['probability'] - batch_skill['probability']) < 1e-10
            mean_match = abs(ind_skill['mean'] - batch_skill['mean']) < 1e-10

            if not (name_match and prob_match and mean_match):
                skill_scores_match = False
                print(f"\n  Skill {j+1} mismatch: {ind_skill['skill_name']}")
                print(f"    Individual: prob={ind_skill['probability']:.10f}, mean={ind_skill['mean']:.10f}")
                print(f"    Batch:      prob={batch_skill['probability']:.10f}, mean={batch_skill['mean']:.10f}")

    if skill_scores_match and num_skills_match:
        print(f"\nAll Skill Scores: ✓ MATCH")
    else:
        skill_scores_match = False
        print(f"\nAll Skill Scores: ✗ MISMATCH")

    # Overall test case result
    test_match = score_match and num_skills_match and skill_scores_match
    all_match = all_match and test_match

    print(f"\nTest Case Result: {'✓ PASS' if test_match else '✗ FAIL'}")

print("\n" + "=" * 80)
print("FINAL RESULT")
print("=" * 80)
if all_match:
    print("✓ SUCCESS: batch_match_score produces IDENTICAL results to individual match_score calls")
else:
    print("✗ FAILURE: Results differ between batch and individual calls")
print("=" * 80 + "\n")

# Show detailed comparison for first test case
print("\n" + "=" * 80)
print("DETAILED COMPARISON - Test Case 1: " + test_cases[0]['name'])
print("=" * 80)
print("\nIndividual Result:")
print(json.dumps(individual_results[0], indent=2))
print("\nBatch Result:")
print(json.dumps(batch_results[0], indent=2))
print("\n" + "=" * 80)
