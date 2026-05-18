from flask import Blueprint, jsonify, request
from models.opportunity import Opportunity
from services.pipeline_service import PipelineService
from services.monitoring_service import MonitoringService
from scrapers.eventbrite_scraper import EventbriteScraper
from scrapers.f6s_scraper import F6SScraper
from scrapers.startup_india_scraper import StartupIndiaScraper
from scrapers.meity_scraper import MeITYScraper
from scrapers.niti_aayog_scraper import NitiAayogScraper
from scrapers.msme_scraper import MSMEScraper

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/opportunities", methods=["GET"])
def get_opportunities():
    """Get all opportunities with optional filtering"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    q = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()
    kind = request.args.get("type", "").strip()
    
    query = Opportunity.query
    if q:
        query = query.filter(Opportunity.title.ilike(f"%{q}%"))
    if source:
        query = query.filter(Opportunity.source_platform == source)
    if kind:
        query = query.filter(Opportunity.opportunity_type == kind)
    
    pagination = query.order_by(Opportunity.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "data": [{
            "id": item.id,
            "title": item.title,
            "opportunity_type": item.opportunity_type,
            "organizer": item.organizer,
            "location": item.location,
            "eligibility": item.eligibility,
            "deadline": item.deadline.isoformat() if item.deadline else None,
            "source_platform": item.source_platform,
            "source_link": item.source_link,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat()
        } for item in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    })


@api_bp.route("/api/opportunities/<int:id>", methods=["GET"])
def get_opportunity(id):
    """Get a single opportunity by ID"""
    item = Opportunity.query.get_or_404(id)
    return jsonify({
        "id": item.id,
        "title": item.title,
        "opportunity_type": item.opportunity_type,
        "organizer": item.organizer,
        "location": item.location,
        "eligibility": item.eligibility,
        "deadline": item.deadline.isoformat() if item.deadline else None,
        "source_platform": item.source_platform,
        "source_link": item.source_link,
        "tags": item.tags,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat()
    })


@api_bp.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    """Manually trigger scraping from all sources"""
    try:
        pipeline = PipelineService()
        records = []
        
        scrapers = [
            StartupIndiaScraper(),
            MeITYScraper(),
            NitiAayogScraper(),
            MSMEScraper(),
            F6SScraper(),
            EventbriteScraper()
        ]
        
        for scraper in scrapers:
            try:
                records.extend(scraper.scrape())
            except Exception as e:
                continue
        
        result = pipeline.process(records)
        return jsonify({
            "status": "success",
            "inserted": result["inserted"],
            "failed": len(result["failed"])
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route("/api/stats", methods=["GET"])
def get_stats():
    """Get statistics about opportunities"""
    total = Opportunity.query.count()
    grants = Opportunity.query.filter_by(opportunity_type="grant").count()
    accelerators = Opportunity.query.filter_by(opportunity_type="accelerator").count()
    programs = Opportunity.query.filter_by(opportunity_type="program").count()
    
    # Source distribution
    sources = {}
    for item in Opportunity.query.all():
        source = item.source_platform
        sources[source] = sources.get(source, 0) + 1
    
    return jsonify({
        "total": total,
        "grants": grants,
        "accelerators": accelerators,
        "programs": programs,
        "sources": sources
    })


@api_bp.route("/api/monitoring/stats", methods=["GET"])
def get_monitoring_stats():
    """Get scraper monitoring statistics"""
    hours = request.args.get("hours", 24, type=int)
    stats = MonitoringService.get_all_stats(hours=hours)
    failures = MonitoringService.get_recent_failures(hours=hours)
    
    return jsonify({
        "source_stats": stats,
        "recent_failures": failures,
        "hours_analyzed": hours
    })
