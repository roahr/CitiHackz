# Digital Footprint Scoring System Documentation

## Overview

The Digital Footprint Evaluation System analyzes a company's public perception and impact by analyzing recent news articles. The system uses natural language processing to classify articles across multiple dimensions and produces a comprehensive score that reflects the company's current digital footprint.

## Scoring Dimensions

The system evaluates companies across three key dimensions:

1. **Operations Impact** - How news relates to the company's business operations, processes, products, and services
2. **Reputation Impact** - How news affects the company's public image, brand perception, and stakeholder trust
3. **Financial Impact** - How news reflects or influences the company's financial performance, market position, and investor confidence

## Classification Categories

Each article is classified into one of three categories for each dimension:

| Category | Description | Base Score |
|----------|-------------|------------|
| RED | Negative impact (controversies, losses, problems) | -0.6 |
| BLUE | Neutral or mixed impact (routine updates, minor changes) | 0.1 |
| GREEN | Positive impact (growth, innovations, achievements) | 0.7 |

## Weighting System

### Dimensional Weights

Each dimension has different weights based on the category:

| Category | Operations Weight | Reputation Weight | Financial Weight |
|----------|-------------------|-------------------|------------------|
| RED | 1.2 | 1.5 | 1.3 |
| BLUE | 1.0 | 1.0 | 1.0 |
| GREEN | 1.1 | 1.2 | 1.4 |

This weighting system reflects that:
- Negative reputation impact (RED) has a higher penalty factor (1.5)
- Positive financial news (GREEN) has a higher reward factor (1.4)

### Recency Weights

Article recency affects scoring impact:

| Article Age | Weight |
|-------------|--------|
| ≤ 7 days | 1.5 |
| 8-30 days | 1.2 |
| 31-90 days | 1.0 |
| > 90 days | 0.7 |

More recent articles have a greater impact on the overall score, reflecting the dynamic nature of public perception and market response.

## Composite Score Calculation

The final composite score is calculated as a weighted average of the three dimensions:

```
Composite Score = (Operations Score × 0.3) + (Reputation Score × 0.4) + (Financial Score × 0.3)
```

## Rating Thresholds

The overall rating is determined by the composite score:

| Composite Score Range | Rating | Interpretation |
|-----------------------|--------|----------------|
| ≥ 0.3 | GREEN | Positive digital footprint |
| -0.1 to 0.3 | BLUE | Neutral digital footprint |
| < -0.1 | RED | Negative digital footprint |

### Override Rules

- If any dimension score falls below -0.5, the rating cannot exceed BLUE, regardless of the composite score
- This ensures that severe negative impacts in any single area are appropriately reflected in the overall rating

## Score Interpretation

| Rating | Score Range | Interpretation | Recommended Action |
|--------|-------------|----------------|-------------------|
| GREEN | 0.5 to 1.0 | Excellent digital footprint | Maintain current strategies, leverage positive perception |
| GREEN | 0.3 to 0.5 | Good digital footprint | Identify strengths, continue positive initiatives |
| BLUE | 0.1 to 0.3 | Slightly positive | Monitor closely, enhance positive aspects |
| BLUE | -0.1 to 0.1 | Neutral | Develop strategies to improve perception |
| RED | -0.4 to -0.1 | Moderately negative | Address specific issues, develop response plan |
| RED | -1.0 to -0.4 | Significantly negative | Immediate reputation management needed |

## System Limitations

1. **Source Dependency**: Results are limited by the availability and quality of news articles
2. **Classification Accuracy**: Natural language processing may occasionally misinterpret complex or nuanced articles
3. **Time Window**: The default analysis covers the last 90 days; historical trends beyond this window are not reflected
4. **English Language Bias**: The system primarily analyzes English-language news sources
5. **Volume Sensitivity**: Companies with few news mentions may have less statistically reliable results

## Usage Recommendations

- Run evaluations quarterly for trend analysis
- Compare results against industry peers for benchmarking
- Use as one component of a broader reputation management strategy
- Review key topics identified for strategic planning
- Consider supplementing with social media and other digital channel analysis