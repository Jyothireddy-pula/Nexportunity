from app import create_app
from services.pipeline_service import PipelineService
from scrapers.eventbrite_scraper import EventbriteScraper
from scrapers.f6s_scraper import F6SScraper
from scrapers.startup_india_scraper import StartupIndiaScraper
from scrapers.meity_scraper import MeITYScraper
from scrapers.niti_aayog_scraper import NitiAayogScraper
from scrapers.msme_scraper import MSMEScraper

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        print("Starting manual scrape...")
        pipeline = PipelineService()
        records = []
        
        scrapers = [
            ("Startup India", StartupIndiaScraper()),
            ("MeITY", MeITYScraper()),
            ("NITI Aayog", NitiAayogScraper()),
            ("MSME", MSMEScraper()),
            ("F6S", F6SScraper()),
            ("Eventbrite", EventbriteScraper())
        ]
        
        for name, scraper in scrapers:
            try:
                print(f"Scraping {name}...")
                scraped = scraper.scrape()
                print(f"  Found {len(scraped)} items")
                records.extend(scraped)
            except Exception as e:
                print(f"  Error: {e}")
        
        print(f"\nProcessing {len(records)} total records...")
        result = pipeline.process(records)
        print(f"Inserted: {result['inserted']}")
        print(f"Failed: {len(result['failed'])}")
        
        if result['failed']:
            print("\nFailed records:")
            for fail in result['failed']:
                print(f"  - {fail['record']}: {fail['error']}")
        
        print("\nDone! Check the dashboard at http://127.0.0.1:5000")
