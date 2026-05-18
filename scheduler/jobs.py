from apscheduler.schedulers.background import BackgroundScheduler
import time

from services.pipeline_service import PipelineService
from services.monitoring_service import MonitoringService, ScraperStatus
from scrapers.eventbrite_scraper import EventbriteScraper
from scrapers.f6s_scraper import F6SScraper
from scrapers.startup_india_scraper import StartupIndiaScraper
from scrapers.meity_scraper import MeITYScraper
from scrapers.niti_aayog_scraper import NitiAayogScraper
from scrapers.msme_scraper import MSMEScraper

scheduler = BackgroundScheduler()


def scrape_all_job():
    pipeline = PipelineService()
    records = []
    
    scrapers = [
        (StartupIndiaScraper(), "Startup India"),
        (MeITYScraper(), "MeITY"),
        (NitiAayogScraper(), "NITI Aayog"),
        (MSMEScraper(), "MSME"),
        (F6SScraper(), "F6S"),
        (EventbriteScraper(), "Eventbrite")
    ]
    
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
            duration = time.time() - start_time
            MonitoringService.record_execution(
                source=source_name,
                status=ScraperStatus.ERROR,
                items_scraped=0,
                duration_seconds=duration,
                error_message=str(e)
            )
            continue
    
    return pipeline.process(records)


def start_scheduler():
    if not scheduler.get_jobs():
        scheduler.add_job(scrape_all_job, "interval", minutes=1, id="scrape_all", replace_existing=True)
    if not scheduler.running:
        scheduler.start()
