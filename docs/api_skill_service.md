# Skill Service API Specification (Port 5001)

Base URL: `http://localhost:5001`

All responses follow the standard JSON envelope with `success`, `data`, and `error`.

---

## 1. System Health
### `GET /api/health`
Checks service connectivity and database responsiveness.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "service": "skill-service",
    "status": "healthy",
    "mongodb": "connected",
    "version": "1.0.0"
  }
### `GET /api/system/status`
Returns composite service health plus real-time reachability and round-trip latency to Opportunity Service.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "timestamp": "2026-10-14T21:40:00Z",
    "skill_service": {
      "service": "skill-service",
      "status": "healthy",
      "database": "connected"
    },
    "opportunity_service": {
      "status": "healthy",
      "reachable": true,
      "latency_ms": 14.8,
      "url": "http://localhost:5002"
    }
  }
}
```

---

## 2. Students API
### `GET /api/students`
Paginated search and filter across students.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `page_size` (int, default: 20, max: 100)
  - `search` (string): Text search across `name`, `college`, `department`.
  - `department` (string): Case-insensitive match.
  - `year` (int: 1–4): Exact match.
  - `career_goal` (string): Filter by Career ObjectId.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "660c1d2e8f1b2c001a1e4f11",
      "name": "Alice Sharma",
      "email": "alice.sharma@example.com",
      "college": "IIT Bombay",
      "department": "Computer Science",
      "year": 3,
      "career_goal": "660c1d2e8f1b2c001a1e4f01",
      "skills": [
        { "name": "python", "level": 4, "updated_at": "2026-10-14T10:00:00Z" }
      ],
      "created_at": "2026-10-14T10:00:00Z",
      "updated_at": "2026-10-14T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1 }
}
```

### `POST /api/students`
Create a new student.
- **Body**:
```json
{
  "name": "Alice Sharma",
  "email": "alice.sharma@example.com",
  "college": "IIT Bombay",
  "department": "Computer Science",
  "year": 3,
  "career_goal": "660c1d2e8f1b2c001a1e4f01",
  "skills": [
    { "name": "python", "level": 4 }
  ]
}
```
- **Response `201 Created`**

### `GET /api/students/<id>`
Retrieve a student by ObjectId.

### `PUT /api/students/<id>`
Update student profile fields (`name`, `college`, `department`, `year`, `career_goal`).

### `DELETE /api/students/<id>`
Delete a student record.

---

## 3. Student Skills Sub-resource
### `POST /api/students/<id>/skills`
Add or update a skill in the student's profile.
- **Body**:
```json
{
  "name": "docker",
  "level": 3
}
```

### `PUT /api/students/<id>/skills/<skill_name>`
Update the proficiency level (1–5) for a specific skill.
- **Body**:
```json
{
  "level": 4
}
```

### `DELETE /api/students/<id>/skills/<skill_name>`
Remove a skill from the student's skill list.

---

