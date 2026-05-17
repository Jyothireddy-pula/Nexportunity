import random

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class BaseScraper:
    HEADERS = [
        {"User-Agent": "Mozilla/5.0"},
        {"User-Agent": "Chrome/124.0"},
        {"User-Agent": "Safari/537.36"},
    ]

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def fetch(self, url: str) -> str:
        response = self.session.get(url, headers=random.choice(self.HEADERS), timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def scrape(self) -> list[dict]:
        raise NotImplementedError
