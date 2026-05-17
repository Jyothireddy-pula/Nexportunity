from app.extensions import db
from models.opportunity import Opportunity


class OpportunityService:
    @staticmethod
    def create(data: dict) -> Opportunity:
        item = Opportunity(**data)
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def list_all(limit: int = 100):
        return Opportunity.query.order_by(Opportunity.created_at.desc()).limit(limit).all()
