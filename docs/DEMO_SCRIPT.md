# SkillBridge: 5-7 Minute Viva & Demonstration Script 🎬

This script guides you through an impressive, structured 5–7 minute viva and live software demonstration for evaluators.

---

## ⏱️ Timeline Overview

| Time | Phase | Focus |
|---|---|---|
| **0:00 - 1:00** | Introduction & Problem | Motivation, problem statement, architecture slide |
| **1:00 - 2:30** | Frontend Dashboard & Core User Flow | Readiness gauge, skill inventory, gap visualizer, topological roadmap |
| **2:30 - 3:45** | Opportunity Matching & Inter-Service REST | Live match rankings, explainable reasons, inspect drawer |
| **3:45 - 4:45** | Architecture & Microservices Resilience | System status topology, circuit breaker / graceful degradation proof |
| **4:45 - 5:45** | Postman API & MongoDB Atlas Isolation | Live Postman runner, Atlas clusters, database-per-service proof |
| **5:45 - 6:30** | CI/CD, Deployment & Wrap-Up | Render blueprint, Vercel SPA, GitHub Actions, smoke tests |

---

## Detailed Step-by-Step Script

### Phase 1: Motivation & Architecture (1 Minute)
* **What to Show**: `README.md` or Architecture Diagram (`docs/architecture.md`).
* **What to Say**:
  > *"Good morning professors. Today we are presenting **SkillBridge**, a microservices-based platform designed to solve a critical problem for engineering students: the divergence between academic curricula and industrial expectations.
  >
  > Instead of a brittle monolith, SkillBridge is built as two decoupled microservices following the **Database-per-Service** design:
  > 1. **Skill Service** on port 5001, owning student academic data, career definitions, gap analysis, and learning roadmaps in `skill_db`.
  > 2. **Opportunity Service** on port 5002, owning experiential opportunities (internships, hackathons) in `opportunity_db`.
  > Both connect to a modern React 18 single-page dashboard. Let me demonstrate the live system."*

---

### Phase 2: Live Frontend Dashboard Flow (1.5 Minutes)
* **What to Show**: Open `http://localhost:5173/` in your browser.
* **Actions**:
  1. Show **Top Navbar**: Toggle Dark/Light mode and point out the live **Services Operational** pill and active student switcher.
  2. Press `Ctrl + K` to open the **Command Palette**: Search for a page or switch to student *"Alex Chen"*.
  3. Show **Dashboard**:
     - Point out the **Career Readiness Score** gauge (e.g. 68.5%) and explain the weighted math.
     - Hover over the Recharts **Skill Radar Chart** showing current proficiencies vs. career targets.
  4. Navigate to **"My Skills"**:
     - Adjust a skill slider (e.g., Python from Level 3 to Level 4) or click **Add Skill**.
     - Notice the instantaneous state update without full page reloads.
  5. Navigate to **"Career Goal & Gap Analysis"**:
     - Switch between target careers (e.g. *Full Stack Developer* vs *Data Scientist*).
     - Point out the 3 columns: **Matched** (green), **Developing** (amber with deficit counts), and **Missing** (rose with prerequisite badges).
  6. Navigate to **"Learning Roadmap"**:
     - Show the **Timeline View**: Explain that stages are sequenced using Kahn's topological sort algorithm over career prerequisites.
     - Switch to the **Kanban Board**: Drag or toggle a stage from `Not Started` to `In Progress` or `Completed`.
* **What to Say**:
  > *"Notice how the roadmap isn't static text. It dynamically recomputes when a student updates their skills. Prerequisites like Linux Basics are automatically scheduled before advanced containerization stages."*

---

### Phase 3: Opportunity Matching & Explainability (1 Minute)
* **What to Show**: Navigate to **"Opportunities"** page.
* **Actions**:
  1. Point out the match percentage badges (e.g., *92% Match*).
  2. Highlight the human-readable **Reason String**: *"Strong match on Python (Lv. 3). Opportunity provides practical experience to advance SQL and learn Docker."*
  3. Click **Inspect** on any opportunity card:
     - Slide over the drawer showing required skills vs. student level, stipend, organization, and direct Apply URL.
* **What to Say**:
  > *"Unlike keyword search on LinkedIn, our Opportunity Service computes explainable match scores. It rewards student proficiencies, partially scores developing skills, and awards a growth bonus if an opportunity teaches a skill missing from their career goal."*

---

### Phase 4: Inter-Service Architecture & Graceful Degradation (1 Minute)
* **What to Show**: Navigate to **"System Status"** page.
* **Actions**:
  1. Show the **Interactive Microservices Topology** diagram:
     - Frontend (Port 5173) $\to$ Inter-Service REST Layer $\to$ Isolated MongoDB Atlas databases.
  2. Click **Ping Microservices**: Watch the real-time round-trip latency update.
  3. **Demonstrate Graceful Degradation**:
     - Explain: *"If Opportunity Service goes down, Skill Service does NOT crash. It falls back gracefully, preserving student roadmaps and gap scores while reporting degraded recommendations."*

---

### Phase 5: Postman & Database Proof (1 Minute)
* **What to Show**: Postman and MongoDB Atlas.
* **Actions**:
  1. Open Postman: Show the `SkillBridge Microservices API Collection`.
  2. Run the **"10. Full Workflow"** folder:
     - Show all 7 requests passing in sequence with automated environment variable propagation.
  3. Show MongoDB:
     - Point out `skill_db` containing `students`, `careers`, `roadmaps`.
     - Point out `opportunity_db` containing `opportunities`.
     - Emphasize zero shared collections and zero cross-database queries.

---

### Phase 6: Production CI/CD & Wrap-Up (30 Seconds)
* **What to Show**: Terminal / GitHub Actions `.github/workflows/ci.yml`.
* **Actions**:
  1. Run `python scripts/smoke_test.py`: Show the automated PASS table.
  2. Mention Docker Compose (`docker-compose up --build`) and Render / Vercel configurations.
* **What to Say**:
  > *"All 58 backend tests and frontend production builds pass in CI/CD. The system is completely containerized with Docker and ready for independent cloud deployment on Render and Vercel. Thank you, and we welcome your questions!"*
