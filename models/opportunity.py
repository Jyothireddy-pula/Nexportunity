from app.extensions import db
from database.base import TimestampMixin


class Opportunity(TimestampMixin, db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    normalized_title = db.Column(db.String(300), nullable=False, index=True)
    opportunity_type = db.Column(db.String(80), nullable=False, index=True)
    organizer = db.Column(db.String(200), nullable=False, default="Unknown")
    location = db.Column(db.String(120), nullable=False, default="Global")
    eligibility = db.Column(db.Text, nullable=False, default="Not specified")
    deadline = db.Column(db.String(80), nullable=True, index=True)
    source_platform = db.Column(db.String(80), nullable=False, index=True)
    source_link = db.Column(db.String(500), nullable=False, unique=True)
    tags = db.Column(db.String(300), nullable=False, default="startup")
    row_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)

    __table_args__ = (
        db.UniqueConstraint("normalized_title", "source_platform", name="uq_title_source"),
    )
