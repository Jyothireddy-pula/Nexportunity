from flask import Blueprint, render_template
from models.opportunity import Opportunity
from collections import Counter

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/analytics")
def analytics():
    """Display analytics dashboard with source distribution and statistics"""
    
    # Get all opportunities
    opportunities = Opportunity.query.all()
    
    # Source distribution
    source_counts = Counter([opp.source_platform for opp in opportunities])
    
    # Opportunity type distribution
    type_counts = Counter([opp.opportunity_type for opp in opportunities])
    
    # Location type distribution
    location_counts = Counter([opp.location_type or "unknown" for opp in opportunities])
    
    # Startup stage distribution
    stage_counts = Counter([opp.startup_stage or "unknown" for opp in opportunities])
    
    # Tag distribution
    all_tags = []
    for opp in opportunities:
        all_tags.extend([tag.strip() for tag in opp.tags.split(",")])
    tag_counts = Counter(all_tags)
    
    # Recent activity (last 10)
    recent = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(10).all()
    
    return render_template("analytics.html",
                         total=len(opportunities),
                         source_counts=dict(source_counts),
                         type_counts=dict(type_counts),
                         location_counts=dict(location_counts),
                         stage_counts=dict(stage_counts),
                         tag_counts=dict(tag_counts.most_common(20)),
                         recent=recent)
