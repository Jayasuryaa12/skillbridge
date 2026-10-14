# SkillBridge 🎓

**A Microservices-Based Platform for Student Skill Gap Analysis and Opportunity Discovery**

---

## Architecture

```
skillbridge/
  skill-service/          Flask API · port 5001 · MongoDB: skill_db
  opportunity-service/    Flask API · port 5002 · MongoDB: opportunity_db
  frontend/               React 18 + Vite + Tailwind CSS (Phase 4)
  docs/                   Architecture, algorithm & API docs
  postman/                Postman collection & environment
```

## Services

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| skill-service | 5001 | skill_db | Students, Careers, Roadmaps, Skill-Gap Analysis |
| opportunity-service | 5002 | opportunity_db | Opportunities Catalog |

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (or local MongoDB 6+)
- Node.js 18+ (for frontend, Phase 4)

### 1. Clone the repo

```bash
git clone <repo-url>
cd skillbridge
```

### 2. Start skill-service

```bash
cd skill-service
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env       # Edit MONGO_URI with your Atlas connection string
python scripts/seed.py     # Seed careers, students, resources
python run.py              # Starts on http://localhost:5001
```

### 3. Start opportunity-service

```bash
cd ../opportunity-service
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env       # Edit MONGO_URI
python scripts/seed.py     # Seeds 30+ opportunities
python run.py              # Starts on http://localhost:5002
```

## Health Checks

```bash
curl http://localhost:5001/api/health
curl http://localhost:5002/api/health
```

## Phase Progress

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Backend microservices, CRUD, MongoDB, seed data, tests | ✅ Complete |
| Phase 2 | Inter-service communication | 🔜 Pending |
| Phase 3 | Advanced gap analysis + recommendations | 🔜 Pending |
| Phase 4 | React frontend | 🔜 Pending |
| Phase 5 | Deployment, Postman, docs, report | 🔜 Pending |

## Running Tests

```bash
# skill-service tests
cd skill-service
pytest tests/ -v

# opportunity-service tests
cd opportunity-service
pytest tests/ -v
```

---

*SkillBridge — Bridging the gap between student skills and career opportunities.*
