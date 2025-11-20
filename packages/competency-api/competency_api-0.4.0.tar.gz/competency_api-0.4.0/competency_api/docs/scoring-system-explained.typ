= Multi-Factor Scoring System - Calculating Final Match Scores

== Overview

The scoring system combines multiple approaches to produce a nuanced, reliable match score. It balances exact matches, semantic similarities, probabilistic assessments, and confidence levels to create a fair and explainable scoring mechanism.

== The Scoring Pipeline

```
1. Exact Match Detection
        ↓
2. Similarity Assessment
        ↓
3. Weighted Mixture Creation
        ↓
4. Probabilistic Scoring
        ↓
5. Direct Ratio Calculation
        ↓
6. Score Combination
        ↓
7. Penalty Application
        ↓
8. Final Score Output
```

== Component 1: Exact Match Handling

When a candidate has the exact skill requested:

```
If candidate_skill.name == required_skill.name:
    
    If candidate_level ≥ required_level:
        score = 1.0  # Perfect match
    Else:
        score = 0.9 × (candidate_level / required_level)
```

*Rationale*: 
- Exact matches deserve special treatment
- Meeting/exceeding requirements → perfect score
- Below requirements → proportional penalty with 0.9 ceiling

== Component 2: Similarity-Based Penalties

For non-exact matches, the system first checks maximum similarity:

```
max_similarity = max(all similarities to required skill)

If max_similarity < 0.4:
    penalty = (max_similarity / 0.4) × 0.3
    return penalty  # Max possible score: 30%

Else if max_similarity < 0.6:
    penalty = 0.3 + ((max_similarity - 0.4) / 0.2) × 0.4
    return penalty  # Score range: 30% - 70%

Else:
    continue to full calculation  # No penalty
```

*Penalty Curve Visualization*:
```
Score
  1.0 │                            ____________
      │                          /
  0.7 │                    _____/
      │                  /
  0.3 │            _____/
      │          /
  0.0 │_________/
      └────────────────────────────────────────
       0    0.2    0.4    0.6    0.8    1.0
                  Max Similarity
```

== Component 3: Probabilistic Scoring

For similar skills (max_similarity ≥ 0.6):

=== A. Exceedance Probability
```
exceed_prob = P(mixture > threshold)
            = 1 - CDF_mixture(threshold)
```

This calculates the probability that the skill mixture exceeds the required level.

=== B. Direct Ratio Score
```
direct_ratio = Σᵢ wᵢ × min(candidate_ratioᵢ / threshold, 1.0)
```

This computes a weighted average of how well each skill meets the requirement.

== Component 4: Adaptive Score Combination

The system combines probabilistic and direct scores with adaptive weights:

```
confidence = 1 - variance(mixture)
mean_skill = E[mixture]

If mean_skill ≥ threshold:
    max_similarity_factor = 0.85
    ratio_weight = (0.5 + 0.15 × confidence) × max_similarity_factor
Else:
    max_similarity_factor = 0.7
    ratio_weight = (0.3 + 0.2 × confidence) × max_similarity_factor

prob_weight = 1 - ratio_weight

raw_score = ratio_weight × direct_ratio + prob_weight × exceed_prob
```

*Key Insights*:
- Higher confidence → more weight on direct ratio
- Meeting threshold → more balanced weighting
- Similarity factor prevents overconfidence in weak matches

== Component 5: Score Dampening

High scores receive additional dampening:

```
If raw_score > 0.8:
    final_score = 0.8 + (raw_score - 0.8) × 0.5
Else:
    final_score = raw_score
```

This prevents overconfident predictions for non-exact matches.

== Complete Scoring Example

=== Scenario
*Required*: "Machine Learning" at 4/5 (0.8)
*Candidate has*:
- "Deep Learning": 3/5
- "Statistics": 4/5
- "Python": 5/5

=== Step-by-Step Calculation

*1. Check Exact Match*
- No skill named "Machine Learning" → continue

*2. Calculate Similarities*
```
sim("ML", "Deep Learning") = 0.88
sim("ML", "Statistics") = 0.72
sim("ML", "Python") = 0.75
max_similarity = 0.88 → No penalty (> 0.6)
```

