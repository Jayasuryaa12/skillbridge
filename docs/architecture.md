# SkillBridge Microservices Architecture Documentation

## 1. System Overview
**SkillBridge** is a distributed, microservices-based platform engineered to bridge the divide between student academic skill sets and current industry requirements. It provides:
1. Student skill profiling and career path tracking.
2. Rule-based, deterministic skill gap analysis with radar-chart readiness scoring.
3. Automated prerequisite-aware learning roadmap generation.
4. Comprehensive discovery and filtering of experiential opportunities (internships, hackathons, projects, workshops).

---

## 2. Monorepo Structure

```
skillbridge/
├── skill-service/          # Flask Microservice (Port 5001, DB: skill_db)
│   ├── app/
│   │   ├── models/         # Marshmallow schemas & validation rules
│   │   ├── routes/         # REST blueprints (students, careers, roadmaps, health)
│   │   ├── services/       # Business logic (gap analysis, topological sort, CRUD)
│   │   ├── utils/          # Standard response formatters, ObjectId serializers
│   │   ├── config.py       # Multi-environment configurations (Dev, Test, Prod)
│   │   └── db.py           # MongoDB connection pooling & index management
│   ├── data/               # Seed datasets (careers.json, students.json, resources_catalog.json)
│   ├── scripts/            # Seed and administrative CLI tools
│   ├── tests/              # Pytest unit & integration test suites
│   ├── requirements.txt
│   ├── run.py
│   └── Procfile
├── opportunity-service/    # Flask Microservice (Port 5002, DB: opportunity_db)
│   ├── app/
│   │   ├── models/         # Opportunity validation schemas
│   │   ├── routes/         # Opportunities and health blueprints
│   │   ├── services/       # Opportunity filtering, multi-field search, stats
│   │   ├── utils/          # Standard JSON responses, helpers
│   │   ├── config.py
│   │   └── db.py
│   ├── data/               # Seed datasets (32 diverse opportunities)
│   ├── scripts/            # Seeding scripts
│   ├── tests/              # Pytest test suites
│   ├── requirements.txt
│   ├── run.py
│   └── Procfile
├── postman/                # Automated Postman Collection and Environment
├── docs/                   # Architecture, API specifications, and algorithm docs
└── README.md
```

---

## 3. Database Ownership & Isolation
In accordance with microservice design principles:
- **Zero Database Sharing**: `skill-service` exclusively owns and accesses `skill_db`. `opportunity-service` exclusively owns and accesses `opportunity_db`.
- **Decoupled Lifecycles**: Schemas, indexes, and migrations can evolve independently without impacting neighboring services.
- **Cross-Service Communication**: Future inter-service workflows (Phase 2) communicate strictly via HTTP REST or asynchronous messaging, never direct database queries.

---

## 4. Collection Schemas & Indexing Strategy

### `skill_db` (Skill Service)
1. **`students`**:
   - `_id`: ObjectId
   - `name`: string
   - `email`: string (Unique index)
   - `college`: string
   - `department`: string
   - `year`: integer (1–4)
   - `career_goal`: string (Career ObjectId)
   - `skills`: array of `{ name: string, level: 1..5, updated_at: ISODate }`
   - `created_at`: ISODate, `updated_at`: ISODate
   - *Indexes*: Unique on `email`, Text search on `name`, `college`, `department`, Ascending on `career_goal`, Ascending on `year`.

2. **`careers`**:
   - `_id`: ObjectId
   - `title`: string
   - `slug`: string (Unique index)
   - `description`: string
   - `category`: string
   - `required_skills`: array of `{ name, required_level (1..5), importance (1..5), prerequisites: [string], category: string }`
   - `created_at`: ISODate, `updated_at`: ISODate
   - *Indexes*: Unique on `slug`, Text search on `title`, `description`, Ascending on `category`.

3. **`roadmaps`**:
   - `_id`: ObjectId
   - `student_id`: string (Student ObjectId)
   - `career_id`: string (Career ObjectId)
   - `stages`: array of ordered stages with learning resources and status (`not_started`, `in_progress`, `completed`).
   - `total_estimated_weeks`: integer
   - `generated_at`: ISODate
   - *Indexes*: Compound index on `(student_id, career_id)`, Ascending on `student_id`.

### `opportunity_db` (Opportunity Service)
1. **`opportunities`**:
   - `_id`: ObjectId
   - `title`: string
   - `type`: `project` | `hackathon` | `internship` | `workshop`
   - `organization`: string
   - `description`: string
   - `required_skills`: array of `{ name: string, min_level: 1..5 }`
   - `difficulty`: `beginner` | `intermediate` | `advanced`
   - `mode`: `online` | `offline` | `hybrid`
   - `location`: string (optional)
   - `start_date`, `deadline`: ISODate strings (optional)
   - `duration`, `stipend`, `prize`: string (optional)
   - `apply_url`: string
   - `tags`: array of string
   - `status`: `open` | `closed`
   - *Indexes*: Text search on `title`, `description`, `organization`, Ascending indexes on `type`, `difficulty`, `mode`, `status`, `deadline`, `tags`, and `required_skills.name`.

---

## 5. Standard API Response Envelope
Both microservices implement a uniform response protocol:

### Success:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human-readable confirmation",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 42,
    "total_pages": 3
  }
}
```

### Error:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body.",
    "details": {
      "email": ["Not a valid email address."]
    }
  }
}
```
