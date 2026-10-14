"""
Standardised JSON response helpers for skill-service.

Every response produced by this service must go through one of these helpers
to guarantee a consistent envelope shape:

Success:  { "success": true,  "data": ..., "message": "...", "pagination": ... }
Error:    { "success": false, "error": { "code": "...", "message": "...", "details": ... } }
"""

from typing import Any, Optional

from flask import jsonify


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
):
    """Return a standard success JSON response."""
    return (
        jsonify({"success": True, "message": message, "data": data}),
        status_code,
    )


def created_response(data: Any = None, message: str = "Created successfully"):
    """Shorthand for HTTP 201 Created."""
    return success_response(data=data, message=message, status_code=201)


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
):
    """Return a paginated success response with pagination metadata."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }
        ),
        200,
    )


def error_response(
    code: str,
    message: str,
    details: Any = None,
    status_code: int = 400,
):
    """Return a standard error JSON response."""
    return (
        jsonify(
            {
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                },
            }
        ),
        status_code,
    )
