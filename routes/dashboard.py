from flask import Blueprint, render_template, request

from models.opportunity import Opportunity

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def dashboard():
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

    items = query.order_by(Opportunity.created_at.desc()).limit(100).all()
    return render_template("dashboard.html", items=items, q=q, source=source, kind=kind)
