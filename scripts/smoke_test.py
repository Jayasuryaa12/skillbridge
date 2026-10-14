#!/usr/bin/env python3
"""
SkillBridge Smoke Test Suite
============================
Automated post-deployment verification script.
Tests:
  1. Skill Service health check (/health & /api/health)
  2. Opportunity Service health check (/health & /api/health)
  3. Inter-service connectivity (/api/system/status)
  4. Student CRUD lifecycle (Create, Read, Update Skill, Delete)
  5. Multi-service recommendation pipeline (/recommendations)

Usage:
  python scripts/smoke_test.py --skill-url https://skill-svc.onrender.com --opp-url https://opp-svc.onrender.com
  python scripts/smoke_test.py  # Defaults to localhost:5001 & localhost:5002
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Optional


class TerminalColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_banner():
    print(f"{TerminalColors.BOLD}{TerminalColors.OKCYAN}")
    print("=" * 72)
    print("  SKILLBRIDGE POST-DEPLOYMENT SMOKE VERIFICATION SUITE")
    print("=" * 72)
    print(f"{TerminalColors.ENDC}")


def make_request(
    url: str,
    method: str = "GET",
    data: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any], float]:
    """Execute HTTP request and return (status_code, response_json, duration_ms)."""
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    start = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            raw = resp.read().decode("utf-8")
            try:
                res_json = json.loads(raw)
            except Exception:
                res_json = {"raw": raw}
            return resp.status, res_json, duration_ms
    except urllib.error.HTTPError as err:
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        raw = err.read().decode("utf-8")
        try:
            res_json = json.loads(raw)
        except Exception:
            res_json = {"raw": raw}
        return err.code, res_json, duration_ms
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        return 0, {"error": str(exc)}, duration_ms


def run_smoke_tests(skill_url: str, opp_url: str, secret_key: Optional[str] = None) -> bool:
    skill_url = skill_url.rstrip("/")
    opp_url = opp_url.rstrip("/")

    results = []

    print(f"Target Skill Service:       {skill_url}")
    print(f"Target Opportunity Service: {opp_url}")
    if secret_key:
        print(f"Shared Inter-Service Key:   {'*' * 8}")
    print("-" * 72)

    # ── Test 1: Skill Service Health Check ──────────────────────────────────────
    code, data, latency = make_request(f"{skill_url}/health")
    if code != 200:
        # Fallback to /api/health
        code, data, latency = make_request(f"{skill_url}/api/health")

    is_ok = code == 200 and data.get("data", {}).get("database") == "connected"
    results.append({
        "name": "Skill Service /health",
        "endpoint": f"{skill_url}/health",
        "passed": is_ok,
        "code": code,
        "latency": f"{latency} ms",
        "notes": f"DB: {data.get('data', {}).get('database', 'unknown')}",
    })

    # ── Test 2: Opportunity Service Health Check ────────────────────────────────
    code, data, latency = make_request(f"{opp_url}/health")
    if code != 200:
        code, data, latency = make_request(f"{opp_url}/api/health")

    is_ok = code == 200 and data.get("data", {}).get("database") == "connected"
    results.append({
        "name": "Opportunity Service /health",
        "endpoint": f"{opp_url}/health",
        "passed": is_ok,
        "code": code,
        "latency": f"{latency} ms",
        "notes": f"DB: {data.get('data', {}).get('database', 'unknown')}",
    })

    # ── Test 3: Inter-Service System Status ────────────────────────────────────
    code, data, latency = make_request(f"{skill_url}/api/system/status")
    opp_status = data.get("data", {}).get("opportunity_service", {})
    reachable = opp_status.get("reachable", False) or opp_status.get("status") == "healthy"
    is_ok = code == 200 and reachable
    results.append({
        "name": "Inter-Service Status",
        "endpoint": f"{skill_url}/api/system/status",
        "passed": is_ok,
        "code": code,
        "latency": f"{latency} ms",
        "notes": f"Opp status: {opp_status.get('status', 'unknown')}",
    })

    # Fetch a career ID so student can have a career_goal for recommendations
    career_id = None
    _, careers_data, _ = make_request(f"{skill_url}/api/careers?limit=1")
    if careers_data.get("data") and len(careers_data["data"]) > 0:
        career_id = careers_data["data"][0]["_id"]

    # ── Test 4: Student CRUD Round Trip ─────────────────────────────────────────
    test_email = f"smoke_test_{int(time.time())}@college.edu"
    test_payload = {
        "name": "Smoke Test Student",
        "email": test_email,
        "college": "Test Tech Institute",
        "department": "Computer Science",
        "year": 3,
        "career_goal": career_id,
        "skills": [{"name": "Python", "level": 3}],
    }

    # Step 4a: Create student
    code, create_data, latency = make_request(f"{skill_url}/api/students", method="POST", data=test_payload)
    student_id = create_data.get("data", {}).get("_id")
    crud_passed = code == 201 and bool(student_id)

    if crud_passed:
        # Step 4b: Read student
        read_code, _, _ = make_request(f"{skill_url}/api/students/{student_id}")
        # Step 4c: Update student
        update_code, _, _ = make_request(
            f"{skill_url}/api/students/{student_id}",
            method="PUT",
            data={"department": "Software Engineering"},
        )
        # Step 4d: Add skill
        skill_code, _, _ = make_request(
            f"{skill_url}/api/students/{student_id}/skills",
            method="POST",
            data={"name": "Docker", "level": 2},
        )
        crud_passed = read_code == 200 and update_code == 200 and skill_code in (200, 201)

    results.append({
        "name": "Student CRUD Lifecycle",
        "endpoint": f"{skill_url}/api/students",
        "passed": crud_passed,
        "code": code,
        "latency": f"{latency} ms",
        "notes": f"Created & verified id={student_id[:8]}..." if student_id else "Creation failed",
    })

    # ── Test 5: Recommendations Pipeline ───────────────────────────────────────
    rec_passed = False
    rec_notes = "No student available"
    rec_target_id = student_id

    if not rec_target_id:
        # Fallback to existing student
        _, st_list, _ = make_request(f"{skill_url}/api/students?limit=1")
        if st_list.get("data") and len(st_list["data"]) > 0:
            rec_target_id = st_list["data"][0]["_id"]

    if rec_target_id:
        req_url = f"{skill_url}/api/students/{rec_target_id}/recommendations"
        if career_id:
            req_url += f"?career_id={career_id}"
        code, rec_data, latency = make_request(req_url)
        rec_list = rec_data.get("data", {}).get("recommendations", [])
        rec_passed = code == 200 and isinstance(rec_list, list)
        count = len(rec_list)
        top_score = rec_list[0].get("match_score", 0) if count > 0 else 0
        rec_notes = f"{count} matches, top score: {top_score}%"

    results.append({
        "name": "Recommendation Engine",
        "endpoint": f"{skill_url}/api/students/.../recommendations",
        "passed": rec_passed,
        "code": code if rec_target_id else 0,
        "latency": f"{latency} ms" if rec_target_id else "N/A",
        "notes": rec_notes,
    })

    # Clean up test student if created
    if student_id:
        make_request(f"{skill_url}/api/students/{student_id}", method="DELETE")

    # ── Print Formatted Results Table ──────────────────────────────────────────
    print(f"\n{'TEST SUITE COMPONENT':<30} | {'STATUS':<8} | {'CODE':<5} | {'LATENCY':<10} | {'NOTES'}")
    print("-" * 84)

    all_passed = True
    for res in results:
        status_str = "[PASS]" if res["passed"] else "[FAIL]"
        if not res["passed"]:
            all_passed = False
        print(f"{res['name']:<30} | {status_str:<8} | {res['code']:<5} | {res['latency']:<10} | {res['notes']}")

    print("-" * 84)
    if all_passed:
        print("\n[SUCCESS] ALL SMOKE TESTS PASSED! Microservices deployment is fully operational.\n")
    else:
        print("\n[FAILED] SOME SMOKE TESTS FAILED. Inspect logs above for troubleshooting.\n")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="SkillBridge Microservices Deployment Smoke Test")
    parser.add_argument(
        "--skill-url",
        default=os.getenv("SKILL_SERVICE_URL", "http://localhost:5001"),
        help="Base URL of deployed Skill Service",
    )
    parser.add_argument(
        "--opp-url",
        default=os.getenv("OPPORTUNITY_SERVICE_URL", "http://localhost:5002"),
        help="Base URL of deployed Opportunity Service",
    )
    parser.add_argument(
        "--key",
        default=os.getenv("INTER_SERVICE_KEY"),
        help="Inter-service shared authentication key",
    )

    args = parser.parse_args()
    print_banner()

    success = run_smoke_tests(args.skill_url, args.opp_url, args.key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
