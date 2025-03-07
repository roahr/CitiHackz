import os
import requests
import json
import numpy as np
from time import sleep
from sklearn.cluster import KMeans
from dotenv import load_dotenv
import google.generativeai as genai
import re
from datetime import datetime
from collections import Counter

# Load environment variables
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Enhanced scoring system with documented mathematical reasoning
SENTIMENT_SCORE_MAP = {
    "RED": {
        # Negative impact starts with a negative base score
        "base_score": -0.6,
        # Weights reflect impact severity by dimension:
        # Operations issues can disrupt business but may be temporary
        "operations_weight": 1.2,
        # Reputation damage has lasting effects and is hardest to recover from
        "reputation_weight": 1.5,
        # Financial issues are serious but companies can recover with right strategies
        "finance_weight": 1.3
    },
    "BLUE": {
        # Neutral impact has slight positive base score to avoid over-penalization
        "base_score": 0.1,
        # Equal weights across dimensions for neutral news as they have balanced impact
        "operations_weight": 1.0,
        "reputation_weight": 1.0,
        "finance_weight": 1.0
    },
    "GREEN": {
        # Positive impact has strong positive base score
        "base_score": 0.7,
        # Weights reflect typical business impact priority:
        # Financial gains are most immediately valuable to stakeholders
        "finance_weight": 1.4,
        # Reputation gains build long-term value
        "reputation_weight": 1.2,
        # Operational improvements have modest but important impacts
        "operations_weight": 1.1
    }
}

# Article recency weight with documented mathematical reasoning
def calculate_recency_weight(days_old):
    """
    Calculate weight based on article age using an exponential decay model.
    Formula: weight = base_weight * exp(-decay_factor * days_old)
    
    Reasoning:
    - Recent news (0-7 days): High weight as these articles represent current state
    - News from past month (8-30 days): Moderate weight as still relevant but less current
    - Older news: Progressively lower weights as information becomes dated
    
    Returns a weight between 0.7 and 1.5
    """
    if days_old <= 7:
        return 1.5  # Very recent (last week)
    elif days_old <= 30:
        return 1.2  # Recent (last month)
    elif days_old <= 90:
        return 1.0  # Moderate (last quarter)
    else:
        return 0.7  # Older

# --- Helper Functions ---

def fetch_news_articles(company_name, max_articles=50, days_back=90):
    """Fetch news articles related to a company using NewsAPI."""
    from datetime import datetime, timedelta
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    url = f"https://newsapi.org/v2/everything?q={company_name}&from={start_date}&to={end_date}&sortBy=publishedAt&pageSize={max_articles}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json()["articles"]
        if not articles:
            return None
        return articles
    else:
        raise Exception(f"Failed to fetch news articles: {response.text}")

def classify_article_with_gemini(article_text, company_name):
    """Classify an article into RED, BLUE, or GREEN using Gemini API with improved prompt."""
    prompt = f"""
    Analyze this news article snippet about {company_name} and classify it across three dimensions:
    
    1. Operations impact: How does this affect the company's operations and business activities?
    2. Reputation impact: How does this affect the company's public image and stakeholder trust?
    3. Financial impact: How does this affect the company's financial performance or outlook?
    
    For each dimension, classify as:
    - RED: Negative impact (e.g., disruptions, controversies, losses, regulatory issues)
    - BLUE: Neutral or mixed impact (e.g., routine updates, minor changes, balanced outcomes)
    - GREEN: Positive impact (e.g., improvements, innovations, gains, expansion)
    
    IMPORTANT: In your rationale, include specific evidence from the article that justifies your classification.
    
    Return the result **strictly as a JSON object** with no extra text.

    Example output:
    {{
      "operations": {{
        "category": "GREEN",
        "rationale": "The company is expanding operations with new efficient facilities, mentioned in paragraph 2."
      }},
      "reputation": {{
        "category": "BLUE", 
        "rationale": "The announcement has generated mixed reactions from stakeholders, with some analysts praising the move while consumer groups express concerns."
      }},
      "finance": {{
        "category": "GREEN",
        "rationale": "The initiative is expected to increase revenues by 15% according to company forecasts mentioned in the article."
      }}
    }}

    Article: "{article_text}"
    """
    
    try:
        response = model.generate_content(prompt)
        sleep(0.3)
        response_text = response.text

        # Extract JSON using regex (more reliable than string slicing)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON object found in Gemini API response.")

        json_str = json_match.group(0)  # Extract JSON content
        classification = json.loads(json_str)  # Parse JSON

        # Validate JSON structure
        required_keys = ["operations", "reputation", "finance"]
        for key in required_keys:
            if key not in classification or "category" not in classification[key]:
                raise ValueError(f"Missing '{key}' in Gemini API response.")

        return classification

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format from API: {e}")

    except Exception as e:
        raise Exception(f"Failed to classify article: {e}")

