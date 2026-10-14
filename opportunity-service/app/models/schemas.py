"""Marshmallow validation schemas for opportunity-service."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema


class RequiredSkillOpportunitySchema(Schema):
    """A skill requirement attached to an opportunity."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    min_level = fields.Int(required=True, validate=validate.Range(min=1, max=5))

    class Meta:
        unknown = EXCLUDE


class CreateOpportunitySchema(Schema):
    """Validate the body of POST /api/opportunities."""

    title = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    type = fields.Str(
        required=True,
        validate=validate.OneOf(["project", "hackathon", "internship", "workshop"]),
    )
    organization = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    required_skills = fields.List(
        fields.Nested(RequiredSkillOpportunitySchema), load_default=[]
    )
    difficulty = fields.Str(
        required=True,
        validate=validate.OneOf(["beginner", "intermediate", "advanced"]),
    )
    mode = fields.Str(
        required=True,
        validate=validate.OneOf(["online", "offline", "hybrid"]),
    )
    location = fields.Str(load_default=None, allow_none=True)
    start_date = fields.Str(load_default=None, allow_none=True)   # ISO date string
    deadline = fields.Str(load_default=None, allow_none=True)      # ISO date string
    duration = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    stipend = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    prize = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    apply_url = fields.Str(required=True, validate=validate.Length(min=5, max=500))
    tags = fields.List(fields.Str(validate=validate.Length(max=50)), load_default=[])
    status = fields.Str(
        load_default="open",
        validate=validate.OneOf(["open", "closed"]),
    )

    class Meta:
        unknown = EXCLUDE


class UpdateOpportunitySchema(Schema):
    """Validate the body of PUT /api/opportunities/<id>. All fields optional."""

    title = fields.Str(validate=validate.Length(min=2, max=200))
    type = fields.Str(validate=validate.OneOf(["project", "hackathon", "internship", "workshop"]))
    organization = fields.Str(validate=validate.Length(min=2, max=200))
    description = fields.Str(validate=validate.Length(min=10, max=5000))
    required_skills = fields.List(fields.Nested(RequiredSkillOpportunitySchema))
    difficulty = fields.Str(validate=validate.OneOf(["beginner", "intermediate", "advanced"]))
    mode = fields.Str(validate=validate.OneOf(["online", "offline", "hybrid"]))
    location = fields.Str(allow_none=True)
    start_date = fields.Str(allow_none=True)
    deadline = fields.Str(allow_none=True)
    duration = fields.Str(allow_none=True, validate=validate.Length(max=100))
    stipend = fields.Str(allow_none=True, validate=validate.Length(max=100))
    prize = fields.Str(allow_none=True, validate=validate.Length(max=100))
    apply_url = fields.Str(validate=validate.Length(min=5, max=500))
    tags = fields.List(fields.Str(validate=validate.Length(max=50)))
    status = fields.Str(validate=validate.OneOf(["open", "closed"]))

    class Meta:
        unknown = EXCLUDE

    @validates_schema
    def at_least_one_field(self, data: dict, **kwargs) -> None:
        if not data:
            raise ValidationError("At least one field must be provided for update.")
