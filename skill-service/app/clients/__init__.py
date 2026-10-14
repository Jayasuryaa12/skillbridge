"""App clients package shim."""

import sys
from pathlib import Path

# Ensure root clients directory is on path
SERVICE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

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
