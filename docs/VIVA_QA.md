# SkillBridge: 25 High-Probability Viva Questions & Model Answers 🎓

This reference prepares you for rigorous academic and architectural questioning during project defense.

---

### Section 1: Microservices Architecture & Distributed Systems

#### Q1. What is the fundamental difference between a Monolithic and a Microservices architecture, and why did you choose microservices for SkillBridge?
**Answer:** A monolith packages all business domains into a single deployable unit sharing one database. Microservices decompose functionality into autonomous services organized around business capabilities, each with its own database. In SkillBridge, student academic records and career roadmaps belong to the *Skill domain*, while external experiential listings belong to the *Opportunity domain*. Decoupling allows independent deployment, isolated scaling, and prevents an outage in the external catalog from disabling student academic planning.

#### Q2. What is the "Database-per-Service" pattern and why is it critical in microservices?
**Answer:** It mandates that each microservice exclusively owns and manages its private database; no other service can directly access or query its tables/collections. This eliminates runtime database schema coupling, prevents uncoordinated table locks, and ensures failure blast radius isolation. In SkillBridge, `skill-service` owns `skill_db` and `opportunity-service` owns `opportunity_db`. All data exchanges must happen via published REST APIs.

#### Q3. How do you handle relationships across services without database foreign keys?
**Answer:** We store the referenced entity's identifier (`ObjectId` as string) in the dependent document (e.g., student's `career_goal` holds the career ID). Cross-domain aggregation (e.g. merging student skills with matched opportunities) is handled at the application layer via authenticated REST calls rather than database-level `$lookup` or SQL JOINs.

#### Q4. Why did you choose synchronous REST over asynchronous message brokers (e.g., RabbitMQ or Kafka)?
**Answer:** The primary student user journey requires immediate, synchronous feedback (e.g., "Give me my readiness score and ranked opportunities right now"). Synchronous HTTP REST provides low request-response latency, simple debugging, and self-documenting endpoints without the operational overhead of running a dedicated distributed message broker.

#### Q5. What is the Service Registry / Discovery mechanism in your deployment?
**Answer:** In cloud deployment on Render/Docker Compose, discovery is handled via DNS-based environment variables (`OPPORTUNITY_SERVICE_URL`). When services run in containers, internal Docker DNS translates service names (e.g. `http://opportunity-service:5002`) to container IPs.

---

### Section 2: REST APIs & Protocols

#### Q6. What are the key constraints of a RESTful architecture?
**Answer:**
1. Client-Server separation of concerns.
2. Statelessness (each request contains all context needed to execute).
3. Cacheability (responses declare cache headers).
4. Uniform Interface (resource identification via URIs, standard HTTP verbs: GET, POST, PUT, DELETE).
5. Layered System (proxies, gateways, and load balancers can sit between client and server).

