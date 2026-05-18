from marshmallow import ValidationError

from models.opportunity import Opportunity
from services.duplicate_service import DuplicateService
from services.opportunity_service import OpportunityService
from services.tagging_service import TaggingService
from services.email_service import EmailService, EmailConfig
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
                # Apply AI auto-tagging
                record["tags"] = TaggingService.generate_tags(
                    record.get("title", ""),
                    record.get("eligibility", ""),
                    record.get("tags", "")
                )
                
                # Classify startup stage
                record["startup_stage"] = TaggingService.classify_stage(
                    record.get("title", ""),
                    record.get("eligibility", "")
                )
                
                # Detect location type
                record["location_type"] = TaggingService.detect_location_type(
                    record.get("location", "")
                )
                
                # Detect funding range
                record["funding_range"] = TaggingService.detect_funding_range(
                    record.get("title", ""),
                    record.get("eligibility", "")
                )
                
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
        
        # Send email alert if new opportunities were added
        if inserted > 0:
            sources = list(set(record.get("source_platform", "") for record in records))
            EmailService.send_new_opportunities_alert(inserted, sources)
        
        return {"inserted": inserted, "failed": failed}
