import requests
from bs4 import BeautifulSoup
import os, io 


"""
def headlines():

    url = "https://www.svt.se/nyheter/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    print("  this function is something....")
    print("Responses are :  ", response)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hämta alla nyhetsrubriker
        headlines = soup.find_all("h2", class_="nyh__headline")  # Justera klassen beroende på HTML-strukturen
        
        for h in headlines:
            print(h.get_text(strip=True))
        
        printint("The output is: ",  url)
        return url
    else:
        print("Kunde inte hämta sidan.")



a= headlines()
print(" the result is: ", a)



########################################

import requests
from bs4 import BeautifulSoup

# Request the page
url = 'https://www.expressen.se'  # Replace with the actual URL
response = requests.get(url)

# Check if the request was successful (HTTP Status Code 200)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print the title to confirm the page loaded
    print("Page Title:", soup.title.string)

    # Find all article links on the site
    # You can modify this to look for specific classes or elements related to articles
    articles = soup.find_all('a', href=True)

    # Extract and print the article links
    for article in articles:
        link = article.get('href')
        # Filter for article links (you can refine this depending on how article links are structured)
        if link and 'expressen.se' in link:  # Make sure it's a valid link on the di.se domain
            print("Article Link:", link)
        else:
            continue
else:
    print(f"Failed to retrieve the page, status code: {response.status_code}")



########################################

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup


print("Hello World .....")
# Request the page
url = 'https://www.di.se'  # Replace with the actual URL
print(f"Requesting URL: {url}")  # Logging the URL being requested

# Sending request with headers to simulate a browser request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
response = requests.get(url, headers=headers)

# Check if the request was successful (HTTP Status Code 200)
print(f"Status Code: {response.status_code}")  # Logging the status code to understand what happened
if response.status_code == 200:
    print("Page loaded successfully!")  # Logging successful page load
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print the title to confirm the page loaded
    print("Page Title:", soup.title.string)

    # Find all article links on the site
    articles = soup.find_all('a', href=True)
    print(f"Found {len(articles)} links on the page.")  # Logging the number of links found

    # Check and print the first 10 links to inspect their structure
    for i, article in enumerate(articles[:10]):  # Limiting to first 10 for inspection
        link = article.get('href')
        print(f"Link {i + 1}: {link}")

    article_found = False
    # Refined filter for article links (inspect their structure)
    # Filter for article links by looking for URL patterns
    article_links = []
    for article in articles:
        link = article.get('href')
        if link and ('/nyhet/' in link or '/artiklar/' in link):  # Looking for article URLs
            if link.startswith('http'):
                article_links.append(link)
            else:
                article_links.append('https://www.di.se' + link)  # Handle relative links

    # Print the filtered article links
    if article_links:
        print("Found article links:")
        for link in article_links:
            print(link)
    else:
        print("No article links found.")


        if not article_found:
            print("No article links found matching the criteria.")
        else:
            print(f"Failed to retrieve the page, status code: {response.status_code}")  # Logging failure

            # If the status code isn't 200, print the response content
            print("Response Content:")
            print(response.text[:500])  # Print first 500 characters to get a glimpse of the response






import random
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_articles(urls, company):
    # Start a session
    session = requests.Session()

    # Set up headers for the requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Get today's date in 'YYYY-MM-DD' format
    today = datetime.today().strftime('%Y-%m-%d')
    
    articles_data = []

    # Loop through all the URLs provided
    for url in urls:
        print(f"Requesting URL: {url}")
        
        # Make the request with the session object
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            print(f"Page loaded successfully from {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all article links
            articles = soup.find_all('a', href=True)

            relevant_articles = []
            for article in articles:
                text = article.get_text().lower()

                # Extract date if present (for demonstration purposes, we'll assume the date is in a 'time' tag)
                date_tag = article.find('time')  # You can adjust this to your needs based on the website's structure
                if date_tag:
                    date_str = date_tag.get('datetime')  # Assuming the date is in a 'datetime' attribute
                    if date_str:
                        # Extract just the date part (year-month-day)
                        article_date = date_str.split('T')[0]

                        # Filter articles by today's date
                        if article_date == today and any(keyword.lower() in text for keyword in company):
                            relevant_articles.append({
                                "title": text,
                                "url": article['href'],
                                "date": article_date
                            })

            if relevant_articles:
                articles_data.extend(relevant_articles)
            else:
                print(f"No relevant articles found on {url}")
        else:
            print(f"Failed to retrieve data from {url}, status code: {response.status_code}")

    return articles_data

# Example usage
company_name = "Apple"
urls = [
    'https://www.bloomberg.com',
    'https://www.reuters.com',
    'https://finance.yahoo.com',
    'https://techcrunch.com',
    'https://www.marketwatch.com',
    'https://www.cnbc.com',
    'https://www.wsj.com'
]
articles = fetch_articles(urls, company_name)

# Print the articles fetched
for article in articles:
    print(f"Title: {article['title']}, URL: {article['url']}, Date: {article['date']}")


"""

