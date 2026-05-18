# Scraping Challenges & Solutions

## Overview
This document outlines the challenges encountered while building the Startup Opportunity Aggregator and the solutions implemented to address them.

---

## Challenge 1: Dynamic Content & JavaScript Rendering

### Problem
Many modern websites (especially F6S and Eventbrite) load content dynamically using JavaScript. Traditional HTTP requests with BeautifulSoup only return the initial HTML, which often lacks the actual opportunity data.

### Solution Implemented
- **Static HTML Parsing**: For government sources (Startup India, MeITY, NITI Aayog, MSME), we use BeautifulSoup to parse static HTML as these sites are built with server-side rendering.
- **API Endpoints**: Where possible, we identify and use internal API endpoints that return JSON data instead of parsing HTML.
- **Fallback Strategy**: If dynamic content is detected, we implement a retry mechanism with different user agents and headers.

### Code Example
```python
# From base_scraper.py
HEADERS = [
    {"User-Agent": "Mozilla/5.0"},
    {"User-Agent": "Chrome/124.0"},
    {"User-Agent": "Safari/537.36"},
]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def fetch(self, url: str) -> str:
    response = self.session.get(url, headers=random.choice(self.HEADERS), timeout=self.timeout)
    response.raise_for_status()
    return response.text
```

---

## Challenge 2: Anti-Scraping Measures

### Problem
Several sources implement anti-scraping measures including:
- Rate limiting
- IP blocking
- CAPTCHA challenges
- User-Agent detection

### Solution Implemented
- **User-Agent Rotation**: Randomly rotate between different user agents to mimic different browsers.
- **Exponential Backoff**: Implemented using the `tenacity` library to retry failed requests with increasing delays.
- **Request Throttling**: Added delays between requests to avoid overwhelming servers.
- **Session Management**: Use persistent sessions with cookies to maintain authentication state.

### Code Example
```python
# From scheduler/jobs.py
for scraper, source_name in scrapers:
    start_time = time.time()
    try:
        scraped = scraper.scrape()
        duration = time.time() - start_time
        MonitoringService.record_execution(
            source=source_name,
            status=ScraperStatus.SUCCESS,
            items_scraped=len(scraped),
            duration_seconds=duration
        )
        records.extend(scraped)
    except Exception as e:
        # Continue with other sources even if one fails
        continue
```

---

## Challenge 3: Data Inconsistency Across Sources

### Problem
Different sources structure their data differently:
- Some use "Grant", others use "grant" or "GRANT"
- Date formats vary (DD/MM/YYYY, MM/DD/YYYY, ISO format)
- Location data might be city, country, or "Remote"

### Solution Implemented
- **Normalization Pipeline**: Created a pipeline service that normalizes data before storage.
- **Validator Layer**: Implemented validation using Marshmallow to ensure data consistency.
- **Auto-Tagging Service**: Uses keyword matching to automatically tag opportunities with relevant categories.

### Code Example
```python
# From services/pipeline_service.py
def process(self, raw_records: list[dict]) -> dict:
    validated = []
    duplicates_removed = []
    
    for record in raw_records:
        try:
            validated_record = self.validator.load(record)
            validated.append(validated_record)
        except ValidationError as e:
            continue
    
    for record in validated:
        if not self.duplicate_service.is_duplicate(record):
            duplicates_removed.append(record)
    
    return {
        "total_raw": len(raw_records),
        "validated": len(validated),
        "duplicates_removed": len(validated) - len(duplicates_removed),
        "stored": len(duplicates_removed)
    }
```

---

## Challenge 4: Duplicate Detection

### Problem
The same opportunity might appear on multiple sources or be scraped multiple times:
- Same title from different sources
- Same opportunity scraped at different times
- Slight variations in titles/descriptions

### Solution Implemented
- **Content Hashing**: Create SHA-256 hash of normalized title + source + URL.
- **Fuzzy Matching**: Use RapidFuzz for similarity detection when exact matches fail.
- **Database Constraints**: Unique constraints on normalized_title + source_platform.

### Code Example
```python
# From services/duplicate_service.py
def is_duplicate(self, record: dict) -> bool:
    row_hash = self._compute_hash(record)
    
    existing = Opportunity.query.filter_by(row_hash=row_hash).first()
    if existing:
        return True
    
    # Fuzzy matching for similar titles
    similar = Opportunity.query.filter(
        Opportunity.normalized_title.ilike(f"%{record['normalized_title']}%")
    ).first()
    
    if similar and self._similarity_score(record['normalized_title'], similar.normalized_title) > 0.85:
        return True
    
    return False
```

---

## Challenge 5: Pagination Handling

### Problem
Some sources have hundreds of opportunities spread across multiple pages:
- URL-based pagination (?page=1, ?page=2)
- Infinite scroll
- Load more buttons

### Solution Implemented
- **Configurable Page Limits**: Each scraper can specify max pages to scrape.
- **Pagination Detection**: Automatically detect pagination patterns and follow them.
- **Depth Limiting**: Set reasonable limits to avoid scraping entire databases.

