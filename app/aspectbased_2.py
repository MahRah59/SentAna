# aspectbased_2.py


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

#https://customsearch.googleapis.com/customsearch/v1?q=Apple+news+-site%3AApple.com&cx=0537f5d70cf294823&num=1&key=AIzaSyB1MxcYT2cv9A4oMLzvybL5QkGYxix7FtM

"""
import time
#

#def wait_for_quota_reset():
 #   print("Quota exceeded, waiting for reset...")
  #  time.sleep(60)  # Wait for 60 seconds before retrying

# Call the function when quota is exceeded
#wait_for_quota_reset()

print("API Key:", API_KEY)

# Function to check if the URL is valid (not from the company's official sites or social media)
def is_valid_url(url, company_name):
    # Convert the company name to lowercase to handle case insensitivity
    company_name = company_name.lower()

    # List of social media sites to exclude
    exclude_domains = [
        "facebook.com", "youtube.com", "reddit.com", "x.com", "instagram.com",
        "linkedin.com", "twitter.com"
    ]
    
    # Generate company-related domains to exclude based on company name, e.g. "apple.com", "google.com", etc.
    company_related_domains = [
        f"{company_name}.com", f"media.{company_name}.com", f"www.{company_name}.com"
    ]
    
    
    # Combine the exclusion lists
    exclude_domains.extend(company_related_domains)

    # Check if the URL contains any excluded domain or social media domain
    url = url.lower()  # Make sure to handle case insensitivity
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    # Ensure hostname is not None
    if not hostname:
        return False

    for domain in exclude_domains:
        if domain in hostname:
            print(f"Skipping URL (company-related/social media): {url}")
            return False  


    # Check if the hostname contains any excluded domain
    for domain in exclude_domains:
        if domain in hostname:
            print(f"Skipping URL (company-related/social media): {url}")
            return False  # If the URL contains any excluded domain, it's not valid

    return True  # If no exclusions are found, the URL is valid

# Fetch content from the URLs
def fetch_content_from_url(url, company_name):
    try:
        if is_valid_url(url, company_name):  # Only proceed if the URL is valid
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Fetching content for: {url}")
                return response.text  # Return the content of the page
            else:
                print(f"Failed to retrieve content from {url}, status code: {response.status_code}")
        else:
            return None  # If URL is invalid, return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching content from {url}: {e}")
        return None

# Function to search using Google Custom Search API and return URLs
def google_search(query, api_key, cse_id, num_results=10):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=str(num_results)).execute()
    num_results = str(10)
    return num_results

# Fetch URLs dynamically from Google Search results
def search_and_fetch_articles(query, company_name, api_key, cse_id):
    # Fetch search results based on the query
    results = google_search(query, api_key, cse_id, num_results=10)

    # Loop through the search results and fetch the content for each URL
    for i, result in enumerate(results, 1):
        url = result['link']
        content = fetch_content_from_url(url, company_name)
        
        if content:
            # Save content into a single file with a header (source URL)
            with open("company_articles.txt", "a") as file:
                file.write(f"Source: {url}\n")
                file.write(content + "\n\n")  # Separate articles with newlines

        # Add delay to prevent exceeding rate limits (100 requests per minute)
        time.sleep(6)  # Adjust the sleep time as needed       

# Example query for a given company (e.g., "Apple")
company_name = "Apple"
query = f"{company_name} news -site:{company_name}.com"
API_KEY = 'YOUR_GOOGLE_API_KEY'
CUSTOM_SEARCH_ENGINE_ID = 'YOUR_CUSTOM_SEARCH_ENGINE_ID'

# Call the function to fetch articles
search_and_fetch_articles(query, company_name, API_KEY, CUSTOM_SEARCH_ENGINE_ID)



import googleapiclient.discovery

# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"

# Function to perform Google Search using Custom Search API
def google_search(query, api_key, cse_id, num_results=10):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
    return res.get('items', [])

# Function to filter out social media and irrelevant domains
def is_valid_url(url):
    exclude_domains = ["x.com", "reddit.com", "wikipedia.org", "facebook.com", 
                       "instagram.com", "linkedin.com", "twitter.com", "youtube.com"]
    
    for domain in exclude_domains:
        if domain in url:
            return False  # Exclude these domains
    
    return True  # Keep the valid results

# Function to format and print results with colors
def format_results(results):
    valid_results = []
    
    for i, result in enumerate(results, start=1):
        title = result.get("title", "No Title")
        link = result.get("link", "No Link")
        
        if is_valid_url(link):  # Check if the URL is valid
            formatted_entry = f"{BOLD}{i}. {title}{RESET}\n   {BLUE}{link}{RESET}\n"
            valid_results.append(formatted_entry)

    if valid_results:
        print("\n".join(valid_results))  # Print filtered results with colors
        save_results(valid_results)  # Save to file
    else:
        print("No valid results found after filtering.")

# Function to save results to a text file (without colors)
def save_results(results):
    with open("filtered_search_results.txt", "w") as file:
        plain_text_results = [entry.replace(BOLD, "").replace(RESET, "").replace(BLUE, "") for entry in results]
        file.write("\n".join(plain_text_results))
    print("\n✅ Filtered results saved to 'filtered_search_results.txt'.")



# Query and execution
query = "Apple news -site:Apple.com"
search_results = google_search(query, API_KEY, CUSTOM_SEARCH_ENGINE_ID)

if search_results:
    format_results(search_results)
else:
    print("No results found.")



#########################################################
#Working: 
#########################################################
import googleapiclient.discovery
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from termcolor import colored  # For colored output in terminal



# ✅ Function to fetch Google search results
def google_search(query, api_key, cse_id, num_results=10):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
    return res.get('items', [])


# ✅ Function to extract article content from URLs
def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract readable text
        paragraphs = soup.find_all("p")
        text_content = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
        return text_content[:1000]  # Limiting content to 1000 chars for preview
    except requests.exceptions.RequestException as e:
        print(colored(f"⚠ Failed to fetch content: {url}", "red"))
        return None

# ✅ Function to format and print results with colors
def format_results(results, output_file="search_results.txt"):
    with open(output_file, "w", encoding="utf-8") as file:
        for i, result in enumerate(results, start=1):
            title = result.get("title", "No Title")
            link = result.get("link", "No Link")
            
            # 🎨 Print colored output
            print(colored(f"{i}. {title}", "cyan"))
            print(colored(f"   {link}", "green"))
            print("-" * 80)

            # ✍ Save results to file
            file.write(f"{i}. {title}\n{link}\n{'-'*80}\n")

# ✅ Run search and process results
company_name = "Apple"
query = f"{company_name} news -site:{company_name}.com"

search_results = google_search(query, API_KEY, CUSTOM_SEARCH_ENGINE_ID)

if search_results:
    format_results(search_results)
    print(colored("\n✅ Results saved to 'search_results.txt'", "yellow"))
else:
    print(colored("❌ No results found.", "red"))

#########################################################



#########################################################
# working 2: 
#########################################################
import googleapiclient.discovery
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import time

# 🚫 Excluded domains (social media, wiki, paywalled sites, etc.)
EXCLUDED_DOMAINS = [
    "reddit.com", "x.com", "facebook.com", "twitter.com", "linkedin.com",
    "youtube.com", "instagram.com", "wikipedia.org", "marketwatch.com", 
    "barrons.com", "ft.com"
]

# ✅ User-Agent headers to bypass blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}

def generate_exclusion_domains(company_name):
    #Dynamically generates company-specific domains to exclude
    company_name = company_name.lower()
    return [
        f"{company_name}.com", f"www.{company_name}.com", f"news.{company_name}.com",
        f"blog.{company_name}.com", f"developer.{company_name}.com", f"support.{company_name}.com"
    ]

def google_search(query, api_key, cse_id, company_name, num_results=10, max_pages=6):
    #Fetch multiple pages of Google search results, excluding unwanted sites.
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    all_results = []

    # Dynamically exclude company-specific domains
    company_exclusions = generate_exclusion_domains(company_name)
    all_exclusions = EXCLUDED_DOMAINS + company_exclusions

    for page in range(max_pages):
        start = page * num_results + 1
        try:
            res = service.cse().list(q=query, cx=cse_id, num=num_results, start=start).execute()
            items = res.get("items", [])
            filtered_items = [
                item for item in items if not any(domain in item.get("link", "") for domain in all_exclusions)
            ]
            all_results.extend(filtered_items)
        except Exception as e:
            print(colored(f"⚠ Error fetching results: {e}", "red"))
            break

    return all_results

def fetch_article_text(url):
    #Fetch and clean article text while handling sites that block requests.
    try:
        # Check if the site blocks access (e.g., MarketWatch)
        if "marketwatch.com" in url:
            print(colored(f"⚠ MarketWatch article requires manual access: {url}", "red"))
            # Try Google Cache instead
            google_cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            response = requests.get(google_cache_url, headers=HEADERS, timeout=10)
        else:
            response = requests.get(url, headers=HEADERS, timeout=10)

        response.raise_for_status()  # Raise an error for HTTP errors
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unnecessary elements
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.extract()
        
        # Extract main content
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs if len(p.get_text()) > 50)  # Avoid short texts
        
        return text.strip() if text else None
    
    except requests.exceptions.HTTPError as e:
        print(colored(f"⚠ HTTP Error for {url}: {e}", "red"))
    except requests.exceptions.RequestException as e:
        print(colored(f"⚠ Request Error for {url}: {e}", "red"))
    
    return None


def fetch_marketwatch_articles_google(query, api_key, cse_id):
    #Fetch MarketWatch article titles & snippets using Google Custom Search.
    marketwatch_query = f"{query} site:marketwatch.com"

    try:
        service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=marketwatch_query, cx=cse_id, num=5).execute()
        items = res.get("items", [])

        articles = []
        for item in items:
            title = item.get("title", "No Title")
            link = item.get("link", "No Link")
            snippet = item.get("snippet", "No Snippet Available")  # ✅ Extract snippet instead
            
            articles.append({
                "title": title,
                "link": link,
                "snippet": snippet  # ✅ Store snippet instead of full article
            })

        return articles

    except Exception as e:
        print(colored(f"⚠ Error fetching MarketWatch articles via Google: {e}", "red"))
        return []



def fetch_financial_news(company_name):
    #Fetch financial news articles from CNBC and Financial Times.
    news_sources = {
        "CNBC": f"https://www.cnbc.com/search/?query={company_name}",
        "Financial Times": f"https://www.ft.com/search?q={company_name}"

    }

    all_articles = []

    for source, url in news_sources.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # ✅ Extract different structures based on the website
            if source == "CNBC":
                articles = soup.find_all("div", class_="SearchResult-searchResult")[:5]
            elif source == "Financial Times":
                articles = soup.find_all("a", class_="js-teaser-heading-link")[:5]
            else:
                continue

            for article in articles:
                if source == "Financial Times":
                    title = article.get_text(strip=True)
                    link = "https://www.ft.com" + article["href"] if not article["href"].startswith("http") else article["href"]
                else:
                    title_tag = article.find("a")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        link = title_tag["href"]
                        if not link.startswith("http"):
                            link = f"https://{source.lower().replace(' ', '')}.com{link}"
                    else:
                        continue

                all_articles.append({"title": title, "link": link})

        except Exception as e:
            print(colored(f"⚠ Error fetching {source} articles: {e}", "red"))

    return all_articles

# ✅ INPUT: Change the company name for different searches
company_name = "Tesla"
query = f"{company_name} news -site:{company_name}.com"
max_pages = 6

# 🔹 Step 1: Fetch Google Search Results
search_results = google_search(query, API_KEY, CUSTOM_SEARCH_ENGINE_ID, company_name, max_pages=max_pages)

# 🔹 Step 2: Fetch CNBC, FT, and MarketWatch articles
financial_articles = fetch_financial_news(company_name)
marketwatch_articles = fetch_marketwatch_articles_google(query, API_KEY, CUSTOM_SEARCH_ENGINE_ID)

# 🔹 Step 3: Merge all sources
search_results.extend(financial_articles)
search_results.extend(marketwatch_articles)  # ✅ Now MarketWatch articles are included

# 🔹 Step 4: Process and Save Results
output_file = "search_results.txt"

with open(output_file, "w", encoding="utf-8") as f:
    if search_results:
        print(colored("\n🔹 Extracting Articles:\n", "cyan"))
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "No Title")
            link = result.get("link", "No Link")
            snippet = result.get("snippet", "")  # ✅ Add snippet for MarketWatch

            print(colored(f"{i}. {title}", "yellow"))
            print(colored(f"   {link}", "blue"))

            if "marketwatch.com" in link:
                print(colored(f"⚠ MarketWatch article requires manual access: {link}", "red"))
                f.write(f"{i}. {title}\n{link}\nSnippet: {snippet}\n{'-'*80}\n")  # ✅ Store snippet
            else:
                article_text = fetch_article_text(link)
                if article_text:
                    print(colored(f"✅ Article Extracted!", "green"))
                    f.write(f"{i}. {title}\n{link}\n{article_text}\n{'-'*80}\n")
            
            print("-" * 80)

        print(colored(f"\n✅ Extracted content saved to '{output_file}'", "green"))
    else:
        print(colored("❌ No results found.", "red"))



 """       
