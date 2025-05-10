#internet_search_3
import os
import os
import requests
import googleapiclient.discovery
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
from datetime import datetime
from time import time
from deep_translator import GoogleTranslator, exceptions



import logging
logger = logging.getLogger(__name__)


# ✅ API Keys
CUSTOM_SEARCH_ENGINE_ID = '0537f5d70cf294823'
API_KEY = 'AIzaSyB1MxcYT2cv9A4oMLzvybL5QkGYxix7FtM'
API_KEY_GNews = '8847423999e0049996b2f049ecf7afcc'

API_KEYS = {
    "newsapi": "1461c045f14b46ae9c0037f7232e21fb",
    #"gnews": "8847423999e0049996b2f049ecf7afcc",
    "contextualweb": "yYyZtn2xQL4bchfXJv6cgwt3",
    "serpapi": "55384b7fbd2c9ba4b1abe95ff36dab830a911fd800646d5d83f349a049bc45cd"

}

#https://gnews.io/api/v4/search?q=apple&lang=en&token='8847423999e0049996b2f049ecf7afcc'


# ✅ Preferred sources (domains only)ƒ
PREFERRED_SOURCES = {
    "www.cnbc.com",
    "www.ft.com",
    "www.theguardian.com",
    "www.di.se",
    "www.marketwatch.com",
    "www.bbc.com",
    "www.dn.se",
    }

# ✅ Search templates for preferred sources
SEARCH_TEMPLATES = {
    "www.cnbc.com": "https://www.cnbc.com//search/?query= &qsearchterm= ",
    "www.ft.com": "https://www.ft.com/search?q=",
    "www.theguardian.com": "https://www.theguardian.com/search?q=",
    "www.di.se": "https://www.di.se/search/?query=",
    "www.marketwatch.com": "https://www.marketwatch.com/search?q=",
    "www.bbc.com": "https://www.bbc.com/search?q=",
    "www.dn.se": "https://www.dn.se/sok/?q=",
    }


PAYWALLED_DOMAINS = [
    "ft.com",              # Financial Times
    "bloomberg.com",
    "economist.com",
    "wsj.com",             # Wall Street Journal
    "nytimes.com",         # Partial paywall
    "thetimes.co.uk",
    "telegraph.co.uk",
    "handelsblatt.com",    # German financial site
    "lesechos.fr",         # French economic newspaper
    "businessinsider.com", # Varies by region
]

API_REQUIRED_DOMAINS = [
    "twitter.com",         # Now X; heavily restricted scraping
    "reddit.com",
    "newsapi.org",         # Aggregated news API
    "gnews.io",
    "facebook.com",        # Graph API for official access
    "instagram.com",       # Also under Facebook's Graph API
    "youtube.com",         # Requires YouTube Data API for structured access
    "linkedin.com",        # Scraping blocked; API access limited
]

# 🚫 Generic Exclusion Keywords (Hardcoded)
GENERIC_EXCLUSIONS = [
    "login", "subscribe", "register", "privacy", "terms", "contact",
    "about company", "careers", "help", "faq", "advertisement", "cookie-policy",
    "video", " about us", "stream", "prenumeration", "Logga in", "om oss", "Kontakta oss", "tjänster",
    "services", "Stock Price and Chart"
]

# ✅ Contextual Keywords for Filtering Articles About Ericsson the Company
GENERIC_CONTEXT_KEYWORDS = [

"news" "nyheter", "article", "omdöme", "competition", "konkurrens", "market", "sales", "contract", "report", "annual report"
  "technology", "CEO", "revenue", "product", "Service", "innovation", "revenue", "customer support", 
    "kundtjänst", "launch", "announcement", "financial", 
    "strategy", "growth", "performance"
]

# ✅ Headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}

# ✅ Temp files
SEARCH_RESULTS_FILE = "search_results.txt"
SEARCH_HEADLINES_FILE = "search_Headlines_results.txt"
SEARCH_SUMMARY_FILE = "search_filtering_summary.txt"