"""
#######################################################
# Gemini suggestion: 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, keywords):
    driver.get(url)
    try:
        # Wait for article links to load
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.SearchResult-title')))

        articles = driver.find_elements(By.CSS_SELECTOR, 'a.SearchResult-title')
        relevant_articles = []
        for article in articles:
            text = article.text.strip()
            link = article.get_attribute('href')
            if any(keyword.lower() in text.lower() for keyword in keywords) or any(keyword.lower() in link.lower() for keyword in keywords):
                relevant_articles.append({
                    "title": text,
                    "url": link
                })
        return relevant_articles

    except TimeoutException:
        print("Error fetching articles: Timeout waiting for elements to load.")
    except NoSuchElementException:
        print("Error fetching articles: Element not found on the page.")
    except WebDriverException as e:
        print(f"Error fetching articles: WebDriver error: {e}")
    except Exception as e:
        print(f"Error fetching articles: An unexpected error occurred: {e}")
    return []

# ... (rest of your code)

company_name = "Apple"
keywords = ["Apple", "iPhone", "MacBook", "Tim Cook", "Steve Wozniak", "iOS", "Apple Inc."]
search_url = 'https://www.cnbc.com/search/?query=Apple&qsearchterm=Apple'

articles = fetch_articles(search_url, keywords)

for article in articles:
    print(f"Title: {article['title']}, URL: {article['url']}")

driver.quit()

"""

"""

#ChatGPT
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Selenium WebDriver (this example uses Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, keywords):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load dynamically

    # Find all links on the page
    articles = driver.find_elements(By.TAG_NAME, 'a')

    relevant_articles = []
    for article in articles:
        text = article.text.strip()
        link = article.get_attribute('href')

        # Check if the link text or URL contains any of the company-related keywords
        if any(keyword.lower() in text.lower() for keyword in keywords) or any(keyword.lower() in link.lower() for keyword in keywords):
            relevant_articles.append({
                "title": text,
                "url": link
            })

    return relevant_articles

# Example usage
company_name = "Apple"
keywords = ["Apple", "iPhone", "MacBook", "Tim Cook", "Steve Wozniak", "iOS", "Apple Inc."]

# URL of the search results for Apple on CNBC
search_url = 'https://www.cnbc.com/search/?query=Apple&qsearchterm=Apple'

articles = fetch_articles(search_url, keywords)

# Print the articles fetched
for article in articles:
    print(f"Title: {article['title']}, URL: {article['url']}")

# Close the driver after use
driver.quit()

"""


