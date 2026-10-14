# SkillBridge: A Microservices-Based Platform for Student Skill Gap Analysis and Opportunity Discovery 🎓

## Comprehensive Project Report

---

## 1. Abstract
The modern computing landscape is evolving at a breakneck pace, creating a significant divergence between conventional university computer science curricula and industrial expectations. Many engineering students lack deterministic visibility into their actual preparedness for target technical roles (such as Full Stack Engineer, Cloud Architect, or AI Engineer) and miss experiential growth opportunities (internships, hackathons, open-source projects) that specifically address their learning deficits. 

This project presents **SkillBridge**, a cloud-native, distributed microservices platform engineered to evaluate student competencies against real-world job roles and automatically discover career-advancing opportunities. Using a **Database-per-Service** design, SkillBridge decouples student profile and learning roadmaps (**Skill Service**, Python/Flask, MongoDB) from the dynamic opportunities marketplace (**Opportunity Service**, Python/Flask, MongoDB). The platform features an explainable skill-gap scoring formula, Kahn's algorithm-based topological roadmap DAG generation, an authenticated inter-service matching pipeline with graceful degradation, and a SaaS-style React 18 + Tailwind CSS single-page application.

---

## 2. Problem Statement
1. **Curricular Skill Disconnect**: University courses emphasize foundational theory, often omitting modern production technologies (e.g., Docker, Kubernetes, CI/CD, React 18, FastAPI).
2. **Subjective & Unexplainable Guidance**: Students lack standardized numeric metrics to determine their readiness for specialized careers.
3. **Disjointed Opportunity Searching**: Job boards (LinkedIn, Indeed) prioritize experienced professionals with keyword matching, overwhelming students with roles they are underqualified for while failing to highlight opportunities that teach their missing skills.
4. **Architectural Fragility in Legacy Portals**: Monolithic student portals suffer from single-point-of-failure risks where external catalog outages block students from viewing course roadmaps and profiles.

---

## 3. Objectives
- **Decoupled Distributed Architecture**: Develop independent microservices adhering to the Database-per-Service pattern with zero database-level sharing.
- **Rule-Based Skill Gap Analysis**: Implement an explainable algorithm calculating career readiness percentage, classifying skills into *Matched*, *Developing*, and *Missing*.
- **Topological Learning Roadmaps**: Automate prerequisite-respecting curriculum paths using Kahn's topological sort algorithm over Directed Acyclic Graphs (DAGs).
- **Inter-Service REST Orchestration**: Connect services via HTTP REST with connection pooling, circuit-like retries, shared-secret token authentication, and graceful degradation during partial outages.
- **High-Polish SaaS User Interface**: Deliver a modern dashboard featuring light/dark themes, interactive radar charts, kanban roadmap boards, command palette (`Ctrl+K`), and live microservices topology health indicators.
- **Production-Ready Cloud Infrastructure**: Provide automated Docker Compose configurations, Render web service blueprints with cold-start resilience, and Vercel SPA routing.

---

## 4. Literature & Existing Systems Review
Existing platforms fall into three primary categories:
1. **General Job Search Portals (LinkedIn, Indeed, Glassdoor)**: Emphasize applicant volume and employer-paid promotion; lack student-centric skill-gap analytics or prerequisite-based roadmaps.
2. **Curated Roadmap Repositories (Roadmap.sh)**: Provide static community guides without individualized profile evaluation or live opportunity matching.
3. **Campus Placement Portals**: Often developed as legacy monolithic web applications using unified SQL databases, resulting in maintenance gridlocks and poor failure isolation.

**SkillBridge Innovation**: Integrates personalized gap scoring, dynamic roadmap generation, and explainable opportunity matching within an enterprise microservices paradigm with strict domain decoupling.

---

## 5. System Architecture
SkillBridge comprises three autonomous tiers communicating across well-defined network boundaries:

```
+-------------------------------------------------------------+
|               Client Tier (React 18 + Vite)                 |
|            Hosted on Vercel (Client Port 5173)              |
+---------------+-----------------------------+---------------+
                |                             |
                | HTTP REST                   | HTTP REST
                v                             v
+-------------------------------+   +-------------------------------+
|    Skill Service (Flask)      |   |  Opportunity Service (Flask)  |
|         Port 5001             |   |          Port 5002            |
| - Student Profiles & Skills   |   | - Opportunity Catalog         |
| - Career Target Definitions   |   | - Type / Difficulty Filters   |
| - Skill Gap Engine            |   | - Match Scoring Engine        |
| - Roadmap DAG Topological Sort|   | - Aggregated Analytics        |
+---------------+---------------+   +---------------+---------------+
                |                                   ^
                | Inter-Service REST (X-Service-Key)|
                +-----------------------------------+
                |                                   |
                v PyMongo                           v PyMongo
+-------------------------------+   +-------------------------------+
|      skill_db (MongoDB)       |   |   opportunity_db (MongoDB)    |
| - students                    |   | - opportunities               |
| - careers                     |   +-------------------------------+
| - roadmaps                    |
+-------------------------------+
```

