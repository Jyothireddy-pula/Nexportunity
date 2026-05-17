from marshmallow import ValidationError

from models.opportunity import Opportunity
from services.duplicate_service import DuplicateService
from services.opportunity_service import OpportunityService
from validators.opportunity_validator import OpportunitySchema


class PipelineService:
    def __init__(self, duplicate_threshold: int = 90):
        self.schema = OpportunitySchema()
        self.dupes = DuplicateService(threshold=duplicate_threshold)

    def process(self, records: list[dict]) -> dict:
        inserted = 0
        failed = []
        existing = [
            {
                "normalized_title": row.normalized_title,
                "source_link": row.source_link,
                "row_hash": row.row_hash,
            }
            for row in Opportunity.query.all()
        ]
        for record in records:
            try:
                clean = self.schema.load(record)
                if self.dupes.is_duplicate(clean, existing):
                    continue
                created = OpportunityService.create(clean)
                existing.append({"normalized_title": created.normalized_title, "source_link": created.source_link, "row_hash": created.row_hash})
                inserted += 1
            except ValidationError as exc:
                failed.append({"record": record, "error": exc.messages})
            except Exception as exc:
                failed.append({"record": record, "error": str(exc)})
        return {"inserted": inserted, "failed": failed}