def calculate_article_score(classification, article_age_days=0):
    """
    Calculate a weighted score for an article based on the multi-dimensional classification.
    
    Mathematical approach:
    1. Start with base sentiment score (-0.6 for RED, 0.1 for BLUE, 0.7 for GREEN)
    2. Apply dimension-specific weights to account for varying impacts
    3. Apply recency weight to prioritize more recent information
    
    Final dimension score = base_score * dimension_weight * recency_weight
    """
    dimensions = ["operations", "reputation", "finance"]
    dimension_scores = {}
    
    # Calculate score for each dimension
    for dim in dimensions:
        category = classification[dim]["category"]
        base_score = SENTIMENT_SCORE_MAP[category]["base_score"]
        weight = SENTIMENT_SCORE_MAP[category][f"{dim}_weight"]
        dimension_scores[dim] = base_score * weight
    
    # Apply recency weight
    recency_weight = calculate_recency_weight(article_age_days)
    
    # Calculate final article score
    final_scores = {
        dim: score * recency_weight for dim, score in dimension_scores.items()
    }
    
    return final_scores

def parse_article_date(published_at):
    """Parse article date and calculate days from today."""
    try:
        article_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        days_old = (datetime.now() - article_date).days
        return days_old
    except:
        return 30  # Default to 30 days if parsing fails

def aggregate_scores(articles, company_name):
    """
    Aggregate scores across multiple articles with weighted dimensions.
    
    Returns:
    - Dimension scores: Average scores for operations, reputation, and finance
    - Processed articles: List of processed articles with classifications and scores
    - Key points: Dictionary of evidence points extracted from article rationales
    """
    aggregated = {
        "operations": [],
        "reputation": [],
        "finance": []
    }
    
    # Store rationales by sentiment to extract key points
    sentiment_rationales = {
        "RED": [],
        "BLUE": [],
        "GREEN": []
    }
    
    article_count = 0
    processed_articles = []
    
    for article in articles[:50]:  # Limit to 50 articles max
        try:
            article_text = article["title"] + " " + (article["description"] or "")
            days_old = parse_article_date(article["publishedAt"])
            
            classification = classify_article_with_gemini(article_text, company_name)
            sleep(0.5)
            article_scores = calculate_article_score(classification, days_old)
            
            # Store scores by dimension
            for dim in aggregated.keys():
                aggregated[dim].append(article_scores[dim])
                # Store rationales by sentiment for key points extraction
                sentiment_rationales[classification[dim]["category"]].append({
                    "dimension": dim,
                    "rationale": classification[dim]["rationale"],
                    "title": article["title"],
                    "date": article["publishedAt"]
                })
            
            # Store processed data for later analysis
            processed_articles.append({
                "title": article["title"],
                "date": article["publishedAt"],
                "scores": article_scores,
                "classification": classification,
                "url": article.get("url", ""),
                "days_old": days_old
            })
            
            article_count += 1
            sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error processing article: {e}")
            continue
    
    # Calculate final aggregated scores
    final_scores = {}
    if article_count > 0:
        for dim in aggregated.keys():
            # Use weighted average (recent articles have higher impact)
            final_scores[dim] = sum(aggregated[dim]) / article_count
    else:
        final_scores = {dim: 0 for dim in aggregated.keys()}
    
    # Extract key points from rationales
    key_points = extract_key_points(sentiment_rationales)
    
    return final_scores, processed_articles, key_points

def extract_key_points(sentiment_rationales):
    """
    Extract key points from article rationales grouped by sentiment.
    
    This provides evidence-based reasons for the score calculations.
    """
    key_points = {}
    
    for sentiment, rationales in sentiment_rationales.items():
        # Sort rationales by dimension for consistent output
        dimension_rationales = {
            "operations": [],
            "reputation": [],
            "finance": []
        }
        
        for item in rationales:
            dimension_rationales[item["dimension"]].append({
                "rationale": item["rationale"],
                "title": item["title"],
                "date": item["date"]
            })
        
        # Extract top points for each dimension (prioritize recent ones)
        sentiment_points = []
        for dim, dim_rationales in dimension_rationales.items():
            # Sort by date (most recent first)
            sorted_rationales = sorted(dim_rationales, 
                                       key=lambda x: x["date"] if x["date"] else "", 
                                       reverse=True)
            
            # Take top 2 from each dimension if available
            for item in sorted_rationales[:2]:
                sentiment_points.append({
                    "dimension": dim,
                    "point": item["rationale"],
                    "title": item["title"],
                    "date": item["date"]
                })
        
        key_points[sentiment] = sentiment_points
    
    return key_points