######################################################
        
    
import googleapiclient.discovery
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import time
import re


# ✅ Preferred sources for direct web scraping
PREFERRED_SOURCES = {
    "CNBC": "https://www.cnbc.com/search/?query=",
    "Financial Times": "https://www.ft.com/search?q=",
    "The Guardian": "https://www.theguardian.com/search?q=",
    "DI": "https://www.di.se/search/?query="

}


# 🚫 Excluded domains (social media, wiki, company websites, paywalled sites)
EXCLUDED_DOMAINS = [
    "reddit.com", "x.com", "facebook.com", "twitter.com", "linkedin.com",
    "youtube.com", "instagram.com", "wikipedia.org", "marketwatch.com", 
    "barrons.com", "ft.com"
]

# ✅ Headers to bypass restrictions
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}


import re

def generate_exclusion_domains(company_name):
    """Dynamically exclude company-related domains and variations."""
    company_name = company_name.lower()

    # Common suffixes found in official company websites
    common_suffixes = [
        "official", "group", "global", "corporate", "media", "news", "forum", "support",
        "careers", "investors", "press", "blog", "help", "about", "info", "trucks", "buses", "motors"
    ]

    # Exclude known company domains
    exclusions = {f"{company_name}.com"}  # Main domain
    exclusions.update({f"{company_name}{suffix}.com" for suffix in common_suffixes})  # Variations like "volvocars.com"
    exclusions.update({f"{prefix}.{company_name}.com" for prefix in common_suffixes})  # Subdomains like "news.volvo.com"

    # **🔍 Regex to detect additional company domains**
    patterns = [
        rf"{company_name}[a-z\-]*\.com",  # Matches 'volvocars.com', 'toyota-usa.com'
        rf"[a-z\-]+\.{company_name}\.com",  # Matches 'news.toyota.com', 'blog.tesla.com'
        rf"{company_name}\.[a-z]+"  # Matches 'tesla.us', 'nvidia.eu'
    ]

    exclusions.update(patterns)

    return list(exclusions)