*3. Create Weights*
```
w_DL = 0.88 / 2.35 = 0.374
w_Stats = 0.72 / 2.35 = 0.306
w_Python = 0.75 / 2.35 = 0.319
```

*4. Calculate Scores*
```
Mixture: combination of Beta distributions
E[mixture] = 0.374×0.6 + 0.306×0.8 + 0.319×1.0 = 0.79
Variance = 0.15 → confidence = 0.85

exceed_prob = P(mixture > 0.8) ≈ 0.45
direct_ratio = 0.374×(0.6/0.8) + 0.306×1.0 + 0.319×1.0 = 0.906
```

*5. Combine Scores*
```
mean_skill (0.79) < threshold (0.8) → lower weight case
max_similarity_factor = 0.7
ratio_weight = (0.3 + 0.2×0.85) × 0.7 = 0.329
prob_weight = 0.671

raw_score = 0.329×0.906 + 0.671×0.45 = 0.599
```

*6. Apply Dampening*
```
raw_score (0.599) < 0.8 → no dampening
final_score = 0.599 ≈ 0.60
```

== Overall Score Aggregation

For multiple required skills:

```
overall_score = Σᵢ scoreᵢ / n_required_skills
```

Simple average ensures:
- All requirements equally important
- Score remains in [0, 1] range
- Easy interpretation

== Score Interpretation Guidelines

=== Score Ranges
```
0.9 - 1.0: Excellent match (likely exceeds requirements)
0.7 - 0.9: Good match (meets most requirements)
0.5 - 0.7: Moderate match (partially qualified)
0.3 - 0.5: Weak match (significant gaps)
0.0 - 0.3: Poor match (unqualified)
```

=== Confidence Indicators
Each score comes with:
- *Confidence interval*: Range of plausible values
- *Variance*: Uncertainty measure
- *Contributing skills*: Which skills led to the score

== Design Principles

=== 1. Conservative Estimation
- Non-exact matches capped below 1.0
- High scores dampened
- Low similarities heavily penalized

=== 2. Explainability
Every score can be decomposed:
- Exact match bonus
- Similarity weights
- Probabilistic vs deterministic components
- Applied penalties

=== 3. Adaptability
The system adapts based on:
- Confidence levels
- Whether requirements are met
- Maximum similarity found

=== 4. Fairness
- Recognizes transferable skills
- Doesn't over-penalize naming differences
- Provides partial credit for related expertise

== Advanced Features

=== 1. Skill Importance Weighting
Optional importance weights for requirements:
```
weighted_score = Σᵢ importanceᵢ × scoreᵢ / Σᵢ importanceᵢ
```

=== 2. Minimum Threshold Requirements
Mark some skills as mandatory:
```
If any mandatory_skill_score < threshold:
    overall_score = min(overall_score, penalty)
```

=== 3. Bonus Skills
Credit for exceeding requirements:
```
If candidate has relevant skills not required:
    bonus = small_bonus × relevance
    overall_score = min(1.0, overall_score + bonus)
```

== Practical Implications

=== For Recruiters
- *Scores are comparative*: 0.7 might be excellent for a rare skillset
- *Check components*: Overall score may hide strengths/weaknesses
- *Consider confidence*: High score with low confidence needs verification

=== For Candidates
- *Related skills matter*: Your "Data Science" experience counts for "ML"
- *Exact matches best*: Use standard skill names when possible
- *Combinations valued*: Multiple related skills can compensate

=== For System Designers
- *Tunable parameters*: Similarity thresholds, weights, penalties
- *Extensible framework*: Easy to add new scoring factors
- *Performance scalable*: Efficient for large-scale matching

== The Bottom Line

This multi-factor scoring system creates nuanced, fair assessments by:
+ Rewarding exact matches appropriately
+ Recognizing related expertise through semantic similarity
+ Quantifying uncertainty with probability distributions
+ Combining multiple scoring approaches adaptively
+ Providing explainable, interpretable results

The result is a system that can distinguish between "has the exact skills", "has very similar skills", "could probably do it", and "unlikely to succeed" - providing the nuanced assessment that human talent deserves.