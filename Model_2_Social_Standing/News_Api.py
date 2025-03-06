import os
import requests
import json
import numpy as np
from time import sleep
from sklearn.cluster import KMeans
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Enhanced scoring system
SENTIMENT_SCORE_MAP = {
    "RED": {
        "base_score": -0.6,
        "operations_weight": 1.2,
        "reputation_weight": 1.5,
        "finance_weight": 1.3
    },
    "BLUE": {
        "base_score": 0.1,
        "operations_weight": 1.0,
        "reputation_weight": 1.0,
        "finance_weight": 1.0
    },
    "GREEN": {
        "base_score": 0.7,
        "operations_weight": 1.1,
        "reputation_weight": 1.2,
        "finance_weight": 1.4
    }
}

# Article recency weight - more recent articles have higher impact
def calculate_recency_weight(days_old):
    """Calculate weight based on article age (more recent = higher weight)."""
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
    # from datetime import datetime, timedelta
    
    # end_date = datetime.now().strftime('%Y-%m-%d')
    # start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    url = f"https://newsapi.org/v2/everything?q={company_name}&sortBy=publishedAt&pageSize={max_articles}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json()["articles"]
        if not articles:
            return None
        return articles
    else:
        raise Exception(f"Failed to fetch news articles: {response.text}")

def classify_article_with_gemini(article_text, company_name):
    """Classify an article into RED, BLUE, or GREEN with more detailed dimensions using Gemini API."""
    prompt = f"""
    Analyze the following news article snippet about {company_name} and classify it across three dimensions:
    
    1. Operations impact: How does this affect the company's operations and business activities?
    2. Reputation impact: How does this affect the company's public image and stakeholder trust?
    3. Financial impact: How does this affect the company's financial performance or outlook?
    
    For each dimension, classify as:
    - RED: Negative impact (e.g., disruptions, controversies, losses)
    - BLUE: Neutral or mixed impact (e.g., routine updates, minor changes)
    - GREEN: Positive impact (e.g., improvements, innovations, gains)
    
    Return the result as a JSON object with the classification and a brief rationale for each dimension.
    
    Example output:
    {{
      "operations": {{
        "category": "GREEN",
        "rationale": "The company is expanding operations with new efficient facilities."
      }},
      "reputation": {{
        "category": "BLUE", 
        "rationale": "The announcement has generated mixed reactions from stakeholders."
      }},
      "finance": {{
        "category": "GREEN",
        "rationale": "The initiative is expected to increase revenues by 15%."
      }}
    }}
    
    Article: "{article_text}"
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        start_index = response_text.find('{')
        end_index = response_text.rfind('}') + 1

        if start_index == -1 or end_index == 0:
            raise ValueError("Invalid Gemini API response format.")

        json_str = response_text[start_index:end_index]
        classification = json.loads(json_str)

        # Validate response structure
        required_keys = ["operations", "reputation", "finance"]
        for key in required_keys:
            if key not in classification:
                raise ValueError(f"Missing '{key}' in Gemini API response.")
            if "category" not in classification[key]:
                raise ValueError(f"Missing 'category' in '{key}' dimension.")

        return classification
    except Exception as e:
        raise Exception(f"Failed to classify article: {e}")

def calculate_article_score(classification, article_age_days=0):
    """Calculate a weighted score for an article based on the multi-dimensional classification."""
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
    from datetime import datetime
    
    try:
        article_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        days_old = (datetime.now() - article_date).days
        return days_old
    except:
        return 30  # Default to 30 days if parsing fails

def aggregate_scores(articles, company_name):
    """Aggregate scores across multiple articles with weighted dimensions."""
    aggregated = {
        "operations": [],
        "reputation": [],
        "finance": []
    }
    
    article_count = 0
    processed_articles = []
    
    for article in articles[:50]:  # Limit to 50 articles max
        try:
            article_text = article["title"] + " " + (article["description"] or "")
            days_old = parse_article_date(article["publishedAt"])
            
            classification = classify_article_with_gemini(article_text, company_name)
            article_scores = calculate_article_score(classification, days_old)
            
            # Store scores by dimension
            for dim in aggregated.keys():
                aggregated[dim].append(article_scores[dim])
            
            # Store processed data for later analysis
            processed_articles.append({
                "title": article["title"],
                "date": article["publishedAt"],
                "scores": article_scores,
                "classification": classification
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
    
    return final_scores, processed_articles

def determine_overall_rating(scores):
    """Determine overall rating based on multi-dimensional scores."""
    # Calculate composite score (weighted average)
    ops_weight = 0.3
    rep_weight = 0.4
    fin_weight = 0.3
    
    composite_score = (
        scores["operations"] * ops_weight +
        scores["reputation"] * rep_weight +
        scores["finance"] * fin_weight
    )
    
    # Determine rating based on composite score and individual dimensions
    if composite_score >= 0.3:
        rating = "GREEN"
    elif composite_score >= -0.1:
        rating = "BLUE"
    else:
        rating = "RED"
    
    # Check for any severe negative dimension that might override
    min_dimension_score = min(scores.values())
    if min_dimension_score < -0.5 and rating != "RED":
        rating = "BLUE"  # Downgrade to BLUE if any dimension is severely negative
    
    return rating, composite_score

def identify_key_topics(processed_articles, top_n=3):
    """Identify key topics from processed articles."""
    from collections import Counter
    
    # Extract rationales from all dimensions
    all_rationales = []
    for article in processed_articles:
        for dim in ["operations", "reputation", "finance"]:
            if "rationale" in article["classification"][dim]:
                all_rationales.append(article["classification"][dim]["rationale"])
    
    # Simple topic extraction using Gemini
    if not all_rationales:
        return []
    
    combined_rationales = " ".join(all_rationales)
    prompt = f"""
    Based on these news article insights, identify the top {top_n} key topics or themes:

    {combined_rationales}
    
    Return only the list of topics as a JSON array, like:
    ["Topic 1", "Topic 2", "Topic 3"]
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        start_index = response_text.find('[')
        end_index = response_text.rfind(']') + 1
        
        if start_index == -1 or end_index == 0:
            return []
            
        json_str = response_text[start_index:end_index]
        topics = json.loads(json_str)
        return topics
    except:
        return []

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
        dimension_scores, processed_articles = aggregate_scores(articles, company_name)
        
        # Determine overall rating
        overall_rating, composite_score = determine_overall_rating(dimension_scores)
        
        # Identify key topics
        key_topics = identify_key_topics(processed_articles)
        
        # Prepare detailed results
        results = {
            "company": company_name,
            "overall_rating": overall_rating,
            "composite_score": round(composite_score, 2),
            "dimension_scores": {
                dim: round(score, 2) for dim, score in dimension_scores.items()
            },
            "analysis_period": f"Last {days_back} days",
            "articles_analyzed": len(processed_articles),
            "key_topics": key_topics
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
    result = evaluate_company_digital_footprint("Tesla", max_articles=20, days_back=60)
    print(json.dumps(result, indent=4))