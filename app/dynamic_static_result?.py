import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession




"""
from requests_html import HTMLSession

# Define the search URL
url = "https://www.di.se/search/?query=Volvo"

# Fetch and render the page
session = HTMLSession()
response = session.get(url)
response.html.render(timeout=20)  # Execute JavaScript

# Print first 2000 characters of the rendered HTML for inspection
print(response.html.html[:2000])


"""

"""
from requests_html import HTMLSession
import time

# Define search URL
url = "https://www.di.se/search/?query=Volvo"

# Create session and fetch the page
session = HTMLSession()
response = session.get(url)

# Render JavaScript
try:
    response.html.render(timeout=30, sleep=3, scrolldown=5)  # Longer timeout, force scrolling
    print("✅ Fully Rendered Page Loaded Successfully!\n")
except Exception as e:
    print("❌ Error during rendering:", e)
    exit()

# Print the first 2000 characters for debugging
print(response.html.html[:2000])

"""

"""

import asyncio
from pyppeteer import launch

async def fetch_full_page(url):
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url, {"waitUntil": "networkidle2"})  # Wait until network is idle
    content = await page.content()  # Get fully loaded HTML
    print(content[:2000])  # Print first 2000 characters to inspect
    await browser.close()

url = "https://www.di.se/search/?query=Volvo"
asyncio.run(fetch_full_page(url))

"""

"""
import asyncio
from pyppeteer import launch

async def fetch_with_scrolling(url):
    browser = await launch(headless=False, args=['--no-sandbox'])  # Set headless=False to see the page
    page = await browser.newPage()
    
    # Set a real user-agent to avoid bot detection
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    await page.goto(url, {"waitUntil": "networkidle2"})  # Wait until network requests settle

    # Scroll down to trigger lazy loading
    for _ in range(3):  # Scroll multiple times
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(3)  # Allow time for content to load

    content = await page.content()  # Get fully loaded HTML
    print(content[:2000])  # Print first 2000 characters to inspect
    await browser.close()

url = "https://www.di.se/search/?query=Volvo"
asyncio.run(fetch_with_scrolling(url))

"""

import requests
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
import time