def fetch_articles_controller(search_config):
    logger.info(f"\n\n Search Conif is: {search_config}\n\n ")
    company_name = search_config.get("company_name", "")
    keywords = search_config.get("keywords", "")
    user_preferred_list = search_config.get("user_preferred", [])
    raw_exclusions = search_config.get("user_exclusions", [])
    time_filter = search_config.get("time_filter", "any")

    # ⬇ Modular preprocessing
    user_exclusion_sites = extract_sites_from(raw_exclusions)
    user_exclusion_keywords = extract_keywords_from(raw_exclusions)

    final_sources = get_final_preferred_sources(user_preferred_list, user_exclusion_sites, PREFERRED_SOURCES)
    logger.info(f" \n\n Final Sources are: {final_sources}\n\n ")
    exclusion_keywords = get_exclusion_keywords(user_exclusion_keywords, GENERIC_EXCLUSIONS)
    combined_keywords = get_combined_context_keywords(keywords, GENERIC_CONTEXT_KEYWORDS)

    # ⬇ Query building
    queries = build_search_queries(company_name, keywords)
    print("🔎 Queries for focused search:")
    for q in queries:
        logger.info(f"\n\n The Query is::::::  {q}")
    
    # A: Scrape 
    start = time()
    scrape_query = simplify_query_for_scraping(company_name, keywords)
    preferred_results = scrape_preferred_sources(scrape_query, SEARCH_TEMPLATES, HEADERS)
    logger.info(f"\n\n  Duration for Scrapping is: {time() - start:.2f}s\n") 
    log_to_file("Scraped Results", preferred_results)

    # Step 1 — Filter out invalid scrape results
    excluded_scrape = [
        r for r in preferred_results
        if not r.get("url") or "#" in r.get("url") or "mailto:" in r.get("url")
    ]
    print(f"❌ Scrape entries removed due to invalid URLs: {len(excluded_scrape)}")
    logger.info(f"\n\n Excluded Scrape is:  {excluded_scrape}\n") 

    # Step 2 — Keep only valid ones
    valid_scrape_results = [
        r for r in preferred_results
        if r.get("url") and r.get("url").startswith("http") and "#" not in r.get("url") and "mailto:" not in r.get("url")
    ]
    logger.info(f" \n\n Validated Scrape Results :{valid_scrape_results}\n") 


    # B: Google 
    start = time()
    google_results = google_search(queries, API_KEY, CUSTOM_SEARCH_ENGINE_ID)
    logger.info (f"Duration for Google Search is: {time() - start:.2f}s\n") 
    log_to_file("Google Search Results", google_results, mode="w")


    # C: Gnews 
    start = time()
    gnews_results = fetch_articles_from_gnews(company_name, combined_keywords)
    print(f"📡 Duration for GNews fetch: {time() - start:.2f}s | Articles fetched: {len(gnews_results)}")
    logger.info(f"\n\n \n\n Gnews results are: {gnews_results}\n") 

    # Why should we do in this way and not in preferred??? 
    # D: Di+Dn 
    di_dn_results = get_articles_from_di_and_dn(company_name)
    print(f"📰 DI/DN: {len(di_dn_results)} artiklar hämtade.")

    # E: SerpApi 
    company_name = search_config.get("company_name")
    keywords = search_config.get("keywords", "")
    query = f"{company_name} {keywords}"

    # E: Newsapi 
    newsapi_results = fetch_from_newsapi(query, API_KEYS["newsapi"],  page_size=50)

    # F: SerpApi 
    serpapi_results = fetch_from_serpapi(query, API_KEYS["serpapi"],  num_results=50)
   
    # G: ContextualWeb 
    contextualweb_results = fetch_from_contextualweb(query, API_KEYS["contextualweb"],  count=50)

    all_normalized = normalize_results(
    valid_scrape_results,
    google_results,
    gnews_results,
    newsapi_results,
    serpapi_results,
    contextualweb_results,
    di_dn_results
)


    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    company_name = search_config.get("company_name", "unknown")

    start = time()

    deduped = deduplicate_results(all_normalized)
    logger.info(f"\n\n⏱️ Duration for deduplicate is : {time() - start:.2f}s\n") 
    log_to_file("\n\n \n\n Deduplicated Results", deduped)


    non_pdf_results = filter_pdf_urls(deduped)
    logger.info(f"\n\n📄 PDF articles filtered: {len(non_pdf_results)}\n")

    cleaned, early_reasons = filter_disallowed_sources(non_pdf_results, company_name)
    #print("✅ Company-owned and Disallowed URLs:", [r["url"] for r in cleaned])
    logger.info(f"\n\n🚫 Company-owned / Disallowed URLs Filtered: {len(early_reasons)}\n") 

    without_excluded_keywords = filter_excluded_keywords_metadata(cleaned, exclusion_keywords)
    logger.info(f"\n\n📝 Keyword Excluded Filtered (metadata/title): {len(cleaned) - len(without_excluded_keywords)}\n") 


    paywall_filtered = handle_paywalled_sources(without_excluded_keywords)
    logger.info(f"\n\n✅ Paywall-passed URLs:\n", [r["url"] for r in paywall_filtered])

    api_filtered = handle_api_limited_sources(paywall_filtered)
    logger.info(f"\n\n✅ API-passed URLs:", [r["url"] for r in api_filtered])

    enriched_articles, enrichment_reasons = enrich_articles_with_full_text(
        api_filtered,
        log_file_path="failed_extractions.log",
        company_name=company_name,
        session_id=session_id
    )

    log_to_file("\n\n \n\n Enriched Results", enriched_articles)

    enriched_urls = {r["url"] for r in enriched_articles}
    combined_urls = {r["url"] for r in all_normalized}
    enriched_removed = sorted(combined_urls - enriched_urls)

    for result in enriched_articles:
        result["content"] = fetch_article_text(result["url"], HEADERS)

    for r in enriched_articles:
        if isinstance(r, dict):
            print(f"✔️ Pre-Relevance Filter Article: {r.get('url')}")
            #print(f"→ Content snippet: {r.get('content', '')[:200]}")
        else:
            print(f"⚠️ Unexpected type in enriched list: {type(r)} — value: {r}")

    logger.info(f"\n\n📦 Before Relevance Filter:\n") 
    logger.info(f"\n\n→ Input to relevance filter:\n", [r.get("url") for r in enriched_articles])

    start = time()
    relevant, relevance_reasons = filter_irrelevant_content(enriched_articles, combined_keywords, company_name)
    logger.info(f"\n\n⏱️ Duration for Relevance filter is : {time() - start:.2f}s")
    log_to_file("Final Filtered Results", (relevant))

    final_relevant = multilingual_processing_debug(
    relevant,
    exclusion_keywords,
    combined_keywords,
    company_name,
    fallback_threshold=35  # Adjust if needed
    )

    #final_relevant = [r for r in final_relevant if filter_low_quality_articles(r.get("content", ""))]
    final_relevant = filter_low_quality_articles(final_relevant)


    aggregated_text = aggregate_text(final_relevant)

    logger.info(f"\n\n🔍 Google Results ----------: {len(google_results)}\n") 
    logger.info(f"\n\n🗞️ Scraped Results ---------: {len(preferred_results)}\n") 
    logger.info(f"\n\n🗞️ Gnews Results ---------: {len(gnews_results)}\n") 
    logger.info(f"\n\n🗞️ Dn+Di Results ---------: {len(di_dn_results)}\n") 
    logger.info(f"\n\n🗞️ NewsApi Results ---------: {len(newsapi_results)}\n") 
    logger.info(f"\n\n🗞️ SerpApi Results ---------: {len(serpapi_results)}\n") 
    logger.info(f"\n\n🗞️ ContextualWeb Results ---------: {len(contextualweb_results)}\n") 


    logger.info(f"\n\n🔀 Combined: {len(all_normalized)}\n") 
    logger.info(f"\n\n🏢 Deduplicated Filtered: {len(deduped)}\n") 
    logger.info(f"\n\n🏢 PDf Filtered: {len(non_pdf_results)}\n")
    logger.info(f"\n\n🏢 Company-owned/Disallowd URL:s Filtered: {len(cleaned)}\n") 
    logger.info(f"\n\n🏢 Key_word_excluded Filtered: {len(without_excluded_keywords)}\n") 
    logger.info(f"\n\n💰 Paywall filtered: {len(paywall_filtered)}\n") 
    logger.info(f"\n\n🔌 API filtered: {len(api_filtered)}\n") 
    logger.info(f"\n\n🧽 Enriched Filtered: {len(enriched_articles)}\n") 
    logger.info(f"\n\n🧽 Relevant Filtered: {len(relevant)}\n") 

    logger.info(f"\n\n🧽 Relevant Filtered: {aggregated_text}\n") 



    print(f"✅ Final articles: {len(relevant)}")


    f = open("/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/aggregated.txt", "w")
    for item in aggregated_text:
        f.write(item)
        f.write("\n\n\n\n")
    f.close()

    dedup_removed = sorted({r['url'] for r in all_normalized} - {r['url'] for r in deduped})
    company_removed = sorted({r['url'] for r in deduped} - {r['url'] for r in cleaned})
    without_excluded_keywords_removed = sorted({r['url'] for r in cleaned} - {r['url'] for r in without_excluded_keywords})
    paywall_removed = sorted({r['url'] for r in without_excluded_keywords} - {r['url'] for r in paywall_filtered})
    api_removed = sorted({r['url'] for r in paywall_filtered} - {r['url'] for r in api_filtered})
    enriched_removed = sorted({
    r['url'] for r in api_filtered
        } - {
            r['url'] for r in enriched_articles if isinstance(r, dict) and 'url' in r
        })
    relevance_removed = sorted({r['url'] for r in enriched_articles} - {r['url'] for r in relevant})

    meta = {
        "keywords": keywords,
        "company_name": company_name,
        "preferred_sources": final_sources,
        "exclusion_sites": user_exclusion_sites,
        "exclusion_keywords": exclusion_keywords,
        "time_filter": time_filter
    }

    summary_info = {
    "google_results": len(google_results),
    "scraped_results": len(preferred_results),
    "gnews_results": len(gnews_results),
    "combined": len(all_normalized),
    "disallowed_filtered": len(early_reasons),
    "keyword_filtered": len(cleaned) - len(without_excluded_keywords),
    "paywall_filtered": len(paywall_filtered),
    "api_filtered": len(api_filtered),
    "enriched_filtered": len(enriched_articles),
    "final_articles": len(relevant),
    "✅ Final url": sorted([r['url'] for r in relevant]),

    "❌ Removed - Deduplication": dedup_removed,
    "Reasons - ❌ Removed - Deduplication": {url: "duplicate content or URL" for url in dedup_removed},

    "❌ Removed - Company-owned": company_removed,
    "Reasons - ❌ Removed - Company-owned": {url: "company-owned source" for url in company_removed},

    "❌ Removed - Keyword Excluded": without_excluded_keywords_removed,
    "Reasons - ❌ Removed - Keyword Excluded": {url: "excluded by keyword filter" for url in without_excluded_keywords_removed},

    "❌ Removed - Paywall": paywall_removed,
    "Reasons - ❌ Removed - Paywall": {url: "paywalled site" for url in paywall_removed},

    "❌ Removed - API Filtering": api_removed,
    "Reasons - ❌ Removed - API Filtering": {url: "API-limited access" for url in api_removed},

    "❌ Removed - Enriched": enriched_removed,
    "Reasons - ❌ Removed - Enriched": {url: enrichment_reasons.get(url, "") for url in enriched_removed},

    "❌ Removed - Relevance": relevance_removed,
    "Reasons - ❌ Removed - Relevance": {url: relevance_reasons.get(url, "") for url in relevance_removed}
}

    logger.info(f"\n\n Meta data is:  ------- {meta}\n") 
    logger.info(f"\n\n Summery info is:  ------- {summary_info}\n") 
    logger.info(f"\n\n🧾 Combined URLs ({len(all_normalized)}):\n") 
   

    logger.info(f"\n\n \n\n Google Search Results are: {google_results}\n")

    for item in preferred_results:
        logger.info(f"\n\n Item in preferred_results: {item}\n") 

    for item in all_normalized:
        logger.info(f"\n\n Item in combined: {item}\n") 
    
    for item in deduped:
        logger.info(f"\n\n Item in deduped: {item}\n") 

    for item in non_pdf_results:
        logger.info(f"\n\n Item in Non PDF Result: {item}\n")

    for item in cleaned:
        logger.info(f"\n\n Item in cleaned: {item}\n") 

    for item in without_excluded_keywords:
        logger.info(f"\n\n Item in without_excluded_keywords: {item}\n") 

    for item in paywall_filtered:
        logger.info(f"\n\n Item in paywall_filtered: {item}\n") 

    for item in api_filtered:
        logger.info(f"\n\n Item in api_filtered: {item}\n") 

    for item in enriched_articles:
        logger.info(f"\n\n Item in enriched_articles: {item}\n") 
    
    for item in enriched_urls:
        logger.info(f"\n\n Item in enriched_urls: {item}\n") 

    for item in relevant:
        logger.info(f"\n\n Item in relevant: {item}\n") 

    for item in final_relevant:
        logger.info(f"\n\n Item in final_relevant: {item}\n") 

    

    write_filtering_summary(summary_info, SEARCH_SUMMARY_FILE)
    write_search_results(relevant, meta, SEARCH_RESULTS_FILE)
    append_headlines(relevant, company_name, SEARCH_HEADLINES_FILE)

    return aggregated_text, SEARCH_RESULTS_FILE


