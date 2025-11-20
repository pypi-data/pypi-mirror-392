#import "@preview/modern-cv:0.1.0": *

= Semantic Similarity Between Skill Lists - Overview

This document explains how the competency_api system calculates semantic similarity between lists of skills using a sophisticated multi-layered approach combining neural embeddings, statistical modeling, and geometric similarity.

== System Architecture

The skill matching system consists of five key components:

+ *#link("embeddings-explained.typ")[Text Embeddings]* -- Converting skill names to high-dimensional vectors
+ *#link("cosine-similarity-explained.typ")[Cosine Similarity]* -- Measuring semantic distance between skills
+ *#link("beta-distributions-explained.typ")[Beta Distributions]* -- Probabilistic modeling of skill proficiency
+ *#link("weighted-mixing-explained.typ")[Weighted Skill Mixing]* -- Combining similar skills based on semantic weights
+ *#link("scoring-system-explained.typ")[Multi-Factor Scoring]* -- Final score calculation with multiple approaches

== High-Level Process Flow

```
Candidate Skills          Required Skills
      ↓                         ↓
   Embedding                Embedding
      ↓                         ↓
 Vector Space              Vector Space
      ↓                         ↓
      └──── Similarity Matrix ────┘
                    ↓
            Weighted Mixing
                    ↓
           Beta Distributions
                    ↓
            Final Scoring
                    ↓
            Match Result
```

== Core Concepts

=== 1. Semantic Understanding
The system understands that "Data Science" relates to "Machine Learning" through neural embeddings that capture meaning as geometric relationships in high-dimensional space.

=== 2. Uncertainty Quantification
Instead of simple yes/no matching, the system models skill proficiency as probability distributions, capturing both the expected level and confidence in that assessment.

=== 3. Intelligent Skill Transfer
The system can infer that someone with strong "Python" and "Statistics" skills likely has some "Machine Learning" capability, while being appropriately conservative about the confidence level.

== Key Innovations

- *Beyond Keyword Matching*: Uses deep semantic understanding rather than exact string matching
- *Probabilistic Framework*: Handles uncertainty and partial matches naturally
- *Geometric Reasoning*: Skills exist in a mathematical space where relationships are distances
- *Adaptive Confidence*: Stricter requirements for low-similarity matches prevent false positives

== Mathematical Foundation

The system is built on solid mathematical principles:

- *Vector Embeddings*: Skills as points in 384-dimensional space
- *Cosine Similarity*: Angular distance between skill vectors
- *Beta Distributions*: Modeling skill proficiency with uncertainty
- *Mixture Models*: Weighted combination of probability distributions

== Example Use Case

When matching a candidate with "Python" (5/5) and "Statistics" (3/5) against a requirement for "Machine Learning" (4/5):

+ The system recognizes Python and Statistics are semantically related to ML
+ It creates a weighted mixture based on similarity scores
+ It calculates the probability of meeting the ML requirement
+ It outputs a nuanced score reflecting both capability and confidence

== Benefits

- *Nuanced Matching*: Captures partial matches and related skills
- *Explainable Results*: Provides similarity scores and confidence intervals
- *Robust to Variations*: Handles different skill naming conventions
- *Mathematically Principled*: Based on established statistical and geometric methods

Continue reading the detailed explanations for each component to fully understand the system's sophistication.