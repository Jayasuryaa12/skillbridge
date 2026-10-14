# SkillBridge: Evaluation Criteria & Marks-Mapping Checklist 🎯

This table maps every project requirement and grading criterion across **Phases 1 through 5** directly to its implementation files and verification proofs in the repository.

---

## 📋 Master Evaluation Matrix

| Phase | Evaluation Criterion | Implementation Location in Repository | Verification Proof / Command |
|---|---|---|---|
| **Phase 1** | **Microservice Decomposition** | [`skill-service/`](skill-service/) (Port 5001)<br/>[`opportunity-service/`](opportunity-service/) (Port 5002) | Independent Flask app factories in `app/__init__.py` |
| **Phase 1** | **Database-per-Service Isolation** | `skill_db` in [`skill-service/app/db.py`](skill-service/app/db.py)<br/>`opportunity_db` in [`opportunity-service/app/db.py`](opportunity-service/app/db.py) | No shared collections; separate MongoDB connection clients |
| **Phase 1** | **Full CRUD & Schema Validations** | [`skill-service/app/routes/`](skill-service/app/routes/)<br/>[`opportunity-service/app/routes/`](opportunity-service/app/routes/) | Marshmallow schemas in `models/schemas.py`; 422 on invalid data |
| **Phase 1** | **Data Seeding Scripts** | [`skill-service/scripts/seed.py`](skill-service/scripts/seed.py)<br/>[`opportunity-service/scripts/seed.py`](opportunity-service/scripts/seed.py) | Seeds 4 students, 5 careers, and 32 opportunities |
| **Phase 1** | **Unit & Integration Tests** | [`skill-service/tests/`](skill-service/tests/)<br/>[`opportunity-service/tests/`](opportunity-service/tests/) | Run `pytest` across both test directories (58 passed) |
| **Phase 2** | **Rule-Based Opportunity Match Engine** | [`opportunity-service/app/services/matching_service.py`](opportunity-service/app/services/matching_service.py) | `POST /api/opportunities/match` returns ranked scores (0-100%) |
| **Phase 2** | **Inter-Service REST Client** | [`skill-service/clients/opportunity_client.py`](skill-service/clients/opportunity_client.py) | Persistent session, connection pooling, retries, `X-Service-Key` |
| **Phase 2** | **Graceful Degradation Under Outages** | [`skill-service/app/routes/students.py`](skill-service/app/routes/students.py#L285-L350) | Returns 200 OK with local gap analysis intact when Opp Service is down |
| **Phase 2** | **System Status & Health Monitoring** | [`skill-service/app/routes/health.py`](skill-service/app/routes/health.py#L44-L87) | `GET /api/system/status` measures cross-service round-trip latency |
| **Phase 3** | **SaaS Dashboard UI & Design System** | [`frontend/tailwind.config.js`](frontend/tailwind.config.js)<br/>[`frontend/src/index.css`](frontend/src/index.css) | Custom color tokens (indigo, emerald, amber, rose, slate) |
| **Phase 3** | **Dark / Light Mode Toggle** | [`frontend/src/context/ThemeContext.jsx`](frontend/src/context/ThemeContext.jsx) | Persists to `localStorage`, detects OS preference |
| **Phase 3** | **Command Palette & Student Switcher** | [`frontend/src/components/layout/CommandPalette.jsx`](frontend/src/components/layout/CommandPalette.jsx)<br/>[`frontend/src/context/StudentContext.jsx`](frontend/src/context/StudentContext.jsx) | `Ctrl + K` global shortcut; instant student switching |
| **Phase 3** | **9 Core Frontend Views** | [`frontend/src/pages/`](frontend/src/pages/) | Dashboard, Skills, CareerGoal, Roadmap, Opportunities, Manage, Profile, Status, 404 |
| **Phase 3** | **Topological Roadmap & Kanban Board** | [`frontend/src/pages/Roadmap.jsx`](frontend/src/pages/Roadmap.jsx) | Kahn's DAG order display with Timeline and Kanban tabs |
| **Phase 4** | **Production Readiness (Gunicorn, Python 3.11)** | [`skill-service/Procfile`](skill-service/Procfile), [`opportunity-service/Procfile`](opportunity-service/Procfile)<br/>[`runtime.txt`](skill-service/runtime.txt) | Dynamic `$PORT` binding; Gunicorn WSGI with 2 workers |
| **Phase 4** | **Strict CORS Lockdown** | [`app/config.py`](skill-service/app/config.py#L13-L20) | Restricted to `ALLOWED_ORIGINS` (Vercel domain) on `r"/*"` |
| **Phase 4** | **Render Cold-Start Handling** | [`skill-service/clients/opportunity_client.py`](skill-service/clients/opportunity_client.py)<br/>[`frontend/src/components/layout/ColdStartBanner.jsx`](frontend/src/components/layout/ColdStartBanner.jsx) | 45s wake-up retry + live elapsed timer animated UI banner |
| **Phase 4** | **Render Blueprints & Vercel Config** | [`render.yaml`](render.yaml)<br/>[`frontend/vercel.json`](frontend/vercel.json) | Multi-service Render blueprint + Vercel SPA router rewrites |
| **Phase 4** | **Automated Smoke Test Suite** | [`scripts/smoke_test.py`](scripts/smoke_test.py) | CLI testing live endpoints with formatted PASS/FAIL table |
| **Phase 4** | **GitHub Actions CI Pipeline** | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Runs backend pytest & frontend production build on push |
| **Phase 4** | **Local Docker Compose** | [`docker-compose.yml`](docker-compose.yml)<br/>Dockerfiles in all 3 projects | `docker-compose up --build` runs entire stack |
| **Phase 5** | **Postman Collection & Environments** | [`postman/SkillBridge.postman_collection.json`](postman/SkillBridge.postman_collection.json)<br/>[`postman/SkillBridge_Local.postman_environment.json`](postman/SkillBridge_Local.postman_environment.json)<br/>[`postman/SkillBridge_Production.postman_environment.json`](postman/SkillBridge_Production.postman_environment.json) | 10 folders, test scripts, error cases, and Full Workflow |
| **Phase 5** | **Swagger UI / OpenAPI Documentation** | Live at `/apidocs/` on both services<br/>[`docs/API.md`](docs/API.md) | Flasgger interactive documentation + markdown reference |
| **Phase 5** | **Test Coverage Report (>85%)** | [`pytest --cov`](skill-service/tests/) | Skill Service: 86%, Opportunity Service: 90% |
| **Phase 5** | **Comprehensive Academic Documentation** | [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md)<br/>[`docs/architecture.md`](docs/architecture.md)<br/>[`docs/algorithms.md`](docs/algorithms.md) | Abstract, math formulas, ER diagram, system diagrams |
| **Phase 5** | **Viva Demonstration Kit** | [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)<br/>[`docs/VIVA_QA.md`](docs/VIVA_QA.md) | 5-7 min viva flow + 25 technical Q&A with model answers |
