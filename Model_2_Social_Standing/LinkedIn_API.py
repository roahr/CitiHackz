import json
import time
import os
import sys
from linkedin_api import Linkedin
from dotenv import load_dotenv

# Load LinkedIn Credentials from .env
load_dotenv()
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def main():
    """Main function to authenticate and scrape LinkedIn company profiles."""
    if not (LINKEDIN_USERNAME and LINKEDIN_PASSWORD):
        print("❌ LinkedIn credentials missing. Exiting...")
        sys.exit()

    # Initialize API client with username and password
    try:
        api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD, refresh_cookies=True)
        print("\n✅ LinkedIn API Authentication Successful!")
    except Exception as e:
        print(f"\n❌ Authentication Failed: {str(e)}")
        sys.exit()

    # Example company public IDs (Modify this to scrape multiple companies)
    company_ids = ["google", "microsoft", "amazon"]  

    results = {}

    for company_id in company_ids:
        try:
            # Fetch company profile
            company = api.get_company(company_id)
            
            if not company:  # Check if response is empty
                print(f"\n⚠️ No data found for {company_id}. Check if the company ID is correct.")
                continue
            
            print(f"\n🔍 Raw API Response for {company_id}:")
            print(json.dumps(company, indent=2))  # Inspect available fields

            # Fetch company posts
            posts = api.get_company_updates(company_id, max_results=5)
            if not posts:
                print(f"\n⚠️ No posts found for {company_id}. Might be restricted.")

            # Fetch company job postings
            job_postings = api.get_company_jobs(company_id)
            if not job_postings:
                print(f"\n⚠️ No job postings found for {company_id}. Might be restricted.")

            # Structure the company data as JSON
            company_data = {
                "company_info": {
                    "name": company.get("name", "N/A"),
                    "industry": company.get("industry", "N/A"),
                    "description": company.get("description", "N/A"),
                    "headquarters": company.get("headquarter", {}).get("city", "N/A"),
                    "staff_count": company.get("staffCount", "N/A"),
                    "growth_rate": company.get("growthRate", "N/A"),
                    "followers": company.get("followerCount", "N/A"),
                    "specialties": company.get("specialties", []),
                    "funding": company.get("fundingData", {}).get("totalFunding", "N/A"),
                    "founded_year": company.get("yearFounded", "N/A"),
                    "website": company.get("website", "N/A"),
                    "company_type": company.get("companyType", "N/A"),
                    "locations": company.get("confirmedLocations", []),
                    "ceo": company.get("ceo", {}).get("name", "N/A"),
                    "revenue": company.get("annualRevenue", "N/A"),
                    "business_model": company.get("businessModel", "N/A"),
                    "affiliated_companies": company.get("affiliatedCompanies", [])
                },
                "social_engagement": [
                    {
                        "post_text": post.get("commentary", "No Content"),
                        "likes": post.get("numLikes", 0),
                        "comments": post.get("numComments", 0)
                    }
                    for post in posts
                ] if posts else [],
                "hiring_trends": [
                    {
                        "job_title": job.get("title", "Unknown Position"),
                        "company_name": job.get("companyName", "Unknown"),
                        "location": job.get("formattedLocation", "N/A")
                    }
                    for job in job_postings[:5]
                ] if job_postings else []
            }

            # Store results
            results[company_id] = company_data

            # Cache company data
            cache_company_data(company_id, company_data)

            # Respect LinkedIn API rate limits
            time.sleep(2)

        except Exception as e:
            print(f"\n❌ Error fetching company {company_id}: {str(e)}")

    # Save JSON for further processing
    save_json_output(results)

def cache_company_data(company_id, company_data):
    """Cache company profile, posts, and job data to a JSON file."""
    try:
        os.makedirs("cache", exist_ok=True)
        cache_file = f"cache/company_{company_id}.json"
        with open(cache_file, "w") as f:
            json.dump(company_data, f, indent=2)
        print(f"\n✅ Cached company data at {cache_file}")
    except Exception as e:
        print(f"\n❌ Error caching company data: {str(e)}")

def save_json_output(data):
    """Saves the JSON output for further processing in a pipeline."""
    output_file = "linkedin_company_data.json"
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ JSON Output saved at {output_file}")
    except Exception as e:
        print(f"\n❌ Error saving JSON output: {str(e)}")

if __name__ == "__main__":
    main()
