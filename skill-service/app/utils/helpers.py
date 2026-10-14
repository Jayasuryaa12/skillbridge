"""
Shared utility helpers for skill-service.
"""

import re
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId


# ── ObjectId validation ────────────────────────────────────────────────────

def is_valid_object_id(id_str: Any) -> bool:
    """Return True if *id_str* is a valid 24-hex-char MongoDB ObjectId."""
    try:
        ObjectId(str(id_str))
        return True
    except (InvalidId, TypeError, ValueError):
        return False


# ── Document serialisation ─────────────────────────────────────────────────

def serialize_doc(doc: Optional[dict]) -> Optional[dict]:
    """
    Recursively convert a MongoDB document to a JSON-serialisable dict.

    * ObjectId  → str
    * datetime  → ISO-8601 string
    * lists and nested dicts are processed recursively.
    """
    if doc is None:
        return None
    result: dict = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [_serialize_value(v) for v in value]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value
    return result


def _serialize_value(value: Any) -> Any:
    """Serialize a single value that may be inside a list."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return serialize_doc(value)
    return value


# ── Time helpers ───────────────────────────────────────────────────────────

def now_utc() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


# ── String helpers ─────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """
    Convert *text* to a URL-safe slug.
    Example: "AI/ML Engineer" → "ai-ml-engineer"
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)       # remove special chars except hyphens
    text = re.sub(r"[\s_]+", "-", text)         # spaces/underscores → hyphen
    text = re.sub(r"-{2,}", "-", text)           # collapse multiple hyphens
    text = re.sub(r"^-+|-+$", "", text)          # strip leading/trailing hyphens
    return text


# ── Pagination ─────────────────────────────────────────────────────────────

def parse_pagination(
    args: dict,
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """
    Parse `page` and `page_size` query parameters safely.

    Returns:
        (page, page_size) with sane bounds applied.
    """
    try:
        page = max(1, int(args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = min(max_size, max(1, int(args.get("page_size", default_size))))
    except (ValueError, TypeError):
        page_size = default_size

    return page, page_size
