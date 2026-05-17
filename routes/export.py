import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Blueprint, jsonify

from models.opportunity import Opportunity

export_bp = Blueprint("export", __name__)


def _rows():
    return [{"title": o.title, "type": o.opportunity_type, "organizer": o.organizer, "location": o.location, "eligibility": o.eligibility, "deadline": o.deadline, "source_platform": o.source_platform, "source_link": o.source_link, "tags": o.tags} for o in Opportunity.query.all()]


@export_bp.get("/api/export/json")
def export_json():
    rows = _rows()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path("exports") / f"opportunities_{ts}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return jsonify({"file": str(path), "count": len(rows)})


@export_bp.get("/api/export/csv")
def export_csv():
    rows = _rows()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path("exports") / f"opportunities_{ts}.csv"
    path.parent.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return jsonify({"file": str(path), "count": len(rows)})
