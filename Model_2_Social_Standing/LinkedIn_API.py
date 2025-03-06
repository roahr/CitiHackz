import json
import time
import os
import sys
import re
import pickle
from dotenv import load_dotenv
from linkedin_api import Linkedin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

load_dotenv()

# LinkedIn Credentials (Used only for Selenium)
TEST_LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
TEST_LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# LinkedIn Login URL
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"


def setup_selenium():
    """Launch Selenium browser for manual login (CAPTCHA bypass)"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Open in full-screen mode
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service("path/to/chromedriver")  # Set the correct path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def login_and_save_cookies():
    """Open LinkedIn login page for manual login, solve CAPTCHA, and save cookies."""
    driver = setup_selenium()
    driver.get(LINKEDIN_LOGIN_URL)

    # Wait for manual login and CAPTCHA solving
    print("\nPlease log in to LinkedIn manually and solve any CAPTCHA.")
    input("Press Enter after completing login...")

    # Save cookies
    cookies = driver.get_cookies()
    with open("linkedin_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

    print("\nCookies saved successfully!")
    driver.quit()


def load_cookies():
    """Load saved cookies for LinkedIn API authentication."""
    try:
        with open("linkedin_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
        return cookies
    except FileNotFoundError:
        print("\nNo saved cookies found. Run login_and_save_cookies() first.")
        return None


def main():
    # If no cookies, prompt manual login
    if not os.path.exists("linkedin_cookies.pkl"):
        login_and_save_cookies()

    # Load cookies and authenticate LinkedIn API
    cookies = load_cookies()
    if not cookies:
        print("\nCould not load cookies. Exiting...")
        sys.exit()

    # Initialize LinkedIn API client with cookies
    api = Linkedin("", "", cookies=cookies)

    # Example LinkedIn company URL
    company_url = "https://www.linkedin.com/company/google/"  # Change to real URL

    # Extract company ID from URL
    company_id = extract_company_id(api, company_url)
    if not company_id:
        print(f"Unable to fetch company ID from {company_url}")
        return

    print(f"Extracted Company ID: {company_id}")

    try:
        # Fetch company profile data
        company = api.get_company(company_id)

        # Print company details
        print("\nCompany Profile:")
        print(f"Name: {company.get('name', 'N/A')}")
        print(f"Industry: {company.get('industry', 'N/A')}")
        print(f"Employee Count: {company.get('staffCount', 'N/A')}")
        print(f"Growth Rate: {company.get('growthRate', 'N/A')}")

        # Fetch company posts
        posts = api.get_company_updates(company_id, max_results=5)
        print("\n📢 Recent Posts & Engagement:")
        for post in posts:
            print(f"- {post.get('commentary', 'No Content')[:100]}...")
            print(f"  Likes: {post.get('numLikes', 0)}, Comments: {post.get('numComments', 0)}\n")

        # Fetch job postings
        job_postings = api.get_company_jobs(company_id)
        print("\nHiring Trends:")
        for job in job_postings[:5]:
            print(f"- {job.get('title', 'Unknown Position')} at {job.get('companyName', 'Unknown')}")

        # Cache the company data
        cache_company_data(company_id, company, posts, job_postings)

        # Respect rate limits
        time.sleep(2)

    except Exception as e:
        print(f"Error fetching company data for {company_id}: {str(e)}")


def extract_company_id(api, company_url):
    """Extracts company ID from LinkedIn company URL"""
    try:
        match = re.search(r"company/([^/]+)/?", company_url)
        if match:
            company_name = match.group(1)
            company_data = api.search_companies(company_name)
            if company_data and "elements" in company_data:
                return company_data["elements"][0].get("entityUrn", "").split(":")[-1]  # Extract ID from urn
    except Exception as e:
        print(f"Error extracting company ID: {str(e)}")
    return None


def cache_company_data(company_id, company_data, posts, jobs):
    """Cache company data to a JSON file"""
    try:
        os.makedirs("cache", exist_ok=True)
        cache_file = f"cache/company_{company_id}.json"
        data_to_save = {
            "company_info": company_data,
            "recent_posts": posts,
            "job_postings": jobs,
        }
        with open(cache_file, "w") as f:
            json.dump(data_to_save, f, indent=2)
        print(f"\nCompany data cached to {cache_file}")
    except Exception as e:
        print(f"Error caching company data: {str(e)}")


if __name__ == "__main__":
    main()
