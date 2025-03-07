import os
import requests
import json
import math
import numpy as np
from sklearn.cluster import KMeans
from dotenv import load_dotenv
import praw
from playwright.sync_api import sync_playwright
import pandas as pd
import re
import emoji
import logging
import time
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Helper Functions ---
def initialize_browser():
    """Initialize and return Playwright browser."""
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        return playwright, browser, page
    except Exception as e:
        logger.error(f"Failed to initialize browser: {e}")
        raise

def search_google_maps(page, business_name):
    """Search for a business on Google Maps."""
    try:
        page.goto("https://www.google.com/maps")
        page.wait_for_load_state("networkidle")
        
        search_box = page.locator("input[id='searchboxinput']")
        search_box.fill(business_name)
        search_box.press("Enter")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)  # Additional wait for content to load
        
        logger.info(f"Searched for {business_name} on Google Maps")
    except Exception as e:
        logger.error(f"Error during Google Maps search: {e}")
        raise

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove emojis
    text = emoji.replace_emoji(text, replace='')
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_rating(rating_text):
    """Extract numerical rating from rating text."""
    if not rating_text:
        return 0
    
    # Extract numbers from text like "4.5 stars" or "Rated 4.5 out of 5"
    match = re.search(r'(\d+(\.\d+)?)', rating_text)
    if match:
        return float(match.group(1))
    return 0

def scrape_reviews(page, max_reviews=60):
    """Scrape reviews from Google Maps."""
    reviews = []
    try:
        # Wait for the business details to load
        page.wait_for_timeout(5000)

        # Locate and click the reviews section
        logger.info("Searching for reviews section")
        try:
            review_section = page.get_by_role('tab', name="Reviews")
            review_section.click()
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Could not find review section: {e}")
            return reviews

        # Scroll to load more reviews
        logger.info("Loading reviews...")
        for _ in range(10):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(2000)

        # Extract reviews
        review_elements = page.locator("div[class*='jJc9Ad']")
        count = review_elements.count()
        logger.info(f"Found {count} reviews")

        for i in range(min(count, max_reviews)):
            try:
                element = review_elements.nth(i)
                reviewer = element.locator("div[class*='d4r55']").inner_text()
                rating_text = element.locator("span[aria-label]").get_attribute("aria-label")
                rating = extract_rating(rating_text)
                
                # Try to get expanded review text first, if it exists
                try:
                    more_button = element.locator("button:has-text('More')").first
                    more_button.click()
                    page.wait_for_timeout(500)
                except:
                    pass  # No "More" button found, use available text
                
                review_text = element.locator("span[class*='wiI7pd']").inner_text()
                
                if review_text:
                    reviews.append({
                        "Reviewer": clean_text(reviewer),
                        "Rating": rating,
                        "Review": clean_text(review_text)
                    })
            except Exception as e:
                logger.warning(f"Error extracting review {i}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error during review scraping: {e}")

    return reviews

def save_reviews_to_csv(reviews, filename="google_reviews.csv"):
    """Save reviews to CSV file."""
    if not reviews:
        logger.warning("No reviews to save")
        return
        
    df = pd.DataFrame(reviews)
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Reviews saved to {filename}")

def fetch_google_reviews(business_name):
    """Fetch Google reviews for a company."""
    playwright, browser, page = None, None, None
    
    try:
        playwright, browser, page = initialize_browser()
        
        # Search and scrape reviews
        search_google_maps(page, business_name)
        reviews = scrape_reviews(page, max_reviews=200)
        
        # Extract just the review texts for sentiment analysis
        review_texts = [review["Review"] for review in reviews if review["Review"]]
        
        # Save results
        save_reviews_to_csv(reviews, f"{business_name.replace(' ', '_')}_google_reviews.csv")
        
        return review_texts

    except Exception as e:
        logger.error(f"Unexpected error in fetch_google_reviews: {e}")
        return []

    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()

