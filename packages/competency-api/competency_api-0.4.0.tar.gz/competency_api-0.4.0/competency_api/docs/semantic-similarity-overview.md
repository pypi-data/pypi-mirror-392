# Semantic Similarity Between Skill Lists - Overview

This document explains how the competency_api system calculates semantic similarity between lists of skills using a sophisticated multi-layered approach combining neural embeddings, statistical modeling, and geometric similarity.

## System Architecture

The skill matching system consists of five key components:

1. **[Text Embeddings](./embeddings-explained.md)** - Converting skill names to high-dimensional vectors
2. **[Cosine Similarity](./cosine-similarity-explained.md)** - Measuring semantic distance between skills
3. **[Beta Distributions](./beta-distributions-explained.md)** - Probabilistic modeling of skill proficiency
4. **[Weighted Skill Mixing](./weighted-mixing-explained.md)** - Combining similar skills based on semantic weights
5. **[Multi-Factor Scoring](./scoring-system-explained.md)** - Final score calculation with multiple approaches

## High-Level Process Flow

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

## Core Concepts

### 1. Semantic Understanding
The system understands that "Data Science" relates to "Machine Learning" through neural embeddings that capture meaning as geometric relationships in high-dimensional space.

### 2. Uncertainty Quantification
Instead of simple yes/no matching, the system models skill proficiency as probability distributions, capturing both the expected level and confidence in that assessment.

### 3. Intelligent Skill Transfer
The system can infer that someone with strong "Python" and "Statistics" skills likely has some "Machine Learning" capability, while being appropriately conservative about the confidence level.

## Key Innovations

- **Beyond Keyword Matching**: Uses deep semantic understanding rather than exact string matching
- **Probabilistic Framework**: Handles uncertainty and partial matches naturally
- **Geometric Reasoning**: Skills exist in a mathematical space where relationships are distances
- **Adaptive Confidence**: Stricter requirements for low-similarity matches prevent false positives

## Mathematical Foundation

The system is built on solid mathematical principles:

- **Vector Embeddings**: Skills as points in 384-dimensional space
- **Cosine Similarity**: Angular distance between skill vectors
- **Beta Distributions**: Modeling skill proficiency with uncertainty
- **Mixture Models**: Weighted combination of probability distributions

## Example Use Case

When matching a candidate with "Python" (5/5) and "Statistics" (3/5) against a requirement for "Machine Learning" (4/5):

1. The system recognizes Python and Statistics are semantically related to ML
2. It creates a weighted mixture based on similarity scores
3. It calculates the probability of meeting the ML requirement
4. It outputs a nuanced score reflecting both capability and confidence

## Benefits

- **Nuanced Matching**: Captures partial matches and related skills
- **Explainable Results**: Provides similarity scores and confidence intervals
- **Robust to Variations**: Handles different skill naming conventions
- **Mathematically Principled**: Based on established statistical and geometric methods

Continue reading the detailed explanations for each component to fully understand the system's sophistication.