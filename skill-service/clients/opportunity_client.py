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
        timeout: Optional[tuple[float, float]] = None,
        max_retries: int = 2,
        cold_start_timeout: float = 45.0,
    ):
        self.base_url = (base_url or os.getenv("OPPORTUNITY_SERVICE_URL", "http://localhost:5002")).rstrip("/")
        self.service_key = service_key or os.getenv("INTER_SERVICE_KEY")
        
        # Use provided timeout or cloud-friendly defaults: 15s connect, 25s read
        if timeout is not None:
            self.timeout = timeout
        else:
            connect_t = float(os.getenv("OPPORTUNITY_CONNECT_TIMEOUT", "15.0"))
            read_t = float(os.getenv("OPPORTUNITY_READ_TIMEOUT", "25.0"))
            self.timeout = (connect_t, read_t)

        self.cold_start_timeout = float(os.getenv("COLD_START_TIMEOUT", str(cold_start_timeout)))
        self._in_cold_start_retry = False

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

    def wake_up(self, max_wait: Optional[float] = None) -> bool:
        """
        Send a wake-up ping to Opportunity Service with an extended timeout.
        Handles Render free-tier cold starts when spinning up from idle state.
        """
        wait_timeout = max_wait or self.cold_start_timeout
        logger.info("Pinging Opportunity Service for cold-start wake-up: %s (timeout=%ss)...", self.base_url, wait_timeout)
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=(wait_timeout, wait_timeout))
            if resp.status_code == 200:
                logger.info("Opportunity Service is awake and operational.")
                return True
            resp2 = self.session.get(f"{self.base_url}/api/health", timeout=(wait_timeout, wait_timeout))
            return resp2.status_code == 200
        except Exception as exc:
            logger.warning("Wake-up ping failed or timed out: %s", exc)
            return False

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
            # Render cold-start retry strategy: attempt wake-up ping and retry once
            if not self._in_cold_start_retry:
                try:
                    self._in_cold_start_retry = True
                    logger.info("Triggering wake-up strategy for potential Render free-tier cold start...")
                    if self.wake_up(max_wait=self.cold_start_timeout):
                        logger.info("Opportunity Service awakened! Retrying original request: %s %s", method, url)
                        return self._request(method, path, json_data=json_data, params=params)
                except Exception as retry_exc:
                    logger.warning("Cold-start wake-up retry attempt failed: %s", retry_exc)
                finally:
                    self._in_cold_start_retry = False

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
        clean_skills = [
            {"name": s["name"], "level": int(s.get("level", 1))}
            for s in skills
            if isinstance(s, dict) and "name" in s
        ]
        payload: dict[str, Any] = {
            "skills": clean_skills,
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
