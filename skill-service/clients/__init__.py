"""Clients package for skill-service."""

from clients.opportunity_client import (
    OpportunityClient,
    OpportunityClientError,
    OpportunityInvalidResponseError,
    OpportunityServiceUnavailableError,
    OpportunityUnauthorizedError,
)

__all__ = [
    "OpportunityClient",
    "OpportunityClientError",
    "OpportunityInvalidResponseError",
    "OpportunityServiceUnavailableError",
    "OpportunityUnauthorizedError",
]
