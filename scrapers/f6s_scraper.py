from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.text import build_hash, normalize_title


class F6SScraper(BaseScraper):
    SOURCE = "F6S"
    URL = "https://www.f6s.com/programs"

    def scrape(self):
        html = self.fetch(self.URL)
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for i, card in enumerate(soup.select("a")[:10]):
            title = card.get_text(strip=True)
            href = card.get("href")
            if not title or not href:
                continue
            link = href if href.startswith("http") else f"https://www.f6s.com{href}"
            n = normalize_title(title)
            results.append({"title": title, "normalized_title": n, "opportunity_type": "accelerator", "organizer": "F6S", "location": "Global", "eligibility": "See source", "deadline": None, "source_platform": self.SOURCE, "source_link": link, "tags": "startup,f6s", "row_hash": build_hash(n, self.SOURCE, link)})
        return results
