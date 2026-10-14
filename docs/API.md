# SkillBridge API Reference Specification 📖

SkillBridge microservices expose clean, RESTful APIs formatted with standard JSON envelopes.

- **Skill Service (Port 5001 / Cloud)**: Owns students, skills, careers, learning roadmaps, and gap analysis.
- **Opportunity Service (Port 5002 / Cloud)**: Owns opportunities catalog, filters, and rule-based matching.
- **Interactive Swagger UI**: Available at `/apidocs/` on both services.

---

## Global Response Envelope

All API endpoints return standard response wrappers:

### Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable error description",
    "details": { ... }
  }
}
```

---

## Comprehensive Endpoints Matrix

| Service | Method | Endpoint | Description | Status Codes |
|---|---|---|---|---|
| **Skill** | `GET` | `/health` / `/api/health` | Lightweight service health and MongoDB ping | `200`, `503` |
| **Skill** | `GET` | `/api/system/status` | Composite status with Opportunity Service reachability & latency | `200`, `503` |
| **Skill** | `GET` | `/api/students` | List students with pagination, search, college/dept filter | `200` |
| **Skill** | `POST` | `/api/students` | Create new student profile | `201`, `422`, `409` |
| **Skill** | `GET` | `/api/students/<id>` | Fetch student profile by Mongo ObjectId | `200`, `400`, `404` |
| **Skill** | `PUT` | `/api/students/<id>` | Update student profile fields | `200`, `400`, `404`, `422` |
| **Skill** | `DELETE` | `/api/students/<id>` | Delete student profile and associated roadmap | `200`, `400`, `404` |
| **Skill** | `GET` | `/api/students/<id>/skills` | List student skills with level (1-5) | `200`, `400`, `404` |
| **Skill** | `POST` | `/api/students/<id>/skills` | Add or replace a student skill | `200`, `201`, `422` |
| **Skill** | `PUT` | `/api/students/<id>/skills/<name>` | Update skill proficiency level | `200`, `400`, `404`, `422` |
| **Skill** | `DELETE` | `/api/students/<id>/skills/<name>` | Remove a skill from student profile | `200`, `400`, `404` |
| **Skill** | `GET` | `/api/careers` | List careers catalog with category filters | `200` |
| **Skill** | `POST` | `/api/careers` | Create new career path with DAG prerequisites | `201`, `409`, `422` |
| **Skill** | `GET` | `/api/careers/<id>` | Get career details and required skills | `200`, `400`, `404` |
| **Skill** | `PUT` | `/api/careers/<id>` | Update career details | `200`, `400`, `404` |
| **Skill** | `DELETE` | `/api/careers/<id>` | Remove career | `200`, `400`, `404` |
| **Skill** | `POST` | `/api/students/<id>/career-goal` | Set target career goal for student | `200`, `400`, `404` |
| **Skill** | `GET` | `/api/students/<id>/skill-gap` | Execute rule-based gap analysis (readiness score) | `200`, `400`, `404` |
| **Skill** | `POST` | `/api/students/<id>/roadmap` | Generate DAG topological ordered learning roadmap | `201`, `400`, `404` |
| **Skill** | `GET` | `/api/students/<id>/roadmap` | Retrieve student's current learning roadmap | `200`, `404` |
| **Skill** | `PUT` | `/api/students/<id>/roadmap/stages/<order>` | Update stage status (`not_started`, `in_progress`, `completed`) | `200`, `400`, `404` |
| **Skill** | `GET` | `/api/students/<id>/recommendations` | Inter-service merged opportunity recommendations | `200`, `400`, `502` |
| **Skill** | `GET` | `/api/students/<id>/dashboard` | Aggregate dashboard payload for frontend | `200`, `400`, `404` |
| **Opportunity** | `GET` | `/health` / `/api/health` | Opportunity service health and MongoDB ping | `200`, `503` |
| **Opportunity** | `GET` | `/api/opportunities` | List opportunities with type, mode, difficulty, search | `200` |
| **Opportunity** | `POST` | `/api/opportunities` | Create new opportunity listing | `201`, `422` |
| **Opportunity** | `GET` | `/api/opportunities/<id>` | Fetch opportunity by ID | `200`, `400`, `404` |
| **Opportunity** | `PUT` | `/api/opportunities/<id>` | Update opportunity | `200`, `400`, `404` |
| **Opportunity** | `DELETE` | `/api/opportunities/<id>` | Delete opportunity | `200`, `400`, `404` |
| **Opportunity** | `GET` | `/api/opportunities/stats` | Aggregated opportunity statistics | `200` |
| **Opportunity** | `POST` | `/api/opportunities/match` | Internal secured matching engine (requires `X-Service-Key`) | `200`, `401`, `422` |

---

## Detailed Endpoint Specifications

### 1. Skill Gap Analysis
`GET /api/students/<id>/skill-gap?career_id=<optional>`

Calculates student readiness score (0-100%) against career target requirements.

#### Response Example (`200 OK`):
```json
{
  "success": true,
  "data": {
    "career": {
      "_id": "6acfa120de4c9cd241fca901",
      "title": "Full Stack Developer",
      "category": "software"
    },
    "readiness_score": 62.5,
    "matched_skills": [
      {
        "name": "JavaScript",
        "current_level": 4,
        "required_level": 4,
        "importance": 5,
        "status": "matched"
      }
    ],
    "developing_skills": [
      {
        "name": "React",
        "current_level": 2,
        "required_level": 4,
        "deficit": 2,
        "importance": 4,
        "status": "developing"
      }
    ],
    "missing_skills": [
      {
        "name": "Docker",
        "current_level": 0,
        "required_level": 3,
        "importance": 3,
        "prerequisites": ["Linux Basics"],
        "status": "missing"
      }
    ]
  },
  "message": "Skill gap analysis completed"
}
```

---

### 2. Learning Roadmap Generation
`POST /api/students/<id>/roadmap`

Executes Kahn's topological sort over the career skill dependency DAG to sequence learning stages.

#### Response Example (`201 Created`):
```json
{
  "success": true,
  "data": {
    "student_id": "6acfb737de4c9cd241fca919",
    "career_id": "6acfa120de4c9cd241fca901",
    "stages": [
      {
        "order": 1,
        "skill": "Python",
        "current_level": 0,
        "target_level": 4,
        "estimated_weeks": 4,
        "status": "in_progress",
        "resources": [
          {
            "title": "Official Python Documentation",
            "url": "https://docs.python.org/3/tutorial/",
            "type": "documentation"
          }
        ]
      },
      {
        "order": 2,
        "skill": "FastAPI",
        "current_level": 0,
        "target_level": 3,
        "estimated_weeks": 3,
        "status": "not_started",
        "resources": []
      }
    ]
  },
  "message": "Roadmap generated successfully"
}
```

---

### 3. Inter-Service Matching Engine
`POST /api/opportunities/match` (Opportunity Service)
Headers: `X-Service-Key: <secret_key>`

#### Request Body:
```json
{
  "skills": [
    {"name": "Python", "level": 4},
    {"name": "PostgreSQL", "level": 3}
  ],
  "missing_skills": ["Docker", "Kubernetes"],
  "developing_skills": ["FastAPI"],
  "limit": 5,
  "types": ["internship", "project"]
}
```

#### Response Example (`200 OK`):
```json
{
  "success": true,
  "data": [
    {
      "opportunity": {
        "_id": "6acfa910de4c9cd241fca950",
        "title": "Backend Engineering Intern",
        "organization": "Stripe",
        "type": "internship",
        "difficulty": "intermediate",
        "mode": "remote",
        "stipend": "₹45,000 / month",
        "required_skills": [
          {"name": "Python", "min_level": 3},
          {"name": "PostgreSQL", "min_level": 2}
        ]
      },
      "match_score": 87.5,
      "matched_skills": ["Python (Lv. 4 >= 3)", "PostgreSQL (Lv. 3 >= 2)"],
      "skills_to_learn": ["Docker"],
      "reason": "Strong match on core backend skills with room to grow in containerization"
    }
  ],
  "message": "Matching completed successfully"
}
```
