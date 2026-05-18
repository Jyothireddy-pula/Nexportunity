from marshmallow import Schema, fields, validate


class OpportunitySchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=300))
    normalized_title = fields.Str(required=True, validate=validate.Length(min=3, max=300))
    opportunity_type = fields.Str(required=True)
    organizer = fields.Str(required=True)
    location = fields.Str(required=True)
    eligibility = fields.Str(required=True)
    deadline = fields.Str(allow_none=True)
    source_platform = fields.Str(required=True)
    source_link = fields.Url(required=True)
    tags = fields.Str(required=True)
    startup_stage = fields.Str(allow_none=True)
    location_type = fields.Str(allow_none=True)
    funding_range = fields.Str(allow_none=True)
    row_hash = fields.Str(required=True, validate=validate.Length(equal=64))
