
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import re
from urllib.parse import urlparse



CUSTOM_SEARCH_ENGINE_ID = '0537f5d70cf294823'  # Replace with your actual CSE ID
API_KEY = 'AIzaSyB1MxcYT2cv9A4oMLzvybL5QkGYxix7FtM'  # Replace with your API key

######################################################
from requests_html import HTMLSession  # Correct import
from bs4 import BeautifulSoup
import time
import asyncio
import nest_asyncio  # 🚀 Fix for event loop issue
from pyppeteer import launch

# 🔹 Fix event loop issue for Jupyter, nested async calls
nest_asyncio.apply()

CHROME_PATH = "/Users/MR_1/Library/Application Support/pyppeteer/local-chromium/1181205/chrome-mac/Chromium.app/Contents/MacOS/Chromium"

async def launch_browser():
    """Launches the headless browser using Pyppeteer."""
    browser = await launch(headless=True, executablePath=CHROME_PATH, args=['--no-sandbox'])
    print("✅ Chromium launched successfully!")
    await browser.close()

# ✅ Run launch browser first
asyncio.run(launch_browser())

# ✅ Preferred sources
PREFERRED_SOURCES = {
    "CNBC": "https://www.cnbc.com/search/?query=",
    "Financial Times": "https://www.ft.com/search?q=",
    "The Guardian": "https://www.theguardian.com/world?q=",
    "Di.se": "https://www.di.se/search/?query="
}

# ✅ Updated site patterns
SITE_PATTERNS = {
    "cnbc.com": {"tag": "div", "class": "SearchResult-searchResultContent"},  
    "ft.com": {"tag": "a", "class": "js-teaser-heading-link"},
    "theguardian.com": {"tag": "a", "class": "fc-item__link"},
    "di.se": {"tag": "a", "class": "di-teaser__headline"}
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_with_js(url, max_retries=3):
    """Fetch URL and execute JavaScript to load dynamic content."""
    session = HTMLSession()

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=HEADERS)
            response.html.render(timeout=20)  # Render JavaScript
            return response.text
        except Exception as e:
            print(f"⚠ Attempt {attempt + 1} failed: {e}")
            time.sleep(3)

    return None


def fetch_preferred_sources(company_name):
    """Scrapes articles from preferred sources."""
    all_articles = []

    for source, base_url in PREFERRED_SOURCES.items():
        try:
            url = f"{base_url}{company_name}"
            print(f"🔍 Fetching: {url}")

            html = fetch_with_js(url)  # Use JavaScript rendering
            if not html:
                print(f"❌ Failed to fetch {source}")
                continue

            soup = BeautifulSoup(html, "html.parser")

            # 🔍 Debugging: Print a snippet of the page structure
            print(f"\n🔍 DEBUG {source}: First 2000 characters of response")
            print(soup.prettify()[:2000])

            source_domain = base_url.split("//")[-1].split("/")[0]  
            structure = SITE_PATTERNS.get(source_domain, {"tag": "a", "class": "default-class"})

            articles = soup.find_all(structure["tag"], class_=structure["class"])[:5]

            if not articles:
                print(f"⚠ No articles found for {source}. Checking alternative structures...")
                articles = soup.find_all("a", href=True)[:5]  # Try generic extraction

            for article in articles:
                title = article.get_text(strip=True)
                link = article["href"]

                # Fix relative links
                if not link.startswith("http"):
                    link = f"{base_url.rstrip('/')}{link}"

                all_articles.append({"title": title, "link": link})

        except Exception as e:
            print(f"⚠ Error fetching articles from {source}: {e}")

    return all_articles


# ✅ Run the test
company_name = "Volvo"
results = fetch_preferred_sources(company_name)

print("\n🔹 Extracted Articles:")
for idx, article in enumerate(results, 1):
    print(f"{idx}. {article['title']} -> {article['link']}")