## 4. Skill Gap Analysis & Roadmap
### `GET /api/students/<id>/skill-gap`
Execute deterministic rule-based gap analysis comparing the student's skills against their target career goal.
- **Query Parameter (Optional)**: `career_id` (defaults to student's saved `career_goal`).
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "student_id": "660c1d2e8f1b2c001a1e4f11",
    "career_id": "660c1d2e8f1b2c001a1e4f01",
    "career_title": "AI/ML Engineer",
    "readiness_score": 68.5,
    "summary": { "matched": 4, "developing": 3, "missing": 2 },
    "matched": [...],
    "developing": [...],
    "missing": [...],
    "category_scores": [
      { "category": "Core ML", "score": 75.0, "total_skills": 4 }
    ],
    "priority_list": [
      {
        "rank": 1,
        "skill": "PyTorch",
        "status": "MISSING",
        "importance": 5,
        "current_level": 0,
        "target_level": 4,
        "gap_size": 4
      }
    ]
  }
}
```

### `POST /api/students/<id>/roadmap/generate`
Generate (or regenerate) an ordered learning roadmap with topological prerequisite resolution and attached learning resources.
- **Response `201 Created` / `200 OK`**:
```json
{
  "success": true,
  "data": {
    "student_id": "...",
    "career_id": "...",
    "stages": [
      {
        "order": 1,
        "skill": "Python",
        "current_level": 2,
        "target_level": 4,
        "gap_size": 2,
        "importance": 5,
        "estimated_weeks": 4,
        "status": "not_started",
        "resources": [
          { "title": "Python Docs", "url": "https://docs.python.org/3/", "type": "documentation" }
        ]
      }
    ],
    "total_estimated_weeks": 16,
    "generated_at": "2026-10-14T10:00:00Z"
  }
}
```

### `GET /api/students/<id>/roadmap`
Retrieve the active roadmap.

### `PATCH /api/students/<id>/roadmap/stages/<order>`
Update status of a roadmap stage.
- **Body**:
```json
{
  "status": "in_progress"
}
```
Valid statuses: `not_started`, `in_progress`, `completed`.

---

## 5. Inter-Service Recommendations & Dashboard
### `GET /api/students/<id>/recommendations`
Queries the student profile, executes gap analysis, and queries Opportunity Service `/api/opportunities/match` to retrieve ranked opportunities.
- **Query Parameters**:
  - `limit` (int, default: 10, max: 50)
  - `types` (comma-separated): `internship`, `project`, `hackathon`, `workshop`
- **Graceful Degradation**: If Opportunity Service is unreachable, returns `200 OK` with `recommendations: []`, local gap analysis intact, and `opportunity_service: {status: "unavailable"}`.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "student": {
      "_id": "660c1d2e8f1b2c001a1e4f11",
      "name": "Alice Sharma",
      "email": "alice.sharma@example.com"
    },
    "career": {
      "_id": "660c1d2e8f1b2c001a1e4f01",
      "title": "AI/ML Engineer"
    },
    "skill_gap_summary": {
      "readiness_score": 68.5,
      "matched_count": 4,
      "developing_count": 3,
      "missing_count": 2
    },
    "recommendations": [
      {
        "opportunity": {
          "_id": "opp001",
          "title": "Machine Learning Research Intern",
          "type": "internship"
        },
        "match_score": 88.0,
        "matched_skills": ["Python (Lv. 4)"],
        "skills_to_learn": ["PyTorch"],
        "reason": "Matches 1/2 required skills, targets your career gap skills."
      }
    ],
    "opportunity_service": {
      "status": "available"
    }
  }
}
```

### `GET /api/students/<id>/dashboard`
Single unified endpoint for the frontend dashboard combining readiness score, radar category breakdown, skill gap counts, top 5 priority skills, roadmap progress %, top 5 opportunity recommendations, and opportunity catalog stats.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "student": { "_id": "...", "name": "Alice Sharma" },
    "career": { "_id": "...", "title": "AI/ML Engineer" },
    "readiness_score": 68.5,
    "category_scores": [
      { "category": "Core ML", "score": 75.0, "total_skills": 4 }
    ],
    "skill_counts": {
      "matched": 4,
      "developing": 3,
      "missing": 2
    },
    "top_priority_skills": [ ... ],
    "roadmap_progress_percentage": 50.0,
    "top_recommendations": [ ... ],
    "opportunity_stats": {
      "total": 32,
      "by_type": { "internship": 10, "hackathon": 8, "project": 8, "workshop": 6 }
    },
    "opportunity_service": { "status": "available" }
  }
}
```

---

## 5. Careers API
### `GET /api/careers`
List career pathways with optional `search` and `category` filters.

### `POST /api/careers`
Create a new career with required skills, prerequisites, and importance weights.

### `GET /api/careers/<id>`
Retrieve career profile.

### `PUT /api/careers/<id>`
Update career details.

### `DELETE /api/careers/<id>`
Delete a career pathway.
