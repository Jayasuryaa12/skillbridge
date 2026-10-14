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