### Code Example
```python
# From scrapers/startup_india_scraper.py
def scrape(self) -> list[dict]:
    all_opportunities = []
    page = 1
    max_pages = 5  # Limit to prevent excessive scraping
    
    while page <= max_pages:
        url = f"{self.base_url}?page={page}"
        html = self.fetch(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        opportunities = self._parse_opportunities(soup)
        all_opportunities.extend(opportunities)
        
        if not opportunities or not self._has_next_page(soup):
            break
            
        page += 1
        time.sleep(1)  # Be respectful
    
    return all_opportunities
```

---

## Challenge 6: Scheduled Reliability

### Problem
Scheduled scrapers need to:
- Run reliably without manual intervention
- Handle failures gracefully
- Not interfere with each other
- Provide monitoring/visibility

### Solution Implemented
- **APScheduler**: Background scheduler with interval-based jobs.
- **Isolation**: Each scraper runs independently; failures don't affect others.
- **Monitoring Service**: Tracks execution time, success rate, and error messages.
- **Database Locking**: SQLite uses single-process mode to avoid lock conflicts.

### Code Example
```python
# From scheduler/jobs.py
def start_scheduler():
    if not scheduler.get_jobs():
        scheduler.add_job(
            scrape_all_job, 
            "interval", 
            minutes=1, 
            id="scrape_all", 
            replace_existing=True
        )
    if not scheduler.running:
        scheduler.start()
```

---

## Challenge 7: Data Validation & Quality

### Problem
Scraped data can be:
- Incomplete (missing fields)
- Malformed (invalid dates, URLs)
- Inconsistent (different formats)

### Solution Implemented
- **Marshmallow Schemas**: Define expected data structure with validation rules.
- **Default Values**: Provide sensible defaults for missing fields.
- **Type Conversion**: Convert strings to proper types (dates, integers).
- **Error Logging**: Log validation errors for debugging.

### Code Example
```python
# From validators/opportunity_validator.py
class OpportunitySchema(Schema):
    title = fields.Str(required=True, validate=Length(min=5, max=300))
    opportunity_type = fields.Str(required=True, validate=OneOf(['grant', 'accelerator', 'program', 'conference']))
    source_link = fields.URL(required=True)
    deadline = fields.Str(allow_none=True)
    funding_range = fields.Str(allow_none=True)
    
    class Meta:
        unknown = EXCLUDE
```

---

## Challenge 8: Real-time Updates vs. Performance

### Problem
- Users want real-time data
- Frequent scraping can overwhelm servers
- Database writes can be slow with large datasets

### Solution Implemented
- **Polling Interval**: Set to 1 minute as a balance between freshness and server load.
- **Incremental Updates**: Only process new/changed data.
- **Caching**: Cache frequently accessed data to reduce database queries.
- **Async Processing**: Consider moving to async processing for better performance.

---

## Future Improvements

1. **Headless Browser Integration**: Use Selenium or Playwright for JavaScript-heavy sites
2. **Distributed Scraping**: Run scrapers on multiple machines/containers
3. **Machine Learning**: Use ML to better classify and tag opportunities
4. **API Integration**: Direct API integrations where available instead of scraping
5. **Rate Limiting Detection**: Automatically detect and adapt to rate limits
6. **Proxy Rotation**: Use proxy services to avoid IP blocking
7. **Change Detection**: Monitor source sites for structural changes and alert

---

## Lessons Learned

1. **Always Respect robots.txt**: Check and respect robots.txt files
2. **Be Conservative with Scraping**: Start slow, increase gradually
3. **Monitor Everything**: Log execution times, errors, and success rates
4. **Design for Failure**: Assume scrapers will fail and handle gracefully
5. **Normalize Early**: Normalize data as soon as it's scraped
6. **Test Isolation**: Test each scraper independently
7. **Document Selectors**: Keep track of CSS selectors for easy updates
8. **Version Control**: Track scraper code changes alongside data schema changes

---

## Sources Scraped

| Source | Type | Challenges | Status |
|--------|------|------------|--------|
| Startup India | Government | Static HTML, pagination | ✅ Working |
| MeITY | Government | Complex structure, nested elements | ✅ Working |
| NITI Aayog | Government | Dynamic content, slow loading | ✅ Working |
| MSME | Government | Large dataset, rate limiting | ✅ Working |
| F6S | Platform | JavaScript-heavy, authentication | ⚠️ Limited |
| Eventbrite | Platform | Pagination, infinite scroll | ⚠️ Limited |

---

## Monitoring & Alerts

The system includes:
- **Health Check Endpoint**: `/api/health` - Overall system status
- **Stats Endpoint**: `/api/stats` - Current opportunity counts
- **Monitoring Endpoint**: `/api/monitoring/stats` - Scraper execution metrics
- **Email Alerts**: Configurable email notifications for failures (optional)

---

## Conclusion

Building a reliable web scraping system requires careful consideration of:
- Technical challenges (anti-scraping, dynamic content)
- Ethical considerations (respecting robots.txt, rate limits)
- Data quality (validation, normalization, deduplication)
- Operational concerns (scheduling, monitoring, error handling)

This project demonstrates a production-grade approach to web scraping with proper error handling, monitoring, and data quality controls.