"""

SEARCH_URL = "https://www.di.se/search/?query=Volvo"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_FILE = "articles_output.txt"
MAX_ARTICLES = 15  # Only fetch 15 relevant articles

# 🔹 1️⃣ Fetch 15 RELEVANT Articles Only
def fetch_relevant_articles():
    print("\n🟢 Fetching relevant article links...\n")
    response = requests.get(SEARCH_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch articles: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", href=True)

    relevant_links = []
    for article in articles:
        title = article.get_text(strip=True)
        link = article['href']
        full_link = f"https://www.di.se{link}" if link.startswith("/") else link

        # ✅ Allow only real articles (Nyheter, Ledare, Analys)
        if any(section in full_link for section in ["/nyheter/", "/ledare/", "/analys/", "/debatt/", "/ekonomi/", "/naringsliv/"]):
            relevant_links.append((title, full_link))

        # Limit results
        if len(relevant_links) == MAX_ARTICLES:
            break

    if not relevant_links:
        print("\n⚠ No relevant articles found.\n")
        return []

    print(f"\n✅ Found {len(relevant_links)} relevant articles.\n")
    for i, (title, link) in enumerate(relevant_links, 1):
        print(f"{i}. {title} -> {link}")

    return relevant_links


# 🔹 2️⃣ Identify Static, Dynamic, or Paywall
def check_article_type(url):
    print(f"\n🔎 Checking article type: {url}")

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return "❌ Unable to fetch"

    soup = BeautifulSoup(response.text, "html.parser")

    # Detect Paywall
    paywall_detected = bool(
        soup.find(text=lambda text: text and ("subscribe" in text.lower() or "login" in text.lower())) or
        soup.select("div[class*='paywall'], div[class*='premium']")
    )
    if paywall_detected:
        print(f"🔒 Paywall detected for {url}")
        return "🔒 Paywall"

    # Detect Empty Content (Potential Dynamic Loading)
    content_section = soup.select("div.article__content p")
    if not content_section:
        print(f"⚠ Dynamic content detected for {url}")
        return "⚠ Dynamic Loading"

    print(f"✅ Static article detected: {url}")
    return "✅ Static"


# 🔹 3️⃣ Extract Content for Static Articles
def extract_static_article(url):
    print(f"\n📄 Extracting article from: {url}")

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {"title": "No Title", "date": "No Date", "author": "No Author", "content": "❌ Unable to fetch"}

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract Title
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Title Found"

    # Extract Date
    date_tag = soup.find("time")
    date = date_tag.get_text(strip=True) if date_tag else "No Date Found"

    # Extract Author
    author_tag = soup.find("span", class_="byline__author")
    author = author_tag.get_text(strip=True) if author_tag else "No Author Found"

    # Extract Content
    content = "\n\n".join([p.get_text(strip=True) for p in soup.select("div.article__content p")])

    if not content.strip():
        print(f"⚠ Static extraction failed: No content found in {url}")
        return {"title": title, "date": date, "author": author, "content": "⚠ Content Extraction Failed"}

    return {"title": title, "date": date, "author": author, "content": content}


# 🔹 4️⃣ Fetch Dynamic Articles if Needed
async def fetch_dynamic(url):
    print(f"🔄 Trying Dynamic Fetch for {url}...")
    try:
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.setUserAgent(HEADERS["User-Agent"])
        await page.goto(url, {"waitUntil": "networkidle2", "timeout": 30000})

        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")

        # Retry extraction after dynamic fetch
        content_text = "\n\n".join([p.get_text(strip=True) for p in soup.select("div.article__content p")])
        if not content_text.strip():
            return {"title": "No Title", "date": "No Date", "author": "No Author", "content": "⚠ Dynamic Extraction Failed"}
        
        return extract_static_article(url)

    except Exception as e:
        print(f"❌ Dynamic Fetch Failed: {e}")
        return {"title": "No Title", "date": "No Date", "author": "No Author", "content": "❌ Dynamic Fetch Failed"}


# 🔹 5️⃣ Process and Save Articles
def process_and_save_articles(article_links):
    extracted_articles = []

    for i, (title, url) in enumerate(article_links):
        print(f"\n➡️ Processing Article {i+1}/{len(article_links)}: {title}")

        article_type = check_article_type(url)

        if article_type == "✅ Static":
            article_data = extract_static_article(url)

        elif article_type == "⚠ Dynamic Loading":
            article_data = asyncio.run(fetch_dynamic(url))

        elif article_type == "🔒 Paywall":
            article_data = {"title": title, "date": "Unknown", "author": "Unknown", "content": "❌ Paywall Detected"}

        else:
            article_data = {"title": title, "date": "Unknown", "author": "Unknown", "content": "❌ Unable to Fetch"}

        extracted_articles.append(article_data)

    # Save to File
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, article in enumerate(extracted_articles):
            f.write(f"📰 Article {i+1}\n")
            f.write(f"Title: {article['title']}\n")
            f.write(f"Date: {article['date']}\n")
            f.write(f"Author: {article['author']}\n")
            f.write(f"Content:\n{article['content']}\n")
            f.write("=" * 50 + "\n")

    print(f"\n✅ Results saved to {OUTPUT_FILE}")


# 🚀 Run the Script
if __name__ == "__main__":
    start_time = time.time()

    # Step 1: Fetch **only relevant** article links
    article_links = fetch_relevant_articles()

    if article_links:
        # Steps 2-5: Process and save articles
        process_and_save_articles(article_links)

    print(f"\n⏱️ Total Execution Time: {round(time.time() - start_time, 2)} seconds")


"""

import requests
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
import time

import requests
from bs4 import BeautifulSoup
import time

SEARCH_URL = "https://www.di.se/search/?query={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Output file
OUTPUT_FILE = "articles_output.txt"

def fetch_search_results(company_name):
    """Fetches search results and filters out paywalled articles."""
    url = SEARCH_URL.format(company_name)
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Failed with status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="article__main")

    relevant_articles = []
    for article in articles:
        title = article.get("data-title", "No Title Found")
        link = article.get("data-url", "")
        restriction = article.get("data-access-restriction", "")

        if restriction == "Free" and link:
            full_link = f"https://www.di.se{link}"
            relevant_articles.append((title, full_link))

    return relevant_articles

def extract_article_content(url):
    """Extracts title, date, author, and content from an article."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return "❌ Failed to fetch article."

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Title Found"
    date = soup.find("time").get_text(strip=True) if soup.find("time") else "No Date Found"
    author = "No Author Found"

    author_tag = soup.find(class_="byline__author")
    if author_tag:
        author = author_tag.get_text(strip=True)

    paragraphs = soup.select("div.article__content p")
    content = "\n\n".join([p.get_text(strip=True) for p in paragraphs]) or "❌ Unable to extract text."

    return title, date, author, content

def save_articles(articles):
    """Saves extracted articles to a text file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        if not articles:
            file.write("❌ No relevant articles found.\n")
            return

        for i, (title, url) in enumerate(articles, 1):
            print(f"📄 Extracting: {title}")
            title, date, author, content = extract_article_content(url)
            
            file.write(f"📰 Article {i}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Date: {date}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Content:\n{content}\n")
            file.write("=" * 50 + "\n")

            time.sleep(1)  # Avoid aggressive requests

def main():
    """Main function to run the script."""
    company_name = input("Enter company name: ").strip()
    print(f"\n🟢 Searching for articles about '{company_name}'...\n")

    articles = fetch_search_results(company_name)
    print(f"✅ Found {len(articles)} relevant articles.\n")

    save_articles(articles)
    print(f"\n✅ Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