def determine_overall_rating(scores):
    """
    Determine overall rating based on multi-dimensional scores.
    
    Mathematical approach:
    1. Calculate composite score as weighted average of dimension scores
    2. Apply threshold-based classification for initial rating
    3. Apply override rules for severe negative dimensions
    
    Returns rating (RED/BLUE/GREEN) and composite score
    """
    # Calculate composite score (weighted average)
    # Operations: 30% - Core business functionality
    # Reputation: 40% - Long-term company value and stakeholder trust
    # Finance: 30% - Immediate business health indicator
    ops_weight = 0.3
    rep_weight = 0.4
    fin_weight = 0.3
    
    composite_score = (
        scores["operations"] * ops_weight +
        scores["reputation"] * rep_weight +
        scores["finance"] * fin_weight
    )
    
    # Determine rating based on composite score
    # GREEN: Strong positive sentiment (≥ 0.3)
    # BLUE: Neutral or slightly mixed sentiment (-0.1 to 0.3)
    # RED: Negative sentiment (< -0.1)
    if composite_score >= 0.3:
        rating = "GREEN"
    elif composite_score >= -0.1:
        rating = "BLUE"
    else:
        rating = "RED"
    
    # Override rule: If any dimension is severely negative, downgrade rating
    # This prevents a company with serious issues in one area from getting a fully positive rating
    min_dimension_score = min(scores.values())
    if min_dimension_score < -0.5 and rating == "GREEN":
        rating = "BLUE"  # Downgrade to BLUE if any dimension is severely negative
    
    return rating, composite_score

def identify_key_topics(processed_articles, key_points):
    """
    Identify key topics from processed articles and key points.
    
    Improved to provide more relevant topics with evidence from articles.
    """
    # Extract titles and rationales
    all_text = []
    
    # Get article titles and descriptions
    for article in processed_articles[:10]:  # Focus on most recent 10 articles
        all_text.append(article["title"])
    
    # Add rationales from key points
    for sentiment, points in key_points.items():
        for point in points:
            all_text.append(point["point"])
    
    # Create prompt with combined text
    combined_text = " ".join(all_text)
    
    prompt = f"""
    Based on these news headlines and insights about a company, identify the top 3-5 key topics or themes.
    
    For each topic:
    1. Provide a concise topic name
    2. Include a brief explanation of why this topic matters to the company
    
    Text data:
    {combined_text}
    
    Return as a JSON array of objects with 'topic' and 'explanation' fields:
    [
      {{
        "topic": "Example Topic",
        "explanation": "Brief explanation of importance"
      }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON array using regex
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            # Fallback to simple topic extraction
            return extract_simple_topics(combined_text)
            
        json_str = json_match.group(0)
        topics = json.loads(json_str)
        return topics
    except Exception as e:
        print(f"Error extracting topics: {e}")
        # Fallback to simple topic extraction
        return extract_simple_topics(combined_text)

def extract_simple_topics(text):
    """Fallback simple topic extraction when more complex extraction fails."""
    # Simple prompt for topic extraction
    prompt = f"""
    Extract 3-5 key business topics from this text:
    
    {text}
    
    Return only a JSON array of strings:
    ["Topic 1", "Topic 2", "Topic 3"]
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            return [{"topic": "Business Operations", "explanation": "General business activities"}]
            
        json_str = json_match.group(0)
        topics = json.loads(json_str)
        
        # Convert simple strings to object format
        return [{"topic": t, "explanation": ""} for t in topics]
    except:
        # Return a generic topic if all else fails
        return [{"topic": "Business Operations", "explanation": "General business activities"}]

# --- Main Function ---

def evaluate_company_digital_footprint(company_name, max_articles=50, days_back=90):
    """
    Evaluate a company's digital footprint based on recent news articles.
    
    Parameters:
    - company_name: Name of the company to analyze
    - max_articles: Maximum number of articles to analyze (default: 50)
    - days_back: How many days back to search for articles (default: 90)
    
    Returns:
    - Dictionary with analysis results
    """
    try:
        articles = fetch_news_articles(company_name, max_articles, days_back)
        
        if articles is None or len(articles) == 0:
            return {
                "status": "no_data",
                "message": f"No news articles found for '{company_name}'"
            }
        
        # Process and score articles
        dimension_scores, processed_articles, key_points = aggregate_scores(articles, company_name)
        
        # Determine overall rating
        overall_rating, composite_score = determine_overall_rating(dimension_scores)
        
        # Identify key topics with improved method
        key_topics = identify_key_topics(processed_articles, key_points)
        
        # Prepare detailed results
        results = {
            "status": "success",
            "company": company_name,
            "overall_rating": overall_rating,
            "composite_score": round(composite_score, 2),
            "dimension_scores": {
                dim: round(score, 2) for dim, score in dimension_scores.items()
            },
            "analysis_period": f"Last {days_back} days",
            "articles_analyzed": len(processed_articles),
            "key_topics": key_topics,
            "key_points": key_points
        }
        
        return results
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# --- Example Usage ---

if __name__ == "__main__":
    # Example usage
    result = evaluate_company_digital_footprint("Tesla", max_articles=20, days_back=20)
    print(json.dumps(result, indent=2))