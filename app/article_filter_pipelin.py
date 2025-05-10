
def run_article_filter_pipeline(all_results, company_domains, excluded_keywords):
    '''
    Combine, deduplicate, filter, and enrich article search results step by step.
    Args:
        all_results (list): List of result dicts from various sources
        company_domains (list): e.g., ["volvo.com", "bmwgroup.com"]
        excluded_keywords (list): e.g., ["careers", "about", "login", "cookies"]
    Returns:
        Filtered, enriched results
    '''
    from urllib.parse import urlparse
    from newspaper import Article

    def get_domain(url):
        try:
            return urlparse(url).netloc.replace("www.", "")
        except:
            return ""

    def deduplicate(results):
        seen = set()
        deduped = []
        for r in results:
            url = r.get("url", "").strip()
            if url and url not in seen:
                seen.add(url)
                deduped.append(r)
        return deduped

    def filter_company_links(results, company_domains):
        return [r for r in results if get_domain(r.get("url", "")) not in company_domains]

    def filter_by_metadata_keywords(results, keywords):
        return [
            r for r in results
            if not any(k.lower() in (r.get("title", "") + r.get("url", "")).lower() for k in keywords)
        ]

    def enrich_with_full_text(results):
        enriched = []
        for r in results:
            try:
                article = Article(r["url"])
                article.download()
                article.parse()
                r["text"] = article.text.strip()
            except Exception as e:
                r["text"] = ""
            enriched.append(r)
        return enriched

    # Pipeline
    combined = all_results
    step1 = deduplicate(combined)
    step2 = filter_company_links(step1, company_domains)
    step3 = filter_by_metadata_keywords(step2, excluded_keywords)
    step4 = enrich_with_full_text(step3)
    return step4