---

## 6. Technology Stack

| Layer | Technologies Selected | Justification |
|---|---|---|
| **Backend Microservices** | Python 3.11+, Flask 3.0, Gunicorn, PyMongo, Marshmallow | Lightweight micro-framework with rapid cold starts, strict serialization schemas, and high throughput. |
| **Databases** | MongoDB Atlas M0 (Clusters `skill_db` & `opportunity_db`) | Schema flexibility for nested skill arrays and JSON documents without relational join overhead. |
| **Frontend Dashboard** | React 18, Vite 8, Tailwind CSS, Recharts, Lucide React, Framer Motion | Instant HMR, zero runtime styling overhead, accessible components, and rich data visualization. |
| **Inter-Service Layer** | Python Requests, urllib3 Retry, Custom OpportunityClient | Persistent sessions, pooled TCP connections, exponential backoff, and circuit-breaking fallbacks. |
| **API Documentation** | Flasgger (OpenAPI 2.0 / Swagger UI) at `/apidocs` | Interactive self-documenting API explorer. |
| **DevOps & CI/CD** | Docker, Docker Compose, GitHub Actions, Render, Vercel | Ephemeral automated testing, automated container builds, and zero-configuration serverless deployments. |

---

## 7. Module Description

### 7.1 Student & Skills Management (`skill-service`)
- CRUD operations for student academic details (College, Department, Year 1–4).
- Granular skill proficiencies tracked on a standardized 1–5 level scale (Beginner to Expert).
- Unique email constraint, text indexing across student metadata, and defensive schema validations.

### 7.2 Career Catalog & Prerequisite Hierarchy (`skill-service`)
- Curated technical roles (Full Stack Developer, Data Scientist, DevOps Engineer, Cloud Architect, Mobile Developer).
- Each career specifies required skills, required proficiency levels (1–5), importance weights (1–5), and direct skill prerequisites.

### 7.3 Rule-Based Skill Gap Analysis Engine (`skill-service`)
- Computes fulfillment ratios for every required skill:
  $$F(r_i) = \min\left(1.0, \frac{L_{cur}(r_i)}{L_{req}(r_i)}\right)$$
- Calculates career readiness percentage weighted by skill importance.
- Classifies skills into **Matched**, **Developing**, and **Missing**.

### 7.4 Learning Roadmap Generator (`skill-service`)
- Models career prerequisites as a Directed Acyclic Graph (DAG).
- Applies Kahn's topological sorting algorithm to generate an ordered sequence of learning stages.
- Attaches curated documentation, courses, and project resources to each stage.
- Supports lifecycle state transitions (`not_started` $\to$ `in_progress` $\to$ `completed`).

### 7.5 Opportunity Discovery & Catalog (`opportunity-service`)
- Catalogs internships, hackathons, research projects, and technical workshops.
- Rich filtering by type, mode (remote/hybrid/in-person), difficulty, status, and tag search.

### 7.6 Opportunity Matching Engine (`opportunity-service`)
- Evaluates student skills against opportunity requirements.
- Rewards full skill matches (1.0) and developing skills ($0.5 \times \text{ratio}$).
- Awards a growth bonus (+0.25) when an opportunity teaches a skill missing from the student's career path.
- Applies an over-requirement penalty (-0.15) if an opportunity demands proficiencies far beyond the student's current level.
- Generates transparent, human-readable reason strings.

---

## 8. Database Design
Strict adherence to the Database-per-Service pattern guarantees complete isolation:

```mermaid
erDiagram
    STUDENT {
        ObjectId _id PK
        string name
        string email UK
        string college
        string department
        int year
        string career_goal FK
        array skills
        date created_at
    }

    CAREER {
        ObjectId _id PK
        string title
        string slug UK
        string description
        string category
        array required_skills
    }

    ROADMAP {
        ObjectId _id PK
        string student_id FK
        string career_id FK
        array stages
        int total_estimated_weeks
    }

    OPPORTUNITY {
        ObjectId _id PK
        string title
        string organization
        string type
        string difficulty
        string mode
        array required_skills
        string apply_url
        string status
    }

    STUDENT ||--o| CAREER : "references"
    STUDENT ||--o| ROADMAP : "owns"
    CAREER ||--o{ ROADMAP : "structures"
    STUDENT ..o{ OPPORTUNITY : "matches via REST"
```

---

## 9. Inter-Service Communication & Failure Resilience

### 9.1 REST Protocol & Shared Secret Security
Inter-service calls from `skill-service` to `opportunity-service` are routed through a dedicated client (`OpportunityClient`):
- All inter-service requests include the `X-Service-Key` header verified by middleware in Opportunity Service.
- Connections leverage a persistent HTTP session with pool size optimization.

