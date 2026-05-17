from apscheduler.schedulers.background import BackgroundScheduler

from services.pipeline_service import PipelineService
from scrapers.eventbrite_scraper import EventbriteScraper
from scrapers.f6s_scraper import F6SScraper
from scrapers.startup_india_scraper import StartupIndiaScraper

scheduler = BackgroundScheduler()


def scrape_all_job():
    pipeline = PipelineService()
    records = []
    for scraper in (StartupIndiaScraper(), F6SScraper(), EventbriteScraper()):
        try:
            records.extend(scraper.scrape())
        except Exception:
            continue
    return pipeline.process(records)


def start_scheduler():
    if not scheduler.get_jobs():
        scheduler.add_job(scrape_all_job, "interval", minutes=60, id="scrape_all", replace_existing=True)
    if not scheduler.running:
        scheduler.start()
