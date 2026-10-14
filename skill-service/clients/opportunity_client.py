"""
HTTP Client for Opportunity Service.
===================================
Robust, resilient REST client communicating with opportunity-service.
Features:
- Requests Session with connection pooling
- Configurable timeout (connect 3s, read 8s)
- Automatic retry with exponential backoff on 5xx and network dropouts (max 2 retries)
- Optional shared secret authentication via X-Service-Key header
- Outbound request logging with execution duration and status code
- Strict error classification for graceful degradation vs upstream failures
"""

import logging
import os
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


# ── Custom Exceptions ──────────────────────────────────────────────────────────

class OpportunityClientError(Exception):
    """Base exception for all opportunity client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class OpportunityServiceUnavailableError(OpportunityClientError):
    """Raised when opportunity-service cannot be reached or times out."""
    pass


class OpportunityInvalidResponseError(OpportunityClientError):
    """Raised when opportunity-service returns malformed JSON or an unexpected error payload."""
    pass


class OpportunityUnauthorizedError(OpportunityClientError):
    """Raised when opportunity-service rejects the request due to invalid X-Service-Key."""
    pass


# ── Opportunity Client Implementation ─────────────────────────────────────────

class OpportunityClient:
    """Inter-service HTTP client for querying opportunity-service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        service_key: Optional[str] = None,
        timeout: tuple[float, float] = (3.0, 8.0),
        max_retries: int = 2,
    ):
        self.base_url = (base_url or os.getenv("OPPORTUNITY_SERVICE_URL", "http://localhost:5002")).rstrip("/")
        self.service_key = service_key or os.getenv("INTER_SERVICE_KEY")
        self.timeout = timeout

        self.session = requests.Session()

        # Retry strategy: retry on network connection errors, read timeouts, and 500, 502, 503, 504
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
            allowed_methods=["GET", "POST", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        if self.service_key:
            self.session.headers["X-Service-Key"] = self.service_key

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute an outbound HTTP request with timing, logging, and error categorization."""
        url = f"{self.base_url}{path}"
        start_time = time.perf_counter()

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "OUTBOUND %s %s -> %d (%s ms)",
                method,
                url,
                response.status_code,
                duration_ms,
            )

            # 1. Check for Unauthorized (401)
            if response.status_code == 401:
                raise OpportunityUnauthorizedError(
                    "Opportunity Service rejected request: unauthorized or missing service key.",
                    status_code=401,
                )

            # 2. Check for 5xx (failed after retries)
            if response.status_code in (500, 502, 503, 504):
                raise OpportunityServiceUnavailableError(
                    f"Opportunity Service returned status {response.status_code} after retries.",
                    status_code=response.status_code,
                )

            # 3. Parse JSON response safely
            try:
                data = response.json()
            except Exception as json_err:
                raise OpportunityInvalidResponseError(
                    f"Invalid JSON received from Opportunity Service: {json_err}",
                    status_code=502,
                )

            # 4. Check API envelope success flag
            if not response.ok or not data.get("success", False):
                err_msg = (
                    data.get("error", {}).get("message")
                    if isinstance(data, dict)
                    else "Upstream request failed"
                )
                raise OpportunityInvalidResponseError(
                    f"Opportunity Service error: {err_msg}",
                    status_code=response.status_code,
                    details=data.get("error") if isinstance(data, dict) else None,
                )

            return data

        except (requests.ConnectionError, requests.Timeout) as net_err:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(
                "OUTBOUND %s %s FAILED connection/timeout after %s ms: %s",
                method,
                url,
                duration_ms,
                net_err,
            )
            raise OpportunityServiceUnavailableError(
                f"Opportunity Service unavailable at {self.base_url}: {net_err}",
                status_code=503,
            ) from net_err

    def match_opportunities(
        self,
        skills: list[dict[str, Any]],
        missing_skills: list[str],
        developing_skills: list[str],
        limit: int = 10,
        types: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Request ranked opportunity recommendations based on student skills and gaps.
        """
        payload: dict[str, Any] = {
            "skills": skills,
            "missing_skills": missing_skills,
            "developing_skills": developing_skills,
            "limit": limit,
        }
        if types:
            payload["types"] = types

        result = self._request("POST", "/api/opportunities/match", json_data=payload)
        return result.get("data", [])

    def get_opportunity_stats(self) -> dict[str, Any]:
        """Fetch aggregated opportunity statistics."""
        result = self._request("GET", "/api/opportunities/stats")
        return result.get("data", {})

    def check_health(self) -> dict[str, Any]:
        """
        Ping opportunity-service /api/health and measure round-trip latency.
        Returns a structured reachability status dict.
        """
        start_time = time.perf_counter()
        try:
            result = self._request("GET", "/api/health")
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "healthy",
                "reachable": True,
                "latency_ms": duration_ms,
                "data": result.get("data", {}),
            }
        except OpportunityServiceUnavailableError as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "unavailable",
                "reachable": False,
                "latency_ms": duration_ms,
                "error": str(exc),
            }
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "degraded",
                "reachable": False,
                "latency_ms": duration_ms,
                "error": str(exc),
            }