# ADDITIONAL REQUIRED FUNCTION

def aggregate_text(articles):
    return "\n".join(article["content"] for article in articles if article.get("content"))




# 1️⃣ Extract domains from a list
def extract_sites_from(criteria_list):
    domain_pattern = re.compile(r"^(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")
    return {
        match.group(1)
        for item in criteria_list
        if (match := domain_pattern.match(item))
    }

# 2️⃣ Extract keywords (non-domains) from a list
def extract_keywords_from(criteria_list):
    domain_pattern = re.compile(r"^(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")
    return {
        item for item in criteria_list
        if not domain_pattern.match(item)
    }

def get_combined_context_keywords(user_keywords, generic_keywords):
    if isinstance(user_keywords, str):
        user_keywords = [kw.strip() for kw in user_keywords.split(',') if kw.strip()]
    return list(set(generic_keywords + user_keywords))


# 3️⃣ Final preferred sources
def get_final_preferred_sources(user_preferred_list, user_exclusion_sites, base_sources):
    return base_sources.union(set(user_preferred_list)) - set(user_exclusion_sites)

# 4️⃣ Exclusion sites
def get_exclusion_sites(raw_exclusions):
    return extract_sites_from(raw_exclusions)

# 5️⃣ Exclusion keywords
def get_exclusion_keywords(raw_exclusions, base_keywords):
    return set(base_keywords).union(extract_keywords_from(raw_exclusions))


########################################
# build_search_query()
    """
    Constructs a search query string combining the company name with each keyword using OR logic.

    Example:
        Input: company = 'volvo', keywords = 'competitor, news, report'
        Output: 'volvo competitor OR volvo news OR volvo report'
    """
def build_search_queries(company, keywords, mode="broad"):
    if isinstance(keywords, str):
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
    elif isinstance(keywords, list):
        keyword_list = [kw.strip() for kw in keywords if isinstance(kw, str) and kw.strip()]
    else:
        keyword_list = []

    if mode == "broad":
        combined = " OR ".join(keyword_list)
        return [f"{company} AND ({combined})"]

    elif mode == "focused":
        return [f"{company} AND {kw}" for kw in keyword_list]
    


######################################## 

def simplify_query_for_scraping(company, keywords):
    keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
    return f"{company} " + " ".join(keyword_list)


########################################

# google_search()
def google_search(query, api_key, cse_id, num_results=10, max_pages=5):
    print("The Queries for goog_search are::::::::::::", query)
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    results = []
    for page in range(max_pages):
        start = page * num_results + 1
        try:
            res = service.cse().list(q=query, cx=cse_id, num=num_results, start=start).execute()
            results.extend(res.get("items", []))
        except Exception as e:
            print(f"⚠ Google API error: {e}")
            break
    return [{"title": item["title"], "link": item["link"], "source": "google"} for item in results]


########################################


########################################

# scrape_preferred_sources()
def scrape_preferred_sources(query, search_templates, headers):
    print("The Queries for SCRAPE are **************", query)

    results = []
    seen = set()
    encoded_query = quote_plus(query)
    for domain, base_url in search_templates.items():
        search_url = f"{base_url}{encoded_query}"
        try:
            res = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=True)[:5]
            for link in links:
                url = link["href"]
                if not url.startswith("http"):
                    url = f"https://{domain}{url}"
                if url not in seen:
                    seen.add(url)
                    results.append({"title": link.get_text(strip=True), "link": url, "source": domain})
        except Exception as e:
            print(f"⚠ Scraping error from {domain}: {e}")
   
    return results


