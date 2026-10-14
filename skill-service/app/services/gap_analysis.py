"""
Rule-Based Skill Gap Analysis Engine
=====================================
Transparent, deterministic algorithm — no ML required.

Algorithm
---------
For each skill required by the target career:

  MATCHED    : student_level >= required_level
  DEVELOPING : 0 < student_level < required_level   → reports gap_size
  MISSING    : student does not have the skill at all → gap_size = required_level

Readiness score (0–100)
  = [ Σ(importance × min(student_level / required_level, 1.0)) / Σ(importance) ] × 100

Per-category scores   : same formula scoped to each skill category → radar chart data.
Priority list         : MISSING first, then DEVELOPING; both sorted by importance DESC,
                        then gap_size DESC.
"""

from typing import Any


def analyze_skill_gap(
    student: dict[str, Any],
    career: dict[str, Any],
) -> dict[str, Any]:
    """
    Perform a complete skill-gap analysis between *student* and *career*.

    Parameters
    ----------
    student : dict
        Full student document from MongoDB (with ``skills`` list).
    career : dict
        Full career document from MongoDB (with ``required_skills`` list).

    Returns
    -------
    dict
        Keys: student_id, career_id, career_title, readiness_score,
              summary, matched, developing, missing,
              category_scores (for radar chart), priority_list.
    """
    # ── Build student skill lookup: lowercase name → level ─────────────────
    student_skill_map: dict[str, int] = {
        s["name"].strip().lower(): s["level"]
        for s in student.get("skills", [])
    }

    required_skills: list[dict] = career.get("required_skills", [])

    matched: list[dict] = []
    developing: list[dict] = []
    missing: list[dict] = []

    # Per-category accumulators
    cat_weighted: dict[str, float] = {}
    cat_importance: dict[str, float] = {}

    total_weighted: float = 0.0
    total_importance: float = 0.0

    for req in required_skills:
        skill_name: str = req["name"]
        req_level: int = req["required_level"]
        importance: int = req["importance"]
        category: str = req.get("category", "General")
        prerequisites: list[str] = req.get("prerequisites", [])

        student_level: int = student_skill_map.get(skill_name.strip().lower(), 0)

        # Contribution to overall readiness
        contribution = importance * min(student_level / req_level, 1.0)
        total_weighted += contribution
        total_importance += importance

        # Contribution to category score
        cat_weighted[category] = cat_weighted.get(category, 0.0) + contribution
        cat_importance[category] = cat_importance.get(category, 0.0) + importance

        base: dict[str, Any] = {
            "skill": skill_name,
            "required_level": req_level,
            "importance": importance,
            "category": category,
            "prerequisites": prerequisites,
            "student_level": student_level,
        }

        if student_level >= req_level:
            matched.append({**base, "status": "MATCHED"})

        elif student_level > 0:
            gap_size = req_level - student_level
            developing.append({**base, "gap_size": gap_size, "status": "DEVELOPING"})

        else:
            missing.append({**base, "gap_size": req_level, "status": "MISSING"})

    # ── Overall readiness score ────────────────────────────────────────────
    readiness_score: float = 0.0
    if total_importance > 0:
        readiness_score = round((total_weighted / total_importance) * 100, 2)

    # ── Per-category scores (for radar chart) ─────────────────────────────
    category_scores: list[dict] = [
        {
            "category": cat,
            "score": round((cat_weighted[cat] / cat_importance[cat]) * 100, 2)
            if cat_importance[cat] > 0
            else 0.0,
            "total_skills": sum(
                1 for r in required_skills if r.get("category", "General") == cat
            ),
        }
        for cat in cat_weighted
    ]

    # ── Priority list: MISSING first, then DEVELOPING ─────────────────────
    # Within each group: importance DESC, gap_size DESC
    def _priority_key(skill: dict) -> tuple:
        return (-skill["importance"], -skill["gap_size"])

    missing_sorted = sorted(missing, key=_priority_key)
    developing_sorted = sorted(developing, key=_priority_key)

    priority_list: list[dict] = []
    for rank, skill in enumerate(missing_sorted + developing_sorted, start=1):
        priority_list.append(
            {
                "rank": rank,
                "skill": skill["skill"],
                "status": skill["status"],
                "importance": skill["importance"],
                "current_level": skill["student_level"],
                "target_level": skill["required_level"],
                "gap_size": skill["gap_size"],
                "category": skill["category"],
                "action": (
                    "Learn from scratch"
                    if skill["status"] == "MISSING"
                    else "Improve existing knowledge"
                ),
            }
        )

    return {
        "student_id": str(student["_id"]),
        "career_id": str(career["_id"]),
        "career_title": career["title"],
        "readiness_score": readiness_score,
        "readiness_label": _readiness_label(readiness_score),
        "summary": {
            "total_required": len(required_skills),
            "matched": len(matched),
            "developing": len(developing),
            "missing": len(missing),
        },
        "matched": matched,
        "developing": developing,
        "missing": missing,
        "category_scores": category_scores,
        "priority_list": priority_list,
    }


def _readiness_label(score: float) -> str:
    """Convert a numeric readiness score to a human-readable label."""
    if score >= 85:
        return "Job Ready"
    if score >= 65:
        return "Almost Ready"
    if score >= 40:
        return "In Progress"
    if score >= 20:
        return "Early Stage"
    return "Getting Started"
