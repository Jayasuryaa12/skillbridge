"""Marshmallow validation schemas for skill-service."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema


# ── Sub-schemas ────────────────────────────────────────────────────────────

class SkillEntrySchema(Schema):
    """A single skill entry in a student's skill list."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    level = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = EXCLUDE


class RequiredSkillSchema(Schema):
    """A skill requirement in a career document."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    required_level = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    importance = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    prerequisites = fields.List(fields.Str(), load_default=[])
    category = fields.Str(required=True, validate=validate.Length(min=1, max=60))

    class Meta:
        unknown = EXCLUDE


# ── Student schemas ────────────────────────────────────────────────────────

class CreateStudentSchema(Schema):
    """Validate the body of POST /api/students."""

    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    college = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    department = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    year = fields.Int(required=True, validate=validate.Range(min=1, max=4))
    career_goal = fields.Str(load_default=None, allow_none=True)
    skills = fields.List(fields.Nested(SkillEntrySchema), load_default=[])

    class Meta:
        unknown = EXCLUDE


class UpdateStudentSchema(Schema):
    """Validate the body of PUT /api/students/<id>. All fields optional."""

    name = fields.Str(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    college = fields.Str(validate=validate.Length(min=2, max=200))
    department = fields.Str(validate=validate.Length(min=2, max=100))
    year = fields.Int(validate=validate.Range(min=1, max=4))
    career_goal = fields.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @validates_schema
    def at_least_one_field(self, data: dict, **kwargs) -> None:  # noqa: D401
        if not data:
            raise ValidationError("At least one field must be provided for update.")


class AddSkillSchema(Schema):
    """Validate the body of POST /api/students/<id>/skills."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    level = fields.Int(required=True, validate=validate.Range(min=1, max=5))

    class Meta:
        unknown = EXCLUDE


class UpdateSkillSchema(Schema):
    """Validate the body of PUT /api/students/<id>/skills/<name>."""

    level = fields.Int(required=True, validate=validate.Range(min=1, max=5))

    class Meta:
        unknown = EXCLUDE


# ── Career schemas ─────────────────────────────────────────────────────────

class CreateCareerSchema(Schema):
    """Validate the body of POST /api/careers."""

    title = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    slug = fields.Str(load_default=None, allow_none=True)
    description = fields.Str(required=True, validate=validate.Length(min=10, max=3000))
    category = fields.Str(required=True, validate=validate.Length(min=2, max=60))
    required_skills = fields.List(
        fields.Nested(RequiredSkillSchema),
        required=True,
        validate=validate.Length(min=1, max=30),
    )

    class Meta:
        unknown = EXCLUDE


class UpdateCareerSchema(Schema):
    """Validate the body of PUT /api/careers/<id>. All fields optional."""

    title = fields.Str(validate=validate.Length(min=2, max=100))
    description = fields.Str(validate=validate.Length(min=10, max=3000))
    category = fields.Str(validate=validate.Length(min=2, max=60))
    required_skills = fields.List(
        fields.Nested(RequiredSkillSchema),
        validate=validate.Length(min=1, max=30),
    )

    class Meta:
        unknown = EXCLUDE

    @validates_schema
    def at_least_one_field(self, data: dict, **kwargs) -> None:
        if not data:
            raise ValidationError("At least one field must be provided for update.")


# ── Roadmap schemas ────────────────────────────────────────────────────────

class UpdateStageStatusSchema(Schema):
    """Validate the body of PATCH /api/students/<id>/roadmap/stages/<order>."""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(["not_started", "in_progress", "completed"]),
    )

    class Meta:
        unknown = EXCLUDE