### 9.2 Graceful Degradation Guarantees
When Opportunity Service experiences latency or down-time:
1. `OpportunityClient` retries twice with exponential backoff (`0.3s`, `0.6s`).
2. If unreachable, `OpportunityServiceUnavailableError` is caught by the Skill Service route handlers.
3. Skill Service logs the failure and returns HTTP `200 OK` to the frontend with:
   - Complete local skill gap analysis and roadmap progress intact.
   - `top_recommendations: []`
   - `opportunity_service: { status: "unavailable", message: "Opportunity service offline" }`
4. The frontend displays the dashboard smoothly with a degraded status notice rather than an application-wide crash.

---

## 10. Frontend Architecture & Design System
Built from the ground up to reflect a premium SaaS dashboard (Linear / Vercel aesthetic):
- **Design Tokens**: Slate gray neutrals with vibrant indigo accents and semantic badge colors (Emerald = matched, Amber = developing, Rose = missing, Sky = info).
- **Theme Support**: Zero-flicker Light and Dark mode persisted to `localStorage`.
- **Command Palette (`Ctrl+K`)**: Rapid navigation and student switching across the platform.
- **Cold-Start Handling**: Animated banner with live elapsed timer that alerts the user when cloud containers are waking up from idle sleep.
- **Core Views**: Dashboard, Skills Inventory, Career Goal Gap Visualizer, Learning Roadmap (Timeline & Kanban), Opportunity Discovery, Admin Management CRUD, Student Profile, and Live System Architecture Status.

---

## 11. Testing & Quality Assurance

### 11.1 Automated Backend Testing (`pytest` + `pytest-cov`)
- **Total Tests**: **58 Unit & Integration Tests** passing in under 2 seconds.
- **Code Coverage**:
  - `skill-service`: **86% coverage** (Gap analysis 94%, Roadmap 92%, Career 92%, Student 90%).
  - `opportunity-service`: **90% coverage** (Opportunity catalog 96%, Matching 89%, Config 91%).

### 11.2 Post-Deployment Smoke Testing (`scripts/smoke_test.py`)
CLI suite testing health checks, inter-service pings, student CRUD lifecycle, and recommendation pipelines against live cloud endpoints.

### 11.3 Postman API Collection
Comprehensive 10-folder Postman collection with test assertions (status codes, JSON envelopes, latency < 1500ms) and automated environment variable propagation.

---

## 12. Deployment Architecture
- **MongoDB Atlas**: Managed multi-tenant database clusters with IP allowlists (`0.0.0.0/0`).
- **Render**: Blueprint-driven web services for Skill Service and Opportunity Service with Gunicorn WSGI workers, `$PORT` dynamic binding, and `/health` probes.
- **Vercel**: Global edge CDN hosting the React Single Page Application with SPA routing rewrites (`vercel.json`).
- **Docker Compose**: Containerized multi-container environment running MongoDB, both Python APIs, and Nginx.

---

## 13. Results & Visual Verification

### Visual Previews (See `docs/screenshots/` for full resolutions)
1. **Executive Dashboard**: KPI stat cards, readiness progress bar, Recharts skill radar chart, and top recommended opportunities.
2. **Interactive Skill Inventory**: Sliders (1–5), search filters, and add/edit skill modals.
3. **Career Gap Visualizer**: Three-column breakdown of Matched, Developing, and Missing skills.
4. **Learning Roadmap**: Topological timeline sequencing and interactive Kanban board (`Not Started` $\to$ `In Progress` $\to$ `Completed`).
5. **Opportunity Explorer**: Filterable opportunity grid and slide-over application inspection drawer.
6. **Microservices System Status**: Live architecture topology diagram with real-time ping latencies and database status indicators.

---

## 14. Limitations
1. **Deterministic Skill Representation**: Skills are modeled as discrete 1–5 scalar values rather than multi-dimensional competency trees.
2. **Rule-Based Matching**: Matching is deterministic; it does not yet utilize neural embeddings or semantic vector similarity.
3. **Simulated Authentication**: Inter-service calls use shared secret tokens, while frontend student switching currently simulates multi-user tenancy without OAuth2/JWT logins.

---

## 15. Future Scope
- **Machine Learning & NLP Recommendations**: Integrate HuggingFace sentence transformers to parse unstructured opportunity job descriptions and resume PDFs.
- **Enterprise Recruiter Portal**: Allow certified companies to submit listings, review anonymized student candidate pools, and send interview invitations.
- **Automated Skill Verification**: Integrate GitHub and LeetCode APIs to programmatically verify and update student skill proficiencies based on code commits and contest ratings.

---

## 16. Conclusion
SkillBridge successfully demonstrates an enterprise-grade, distributed microservices solution to the student skill gap problem. By strictly adhering to the Database-per-Service pattern, implementing explainable algorithmic scoring, ensuring graceful degradation under failure scenarios, and wrapping the platform in a modern SaaS interface, SkillBridge bridges the critical divide between academia and modern engineering practice.