#### Q7. What is the idempotency of HTTP methods used in SkillBridge?
**Answer:**
- `GET`: Safe and idempotent (multiple reads produce no side-effects).
- `PUT`: Idempotent (updating a student's skills or stage status multiple times leaves the resource in the exact same state).
- `DELETE`: Idempotent (deleting the same ID repeatedly results in the resource being absent).
- `POST`: Non-idempotent (creating a student creates a new document each time unless guarded by unique index constraints).

#### Q8. What is CORS and how is it secured in production?
**Answer:** Cross-Origin Resource Sharing (CORS) is a browser security mechanism that restricts web applications running at one origin from requesting resources from a different origin. In development, we permit `localhost:5173`. In production, CORS is strictly locked down via the `ALLOWED_ORIGINS` environment variable to only permit requests from our deployed Vercel domain (`https://skillbridge.vercel.app`).

#### Q9. How are API errors formatted and communicated?
**Answer:** Both services implement unified JSON error envelopes: `{"success": false, "error": {"code": "...", "message": "...", "details": ...}}`. HTTP status codes are strictly adhered to: 400 for bad parameters, 404 for missing resources, 409 for duplicate unique fields, 422 for schema validation errors, 502 for upstream failures, and 503 for service/database unavailability.

---

### Section 3: Algorithms & Business Logic

#### Q10. Explain the formula used for the Career Readiness Score.
**Answer:** For each required skill $r_i$ with importance weight $W(r_i) \in [1, 5]$ and required level $L_{req} \in [1, 5]$, we compute the fulfillment ratio $F(r_i) = \min(1.0, L_{cur} / L_{req})$. The readiness score is the weighted average:
$$S_{readiness} = \frac{\sum (W(r_i) \times F(r_i))}{\sum W(r_i)} \times 100$$
This ensures high-importance skills (e.g., core languages) contribute proportionally more to the student's readiness than optional electives.

#### Q11. How does the Learning Roadmap generation algorithm work?
**Answer:** Career skill prerequisites form a Directed Acyclic Graph (DAG). We apply **Kahn's Topological Sorting Algorithm**:
1. Compute in-degrees (number of prerequisites) for all missing/developing skills.
2. Enqueue skills with in-degree 0 (no unfulfilled prerequisites), tie-breaking by career importance descending.
3. Dequeue each skill as a roadmap stage, decrement in-degrees of dependent skills, and enqueue new 0 in-degree skills.
This guarantees students always learn foundational prerequisites before advanced dependent technologies.

#### Q12. Explain the Opportunity Match Scoring logic.
**Answer:** For each open opportunity requiring skills $s_j$:
- Fully met skill ($L_{cur} \ge L_{min}$): Contributes $+1.0$.
- Developing skill ($0 < L_{cur} < L_{min}$): Contributes $+0.5 \times (L_{cur} / L_{min})$.
- Growth skill (missing from student, but required by student's career goal): Awards a $+0.25$ bonus because the opportunity actively closes an academic gap.
- Over-requirement penalty: If requirements exceed student level by $\ge 3$, applies a $-0.15$ penalty.
The sum is normalized over required skills to produce an explainable score between 0 and 100%.

---

### Section 4: Fault Tolerance, Resilience & Cold Starts

#### Q13. What is Graceful Degradation and how is it implemented?
**Answer:** When downstream Opportunity Service is down, Skill Service does not return HTTP 500. Instead, it catches `OpportunityServiceUnavailableError`, preserves the student's local gap analysis and learning roadmaps, sets `recommendations: []`, and returns HTTP `200 OK` with a degraded status notice. The frontend continues functioning smoothly without crashing.

#### Q14. How do you handle Render free-tier cold starts?
**Answer:** Render spins down free containers after 15 minutes of inactivity:
1. **Frontend**: Request interceptors detect latency >2.5s and display an animated banner with a live second counter informing the user that cloud instances are spinning up. Axios timeouts are set to 45 seconds to prevent premature failure.
2. **Backend**: `OpportunityClient` includes a `wake_up()` retry strategy with extended 45-second connection timeouts that pings `/health` and retries requests once the downstream container is active.

#### Q15. What retry strategy is configured for inter-service HTTP requests?
**Answer:** `OpportunityClient` uses an `HTTPAdapter` configured with `urllib3.util.Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])`. Transient network drops and server glitches retry automatically before triggering fallback handling.

---

### Section 5: Database & Indexing

#### Q16. Why did you choose MongoDB over PostgreSQL?
**Answer:** MongoDB's flexible document model natively accommodates polymorphic structures like skill arrays (`[{name, level, updated_at}]`), dynamic learning resources in roadmap stages, and variable opportunity requirement criteria. Nested document updates (`$set`, `$pull`, `$push`) happen in a single atomic document operation without multi-table join locking.

#### Q17. What indexes were created and why?
**Answer:**
- `students`: Unique index on `email` (data integrity), text index on `name`, `college`, `department` (fast search), index on `career_goal`.
- `careers`: Unique index on `slug`, text index on `title`, `description`.
- `roadmaps`: Compound index on `(student_id, career_id)`.
- `opportunities`: Text index on `title`, `description`, `organization`, and single-field indexes on `type`, `mode`, `difficulty`, `status`, and `deadline`.

---

### Section 6: Security & Production Operations

#### Q18. How are internal inter-service endpoints secured?
**Answer:** The internal matching endpoint (`POST /api/opportunities/match`) is guarded by shared-secret authentication. Requests must contain an `X-Service-Key` header matching the environment variable `INTER_SERVICE_KEY`. Direct public access without the key is rejected with HTTP `401 Unauthorized`.

#### Q19. How are credentials and secrets managed?
**Answer:** Secrets are never hardcoded in source control. They are read from environment variables via `python-dotenv` locally and injected via Render/Vercel environment settings in cloud production. `.env` is listed in `.gitignore`.

#### Q20. What is Gunicorn and why isn't the Flask development server used in production?
**Answer:** The built-in Flask Werkzeug server is single-threaded and not designed for concurrent traffic. Gunicorn is a production-grade WSGI HTTP server using a pre-fork worker model (`--workers 2 --timeout 120`) capable of handling concurrent requests, process recycling, and high load.

---

### Section 7: Testing & Quality Assurance

#### Q21. How is the codebase tested?
**Answer:** We use `pytest` with `pytest-cov`, `pytest-flask`, and `mongomock`. Tests verify schema serialization, database CRUD operations, gap analysis math, topological sort edge cases, and client connection failure mocks. All 58 unit tests pass with 86–90% code coverage.

#### Q22. What does `mongomock` do in your test suite?
**Answer:** `mongomock` simulates MongoDB in memory without needing a live MongoDB server or network connection. This makes our test suite blazingly fast (0.8s for 44 tests) and completely deterministic in GitHub Actions CI pipelines.

#### Q23. What is the purpose of `scripts/smoke_test.py`?
**Answer:** It is a post-deployment verification script that runs against live cloud URLs. It tests health endpoints, inter-service status reachability, performs a live student CRUD round-trip, verifies the recommendation engine, and outputs a formatted PASS/FAIL summary table.

---

### Section 8: Scaling & Future Improvements

#### Q24. If student traffic spikes by 100x, how would you scale the system?
**Answer:**
1. **Horizontal Scaling**: Deploy multiple stateless Gunicorn container replicas behind Render/AWS Application Load Balancer.
2. **Caching**: Introduce a Redis cache layer for static career requirements and popular opportunity listings.
3. **Database Sharding**: Enable MongoDB Atlas horizontal sharding on `student_id` and read replicas for search queries.

#### Q25. What would you improve in SkillBridge given more time?
**Answer:**
1. **Authentication**: Implement JWT / OAuth2 (Google & GitHub logins) with role-based access control (Student vs Recruiter vs University Admin).
2. **AI / ML Embeddings**: Use sentence transformers to extract skills directly from student resume PDFs and compute semantic similarity for opportunity matching.
3. **Event-Driven Architecture**: Introduce Kafka/RabbitMQ for asynchronous event publishing (e.g. `StudentSkillUpdatedEvent` triggering background roadmap recalculations).