########################################

def fetch_from_newsapi(query, api_key, page_size=100):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    for a in articles:
        a["source_api"] = "NewsAPI"
    return articles



########################################

def fetch_from_contextualweb(query, api_key, count=10):
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/NewsSearchAPI"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }
    params = {
        "q": query,
        "pageNumber": 1,
        "pageSize": count,
        "autoCorrect": True
    }
    response = requests.get(url, headers=headers, params=params)
    response = requests.get(url, headers=headers, params=params)
    print("ContextualWeb status:", response.status_code, response.text[:200])

    articles = response.json().get("value", [])
    for a in articles:
        a["source_api"] = "ContextualWeb"
    return articles

########################################
#Not used
def fetch_from_bing_news(query, api_key, count=10):
    url = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key
    }
    params = {
        "q": query,
        "count": count,
        "mkt": "en-US"
    }
    response = requests.get(url, headers=headers, params=params)
    print("Bing status:", response.status_code, response.text[:200])  # Add this line

    articles = response.json().get("value", [])
    for a in articles:
        a["source_api"] = "BingNews"
    return articles

########################################

def fetch_from_serpapi(query, api_key, num_results=10):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "google",
        "tbm": "nws",
        "api_key": api_key,
        "num": num_results
    }
    response = requests.get(url, params=params)
    print("SerpAPI status:", response.status_code, response.text[:200])

    data = response.json()
    articles = data.get("news_results", [])
    for a in articles:
        a["source_api"] = "SerpAPI"
    return articles

########################################
# Not used
def extract_full_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"❌ Failed to extract full text from {url}: {e}")
        return ""

########################################

import requests
from newspaper import Article

def fetch_articles_from_gnews(company_name, context_keywords, max_articles=10):
    """
    Fetch articles from GNews API, extract full text, and return in normalized format.

    Args:
        company_name (str): The name of the company to search for.
        context_keywords (list): List of additional keywords to refine the search.
        max_articles (int): Maximum number of articles to process (default is 10).

    Returns:
        List of dicts with keys: title, source, published, url, text, source_type.
    """
    API_KEY_GNews = '8847423999e0049996b2f049ecf7afcc'
    base_url = "https://gnews.io/api/v4/search"

    # Build query string
    #query = f"{company_name} {' '.join(context_keywords)}"


    query_keywords = list(set([company_name] + context_keywords))
    query = " ".join(query_keywords[:10])  # limit to 10 keywords max
    params = {
        "q": query,
        "lang": "en",
        "token": API_KEY_GNews,
        "max": max_articles
    }


    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
    except Exception as e:
        print(f"[GNews] Error fetching articles: {e}")
        return []

    results = []

    for article in articles:
        url = article.get("url")
        if not url:
            continue

        try:
            extracted = Article(url)
            extracted.download()
            extracted.parse()
            full_text = extracted.text.strip()

            if full_text:
                results.append({
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "published": article.get("publishedAt"),
                    "url": url,
                    "text": full_text,
                    "source_type": "gnews"
                })
        except Exception as ex:
            print(f"[GNews] Skipped article due to parsing error: {ex}")
            continue

    return results


########################################
#Not used now
def fetch_gnews_metadata(query, api_key, max_results=10):
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "token": api_key,
        "lang": "en",
        "max": max_results
    }
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    for a in articles:
        a["source_api"] = "GNews"
    return articles

########################################

# Normailzation of all results: 

################################################################################


def normalize_results(
    scrape_results, google_results, gnews_results,
    newsapi_results, serpapi_results, contextualweb_results, di_dn_results
):
    normalized = []

    # Scrape
    for item in scrape_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source": item.get("source", "scrape"),
            "published": item.get("published", ""),
            "text": "",
            "source_type": "scrape"
        })

    # Google
    for item in google_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("link", "").strip(),
            "source": item.get("source", "google.com"),
            "published": item.get("published", ""),
            "text": "",
            "source_type": "google"
        })

    # GNews
    for item in gnews_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source": item.get("source", "gnews"),
            "published": item.get("published", ""),
            "text": item.get("text", ""),
            "source_type": "gnews"
        })

    # NewsAPI
    for item in newsapi_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source": item.get("source", {}).get("name", "newsapi"),
            "published": item.get("publishedAt", ""),
            "text": "",
            "source_type": "newsapi"
        })

    # SerpAPI
    for item in serpapi_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("link", "").strip(),
            "source": item.get("source", "serpapi"),
            "published": item.get("date", ""),
            "text": "",
            "source_type": "serpapi"
        })

    # ContextualWeb
    for item in contextualweb_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source": item.get("provider", {}).get("name", "contextualweb"),
            "published": item.get("datePublished", ""),
            "text": "",
            "source_type": "contextualweb"
        })

    # DI/DN articles
    for item in di_dn_results:
        normalized.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source": item.get("source", "di_dn"),
            "published": item.get("published", ""),
            "text": item.get("text", ""),
            "source_type": "di_dn"
        })

    return normalized



################################################################################




def combine_results(scraped, google, gnews):
    seen_urls = set()
    combined = []
    duplicate_urls = []

    for group in [scraped, google, gnews]:
        for item in group:
            url = item.get("url") or item.get("link")
            if not url:
                continue
            if url in seen_urls:
                duplicate_urls.append(url)
                continue
            seen_urls.add(url)
            combined.append(item)

    print(f"🧹 Duplicates removed: {len(duplicate_urls)}")
    print("🗑️ Duplicate URLs:")
    for url in duplicate_urls:
        print(f"- {url}")

    return combined



########################################

#  deduplicate_results()
import hashlib

def deduplicate_results(results):
    seen_urls = set()
    seen_hashes = set()
    deduped = []
    duplicates = []

    for r in results:
        url = r.get("url", "")  # 🔧 Consistent 'url'
        content = r.get("content", "")

        content_hash = hashlib.md5(content.strip().lower().encode("utf-8")).hexdigest() if content else None

        if url not in seen_urls and content_hash not in seen_hashes:
            seen_urls.add(url)
            if content_hash:
                seen_hashes.add(content_hash)
            deduped.append(r)
        else:
            duplicates.append(url)

    print(f"🛽 Deduplicated {len(duplicates)} duplicate URLs")
    for d in sorted(set(duplicates)):
        print(f"🔁 {d}")

    return deduped


########################################

def filter_pdf_urls(results):
    return [r for r in results if not r.get("url", "").lower().endswith(".pdf")]


########################################
# See filter_disallowed_sources function below
from urllib.parse import urlparse

def is_company_domain(url, company_name):
    try:
        domain = urlparse(url).netloc.lower()
        return company_name.lower() in domain
    except:
        return False
# See filter_disallowed_sources function below

def filter_company_owned_content(results, company_name):
    filtered = []
    for r in results:
        url = r.get('url', '')
        domain = urlparse(url).netloc.lower()
        is_owned = company_name.lower() in domain
        print(f"🏢 Checking domain: {domain} | Owned: {is_owned}")
        if not is_owned:
            filtered.append(r)
    return filtered

