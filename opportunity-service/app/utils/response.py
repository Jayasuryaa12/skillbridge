"""
Standardised JSON response helpers for opportunity-service.
Mirrors the same envelope contract used by skill-service.
"""

from typing import Any

from flask import jsonify


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
):
    return (
        jsonify({"success": True, "message": message, "data": data}),
        status_code,
    )


def created_response(data: Any = None, message: str = "Created successfully"):
    return success_response(data=data, message=message, status_code=201)


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
):
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
