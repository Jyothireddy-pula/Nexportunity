import pytest

pytest.importorskip("flask")
pytest.importorskip("flask_sqlalchemy")
pytest.importorskip("sqlalchemy")
pytest.importorskip("marshmallow")
pytest.importorskip("rapidfuzz")

from app import create_app
from app.extensions import db
from models.opportunity import Opportunity
from services.pipeline_service import PipelineService
from utils.text import build_hash, normalize_title


def sample_record(title: str, link: str) -> dict:
    norm = normalize_title(title)
    return {
        "title": title,
        "normalized_title": norm,
        "opportunity_type": "accelerator",
        "organizer": "Unit Test Org",
        "location": "Remote",
        "eligibility": "Open",
        "deadline": None,
        "source_platform": "test-source",
        "source_link": link,
        "tags": "test,startup",
        "row_hash": build_hash(norm, "test-source", link),
    }


def test_health_route():
    app = create_app("testing")
    with app.test_client() as c:
        res = c.get("/api/health")
        assert res.status_code == 200
        assert res.json["status"] == "ok"


def test_pipeline_inserts_and_blocks_duplicates():
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()

        pipeline = PipelineService(duplicate_threshold=90)
        first = sample_record("AI Accelerator Cohort 2026", "https://example.com/1")
        dup = sample_record("AI Accelerator Cohort 2026", "https://example.com/1")
        fuzzy_dup = sample_record("AI  Accelerator  Cohort - 2026", "https://example.com/2")

        result = pipeline.process([first, dup, fuzzy_dup])

        assert result["inserted"] == 1
        assert len(result["failed"]) == 0
        assert Opportunity.query.count() == 1


def test_stats_endpoint():
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(
            Opportunity(**sample_record("Grant Program", "https://example.com/g1"), opportunity_type="grant")
        )
        db.session.add(
            Opportunity(**sample_record("Accel Program", "https://example.com/a1"), opportunity_type="accelerator")
        )
        db.session.commit()

    with app.test_client() as c:
        res = c.get("/api/stats")
        assert res.status_code == 200
        assert res.json["total"] == 2
        assert res.json["grants"] == 1
        assert res.json["accelerators"] == 1