########################################

def filter_disallowed_sources(results, company_name):
    filtered = []
    reasons = {}

    for r in results:
        url = r.get('url', '')
        domain = urlparse(url).netloc.lower()

        if company_name.lower() in domain:
            reasons[url] = "company-owned domain"
            continue

        if is_profile_url(url):
            reasons[url] = "profile/reference/personal URL"
            continue

        filtered.append(r)

    return filtered, reasons


########################################

def handle_paywalled_sources(results):
    paywalled_domains = {"www.ft.com", "www.wsj.com"}
    return [r for r in results if not any(domain in r.get("url", "") for domain in paywalled_domains)]




#  handle_api_limited_sources()
def handle_api_limited_sources(results):
    return results  # Placeholder for future logic

########################################

#  fetch_article_text()
def fetch_article_text(url, headers, debug=False):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        # Remove noisy tags
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.extract()

        # Primary: Extract from <p> tags with minimum length
        paragraphs = soup.find_all("p")
        clean_text = "\n".join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) >= 30)

        # 🔄 Fallback logic if too short
        if len(clean_text.strip()) < 100:
            all_text = soup.get_text(separator="\n").strip()
            if len(all_text) > 300:
                clean_text = all_text
                if debug:
                    print("⚠️ Fallback triggered: Using all visible text.")

        # Final fallback to browser scraping if still too short
        if len(clean_text.strip()) < 50:
            return fetch_article_text_with_browser(url, debug)

        return clean_text

    except Exception as e:
        print(f"⚠ Error fetching {url} via requests: {e}")
        return fetch_article_text_with_browser(url, debug)


########################################



########################################

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_article_text_with_browser(url, debug=False):
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup

    if debug:
        print(f"🧭 Using browser fallback for: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            page.wait_for_timeout(3000)  # Wait for dynamic content to load

            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, "html.parser")

            # Remove noise elements including image/figure blocks
            for tag in soup(["script", "style", "header", "footer", "nav", "aside", "img", "figure"]):
                tag.decompose()

            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) >= 30)
            clean_text = text.strip()

            if debug:
                print(f"🧪 [Browser] Extracted {len(clean_text)} chars from {url}")

            return clean_text if clean_text else None

    except Exception as e:
        if debug:
            print(f"⚠️ Browser fallback failed: {e}")
        return None



#######################################
    
from newspaper import Article

def extract_full_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"[Text Extraction] Failed for {url}: {e}")
        return None

#######################################
    
import os
from newspaper import Article
from datetime import datetime
import requests
import fitz  # PyMuPDF

