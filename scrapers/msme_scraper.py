from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.text import build_hash, normalize_title


class MSMEScraper(BaseScraper):
    """Scraper for MSME schemes and opportunities"""
    SOURCE = "MSME"
    URL = "https://msme.gov.in/schemes"

    def scrape(self):
        html = self.fetch(self.URL)
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # Try to find scheme cards
        cards = soup.select(".scheme-card, .card, .scheme-item, .views-row, .field-title")
        
        if not cards:
            cards = soup.select("a")
        
        for i, card in enumerate(cards[:30]):
            try:
                # Try multiple ways to get title
                title = None
                if card.select_one(".title, .scheme-title, h3, h4, .field-title"):
                    title_elem = card.select_one(".title, .scheme-title, h3, h4, .field-title")
                    title = title_elem.get_text(strip=True)
                else:
                    title = card.get_text(strip=True)
                
                # Try multiple ways to get link
                href = card.get("href")
                if not href and card.select_one("a"):
                    href = card.select_one("a").get("href")
                
                if not title or not href or len(title) < 10:
                    continue
                
                # Ensure link is absolute
                if href.startswith("/"):
                    link = f"https://msme.gov.in{href}"
                elif not href.startswith("http"):
                    link = f"https://msme.gov.in/{href}"
                else:
                    link = href
                
                # Extract location if available
                location = "India"
                if card.select_one(".location, .state"):
                    location = card.select_one(".location, .state").get_text(strip=True)
                
                # Extract deadline if available
                deadline = None
                if card.select_one(".deadline, .date, .last-date"):
                    deadline = card.select_one(".deadline, .date, .last-date").get_text(strip=True)
                
                n = normalize_title(title)
                results.append({
                    "title": title,
                    "normalized_title": n,
                    "opportunity_type": "grant",
                    "organizer": "Ministry of MSME",
                    "location": location,
                    "eligibility": "See source",
                    "deadline": deadline,
                    "source_platform": self.SOURCE,
                    "source_link": link,
                    "tags": "government,india,msme,small-business",
                    "row_hash": build_hash(n, self.SOURCE, link)
                })
            except Exception as e:
                continue
        
        return results