def fetch_reddit_posts(company_name, subreddits=None):
    """Fetch Reddit posts and comments about a company."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        logger.warning("Reddit API credentials not found")
        return []
        
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="public-opinion-scraper"
        )
        
        posts = []
        search_subreddits = subreddits or ["all"]
        
        for subreddit_name in search_subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                for submission in subreddit.search(company_name, limit=10):
                    if company_name.lower() in submission.title.lower() or company_name.lower() in submission.selftext.lower():
                        posts.append(submission.title)
                        posts.append(submission.selftext)
                        
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list()[:20]:  # Limit to first 20 comments per post
                            if len(comment.body) > 20:  # Skip very short comments
                                posts.append(comment.body)
            except Exception as e:
                logger.warning(f"Error searching subreddit {subreddit_name}: {e}")
                continue
                
        # Clean and filter posts
        cleaned_posts = [clean_text(post) for post in posts if post and len(post.strip()) > 20]
        
        logger.info(f"Found {len(cleaned_posts)} relevant Reddit posts/comments for {company_name}")
        return cleaned_posts
        
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {e}")
        return []


def classify_text_with_gemini(text):
    """
    Classify text into RED, BLUE, or GREEN using Gemini API via the genai library.
    Returns a categorization with confidence and rationale.
    """
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not found")
        # Fallback to a simple rule-based classifier
        return fallback_sentiment_classifier(text)
        
    try:
        # Configure the genai library with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Clean and truncate text to avoid token limits
        cleaned_text = clean_text(text)
        if len(cleaned_text) > 500:
            cleaned_text = cleaned_text[:500] + "..."
            
        prompt = f"""
        Classify the following text about a company into one of three categories:
        - RED: Negative sentiment (e.g., complaints, criticism, problems, issues).
        - BLUE: Neutral sentiment (e.g., factual statements, mixed opinions).
        - GREEN: Positive sentiment (e.g., praise, recommendations, satisfaction).

        Provide your classification as a JSON object with the following fields:
        - category: "RED", "BLUE", or "GREEN"
        - confidence: a number between 0 and 1
        - rationale: a 1-sentence explanation for your classification

        Text: "{cleaned_text}"
        """
        
        # Generate content using the genai library
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=200,
            )
        )
        
        # Process the response
        if response:
            generated_text = response.text
            
            time.sleep(0.5)
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                try:
                    classification = json.loads(json_match.group(0))
                    return classification
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from response")
            
            # If no valid JSON, parse manually
            if "RED" in generated_text:
                category = "RED"
            elif "GREEN" in generated_text:
                category = "GREEN"
            else:
                category = "BLUE"
                
            return {
                "category": category,
                "confidence": 0.7,
                "rationale": generated_text[:100]
            }
        else:
            logger.error("Empty response from Gemini API")
            return fallback_sentiment_classifier(text)
            
    except Exception as e:
        logger.error(f"Error in classify_text_with_gemini: {e}")
        return fallback_sentiment_classifier(text)

def fallback_sentiment_classifier(text):
    """Simple rule-based sentiment classifier as fallback."""
    text = text.lower()
    
    # Define sentiment lexicons
    positive_words = [
        "great", "excellent", "good", "love", "best", "amazing", "outstanding", 
        "awesome", "fantastic", "recommend", "perfect", "happy", "satisfied"
    ]
    
    negative_words = [
        "bad", "terrible", "poor", "awful", "horrible", "disappointing", "worst",
        "hate", "problem", "issue", "broken", "failure", "useless", "complaint"
    ]
    
    # Count word occurrences
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    # Determine category
    if positive_count > negative_count + 1:
        category = "GREEN"
        confidence = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        rationale = f"Contains {positive_count} positive terms vs {negative_count} negative terms."
    elif negative_count > positive_count + 1:
        category = "RED"
        confidence = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        rationale = f"Contains {negative_count} negative terms vs {positive_count} positive terms."
    else:
        category = "BLUE"
        confidence = 0.6
        rationale = "Contains a balanced mix of terms or primarily neutral language."
    
    return {
        "category": category,
        "confidence": confidence,
        "rationale": rationale
    }

def calculate_sentiment_score(classification):
    """Convert sentiment classification to a numerical score."""
    # Base scores for each category
    category_base_scores = {
        "RED": 2.5,    # Range: 0-4
        "BLUE": 6.0,   # Range: 4-7
        "GREEN": 8.5   # Range: 7-10
    }
    
    # Get base score from category with fallback to neutral
    base_score = category_base_scores.get(classification.get("category", "BLUE"), 5.0)
    
    # Adjust score based on confidence (higher confidence pushes score toward extremes)
    confidence = classification.get("confidence", 0.7)
    
    if classification.get("category") == "RED":
        # For RED, lower scores are more negative (high confidence pushes lower)
        adjusted_score = base_score - (confidence * 1.5)
        # Ensure score doesn't go below 0
        return max(0, adjusted_score)
    elif classification.get("category") == "GREEN":
        # For GREEN, higher scores are more positive (high confidence pushes higher)
        adjusted_score = base_score + (confidence * 1.5)
        # Ensure score doesn't exceed 10
        return min(10, adjusted_score)
    else:
        # For BLUE, stay close to the middle
        return base_score

def aggregate_scores(texts):
    """Aggregate sentiment scores across multiple texts."""
    if not texts:
        return {
            "avg_score": 5.0,  # Neutral score
            "count": 0,
            "categories": {"RED": 0, "BLUE": 0, "GREEN": 0},
            "confidence": 0.0
        }
    
    total_score = 0
    categories = {"RED": 0, "BLUE": 0, "GREEN": 0}
    total_confidence = 0
    
    for text in texts:
        if not text or len(text.strip()) < 20:  # Skip very short texts
            continue
            
        try:
            classification = classify_text_with_gemini(text[:800])
            time.sleep(0.3)
            score = calculate_sentiment_score(classification)
            
            total_score += score
            categories[classification.get("category", "BLUE")] += 1
            total_confidence += classification.get("confidence", 0.5)
        except Exception as e:
            logger.warning(f"Error processing text: {e}")
            continue
    
    total_items = sum(categories.values())
    
    if total_items == 0:
        return {
            "avg_score": 5.0,
            "count": 0,
            "categories": categories,
            "confidence": 0.0
        }
    
    avg_score = total_score / total_items
    avg_confidence = total_confidence / total_items
    
    # Calculate overall confidence based on sample size and average classification confidence
    # Higher sample sizes increase confidence (sigmoid function)
    sample_confidence = 2 / (1 + math.exp(-0.05 * total_items)) - 1  # Range 0-1
    
    # Combined confidence
    overall_confidence = (sample_confidence + avg_confidence) / 2
    
    return {
        "avg_score": round(avg_score, 2),
        "count": total_items,
        "categories": categories,
        "confidence": round(overall_confidence, 2)
    }

def perform_clustering(scores):
    """Perform K-means clustering on scores if there are enough data points."""
    if len(scores) < 3:
        # Not enough data for meaningful clustering
        return [0] * len(scores)
        
    try:
        X = np.array([[score] for score in scores])
        kmeans = KMeans(n_clusters=min(3, len(scores)), random_state=0, n_init=10).fit(X)
        return kmeans.labels_.tolist()
    except Exception as e:
        logger.error(f"Error in clustering: {e}")
        return [0] * len(scores)

def evaluate_public_opinion(company_name):
    """
    Evaluate public opinion about a company and return comprehensive results.
    """
    try:
        result = {
            "company_name": company_name,
            "sources": {},
            "overall": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Step 1: Fetch data from different sources
        logger.info(f"Fetching Google reviews for {company_name}")
        google_reviews = fetch_google_reviews(company_name)
        
        logger.info(f"Fetching Reddit posts for {company_name}")
        reddit_posts = fetch_reddit_posts(company_name)
        
        # Step 2: Analyze sentiment for each source
        if google_reviews:
            result["sources"]["google"] = aggregate_scores(google_reviews)
            
        if reddit_posts:
            result["sources"]["reddit"] = aggregate_scores(reddit_posts)
        
        # Step 3: Calculate overall score
        source_scores = []
        weights = []
        categories_sum = {"RED": 0, "BLUE": 0, "GREEN": 0}
        
        for source, data in result["sources"].items():
            if data["count"] > 0:
                # Weight by confidence and sample size
                weight = data["confidence"] * math.log(data["count"] + 1, 10)
                source_scores.append(data["avg_score"] * weight)
                weights.append(weight)
                
                # Aggregate categories
                for category, count in data["categories"].items():
                    categories_sum[category] += count
        
        if sum(weights) > 0:
            overall_score = sum(source_scores) / sum(weights)
        else:
            overall_score = 5.0  # Neutral default
        
        # Determine overall category
        if overall_score >= 7:
            overall_category = "GREEN"
        elif overall_score >= 4:
            overall_category = "BLUE"
        else:
            overall_category = "RED"
            
        # Overall confidence based on total sample size
        total_samples = sum(result["sources"].get(s, {}).get("count", 0) for s in result["sources"])
        if total_samples > 0:
            confidence = min(0.95, math.log(total_samples + 1, 10) / 3)
        else:
            confidence = 0.0
            
        # Step 4: Perform clustering for visualization
        all_scores = [data["avg_score"] for source, data in result["sources"].items() if data["count"] > 0]
        cluster_labels = perform_clustering(all_scores)
        
        result["overall"] = {
            "score": round(overall_score, 2),
            "category": overall_category,
            "confidence": round(confidence, 2),
            "category_distribution": categories_sum,
            "total_samples": total_samples,
            "clustering": {
                "labels": cluster_labels,
                "scores": all_scores,
                "sources": list(s for s in result["sources"] if result["sources"][s]["count"] > 0)
            }
        }
        
        # Add interpretation of results
        result["interpretation"] = interpret_results(result)
        
        return result

    except Exception as e:
        logger.error(f"Error in evaluate_public_opinion: {e}")
        return {
            "error": str(e),
            "company_name": company_name,
            "status": "failed"
        }

def interpret_results(result):
    """Generate human-readable interpretation of results."""
    try:
        overall = result.get("overall", {})
        score = overall.get("score", 5.0)
        category = overall.get("category", "BLUE")
        confidence = overall.get("confidence", 0.0)
        total_samples = overall.get("total_samples", 0)
        
        # Confidence level
        if confidence > 0.8:
            confidence_text = "high confidence"
        elif confidence > 0.5:
            confidence_text = "moderate confidence"
        else:
            confidence_text = "low confidence"
            
        # Sample size adequacy
        if total_samples > 100:
            sample_text = "based on a large sample size"
        elif total_samples > 30:
            sample_text = "based on an adequate sample size"
        elif total_samples > 0:
            sample_text = "based on a limited sample size"
        else:
            sample_text = "no data available"
            
        # Main interpretation
        if category == "GREEN":
            main_text = f"The company has a predominantly positive public image (score: {score}/10)"
        elif category == "BLUE":
            main_text = f"The company has a neutral or mixed public image (score: {score}/10)"
        else:
            main_text = f"The company has a predominantly negative public image (score: {score}/10)"
            
        # Source breakdown
        source_texts = []
        for source, data in result.get("sources", {}).items():
            if data.get("count", 0) > 0:
                source_score = data.get("avg_score", 5.0)
                source_category = "positive" if source_score >= 7 else "neutral" if source_score >= 4 else "negative"
                source_texts.append(f"{source.capitalize()} data shows a {source_category} sentiment ({source_score}/10) based on {data.get('count', 0)} samples")
        
        # Combined interpretation
        interpretation = f"{main_text} with {confidence_text}, {sample_text}."
        if source_texts:
            interpretation += " " + " ".join(source_texts) + "."
            
        return interpretation
            
    except Exception as e:
        logger.error(f"Error generating interpretation: {e}")
        return "Unable to generate interpretation due to an error."

# Example usage
if __name__ == "__main__":
    company_name = input("Enter company name to analyze: ")
    result = evaluate_public_opinion(company_name)
    print(json.dumps(result, indent=2))
    
    # Save results to file
    with open(f"{company_name.replace(' ', '_')}_analysis.json", "w") as f:
        json.dump(result, f, indent=2)