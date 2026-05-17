from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.text import build_hash, normalize_title


class EventbriteScraper(BaseScraper):
    SOURCE = "Eventbrite"
    URL = "https://www.eventbrite.com/d/online/startup/"

    def scrape(self):
        html = self.fetch(self.URL)
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for i, card in enumerate(soup.select("a")[:10]):
            title = card.get_text(strip=True)
            href = card.get("href")
            if not title or not href:
                continue
            link = href if href.startswith("http") else f"https://www.eventbrite.com{href}"
            n = normalize_title(title)
            results.append({"title": title, "normalized_title": n, "opportunity_type": "event", "organizer": "Eventbrite", "location": "Online", "eligibility": "Open", "deadline": None, "source_platform": self.SOURCE, "source_link": link, "tags": "startup,event", "row_hash": build_hash(n, self.SOURCE, link)})
        return results