"""

#######################################################
#DEEP SEEK 



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Selenium WebDriver (this example uses Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, keywords):
    
    #Fetches articles from a given URL that match the provided keywords.
    #Args:
     #   url (str): The URL to fetch articles from.
      #  keywords (list): A list of keywords to filter articles.

    #Returns:
     #   list: A list of dictionaries containing article titles and URLs.
    
    driver.get(url)
    time.sleep(3)  # Wait for the page to load dynamically

    # Find all links on the page
    articles = driver.find_elements(By.TAG_NAME, 'a')

    relevant_articles = []
    for article in articles:
        # Get the text and link of the article
        text = article.text.strip() if article.text else ""
        link = article.get_attribute('href') if article.get_attribute('href') else ""

        # Skip if both text and link are empty
        if not text and not link:
            continue

        # Check if the link text or URL contains any of the company-related keywords
        if any(keyword.lower() in text.lower() for keyword in keywords) or any(keyword.lower() in link.lower() for keyword in keywords):
            relevant_articles.append({
                "title": text,
                "url": link
            })

    return relevant_articles

# Example usage
company_name = "Apple"
keywords = ["Apple", "iPhone", "MacBook", "Tim Cook", "Steve Wozniak", "iOS", "Apple Inc."]

# URL of the search results for Apple on CNBC
search_url = 'https://www.cnbc.com/search/?query=Apple&qsearchterm=Apple'

try:
    articles = fetch_articles(search_url, keywords)

    # Print the articles fetched
    for article in articles:
        print(f"Title: {article['title']}, URL: {article['url']}")

finally:
    # Close the driver after use
    driver.quit()



#######################################################
# ChatGPT
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

# Set up Selenium WebDriver (this example uses Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, keywords):
    print(f"Accessing {url} ...")
    driver.get(url)
    time.sleep(5)  # Wait for the page to load dynamically

    # Scroll down to load more content if necessary
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Find all links that contain keywords
    articles = driver.find_elements(By.TAG_NAME, 'a')

    relevant_articles = []
    for article in articles:
        text = article.text.strip() if article.text else ""
        link = article.get_attribute('href') if article.get_attribute('href') else ""

        if not text and not link:
            continue

        if any(keyword.lower() in text.lower() for keyword in keywords) or any(keyword.lower() in link.lower() for keyword in keywords):
            relevant_articles.append({
                "title": text,
                "url": link
            })

    if not relevant_articles:
        print("No relevant articles found.")
    return relevant_articles

# Example usage
company_name = "Apple"
keywords = ["Apple", "iPhone", "MacBook", "Tim Cook", "Steve Wozniak", "iOS", "Apple Inc."]

# URL of the search results for Apple on CNBC
search_url = 'https://www.cnbc.com/search/?query=Apple&qsearchterm=Apple'

try:
    articles = fetch_articles(search_url, keywords)

    if articles:
        for article in articles:
            print(f"Title: {article['title']}, URL: {article['url']}")
    else:
        print("No articles matching the criteria were found.")

finally:
    driver.quit()



#Qwen

#######################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin
import time

# Set up Selenium WebDriver with enhanced options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, keywords):
    print(f"Accessing {url} ...")
    driver.get(url)
    
    try:
        # Wait for cookie consent and accept if present
        try:
            consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"))
            )
            consent_button.click()
            time.sleep(1)
        except:
            pass  # No consent required

        # Wait for search results using more specific selectors
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.SearchResultCard__content"))
        )
    except TimeoutException:
        print("Timeout: Search results container not found.")
        return []

    # Scroll to load more content
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Extract articles with more precise targeting
    articles = driver.find_elements(By.CSS_SELECTOR, "div.SearchResultCard__content a.Card-title")
    base_url = "https://www.cnbc.com"

    relevant_articles = []
    for article in articles:
        try:
            text = article.get_attribute('textContent').strip()
            href = article.get_attribute('href')
            
            if not text or not href:
                continue
            
            # Check keyword matches
            if any(keyword.lower() in text.lower() or keyword.lower() in href.lower() for keyword in keywords):
                full_url = urljoin(base_url, href)
                relevant_articles.append({
                    "title": text,
                    "url": full_url
                })
        except StaleElementReferenceException:
            continue  # Skip elements that become stale

    return relevant_articles

# Example usage
company_name = "Apple"
keywords = ["Apple", "iPhone", "MacBook", "Tim Cook", "iOS", "Apple Inc."]
search_url = 'https://www.cnbc.com/search/?query=Apple&qsearchterm=Apple'

try:
    articles = fetch_articles(search_url, keywords)
    if articles:
        for article in articles:
            print(f"Title: {article['title']}\nURL: {article['url']}\n")
    else:
        print("No relevant articles found.")
finally:
    driver.quit()



######################################################
# Qwen: Selenium  web sceping:

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time
import random

def fetch_company_news(company_name, keywords):
    results = []
    
    with sync_playwright() as p:
        # Launch browser with stealth settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        page.set_default_timeout(60000)
        
        try:
            search_url = f"https://www.cnbc.com/search/?query={company_name}&qsearchterm={company_name}"
            print(f"🚀 Accessing: {search_url}")
            page.goto(search_url)
            
            # Handle cookie consent
            try:
                print("🍪 Handling cookie consent...")
                page.wait_for_selector("button#onetrust-accept-btn-handler", timeout=5000)
                page.click("button#onetrust-accept-btn-handler")
                time.sleep(1)
            except:
                print("  ➔ No cookie prompt found")
            
            # Load more results
            print("🔄 Loading additional articles...")
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 2.5))
                
                try:
                    load_more = page.query_selector("button:has-text('Load More Results')")
                    if load_more:
                        load_more.scroll_into_view()
                        load_more.click(force=True)
                        time.sleep(2)
                except:
                    break
            
            # Extract articles with DEBUGGING
            print("🔍 Extracting articles...")
            article_containers = page.query_selector_all("div.SearchResultCard")
            print(f"  ➔ Found {len(article_containers)} article containers")
            
            base_url = "https://www.cnbc.com"
            
            for container in article_containers:
                try:
                    # Extract title
                    title = container.query_selector("a.Card-title").text_content().strip()
                    
                    # Extract URL
                    href = container.query_selector("a.Card-title").get_attribute("href")
                    full_url = href if href.startswith("http") else urljoin(base_url, href)
                    
                    # Extract summary/snippet
                    snippet = container.query_selector("div.Card-description").text_content().strip()
                    
                    # Debug output
                    print("\n--- Article Debug Info ---")
                    print(f"Title: {title}")
                    print(f"URL: {full_url}")
                    print(f"Snippet: {snippet}")
                    
                    # Check keyword matches in title, URL, AND snippet
                    content = f"{title} {full_url} {snippet}".lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        results.append({
                            "title": title,
                            "url": full_url,
                            "snippet": snippet
                        })
                        print("  ➔ MATCH FOUND")
                    else:
                        print("  ➔ No keyword match")
                
                except Exception as e:
                    print(f"  ❌ Error processing article: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"🚨 Critical error: {str(e)}")
        
        finally:
            print("🧹 Closing browser...")
            context.close()
            browser.close()
    
    return results

# Execution
if __name__ == "__main__":
    COMPANY = "Apple"
    # Expanded keywords including variations and stock ticker
    KEYWORDS = [
        "Apple", "AAPL", "iPhone", "MacBook", "iPad", "Apple Watch",
        "Tim Cook", "iOS", "macOS", "Apple Inc.", "Apple Park"
    ]
    
    print(f"📰 Searching for {COMPANY} news with expanded keywords...")
    articles = fetch_company_news(COMPANY, KEYWORDS)
    
    if articles:
        print(f"\n✅ Found {len(articles)} relevant articles:")
        for idx, article in enumerate(articles, 1):
            print(f"\n{idx}. {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Snippet: {article['snippet']}")
    else:
        print("\n❌ No relevant articles found after expanded checks.")

"""
##################################################################
# ChatGPT

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
driver = webdriver.Chrome(options=chrome_options)

