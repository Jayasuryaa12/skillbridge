"""
Roadmap Generation Service
===========================
Converts the output of gap_analysis.analyze_skill_gap() into a structured,
stage-by-stage learning roadmap.

Algorithm
---------
1. Collect all MISSING + DEVELOPING skills from the gap analysis.
2. Topological sort based on the ``prerequisites`` field (Kahn's algorithm).
   Skills with no prerequisites (or prerequisites already met) come first.
3. Within the same topological level, sort by importance DESC then gap_size DESC.
4. Assign each skill to a numbered stage with:
   - Estimated weeks  (rule-based look-up table)
   - 2–3 learning resources from the resource catalog JSON file
5. Return the complete roadmap document ready for MongoDB upsert.
"""

import json
import os
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

# ── Resource catalog ───────────────────────────────────────────────────────
_CATALOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "resources_catalog.json"
)


def _load_catalog() -> dict[str, list[dict]]:
    """Load the resource catalog from disk. Returns empty dict on failure."""
    try:
        with open(_CATALOG_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_CATALOG: dict[str, list[dict]] = _load_catalog()


def _resources_for(skill_name: str, count: int = 3) -> list[dict]:
    """
    Look up resources for *skill_name* in the catalog.
    Falls back to a generic web-search resource if not found.
    """
    key = skill_name.strip().lower()

    # Exact match
    if key in _CATALOG:
        return _CATALOG[key][:count]

    # Partial match (e.g. "TensorFlow" matches "tensorflow/pytorch")
    for cat_key, resources in _CATALOG.items():
        if key in cat_key or cat_key in key:
            return resources[:count]

    # Generic fallback
    safe_name = skill_name.replace(" ", "+")
    return [
        {
            "title": f"Learn {skill_name} — freeCodeCamp",
            "url": f"https://www.freecodecamp.org/news/search/?query={safe_name}",
            "type": "article",
        },
        {
            "title": f"{skill_name} Full Course — YouTube",
            "url": f"https://www.youtube.com/results?search_query={safe_name}+full+course",
            "type": "video",
        },
    ][:count]


# ── Weeks estimation ───────────────────────────────────────────────────────
_WEEKS_TABLE: dict[int, int] = {1: 2, 2: 4, 3: 7, 4: 11, 5: 16}


def _estimate_weeks(current_level: int, target_level: int) -> int:
    """Estimate learning weeks from *current_level* to *target_level*."""
    gap = max(0, target_level - current_level)
    return _WEEKS_TABLE.get(gap, gap * 3)


# ── Topological sort ───────────────────────────────────────────────────────

def _topo_sort(skills: list[dict]) -> list[dict]:
    """
    Sort *skills* so that prerequisites always precede dependents.
    Implements Kahn's BFS algorithm.  Cycles are broken gracefully —
    any remaining nodes after BFS are appended at the end.

    Parameters
    ----------
    skills : list[dict]
        Each dict must have ``"skill"`` (str) and ``"prerequisites"`` (list[str]).

    Returns
    -------
    list[dict]
        Topologically ordered copy of *skills*.
    """
    names_in_list: set[str] = {s["skill"].lower() for s in skills}
    skill_by_name: dict[str, dict] = {s["skill"].lower(): s for s in skills}

    in_degree: dict[str, int] = {s["skill"].lower(): 0 for s in skills}
    graph: dict[str, list[str]] = defaultdict(list)

    for skill in skills:
        name = skill["skill"].lower()
        for prereq in skill.get("prerequisites", []):
            p = prereq.lower()
            if p in names_in_list:          # only track internal deps
                graph[p].append(name)
                in_degree[name] += 1

    # Seed queue with zero-in-degree nodes
    queue: deque[str] = deque(n for n, deg in in_degree.items() if deg == 0)
    result: list[dict] = []

    while queue:
        node = queue.popleft()
        result.append(skill_by_name[node])
        for neighbour in graph[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # Append any cycle survivors (should be rare with well-formed data)
    seen = {s["skill"].lower() for s in result}
    for skill in skills:
        if skill["skill"].lower() not in seen:
            result.append(skill)

    return result


# ── Public API ─────────────────────────────────────────────────────────────

def generate_roadmap(
    student: dict[str, Any],
    career: dict[str, Any],
    gap_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a complete learning roadmap from the gap analysis result.

    Parameters
    ----------
    student      : Full student document.
    career       : Full career document.
    gap_analysis : Output of ``gap_analysis.analyze_skill_gap()``.

    Returns
    -------
    dict
        Ready-to-upsert roadmap document including ``stages`` list.
    """
    to_learn: list[dict] = gap_analysis["missing"] + gap_analysis["developing"]

    if not to_learn:
        return {
            "student_id": str(student["_id"]),
            "career_id": str(career["_id"]),
            "stages": [],
            "total_estimated_weeks": 0,
            "generated_at": datetime.now(timezone.utc),
            "message": "🎉 No skill gaps found — student already meets all requirements!",
        }

    # Topological sort, then secondary sort by importance DESC, gap_size DESC
    topo_ordered = _topo_sort(to_learn)

    # Group into topological layers for fine-grained secondary ordering
    # (Skills are already topo-ordered; do a stable sort within each "layer"
    #  by building layers based on prerequisite satisfaction.)
    ordered = _sort_within_topo(topo_ordered)

    stages: list[dict] = []
    for order, skill in enumerate(ordered, start=1):
        current_level = skill.get("student_level", 0)
        target_level = skill["required_level"]

        stages.append(
            {
                "order": order,
                "skill": skill["skill"],
                "current_level": current_level,
                "target_level": target_level,
                "gap_size": target_level - current_level,
                "importance": skill["importance"],
                "category": skill.get("category", "General"),
                "estimated_weeks": _estimate_weeks(current_level, target_level),
                "resources": _resources_for(skill["skill"], count=3),
                "status": "not_started",
            }
        )

    return {
        "student_id": str(student["_id"]),
        "career_id": str(career["_id"]),
        "stages": stages,
        "total_estimated_weeks": sum(s["estimated_weeks"] for s in stages),
        "generated_at": datetime.now(timezone.utc),
    }


def _sort_within_topo(skills: list[dict]) -> list[dict]:
    """
    Secondary sort: within skills at the same topological depth,
    order by importance DESC then gap_size DESC.
    Preserves the topo order as the primary constraint.
    """
    # We traverse in topo order and build depth-groups based on
    # when all prerequisites have been "placed".
    placed: set[str] = set()
    layers: list[list[dict]] = []
    remaining = list(skills)

    while remaining:
        layer: list[dict] = []
        still_waiting: list[dict] = []
        for skill in remaining:
            prereqs = {p.lower() for p in skill.get("prerequisites", [])}
            skill_names_in_list = {s["skill"].lower() for s in skills}
            internal_prereqs = prereqs & skill_names_in_list
            if internal_prereqs.issubset(placed):
                layer.append(skill)
            else:
                still_waiting.append(skill)

        if not layer:
            # Break a potential cycle — force-place first remaining skill
            layer.append(still_waiting.pop(0))
            remaining = still_waiting
        else:
            remaining = still_waiting

        # Sort layer: importance DESC, gap_size DESC
        layer.sort(key=lambda s: (-s["importance"], -s.get("gap_size", 0)))
        layers.append(layer)
        placed |= {s["skill"].lower() for s in layer}

    return [s for layer in layers for s in layer]
