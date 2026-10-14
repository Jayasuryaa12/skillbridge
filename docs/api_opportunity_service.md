# Opportunity Service API Specification (Port 5002)

Base URL: `http://localhost:5002`

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
    "service": "opportunity-service",
    "status": "healthy",
    "mongodb": "connected",
    "version": "1.0.0"
  }
}
```

---

## 2. Opportunities API

### `GET /api/opportunities`
List opportunities with multi-parameter filtering, full-text search, and pagination.

- **Query Parameters**:
  - `page` (int, default: 1)
  - `page_size` (int, default: 20, max: 100)
  - `type` (enum): `project` | `hackathon` | `internship` | `workshop`
  - `difficulty` (enum): `beginner` | `intermediate` | `advanced`
  - `mode` (enum): `online` | `offline` | `hybrid`
  - `status` (enum): `open` | `closed` (default: `open`)
  - `skill` (string): Filter opportunities requiring a given skill name
  - `tag` (string): Filter by tag
  - `search` (string): Text search across `title`, `description`, and `organization`
  - `sort_by` (enum): `created_at` | `deadline` | `title` (default: `created_at`)
  - `sort_dir` (enum): `asc` | `desc` (default: `desc`)

- **Response `200 OK`**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "660c1d2e8f1b2c001a1e4f30",
      "title": "Machine Learning Research Intern",
      "type": "internship",
      "organization": "Microsoft Research India",
      "description": "Collaborate directly with senior researchers to innovate algorithms in natural language processing...",
      "required_skills": [
        { "name": "python", "min_level": 4 },
        { "name": "pytorch", "min_level": 3 }
      ],
      "difficulty": "advanced",
      "mode": "hybrid",
      "location": "Bengaluru, India",
      "start_date": "2026-06-01T00:00:00Z",
      "deadline": "2026-03-31T23:59:59Z",
      "duration": "6 months",
      "stipend": "₹80,000 / month",
      "prize": null,
      "apply_url": "https://careers.microsoft.com/research-intern",
      "tags": ["ai", "deep-learning", "nlp", "pytorch"],
      "status": "open",
      "created_at": "2026-10-14T10:00:00Z",
      "updated_at": "2026-10-14T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 32,
    "total_pages": 2
  }
}
```

---

### `GET /api/opportunities/stats`
Returns aggregated counts across categories for dashboards and analytics.

- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "total": 32,
    "by_type": {
      "internship": 10,
      "hackathon": 8,
      "project": 8,
      "workshop": 6
    },
    "by_difficulty": {
      "beginner": 6,
      "intermediate": 16,
      "advanced": 10
    },
    "by_mode": {
      "online": 14,
      "hybrid": 12,
      "offline": 6
    },
    "by_status": {
      "open": 32,
      "closed": 0
    }
  }
}
```

---

### `POST /api/opportunities`
Create a new opportunity.

- **Request Body**:
```json
{
  "title": "Cloud Platform Engineering Intern",
  "type": "internship",
  "organization": "Zomato",
  "description": "Help scale Kubernetes clusters that handle peak dinner rush traffic.",
  "required_skills": [
    { "name": "kubernetes", "min_level": 2 },
    { "name": "docker", "min_level": 3 }
  ],
  "difficulty": "advanced",
  "mode": "hybrid",
  "location": "Gurugram, India",
  "apply_url": "https://zomato.com/careers/infra-intern",
  "tags": ["devops", "kubernetes", "aws"],
  "status": "open"
}
```
- **Response `201 Created`**

---

### `GET /api/opportunities/<id>`
Retrieve a specific opportunity by ObjectId.

---

### `PUT /api/opportunities/<id>`
Update fields of an existing opportunity.

---

### `DELETE /api/opportunities/<id>`
Delete an opportunity.
