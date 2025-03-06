import json
import time
import os
import sys
import re
import pickle
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import linkedin_api with error handling
try:
    from linkedin_api import Linkedin
except ImportError:
    print("linkedin_api package not installed. Install it with: pip install linkedin-api")
    sys.exit(1)

# Load environment variables
load_dotenv()

# LinkedIn Credentials 
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
COOKIES_FILE = "linkedin_cookies.pkl"

def setup_selenium():
    """Launch Selenium browser with anti-detection measures"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use webdriver_manager to automatically handle driver installation
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set navigator.webdriver to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up Selenium: {str(e)}")
        sys.exit(1)

def login_and_save_cookies():
    """Open LinkedIn login page for manual login and save cookies."""
    driver = setup_selenium()
    try:
        driver.get(LINKEDIN_LOGIN_URL)
        
        # Auto-fill credentials if provided (user will still need to solve CAPTCHA)
        if LINKEDIN_USERNAME and LINKEDIN_PASSWORD:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(LINKEDIN_USERNAME)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(LINKEDIN_PASSWORD)
            
            print("\nCredentials auto-filled. Please solve any CAPTCHA if needed and click Sign In.")
        else:
            print("\nPlease log in to LinkedIn manually.")
            
        input("Press Enter after completing login...")
        
        # Check if login was successful by looking for the feed URL
        if "feed" in driver.current_url:
            # Save cookies
            cookies = driver.get_cookies()
            with open(COOKIES_FILE, "wb") as f:
                pickle.dump(cookies, f)
            print("\nLogin successful! Cookies saved.")
        else:
            print("\nLogin unsuccessful. Please try again.")
            
    except Exception as e:
        print(f"Error during login: {str(e)}")
    finally:
        driver.quit()

def load_cookies():
    """Load saved cookies for LinkedIn API authentication."""
    try:
        with open(COOKIES_FILE, "rb") as f:
            cookies = pickle.load(f)
        return cookies
    except FileNotFoundError:
        print(f"\nNo saved cookies found at {COOKIES_FILE}. Will prompt for login.")
        return None
    except Exception as e:
        print(f"\nError loading cookies: {str(e)}")
        return None

def extract_company_id(api, company_url):
    """Extracts company ID from LinkedIn company URL with improved reliability"""
    try:
        # First try to extract from URL
        url_patterns = [
            r"company/(\d+)",  # Numeric ID in URL
            r"company/([^/]+)/?",  # Vanity name
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, company_url)
            if match:
                identifier = match.group(1)
                
                # If numeric ID was found directly, return it
                if identifier.isdigit():
                    print(f"Found numeric company ID: {identifier}")
                    return identifier
                
                # Otherwise, search by company name
                company_name = identifier
                print(f"Searching for company: {company_name}")
                
                # Try to get company by name
                company_data = api.search_companies(company_name)
                
                if company_data and len(company_data.get("elements", [])) > 0:
                    for element in company_data["elements"]:
                        # Extract ID from entityUrn (format: "urn:li:company:123456")
                        urn = element.get("entityUrn", "")
                        if "company:" in urn:
                            company_id = urn.split(":")[-1]
                            print(f"Found company ID: {company_id} for {company_name}")
                            return company_id
                
        print("Company ID not found through URL parsing or API search")
        
        # Fallback: Try to extract directly from the URL
        print("Trying direct URL extraction...")
        response = api.get_company_updates(company_url)
        if response and "company" in str(response):
            # Some debugging info
            print(f"API Response structure: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            return company_url
    
    except Exception as e:
        print(f"Error extracting company ID: {str(e)}")
    
    return None

def get_company_details(api, company_id_or_url):
    """Get company details with better error handling"""
    try:
        print(f"\nFetching details for company ID/URL: {company_id_or_url}")
        company = api.get_company(company_id_or_url)
        
        if not company:
            print("No company data returned from API")
            return None
        
        # Print company details
        print("\n📊 Company Profile:")
        print(f"Name: {company.get('name', 'N/A')}")
        print(f"Industry: {company.get('industry', 'N/A')}")
        print(f"Description: {company.get('description', 'N/A')[:100]}..." 
              if company.get('description') else "Description: N/A")
        print(f"Website: {company.get('companyPageUrl', 'N/A')}")
        print(f"Employee Count: {company.get('staffCount', 'N/A')}")
        print(f"Headquarters: {company.get('headquarter', {}).get('city', 'N/A')}, "
              f"{company.get('headquarter', {}).get('country', 'N/A')}")
        
        return company
    except Exception as e:
        print(f"Error fetching company details: {str(e)}")
        return None

def get_company_updates(api, company_id, max_posts=10):
    """Get company posts with better error handling"""
    try:
        print(f"\nFetching recent posts for company ID: {company_id}")
        posts = api.get_company_updates(company_id, max_results=max_posts)
        
        if not posts:
            print("No posts found or error fetching posts")
            return []
        
        print("\n📢 Recent Posts & Engagement:")
        for i, post in enumerate(posts[:max_posts], 1):
            content = post.get('commentary', {}).get('text', 'No Content')
            print(f"{i}. {content[:100]}..." if len(content) > 100 else content)
            print(f"   Likes: {post.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numLikes', 0)}, "
                  f"Comments: {post.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numComments', 0)}\n")
        
        return posts
    except Exception as e:
        print(f"Error fetching company posts: {str(e)}")
        return []

def get_company_jobs(api, company_id, max_jobs=10):
    """Get company job postings with better error handling"""
    try:
        print(f"\nFetching job postings for company ID: {company_id}")
        job_postings = api.get_company_jobs(company_id)
        
        if not job_postings:
            print("No jobs found or error fetching jobs")
            return []
        
        print("\n💼 Recent Job Postings:")
        for i, job in enumerate(job_postings[:max_jobs], 1):
            print(f"{i}. {job.get('title', 'Unknown Position')} at {job.get('companyName', 'Unknown')}")
            if job.get('location'):
                print(f"   Location: {job.get('location')}")
            print(f"   Posted: {job.get('postedAt', 'Unknown date')}\n")
        
        return job_postings
    except Exception as e:
        print(f"Error fetching company jobs: {str(e)}")
        return []

def get_company_followers(api, company_id):
    """Get company follower count with error handling"""
    try:
        print(f"\nFetching follower count for company ID: {company_id}")
        followers_data = api.get_company_followers(company_id)
        
        follower_count = followers_data.get('paging', {}).get('total', 0)
        print(f"Follower Count: {follower_count}")
        
        return follower_count
    except Exception as e:
        print(f"Error fetching company followers: {str(e)}")
        # Try to get from company data as fallback
        try:
            company = api.get_company(company_id)
            follower_count = company.get('followingInfo', {}).get('followerCount', 0)
            print(f"Follower Count (from company data): {follower_count}")
            return follower_count
        except:
            return 0

def get_industry_benchmarks():
    """Return industry benchmarks for scoring (simplified)"""
    # In a real-world scenario, these would be dynamic, data-driven benchmarks
    return {
        "Technology": {
            "avg_followers": 50000,
            "avg_engagement_rate": 2.5,
            "avg_job_postings": 20,
            "avg_post_frequency": 3.5,  # posts per week
        },
        "Finance": {
            "avg_followers": 30000,
            "avg_engagement_rate": 1.5,
            "avg_job_postings": 15,
            "avg_post_frequency": 2.5,
        },
        # Default values for any industry not specified
        "default": {
            "avg_followers": 20000,
            "avg_engagement_rate": 1.0,
            "avg_job_postings": 10,
            "avg_post_frequency": 2.0,
        }
    }

def calculate_brand_value_score(company_data, company_posts, company_jobs, follower_count):
    """
    Calculate a brand value score based on LinkedIn data
    
    Mathematical logic:
    1. Profile Completeness Score (25%): Based on how complete the company profile is
    2. Engagement Score (30%): Based on post engagement relative to follower count
    3. Content Quality Score (15%): Based on post length, media presence, and consistency
    4. Hiring Activity Score (15%): Based on job posting volume and recency
    5. Network Score (15%): Based on follower count relative to industry benchmarks
    
    Each component is normalized to a 0-100 scale and then weighted
    """
    scores = {}
    benchmarks = get_industry_benchmarks()
    
    # Get industry-specific benchmarks or default
    industry = company_data.get('industry', 'default')
    if industry not in benchmarks:
        industry = "default"
    
    industry_benchmarks = benchmarks[industry]
    
    # 1. Profile Completeness Score (25%)
    profile_fields = [
        'name', 'tagline', 'description', 'website', 'industry', 
        'companyPageUrl', 'headquarter', 'specialities', 'staffCountRange'
    ]
    
    # Count how many fields are filled out
    filled_fields = sum(1 for field in profile_fields if company_data.get(field))
    
    # Normalize to 0-100 scale
    profile_completeness_score = (filled_fields / len(profile_fields)) * 100
    scores["profile_completeness"] = {
        "score": round(profile_completeness_score, 2),
        "weight": 0.25,
        "details": {
            "filled_fields": filled_fields,
            "total_fields": len(profile_fields)
        }
    }
    
    # 2. Engagement Score (30%)
    if company_posts and follower_count > 0:
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        for post in company_posts:
            social_counts = post.get('socialDetail', {}).get('totalSocialActivityCounts', {})
            total_likes += social_counts.get('numLikes', 0)
            total_comments += social_counts.get('numComments', 0)
            total_shares += social_counts.get('numShares', 0)
        
        # Calculate engagement rate: (likes + comments * 2 + shares * 3) / (follower count * post count) * 100
        # Comments and shares are weighted more as they require more effort
        weighted_engagement = total_likes + (total_comments * 2) + (total_shares * 3)
        post_count = len(company_posts)
        
        if post_count > 0:
            engagement_rate = (weighted_engagement / (follower_count * post_count)) * 100
            
            # Normalize engagement rate based on industry benchmarks (max is 3x industry avg)
            normalized_engagement_score = min(100, (engagement_rate / (industry_benchmarks["avg_engagement_rate"] * 3)) * 100)
            
            scores["engagement"] = {
                "score": round(normalized_engagement_score, 2),
                "weight": 0.30,
                "details": {
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "post_count": post_count,
                    "engagement_rate": round(engagement_rate, 2),
                    "industry_avg_rate": industry_benchmarks["avg_engagement_rate"]
                }
            }
        else:
            scores["engagement"] = {"score": 0, "weight": 0.30, "details": {"reason": "No posts found"}}
    else:
        scores["engagement"] = {"score": 0, "weight": 0.30, "details": {"reason": "No posts or followers found"}}
    
    # 3. Content Quality Score (15%)
    if company_posts:
        # Check post frequency (how regularly they post)
        post_dates = []
        post_lengths = []
        posts_with_media = 0
        
        # Analyze posts
        for post in company_posts:
            # Check if post has media
            has_media = False
            if post.get('content', {}).get('images') or post.get('content', {}).get('videos'):
                has_media = True
                posts_with_media += 1
            
            # Get post content length
            content = post.get('commentary', {}).get('text', '')
            post_lengths.append(len(content))
            
            # Extract date if available
            if 'time' in post:
                try:
                    post_date = datetime.fromtimestamp(post['time'] / 1000)  # Convert milliseconds to seconds
                    post_dates.append(post_date)
                except:
                    pass
        
        # Calculate content quality metrics
        avg_post_length = sum(post_lengths) / len(post_lengths) if post_lengths else 0
        media_ratio = posts_with_media / len(company_posts) if company_posts else 0
        
        # Calculate post frequency (posts per week) if we have date information
        post_frequency = 0
        if len(post_dates) >= 2:
            post_dates.sort(reverse=True)  # Sort dates newest to oldest
            date_range_days = (post_dates[0] - post_dates[-1]).days
            if date_range_days > 0:
                post_frequency = (len(post_dates) / date_range_days) * 7  # Convert to posts per week
        
        # Normalize post length score (ideal is 500-1000 characters)
        length_score = min(100, (avg_post_length / 500) * 100) if avg_post_length < 500 else (100 - min(100, max(0, (avg_post_length - 1000) / 50)))
        
        # Normalize media ratio (higher is better, max 100%)
        media_score = media_ratio * 100
        
        # Normalize post frequency against industry benchmark
        frequency_score = min(100, (post_frequency / industry_benchmarks["avg_post_frequency"]) * 100)
        
        # Combine the metrics (weighted average)
        content_quality_score = (length_score * 0.3) + (media_score * 0.3) + (frequency_score * 0.4)
        
        scores["content_quality"] = {
            "score": round(content_quality_score, 2),
            "weight": 0.15,
            "details": {
                "avg_post_length": round(avg_post_length, 2),
                "posts_with_media_percentage": round(media_ratio * 100, 2),
                "post_frequency_per_week": round(post_frequency, 2),
                "industry_avg_frequency": industry_benchmarks["avg_post_frequency"]
            }
        }
    else:
        scores["content_quality"] = {"score": 0, "weight": 0.15, "details": {"reason": "No posts found"}}
    
    # 4. Hiring Activity Score (15%)
    if company_jobs:
        job_count = len(company_jobs)
        
        # Check job recency (percentage of jobs posted in the last 30 days)
        recent_jobs = 0
        
        for job in company_jobs:
            posted_date_str = job.get('postedAt', '')
            if posted_date_str:
                try:
                    # LinkedIn can use various date formats, try to handle common ones
                    if 'ago' in posted_date_str.lower():  # e.g., "2 days ago"
                        recent_jobs += 1  # Assume it's recent if it contains "ago"
                    elif any(term in posted_date_str.lower() for term in ['hour', 'day', 'week', 'month']):
                        recent_jobs += 1
                except:
                    pass
        
        recent_job_ratio = recent_jobs / job_count if job_count > 0 else 0
        
        # Normalize job count relative to industry benchmark
        job_count_score = min(100, (job_count / industry_benchmarks["avg_job_postings"]) * 100)
        
        # Normalize recency (higher is better)
        recency_score = recent_job_ratio * 100
        
        # Combine metrics
        hiring_score = (job_count_score * 0.6) + (recency_score * 0.4)
        
        scores["hiring_activity"] = {
            "score": round(hiring_score, 2),
            "weight": 0.15,
            "details": {
                "job_count": job_count,
                "recent_jobs_ratio": round(recent_job_ratio * 100, 2),
                "industry_avg_job_postings": industry_benchmarks["avg_job_postings"]
            }
        }
    else:
        scores["hiring_activity"] = {"score": 0, "weight": 0.15, "details": {"reason": "No job postings found"}}
    
    # 5. Network Score (15%)
    if follower_count > 0:
        # Normalize against industry benchmark (max is 5x industry avg)
        follower_score = min(100, (follower_count / (industry_benchmarks["avg_followers"] * 5)) * 100)
        
        # Additional weighting for logarithmic scale (diminishing returns for very large follower counts)
        log_factor = min(1.5, max(0.5, (math.log10(follower_count) / math.log10(industry_benchmarks["avg_followers"]))))
        follower_score = follower_score * log_factor
        follower_score = min(100, follower_score)  # Cap at 100
        
        scores["network"] = {
            "score": round(follower_score, 2),
            "weight": 0.15,
            "details": {
                "follower_count": follower_count,
                "industry_avg_followers": industry_benchmarks["avg_followers"],
                "log_scaling_factor": round(log_factor, 2)
            }
        }
    else:
        scores["network"] = {"score": 0, "weight": 0.15, "details": {"reason": "No follower data available"}}
    
    # Calculate final weighted score
    final_score = 0
    for component, data in scores.items():
        final_score += data["score"] * data["weight"]
    
    # Map final score to qualitative rating
    rating = "Unknown"
    if final_score >= 85:
        rating = "Excellent"
    elif final_score >= 70:
        rating = "Very Good"
    elif final_score >= 55:
        rating = "Good"
    elif final_score >= 40:
        rating = "Average"
    elif final_score >= 25:
        rating = "Below Average"
    else:
        rating = "Poor"
    
    # Return comprehensive brand value assessment
    brand_assessment = {
        "company_name": company_data.get('name', 'Unknown'),
        "industry": industry,
        "overall_score": round(final_score, 2),
        "rating": rating,
        "component_scores": scores,
        "assessment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assessment_version": "1.0",
        "recommendations": generate_recommendations(scores)
    }
    
    return brand_assessment

def generate_recommendations(scores):
    """Generate specific recommendations based on component scores"""
    recommendations = []
    
    # Profile completeness recommendations
    if scores.get("profile_completeness", {}).get("score", 0) < 70:
        recommendations.append({
            "category": "Profile Completeness",
            "recommendation": "Complete your LinkedIn company profile with missing information such as headquarters, website, or specialities.",
            "priority": "High"
        })
    
    # Engagement recommendations
    engagement_score = scores.get("engagement", {}).get("score", 0)
    if engagement_score < 50:
        recommendations.append({
            "category": "Engagement",
            "recommendation": "Improve post engagement by asking questions, creating polls, or responding to comments more actively.",
            "priority": "High" if engagement_score < 30 else "Medium"
        })
    
    # Content quality recommendations
    content_score = scores.get("content_quality", {}).get("score", 0)
    content_details = scores.get("content_quality", {}).get("details", {})
    
    if content_score < 60:
        if content_details.get("avg_post_length", 0) < 200:
            recommendations.append({
                "category": "Content Quality",
                "recommendation": "Create more detailed and value-driven content. Aim for 500-1000 characters per post.",
                "priority": "Medium"
            })
        
        if content_details.get("posts_with_media_percentage", 0) < 50:
            recommendations.append({
                "category": "Content Quality",
                "recommendation": "Include more visual elements like images, videos, or infographics in your posts.",
                "priority": "Medium"
            })
        
        if content_details.get("post_frequency_per_week", 0) < content_details.get("industry_avg_frequency", 2):
            recommendations.append({
                "category": "Content Strategy",
                "recommendation": f"Increase posting frequency to at least {content_details.get('industry_avg_frequency', 2)} times per week to match industry average.",
                "priority": "High"
            })
    
    # Hiring activity recommendations
    hiring_score = scores.get("hiring_activity", {}).get("score", 0)
    if hiring_score < 40:
        recommendations.append({
            "category": "Recruitment Branding",
            "recommendation": "Showcase your company culture and employee experiences to enhance your employer brand.",
            "priority": "Medium"
        })
    
    # Network recommendations
    network_score = scores.get("network", {}).get("score", 0)
    if network_score < 50:
        recommendations.append({
            "category": "Network Growth",
            "recommendation": "Run targeted LinkedIn ad campaigns to increase follower count and brand visibility.",
            "priority": "Medium"
        })
    
    # If no specific recommendations were generated, add a generic one
    if not recommendations:
        recommendations.append({
            "category": "General",
            "recommendation": "Maintain your current LinkedIn strategy while experimenting with new content formats.",
            "priority": "Low"
        })
    
    return recommendations

def cache_company_data(company_id, company_data, posts, jobs, follower_count, brand_assessment):
    """Cache company data and brand assessment to JSON file"""
    try:
        if not company_data:
            print("No company data to cache")
            return False
            
        os.makedirs("cache", exist_ok=True)
        cache_file = f"cache/company_{company_id}_assessment.json"
        data_to_save = {
            "company_info": company_data,
            "recent_posts": posts,
            "job_postings": jobs,
            "follower_count": follower_count,
            "brand_assessment": brand_assessment,
            "cache_timestamp": time.time()
        }
        with open(cache_file, "w") as f:
            json.dump(data_to_save, f, indent=2)
        print(f"\n✅ Company data and brand assessment cached to {cache_file}")
        return True
    except Exception as e:
        print(f"Error caching company data: {str(e)}")
        return False

def display_brand_assessment(brand_assessment):
    """Print formatted brand assessment to console"""
    print("\n" + "=" * 50)
    print(f"🏆 BRAND VALUE ASSESSMENT: {brand_assessment['company_name']}")
    print("=" * 50)
    print(f"Industry: {brand_assessment['industry']}")
    print(f"Overall Score: {brand_assessment['overall_score']}/100 ({brand_assessment['rating']})")
    print("-" * 50)
    
    print("\n📊 COMPONENT SCORES:")
    for component, data in brand_assessment['component_scores'].items():
        component_name = component.replace("_", " ").title()
        print(f"• {component_name}: {data['score']}/100 (Weight: {int(data['weight']*100)}%)")
    
    print("\n🔍 KEY INSIGHTS:")
    for component, data in brand_assessment['component_scores'].items():
        if "details" in data and "reason" not in data["details"]:
            component_name = component.replace("_", " ").title()
            print(f"\n{component_name}:")
            for metric, value in data["details"].items():
                metric_name = metric.replace("_", " ").title()
                print(f"  - {metric_name}: {value}")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, rec in enumerate(brand_assessment['recommendations'], 1):
        priority_symbol = "🔴" if rec["priority"] == "High" else "🟠" if rec["priority"] == "Medium" else "🟢"
        print(f"{i}. {priority_symbol} {rec['category']}: {rec['recommendation']}")
    
    print("\n" + "=" * 50)
    print(f"Assessment Date: {brand_assessment['assessment_date']}")
    print("=" * 50)

def main():
    # Check for cached cookies or prompt for login
    if not os.path.exists(COOKIES_FILE):
        print("No cookies found. Starting login process...")
        login_and_save_cookies()
    
    # Load cookies
    cookies = load_cookies()
    if not cookies:
        print("Failed to load cookies. Please try logging in again.")
        login_and_save_cookies()
        cookies = load_cookies()
        if not cookies:
            print("Still unable to load cookies. Exiting...")
            sys.exit(1)
    
    # Initialize LinkedIn API client with cookies
    try:
        api = Linkedin("", "", cookies=cookies)
        print("LinkedIn API initialized successfully with cookies")
    except Exception as e:
        print(f"Error initializing LinkedIn API: {str(e)}")
        print("Please try logging in again")
        login_and_save_cookies()
        sys.exit(1)
    
    # Get company URL from user
    company_url = input("\nEnter LinkedIn company URL (e.g., https://www.linkedin.com/company/google/): ").strip()
    if not company_url:
        company_url = "https://www.linkedin.com/company/google/"
        print(f"Using default company URL: {company_url}")
    
    # Extract company ID
    company_id = extract_company_id(api, company_url)
    if not company_id:
        print(f"Failed to extract company ID from {company_url}")
        company_id = input("Please enter company ID manually (if known): ").strip()
        if not company_id:
            print("No company ID provided. Exiting.")
            sys.exit(1)
    
    # Fetch company data in stages with rate limiting
    print("\n📊 FETCHING COMPANY DATA FOR BRAND ASSESSMENT...")
    
    # Step 1: Get basic company profile
    company_data = get_company_details(api, company_id)
    time.sleep(2)  # Respect rate limits
    
    # Step 2: Get recent posts for engagement analysis
    company_posts = get_company_updates(api, company_id)
    time.sleep(2)  # Respect rate limits
    
    # Step 3: Get job postings for hiring activity
    company_jobs = get_company_jobs(api, company_id)
    time.sleep(2)  # Respect rate limits
    
    # Step 4: Get follower count for network analysis
    follower_count = get_company_followers(api, company_id)
    
    # Calculate brand value score
    print("\n🧮 CALCULATING BRAND VALUE SCORE...")
    if company_data:
        brand_assessment = calculate_brand_value_score(
            company_data, company_posts, company_jobs, follower_count
        )
        
        # Display the assessment
        display_brand_assessment(brand_assessment)
        
        # Cache the data and assessment
        cache_company_data(company_id, company_data, company_posts, company_jobs,follower_count)
        
        return  {"Id":company_id,"data" : company_data, "posts":company_posts,"jobs": company_jobs,"follower_count":follower_count}
    
if __name__ == '__main__':
    main(   )