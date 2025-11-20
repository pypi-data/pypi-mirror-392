#!/usr/bin/env python3

# Candidate 1 scores
candidate1_scores = {
    "Performance Management": 100,
    "Talent Management": 100,
    "Change Management": 100,
    "Talent Acquisition": 96,
    "Stakeholder Management": 95,
    "HR Governance": 90,
    "HR Operations": 89,
    "Employee Relations": 87,
    "Sustainable HR Practices": 86,
    "People Analytics": 84,
    "Learning & Development": 82,
    "Employee Experience": 81,
    "Industry Relations": 80,
    "Digital HR Systems": 77,
    "Workforce Analytics": 76,
    "Total Rewards": 62,
    "Team Leadership": 62,
    "Leadership Development": 62,
    "People Strategy": 61,
    "Strategic Workforce Planning": 61,
    "Facility Management": 60,
    "Succession Planning": 60,
    "Executive Influence": 59,
    "Cost Management": 58,
    "Organisational Design": 53,
    "Business Partnering": 53,
    "Organisational Development": 53,
    "Crisis Management": 52,
    "Executive Communication": 49,
    "Developing Others": 48
}

# Candidate 2 scores
candidate2_scores = {
    "HR Governance": 86,
    "Industry Relations": 81,
    "Employee Relations": 79,
    "HR Operations": 74,
    "Change Management": 73,
    "Digital HR Systems": 72,
    "Sustainable HR Practices": 72,
    "Employee Experience": 70,
    "Talent Acquisition": 64,
    "Learning & Development": 63,
    "Total Rewards": 60,
    "Workforce Analytics": 59,
    "People Analytics": 59,
    "Team Leadership": 53,
    "Leadership Development": 52,
    "Stakeholder Management": 51,
    "Strategic Workforce Planning": 51,
    "Executive Influence": 51,
    "People Strategy": 50,
    "Facility Management": 49,
    "Succession Planning": 48,
    "Performance Management": 48,
    "Crisis Management": 48,
    "Cost Management": 48,
    "Organisational Development": 46,
    "Business Partnering": 46,
    "Organisational Design": 46,
    "Talent Management": 45,
    "Executive Communication": 43,
    "Developing Others": 42
}

# Calculate averages
def calculate_average(scores_dict):
    values = list(scores_dict.values())
    return sum(values) / len(values)

# Calculate and display results
candidate1_avg = calculate_average(candidate1_scores)
candidate2_avg = calculate_average(candidate2_scores)

print("=" * 50)
print("SKILL SCORES ANALYSIS")
print("=" * 50)
print(f"\nCandidate 1:")
print(f"  Total skills: {len(candidate1_scores)}")
print(f"  Sum of scores: {sum(candidate1_scores.values())}%")
print(f"  Average score: {candidate1_avg:.1f}%")

print(f"\nCandidate 2:")
print(f"  Total skills: {len(candidate2_scores)}")
print(f"  Sum of scores: {sum(candidate2_scores.values())}%")
print(f"  Average score: {candidate2_avg:.1f}%")

print(f"\nComparison:")
print(f"  Difference: {abs(candidate1_avg - candidate2_avg):.1f} percentage points")
print(f"  Better performer: Candidate {'1' if candidate1_avg > candidate2_avg else '2'}")
print("=" * 50)