# Define a dictionary for website search URL patterns
websites = {
    "di.se": "https://www.di.se/search/?query={company_name}&qsearchterm={company_name}",
    "dn.se": "https://www.dn.se/search/?query={company_name}&qsearchterm={company_name}",
    "marketwatch.com": "https://www.marketwatch.com/search/?query={company_name}&qsearchterm={company_name}",
    "google.com": "https://www.google.com/search/?query={company_name}&qsearchterm={company_name}",
    "cnbc.com": "https://www.cnbc.com/search/?query={company_name}&qsearchterm={company_name}",
    "ft.com": "https://www.ft.com/search/?query={company_name}&qsearchterm={company_name}",
    # Add more websites here as needed
}

def fetch_articles_from_website(url, company_name):
    """
    Fetches articles from a given URL that match the company name.

    Args:
        url (str): The URL to fetch articles from.
        company_name (str): The name of the company to search for in the article.

    Returns:
        list: A list of dictionaries containing article titles and URLs.
    """
    print(f"Accessing {url} ...")
    driver.get(url)
    time.sleep(5)  # Wait for the page to load dynamically

    # Scroll down to load more content if necessary
    for _ in range(3):  # Adjust to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 3))  # Random sleep for human-like interaction

    # Find all links on the page
    articles = driver.find_elements(By.TAG_NAME, 'a')
    relevant_articles = []

    for article in articles:
        text = article.text.strip() if article.text else ""
        link = article.get_attribute('href') if article.get_attribute('href') else ""

        # Skip if both text and link are empty
        if not text and not link:
            continue

        # Filter out irrelevant links (e.g., ads, login pages, or non-article links)
        if 'ad' in link or 'signup' in link or 'login' in link or 'stock-screener' in link:
            continue
        
        # Skip articles with no meaningful title
        if not text or "filter" in text.lower():
            continue

        # Check if the link text or URL contains the company name or relevant keywords
        if company_name.lower() in text.lower() or company_name.lower() in link.lower():
            relevant_articles.append({
                "title": text,
                "url": link
            })

    return relevant_articles

def search_all_websites(company_name):
    """
    Search for articles about the company on all websites and return the results.

    Args:
        company_name (str): The name of the company to search for in the article.

    Returns:
        list: A list of dictionaries containing article titles and URLs from all websites.
    """
    all_articles = []

    for website, search_url_pattern in websites.items():
        # Build the search URL for the current website
        search_url = search_url_pattern.format(company_name=company_name)

        # Fetch articles from the current website
        articles = fetch_articles_from_website(search_url, company_name)

        # Add the articles to the result list
        all_articles.extend(articles)

    return all_articles

# Example usage
company_name = "Apple"  # Modify the company name here

try:
    articles = search_all_websites(company_name)

    if articles:
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"URL: {article['url']}")
    else:
        print("No articles matching the criteria were found.")

finally:
    driver.quit()





