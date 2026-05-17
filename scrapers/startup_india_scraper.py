from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.text import build_hash, normalize_title


class StartupIndiaScraper(BaseScraper):
    SOURCE = "Startup India"
    URL = "https://www.startupindia.gov.in/content/sih/en/search.html"

    def scrape(self):
        html = self.fetch(self.URL)
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for i, card in enumerate(soup.select("a")[:10]):
            title = card.get_text(strip=True)
            href = card.get("href")
            if not title or not href:
                continue
            link = href if href.startswith("http") else f"https://www.startupindia.gov.in{href}"
            n = normalize_title(title)
            results.append({"title": title, "normalized_title": n, "opportunity_type": "program", "organizer": "Startup India", "location": "India", "eligibility": "See source", "deadline": None, "source_platform": self.SOURCE, "source_link": link, "tags": "startup,india", "row_hash": build_hash(n, self.SOURCE, link)})
        return results
