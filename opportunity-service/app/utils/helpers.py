"""
Shared utility helpers for opportunity-service.
"""

import re
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId


def is_valid_object_id(id_str: Any) -> bool:
    try:
        ObjectId(str(id_str))
        return True
    except (InvalidId, TypeError, ValueError):
        return False


def serialize_doc(doc: Optional[dict]) -> Optional[dict]:
    """Recursively convert a MongoDB document to a JSON-serialisable dict."""
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
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return serialize_doc(value)
    return value


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_pagination(
    args: dict,
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    try:
        page = max(1, int(args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = min(max_size, max(1, int(args.get("page_size", default_size))))
    except (ValueError, TypeError):
        page_size = default_size
    return page, page_size