def enrich_articles_with_full_text(articles, log_file_path="failed_extractions.log", company_name=None, session_id=None):
    enriched = []
    failed_urls = []
    failed_reasons = {}  # 🆕 Track reasons for summary

    total = len(articles)
    success = 0
    fail = 0

    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, art in enumerate(articles[:5]):
        print(f"Article{i+1}: {art}")

    for art in articles:
        url = art.get("url")
        source_type = art.get("source_type", "unknown")

        if not url:
            fail += 1
            reason = "missing URL"
            failed_urls.append((source_type, reason))
            failed_reasons[url] = reason
            continue

        try:
            if url.lower().endswith(".pdf"):
                try:
                    response = requests.get(url, timeout=10)
                    if len(response.content) > 10_000_000:
                        reason = "PDF too large"
                        raise ValueError(reason)

                    if response.status_code == 200:
                        doc = fitz.open(stream=response.content, filetype="pdf")
                        full_text = "\n".join(page.get_text().strip() for page in doc if page.get_text().strip())
                        doc.close()
                        if full_text and len(full_text) > 100:
                            art["content"] = full_text
                            print(f"✅ Enriched content for: {url} | Length: {len(full_text)}")

                            enriched.append(art)
                            success += 1
                            continue
                        else:
                            reason = "PDF content too short or empty"
                    else:
                        reason = f"PDF request failed ({response.status_code})"

                except Exception as e:
                    reason = f"PDF error: {e}"

                fail += 1
                print(f"[Rejected PDF] {url} | Reason: {reason}")
                failed_urls.append((source_type, f"{url} - {reason}"))
                failed_reasons[url] = reason
                continue

            article = Article(url)
            #print(" article is : AAAAAAAAAAAAAAAAAAAAA", article)
            article.download()
            article.parse()
            full_text= fetch_article_text(url, HEADERS)
            #full_text = article.text.strip()
            #print("full text is ......", full_text)


            print(f"🧪 {url} — fetched length: {len(full_text)}")
            #print(full_text[:100])

            if full_text and len(full_text) > 100:
                art["content"] = full_text
                enriched.append(art)
                success += 1
            else:
                fail += 1
                reason = "empty" if not full_text else f"too short ({len(full_text)} chars)"
                print(f"[Rejected] {url} | Reason: {reason}")
                failed_urls.append((source_type, f"{url} - {reason}"))
                failed_reasons[url] = reason

        except Exception as e:
            print(f"[Text Extraction] Failed for {url}: {e}")
            fail += 1
            reason = f"Exception: {e}"
            failed_urls.append((source_type, f"{url} - {reason}"))
            failed_reasons[url] = reason

    print(f"[Text Extraction] Attempted: {total}, Success: {success}, Failed: {fail}")

    if failed_urls:
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n" + "="*70 + "\n")
            log_file.write(f"🔍 Failed Extractions - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if company_name:
                log_file.write(f"Company: {company_name}\n")
            log_file.write(f"Session ID: {session_id}\n")
            log_file.write(f"Total: {total}, Success: {success}, Failed: {fail}\n")
            for source, url in failed_urls:
                log_file.write(f"[{source}] {url}\n")
    for r in enriched:
        print("✅ Enriched article:", r.get("url"))
        #print("📝 Content (first 300 chars):", r.get("content", "")[:300])

    return enriched, failed_reasons


#######################################
    
def filter_excluded_keywords_metadata(results, exclusion_keywords):
    filtered = []
    for r in results:
        url = r.get("url", "").lower()
        title = r.get("title", "").lower()
        if not any(kw.lower() in url or kw.lower() in title for kw in exclusion_keywords):
            filtered.append(r)
    return filtered

    
#######################################

# ✅ Extract inner links from content
def extract_inner_links(html_content, company_name):
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        if company_name.lower() in href.lower() and href.startswith("http"):
            links.append(href)
    return links

# ✅ Try fetching deeper content when surface content is too short
def try_fetch_inner_link_content(r, context_keywords, company_name):
    content = r.get("content", "")
    if not content or len(content) < 100:
        return False

    link = r.get("link", "")
    try:
        soup = BeautifulSoup(content, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            if company_name.lower() in href.lower() or any(kw.lower() in href.lower() for kw in context_keywords):
                full_url = href if href.startswith("http") else requests.compat.urljoin(link, href)
                inner_text = fetch_article_text(full_url, HEADERS)
                if inner_text and len(inner_text.strip()) > 200:
                    r["content"] = inner_text
                    return True
    except Exception as e:
        print(f"⚠️ Error parsing inner links for: {link} - {e}")
    return False

########################################

# ✅ Main relevance filter with fallback for inner links
def is_relevant_article(text, company_name, keywords, min_keyword_hits=1, debug=False):
    if isinstance(keywords, str):
        keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
    elif isinstance(keywords, list):
        keywords = [kw.strip().lower() for kw in keywords if isinstance(kw, str)]

    text_lower = text.lower()
    keyword_matches = [kw for kw in keywords if kw in text_lower]
    company_in_text = company_name.lower() in text_lower

    if debug:
        
        print("\n🧠 DEBUG: Relevance Check")
        print(f"→ Company name found: {company_in_text}")
        print(f"→ Keywords matched: {keyword_matches}")
        print(f"→ Total matches: {len(keyword_matches)} / Required: {min_keyword_hits}")
        print(f"→ Text snippet: {text[:300]}...\n")  # Only part of content


    if company_in_text or len(keyword_matches) >= min_keyword_hits:
        return True, "relevant"
    else:
        return False, "not relevant (no match on company or keywords)"

########################################

def filter_irrelevant_content(results, context_keywords, company_name, fallback_threshold=40):
    print("🧠 Inside filter_irrelevant_content")
    filtered = []
    reasons = {}

    for r in results:
        url = r.get("url", "")
        title = r.get("title", "")
        content = r.get("content", "")

        print(f"\n🔎 URL: {url}")
        print(f"📏 Content length: {len(content.strip()) if content else 0}")

        if not content or len(content.strip()) < 30:
            reasons[url] = "content too short or empty"
            continue

        combined_text = f"{title} {content}"
        is_relevant, reason = is_relevant_article(
            text=combined_text,
            company_name=company_name,
            keywords=context_keywords,
            debug=True
        )

        # Optional fallback: keep if company name appears ≥ 2 times
        if not is_relevant and content.lower().count(company_name.lower()) >= 2:
            print(f"📌 Fallback: company name found multiple times — keeping {url}")
            is_relevant = True
            reason = "Fallback: multiple company mentions"

        if is_relevant:
            strong_matches, soft_matches = count_keyword_matches(combined_text)
            r["strong_matches"] = strong_matches
            r["soft_matches"] = soft_matches

            score = compute_relevance_score(is_relevant, strong_matches, soft_matches)
            r["relevance_score"] = score

            print(f"🧪 Score: {score}, Strong: {strong_matches}, Soft: {soft_matches}")

            if score >= fallback_threshold:  # You can adjust this threshold
                r["flagged_profile"] = is_profile_url(url)
                r["source_type"] = get_source_type(url)
                r["tags"] = assign_tags(combined_text)
                filtered.append(r)
                print(f"✅ Passed relevance: {url}")
            else:
                print(f"❌ Rejected (low score): {url}")
                reasons[url] = f"low relevance score ({score})"
        else:
            print(f"❌ Rejected: {url} | Reason: {reason}")
            reasons[url] = reason

    return filtered, reasons



########################################

# === Multilingual final filter and merge ===

from time import sleep

def multilingual_processing_debug(relevant_articles, exclusion_keywords, combined_keywords, company_name, fallback_threshold=40):
    final_relevant = []
    non_english_articles = []
    language_stats = {}
    excluded_by_keywords = []

    for article in relevant_articles:
        try:
            content = article.get("content", "").strip()
            lang = detect(content) if len(content) > 100 else "unknown"
            logger.info(f" \n\n\n\nT he detected language for the article is: {lang}")
        except Exception as e:
            print(f"Language detection failed: {e}")
            lang = 'unknown'
            article["language"] = lang
            language_stats[lang] = language_stats.get(lang, 0) + 1

            print(f"\n🌍 Language: {lang} | Title: {article.get('title', '')}")

            if lang == "en":
                final_relevant.append(article)
            else:
                content = article["content"][:4990]  # Leave room under 5000 char limit
                logger.info(f" \n\n\n\n The Content of non-English article is: {content}")
                try:
                    article["content"] = translate_large_text(content)
                except exceptions.RequestError:
                    print("🔁 GoogleTranslator failed. Retrying after delay...")
                    sleep(2)
                    try:
                        article["content"] = translate_large_text(content)
                    except Exception as e:
                        print(f"❌ Translation failed again: {e}")
                        article["content"] = content  # fallback: untranslated

                #print(f"🔤 Translated snippet:\n{article['content'][:300]}")

                content_lower = article["content"].lower()
                if any(excl in content_lower for excl in exclusion_keywords):
                    print(f"🛑 Excluded by keywords: {article['url']}")
                    excluded_by_keywords.append(article['url'])
                else:
                    non_english_articles.append(article)

        except Exception as e:
            print(f"❌ Language handling failed for {article['url']}: {e}")

    print(f"\n📬 Filtering {len(non_english_articles)} translated non-English articles with fallback threshold = {fallback_threshold}...")
    filtered_non_english, _ = filter_irrelevant_content(non_english_articles, combined_keywords, company_name, fallback_threshold)

    final_relevant.extend(filtered_non_english)
    print("Final Relevant look like this .....................")
    for i, item in enumerate(final_relevant):
        print(f"[{i}] Type: {type(item)} - Keys: {item.keys() if isinstance(item, dict) else 'Not a dict'}")


    # === Summary Log ===
    print("\n📊 Language Distribution:")
    for lang, count in language_stats.items():
        print(f" - {lang.upper()}: {count} article(s)")

    print(f"🧹 Keyword exclusions: {len(excluded_by_keywords)} article(s)")

    return final_relevant


def aggregate_text(articles):
    return "\n".join(article["content"] for article in articles if article.get("content"))

########################################
#these 2 functions act together:

def is_meaningful_content(text):
    """Returns True if text looks like a real article body."""
    if not text or len(text.strip()) < 200:
        return False, "too short"
    junk_phrases = [
        "By commenting, you agree to the Prohibited Content Policy",
        "Please enable JavaScript to view the comments powered by Disqus",
        "To read the full article, subscribe or login",
        "This page requires JavaScript"
    ]
    for phrase in junk_phrases:
        if phrase.lower() in text.lower():
            return False, f"contains: {phrase[:40]}..."
    return True, ""

def filter_low_quality_articles(articles):
    """Remove articles with no useful content and log reasons."""
    filtered = []
    removed = []
    for a in articles:
        ok, reason = is_meaningful_content(a.get("content", ""))
        if ok:
            filtered.append(a)
        else:
            removed.append((a.get("url", "no-url"), reason))
    print(f"🧹 Filtered out {len(removed)} low-quality articles.")
    for url, reason in removed[:5]:
        print(f"❌ Removed: {url} — Reason: {reason}")
        logger.info(f"\n\n Removed low quality article text: {url} — Reason: {reason}\n\n")
    return filtered



########################################


def write_search_results(articles, meta_info, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("===== METADATA =====\n")
        for k, v in meta_info.items():
            f.write(f"{k}: {v}\n")
        f.write("\n===== ARTICLES =====\n\n")
        for i, a in enumerate(articles, 1):
            f.write(f"{i}. {a['title']}\nSource: {a.get('source', 'unknown')}\nURL: {a.get('url')}\nContent:\n{a.get('content', '')}\n{'='*80}\n\n")


########################################
            
# 🔧 Modified: append_headlines uses 'url' instead of 'link'
def append_headlines(articles, company_name, headline_filepath):
    from datetime import datetime
    with open(headline_filepath, "a", encoding="utf-8") as f:
        f.write(f"\n===== ARTICLE HEADLINES =====\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCompany: {company_name}\n\n")
        for i, a in enumerate(articles, 1):
            f.write(f"{i}. {a['title']}\nSource: {a.get('source', 'unknown')}\nURL: {a.get('url')}\n\n")
        f.write("-"*100 + "\n")


########################################
        
# ✅ Write filtering steps and discarded links to separate file (markdown clickable)
def write_filtering_summary(summary_info, filepath, print_summary=True):
    summary_lines = [
        f"🔍 Google Results: {summary_info.get('google_results', '?')}",
        f"🗞️ Scraped Results: {summary_info.get('scraped_results', '?')}",
        f"🗞️ Gnews Results: {summary_info.get('gnews_results', '?')}",
        f"🔀 all_normalized: {summary_info.get('all_normalized', '?')}",
        f"🚫 Company-owned / Disallowed URLs Filtered: {summary_info.get('disallowed_filtered', '?')}",
        f"📝 Keyword Excluded Filtered (metadata/title): {summary_info.get('keyword_filtered', '?')}",
        f"💰 Paywall Filtered: {summary_info.get('paywall_filtered', '?')}",
        f"🔌 API Filtered: {summary_info.get('api_filtered', '?')}",
        f"🧽 Enriched Filtered: {summary_info.get('enriched_filtered', '?')}",
        f"✅ Final Articles: {summary_info.get('final_articles', '?')}"
    ]

    if print_summary:
        print("\n===== FILTERING SUMMARY =====")
        for line in summary_lines:
            print(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("===== FILTERING SUMMARY =====\n")
        for line in summary_lines:
            f.write(line + "\n")

        for category in [
            "❌ Removed - Deduplication",
            "❌ Removed - Company-owned",
            "❌ Removed - Paywall",
            "❌ Removed - API Filtering",
            "❌ Removed - Enriched",
            "❌ Removed - Relevance"
        ]:
            if category in summary_info:
                f.write(f"\n{category} ({len(summary_info[category])}):\n")
                for item in summary_info[category]:
                    reason = summary_info.get(f"Reasons - {category}", {}).get(item, "")
                    f.write(f"- [{item}]({item})\n{f'  ❓ {reason}' if reason else ''}\n")

        f.write(f"✅ Final articles: {len(summary_info.get('✅ Final url', []))} (enriched and relevant)\n")
        for item in summary_info.get("✅ Final url", []):
            f.write(f"- [{item}]({item})\n")

        f.write("\n" + "="*100 + "\n")



########################################
        
def log_to_file(section_name, data, file_path="debug_log.txt", mode="a"):
    with open(file_path, mode, encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n🔹 {section_name}\n{'='*60}\n")
        if isinstance(data, list):
            for item in data:
                f.write(f"{item}\n")
        elif isinstance(data, dict):
            for key, val in data.items():
                f.write(f"{key}: {val}\n")
        else:
            f.write(str(data) + "\n")
        f.write(f"\n\n\n")
        f.write(f"\n\n\n")
        f.write(f"\n\n\n")



########################################
########################################
########################################
########################################
########################################
########################################
            

# Suggested upgrades for Internet Article Filtering & Tracking

# === 1. Personal and Generic Profile Filter ===
from urllib.parse import urlparse

def is_profile_url(url):
    url = url.lower()
    domain = urlparse(url).netloc
    path = urlparse(url).path

    # Path-based personal/profile filters
    profile_path_keywords = [
        '/in/', '/pub/', '/person/', '/people/', '/jobs/', '/status/', '/@'  # last one for Medium
    ]
    if any(kw in path for kw in profile_path_keywords):
        return True

    # Domain-based generic reference or social media
    profile_domains = [
        'wikidata.org', 'wikipedia.org', 'britannica.com',
        'facebook.com', 'linkedin.com', 'twitter.com',
        'glassdoor.com', 'indeed.com', 'monster.com'
    ]
    if any(domain.endswith(d) for d in profile_domains):
        return True

    return False


########################################
# === 2. Source Type Classification ===
def get_source_type(url):
    if any(domain in url for domain in ['linkedin.com/in/', 'crunchbase.com/person/', 'facebook.com/people/', 'twitter.com/', 'medium.com/@']):
        return 'profile'
    elif 'wikipedia.org' in url or 'wikidata.org' in url or 'britannica.com' in url:
        return 'reference'
    elif any(domain in url for domain in ['glassdoor.com', 'indeed.com', 'monster.com', 'linkedin.com/jobs']):
        return 'job_board'
    elif 'reddit.com/r/' in url or 'github.com/issues' in url or 'stackoverflow.com' in url:
        return 'community'
    elif 'notion.site' in url:
        return 'ai_generated'
    else:
        return 'article_or_news'
########################################
# === 3. Keyword Weighting ===
strong_keywords = {'contract', 'financial', 'report', 'market', 'acquisition', 'CEO', 'investment', 'sales'}
soft_keywords = {'service', 'growth', 'customer', 'innovation', 'launch'}

def count_keyword_matches(text):
    strong = sum(1 for word in strong_keywords if word.lower() in text.lower())
    soft = sum(1 for word in soft_keywords if word.lower() in text.lower())
    return strong, soft

########################################
# === 4. Relevance Scoring ===
def compute_relevance_score(company_found, strong_count, soft_count):
    score = 0
    if company_found:
        score += 50
    score += strong_count * 10
    score += soft_count * 5
    return min(score, 100)

########################################

# === 5. Optional Tagging ===
def assign_tags(text):
    tags = []
    if 'ESG' in text.upper(): tags.append('esg')
    if 'offshore wind' in text.lower(): tags.append('offshore_wind')
    if 'grid' in text.lower(): tags.append('grid_expansion')
    if 'battery' in text.lower(): tags.append('battery_storage')
    if 'acquisition' in text.lower(): tags.append('acquisition')
    return tags



########################################
# === 6. Logging (avoid duplicates) ===
seen_urls = set()
def log_relevance_check(url, title, snippet, company_found, strong, soft):
    if url in seen_urls:
        return
    seen_urls.add(url)
    print(f"\n🧠 DEBUG: Relevance Check")
    print(f"→ Company name found: {company_found}")
    print(f"→ Strong matches: {strong}, Soft matches: {soft}")
    print(f"→ Score: {compute_relevance_score(company_found, strong, soft)}")
    print(f"→ Text snippet: {snippet[:300]}...")
    print(f"✅ Article is relevant: {url}\n")

########################################
    
# === 7. Create Structured Article Entry ===
def create_article_entry(url, title, content, company_found):
    strong, soft = count_keyword_matches(content)
    score = compute_relevance_score(company_found, strong, soft)
    tags = assign_tags(content)
    return {
        'url': url,
        'title': title,
        'summary': content[:250],
        'source_domain': url.split('/')[2],
        'source_type': get_source_type(url),
        'enriched': True,
        'relevance_score': score,
        'company_match': company_found,
        'matched_keywords': list(strong_keywords.union(soft_keywords).intersection(content.lower().split())),
        'strong_matches': strong,
        'soft_matches': soft,
        'flagged_profile': is_profile_url(url),
        'tags': tags,
        'reason_flagged': None
    }
########################################

########################################
########################################
# Di och DN Search ....

########################################
########################################


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import sleep

headers = {"User-Agent": "Mozilla/5.0"}


def get_articles_from_di_and_dn(company_name):
    articles = []
    articles += fetch_articles_from_di(company_name)
    articles += fetch_articles_from_dn(company_name)
    return articles

########################################

# === GENERAL FALL A ===
def fetch_request_bs4_page(url):
    print(f"\U0001F310 Hämtar: {url}")
    response = requests.get(url, headers=headers)
    return response.text

########################################

def extract_articles_with_prefix(html, base_url, prefix, source_name):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen_urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(prefix):
            full_url = urljoin(base_url, href)
            # Filter out irrelevant sections like /kontakt/ /korsord/ etc.
            if any(x in full_url for x in [
                "/kontakt", "/korsord", "/quiz", "/app/", "/webbspel/", "/dodsannonser/", "/ledare/", "/nyhetsbrev/", "/foljer/", "/jobba-pa-dn/", "/sok/?q=", "/om/", "/serier/", "/mat-dryck/", "/insidan/"
            ]):
                continue
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                links.append({
                    "title": a.get_text(strip=True),
                    "url": full_url,
                    "source": source_name,
                    "source_type": "scrape"
                })
    return links

########################################

# === SITE-SPECIFIC FALL A1: di.se ===
def fetch_articles_from_di(query):
    search_url = f"https://www.di.se/search/?query={query}"
    html = fetch_request_bs4_page(search_url)
    return extract_articles_with_prefix(html, "https://www.di.se", "/nyheter/", "di.se")


# === SITE-SPECIFIC FALL A1: dn.se ===
def fetch_articles_from_dn(query):
    search_url = f"https://www.dn.se/sok/?q={query}"
    html = fetch_request_bs4_page(search_url)
    return extract_articles_with_prefix(html, "https://www.dn.se", "/", "dn.se")

# === Article content enrichment ===
def fetch_article_content(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title_tag = soup.find("title")
        content_div = soup.find("div", class_="article__content")
        if content_div:
            paragraphs = content_div.find_all("p")
            content_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        else:
            content_text = ""

        return {
            "url": url,
            "title": title_tag.get_text(strip=True) if title_tag else "Not Found",
            "content": content_text.strip() or "[No content extracted]"
        }
    except Exception as e:
        print(f"❌ Kunde inte hämta {url}: {e}")
        return None



###########################################################################################
# Add this to internet_search
from deep_translator import GoogleTranslator, exceptions
from nltk.tokenize import sent_tokenize
from time import sleep

def translate_large_text(text, source_lang='auto', target_lang='en', chunk_limit=4900, delay=1):
    '''
    Translate large text safely using GoogleTranslator with chunking and retry.
    
    Args:
        text (str): The input text to translate.
        source_lang (str): Source language, default 'auto'
        target_lang (str): Target language, default 'en'
        chunk_limit (int): Max char length per chunk (default 4900)
        delay (int): Delay between chunks to avoid rate-limiting

    Returns:
        str: The translated text
    '''
    sentences = sent_tokenize(text)
    current_chunk = ""
    translated_chunks = []

    def safe_translate(chunk):
        try:
            return GoogleTranslator(source=source_lang, target=target_lang).translate(chunk)
        except exceptions.RequestError:
            sleep(2)
            try:
                return GoogleTranslator(source=source_lang, target=target_lang).translate(chunk)
            except Exception as e:
                print(f"❌ Translation failed: {e}")
                return chunk

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_limit:
            current_chunk += " " + sentence
        else:
            translated = safe_translate(current_chunk.strip())
            translated_chunks.append(translated)
            sleep(delay)
            current_chunk = sentence

    if current_chunk:
        translated_chunks.append(safe_translate(current_chunk.strip()))

    return " ".join(translated_chunks)



########################################
########################################
########################################
########################################
########################################
########################################


"""

keywords = "news, nyheter, article, omdöme, competition, konkurrens, market, sales, contract, report, annual report"
company_name = "volvo"

user_preferred = [
    "www.marketwatch.com",          # known in SEARCH_TEMPLATES
    "www.bbc.com",         # NOT in SEARCH_TEMPLATES → fallback URL used
    "www.dn.se" ,
    "www.gnews.io",
    "www.newsdata.io"   
        # known in SEARCH_TEMPLATES
]

user_exclusions = """
#www.svd.se",
"video",
"stream"
"""

search_config = {
    "company_name": company_name,
    "keywords": keywords,
    "user_preferred": user_preferred,
    "user_exclusions": [x.strip() for x in user_exclusions.split(',') if x.strip()],
    "time_filter": "any"
}

aggregated_text, results_path = fetch_articles_controller(search_config)



# Print basic output
print("\n📝 Aggregated Text Preview:")
print(aggregated_text[:500] if aggregated_text else "No content found.")

print(f"\n📄 Search result saved to: {results_path}")



# Not used: Redefined

    normalized_google_results = []
    for item in google_results:
        normalized_google_results.append({
            "title": item.get("title", "").strip(),
            "url": item.get("link", "").strip(),
            "source": item.get("source", "google.com"),
            "source_type": "google"
        })

     # Step 3 — Normalize
    normalized_scrape_results = []
    for item in valid_scrape_results:
        normalized_scrape_results.append({
            "title": item.get("title", "").strip(),
            "url": item.get("url", "").strip(),
            "source_type": "scrape"
        })

    logger.info(f"\n\n \n\n Normalized Google Search is:  {normalized_scrape_results}")
    logger.info(f"\n\n Normalized Scrap is: {normalized_scrape_results}")

    print(f"📦 Scraped to combine: {len(normalized_scrape_results)}")
    print(f"🌍 Google to combine: {len(normalized_google_results)}")
    print(f"📰 GNews to combine: {len(gnews_results)}")


    combined = combine_results(
    normalized_scrape_results + di_dn_results,
    normalized_google_results,
    gnews_results
)
    #combined = combine_results(normalized_scrape_results, normalized_google_results, gnews_results)
    log_to_file("\n\n \n\n Combined Results", combined)
    print(f"🔀 Combined after merging: {len(combined)}")

    """

