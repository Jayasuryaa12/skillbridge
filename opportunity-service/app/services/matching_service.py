"""
Opportunity Matching Engine — opportunity-service.
===================================================
Rule-based, explainable matching of student profiles and skill gap data
against experiential opportunities.

Algorithm
---------
For each open, non-expired opportunity:
1. Weighted skill overlap:
   - Required skills met by student level count fully (1.0).
   - Developing skills (student_level > 0 but < min_level) count proportionally (ratio * 0.75).
   - Skills absent from student profile count as 0.0 towards overlap.
2. Gap-targeting bonus:
   - +12 bonus if the opportunity teaches a target career MISSING skill.
   - +6 bonus if the opportunity reinforces a DEVELOPING skill.
3. High-gap penalty:
   - -8 penalty if an unlearned skill has min_level >= 3 (demanding barrier).
   - -5 penalty if a developing skill has a gap >= 2.
4. Explainable summary:
   - Returns matched_skills[], skills_to_learn[], and human-readable reason.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo.database import Database

from app.utils.helpers import serialize_doc


def _is_expired(deadline_str: Optional[str]) -> bool:
    """Return True if the ISO deadline string is strictly in the past."""
    if not deadline_str:
        return False
    try:
        # Standardize 'Z' to UTC offset
        clean_str = deadline_str.replace("Z", "+00:00")
        deadline_dt = datetime.fromisoformat(clean_str)
        now = datetime.now(timezone.utc)
        return deadline_dt < now
    except Exception:
        # If deadline parsing fails, don't prematurely exclude
        return False


def match_opportunities(
    db: Database,
    student_skills: list[dict],
    missing_skills: list[str],
    developing_skills: list[str],
    limit: int = 10,
    types: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """
    Rank open opportunities based on student skill overlap, career gap alignment,
    and difficulty prerequisites.
    """
    query: dict[str, Any] = {"status": "open"}
    if types:
        query["type"] = {"$in": types}

    cursor = db.opportunities.find(query)

    # Normalized lookup maps (lowercase keys)
    skill_map: dict[str, int] = {
        s["name"].strip().lower(): int(s["level"]) for s in student_skills if "name" in s and "level" in s
    }
    missing_set: set[str] = {m.strip().lower() for m in missing_skills}
    developing_set: set[str] = {d.strip().lower() for d in developing_skills}

    results: list[dict[str, Any]] = []

    for opp in cursor:
        if _is_expired(opp.get("deadline")):
            continue

        req_skills: list[dict] = opp.get("required_skills", [])
        matched_skills: list[str] = []
        skills_to_learn: list[str] = []

        overlap_score = 0.0
        bonus = 0.0
        penalty = 0.0

        if not req_skills:
            # Universal entry (no specific skill gates)
            final_score = 75.0
            reason = "Open opportunity with no prerequisite barriers; great entry-level learning."
        else:
            for req in req_skills:
                raw_name = req.get("name", "").strip()
                name_key = raw_name.lower()
                min_level = int(req.get("min_level", 1))
                stu_level = skill_map.get(name_key, 0)

                if stu_level >= min_level:
                    overlap_score += 1.0
                    matched_skills.append(f"{raw_name} (Lv. {stu_level})")
                elif stu_level > 0:
                    overlap_score += (stu_level / min_level) * 0.75
                    matched_skills.append(f"{raw_name} (developing: Lv. {stu_level}/{min_level})")
                    if min_level - stu_level >= 2:
                        penalty += 5.0
                else:
                    skills_to_learn.append(raw_name)
                    if name_key in missing_set:
                        bonus += 20.0
                    elif name_key in developing_set:
                        bonus += 10.0
                    elif min_level >= 3:
                        penalty += 8.0

            base_fraction = overlap_score / len(req_skills)
            matched_base = 15.0 if matched_skills else 0.0
            raw_score = (base_fraction * 60.0) + matched_base + min(30.0, bonus) - min(30.0, penalty)

            # Cap bonuses / perfect match rewards
            if len(matched_skills) == len(req_skills) and not skills_to_learn:
                raw_score = max(raw_score, 95.0)

            final_score = round(max(5.0, min(100.0, raw_score)), 1)

            # Build explainable narrative
            reason_parts: list[str] = []
            if matched_skills:
                reason_parts.append(f"Matches {len(matched_skills)}/{len(req_skills)} required skills")
            if bonus > 0:
                reason_parts.append("targets your career gap skills")
            if skills_to_learn:
                reason_parts.append(f"helps you learn {', '.join(skills_to_learn[:2])}")
            if penalty > 0:
                reason_parts.append("has steep skill requirements")

            reason = ", ".join(reason_parts).capitalize() + "." if reason_parts else "Relevant learning opportunity."

        results.append(
            {
                "opportunity": serialize_doc(opp),
                "match_score": final_score,
                "matched_skills": matched_skills,
                "skills_to_learn": skills_to_learn,
                "reason": reason,
            }
        )

    # Sort descending by match_score
    results.sort(key=lambda item: item["match_score"], reverse=True)
    return results[:limit]