# 🔹 **Google Search API Fetcher**
import googleapiclient.discovery

def google_search(query, api_key, cse_id, company_name, num_results=10, max_pages=6):
    """Fetch Google search results while filtering out company-related and unwanted sites."""
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    all_results = []

    # Generate exclusion list dynamically
    company_exclusions = generate_exclusion_domains(company_name)
    all_exclusions = EXCLUDED_DOMAINS + company_exclusions

    for page in range(max_pages):
        start = page * num_results + 1
        try:
            res = service.cse().list(q=query, cx=cse_id, num=num_results, start=start).execute()
            items = res.get("items", [])

            # ✅ STRICTER Filtering to remove company-related domains
            filtered_items = [
                item for item in items if not any(re.search(pattern, item.get("link", "")) for pattern in all_exclusions)
            ]

            all_results.extend(filtered_items)
        except Exception as e:
            print(colored(f"⚠ Error fetching results: {e}", "red"))
            break

    return all_results


# 🔹 **Extracting Full Article Text**
def fetch_article_text(url):
    """Fetches and cleans article text while handling sites that block requests."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Handle HTTP errors

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary elements
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.extract()

        # Extract main content
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs if len(p.get_text()) > 50)  # Filter short texts

        return text.strip() if text else None

    except requests.exceptions.RequestException as e:
        print(colored(f"⚠ Error fetching {url}: {e}", "red"))
        return None

# 🔹 **Scraping Preferred Sources Directly**
# 🔹 **Scraping Preferred Sources Dynamically**
def fetch_preferred_sources(company_name):
    """Scrapes articles from a dynamically defined list of preferred sources."""
    all_articles = []

    # Define structure patterns for each source
    site_patterns = {
        "cnbc.com": {"tag": "div", "class": "SearchResult-searchResult"},
        "ft.com": {"tag": "a", "class": "js-teaser-heading-link"},
        "theguardian.com": {"tag": "a", "class": "u-faux-block-link__overlay"},
        "di.se": {"tag": "a", "class": "js_watch-teaser news-item js_news-item"}
        
    }

    for source, base_url in PREFERRED_SOURCES.items():
        try:
            url = f"{base_url}{company_name}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find which site structure to use dynamically
            source_domain = base_url.split("//")[-1].split("/")[0]  # Extract domain
            structure = site_patterns.get(source_domain, {"tag": "a", "class": "default-class"})

            articles = soup.find_all(structure["tag"], class_=structure["class"])[:5]

            for article in articles:
                title = article.get_text(strip=True)
                link = article["href"]

                if not link.startswith("http"):
                    link = f"{base_url.rstrip('/')}{link}"

                all_articles.append({"title": title, "link": link})

        except Exception as e:
            print(colored(f"⚠ Error fetching articles from {source}: {e}", "red"))

    return all_articles


# 🔹 **Final Processing & SentAna Preprocessing**
def process_results(search_results, output_file="search_results.txt"):
    """Processes, extracts, and saves final articles for SentAna."""
    with open(output_file, "w", encoding="utf-8") as f:
        if search_results:
            print(colored("\n🔹 Extracting Articles:\n", "cyan"))

            for i, result in enumerate(search_results, 1):
                title = result.get("title", "No Title")
                link = result.get("link", "No Link")

                print(colored(f"{i}. {title}", "yellow"))
                print(colored(f"   {link}", "blue"))

                # ✅ Fetch article content
                article_text = fetch_article_text(link)

                if article_text:
                    print(colored(f"✅ Article Extracted!", "green"))
                    f.write(f"{i}. {title}\n{link}\n{article_text}\n{'-'*80}\n")
                else:
                    print(colored(f"⚠ Could not extract full text for {link}", "red"))

                print("-" * 80)

            print(colored(f"\n✅ Extracted content saved to '{output_file}'", "green"))
        else:
            print(colored("❌ No results found.", "red"))

# ✅ **Execution Starts Here**
company_name = "amazon"
query = f"{company_name} news -site:{company_name}.com"
max_pages = 6

# 🔹 **Step 1: Fetch Preferred Sources First**
preferred_articles = fetch_preferred_sources(company_name)

# 🔹 **Step 2: Add Preferred List to Exclusions & Run Google Search**
EXCLUDED_DOMAINS.extend([url.split("//")[-1].split("/")[0] for url in PREFERRED_SOURCES.values()])
search_results = google_search(query, API_KEY, CUSTOM_SEARCH_ENGINE_ID, company_name, max_pages=max_pages)

# 🔹 **Step 3: Merge Both Sources**
final_results = preferred_articles + search_results

# 🔹 **Step 4: Process and Save Data for SentAna**
process_results(final_results)


######################################################