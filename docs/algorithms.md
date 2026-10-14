# SkillBridge Core Algorithms Specification 🧮

This document outlines the mathematical models, algorithmic designs, and worked numeric examples for the three core engines in **SkillBridge**:

1. **Skill Gap & Career Readiness Algorithm** (`skill-service`)
2. **Topological Learning Roadmap DAG Generator** (`skill-service`)
3. **Multi-Factor Opportunity Match Scoring Algorithm** (`opportunity-service`)

---

## 1. Skill Gap Analysis & Readiness Scoring

### Purpose
Determines how well a student's current skill profile fulfills the prerequisites and required proficiencies of a targeted career path.

### Mathematical Formulation
For a target career with required skills $R = \{r_1, r_2, \dots, r_n\}$:
- Each required skill $r_i$ has a required proficiency level $L_{req}(r_i) \in [1, 5]$ and an importance weight $W(r_i) \in [1, 5]$.
- The student has a current proficiency level $L_{cur}(r_i) \in [0, 5]$ (where $0$ indicates skill is missing).

The **Skill Fulfillment Ratio** $F(r_i)$ is clamped between 0 and 1:
$$F(r_i) = \min\left(1.0, \frac{L_{cur}(r_i)}{L_{req}(r_i)}\right)$$

The overall **Career Readiness Score** $S_{readiness} \in [0, 100]$ is the weighted average fulfillment:
$$S_{readiness} = \frac{\sum_{i=1}^{n} \Big( W(r_i) \times F(r_i) \Big)}{\sum_{i=1}^{n} W(r_i)} \times 100$$

### Skill Categorization
- **Matched**: $L_{cur}(r_i) \ge L_{req}(r_i)$
- **Developing**: $0 < L_{cur}(r_i) < L_{req}(r_i)$ (Deficit = $L_{req}(r_i) - L_{cur}(r_i)$)
- **Missing**: $L_{cur}(r_i) == 0$

### Worked Numeric Example
Consider a student targeting **Full Stack Developer** with 4 required skills:

| Skill | Required Level ($L_{req}$) | Importance ($W$) | Student Level ($L_{cur}$) | Fulfillment Ratio ($F$) | Weighted Score ($W \times F$) | Status |
|---|---|---|---|---|---|---|
| **JavaScript** | 4 | 5 | 4 | $\min(1, 4/4) = 1.0$ | $5 \times 1.0 = 5.0$ | Matched |
| **React** | 4 | 4 | 2 | $\min(1, 2/4) = 0.5$ | $4 \times 0.5 = 2.0$ | Developing |
| **Node.js** | 3 | 4 | 3 | $\min(1, 3/3) = 1.0$ | $4 \times 1.0 = 4.0$ | Matched |
| **Docker** | 3 | 3 | 0 | $\min(1, 0/3) = 0.0$ | $3 \times 0.0 = 0.0$ | Missing |
| **Total** | — | **$\sum W = 16$** | — | — | **$\sum (W \times F) = 11.0$** | — |

$$\text{Readiness Score} = \frac{11.0}{16.0} \times 100 = 68.75\% \approx 69\%$$

---

## 2. Learning Roadmap Topological DAG Sequencing

### Purpose
Orders a student's missing and developing skills into a linear, non-conflicting learning path that respects skill dependency hierarchies (e.g., *Linux Basics* must precede *Docker*, which must precede *Kubernetes*).

### Algorithmic Design: Kahn's Algorithm
1. **Graph Construction**: Construct a Directed Acyclic Graph (DAG) $G = (V, E)$, where vertices $V$ are skills needing improvement ($L_{cur} < L_{req}$) and directed edges $(u, v) \in E$ represent "$u$ is a prerequisite for $v$".
2. **In-Degree Calculation**: Compute in-degree $\text{deg}^-(v)$ for every vertex.
3. **Queue Processing**:
   - Initialize a FIFO queue with all vertices having $\text{deg}^-(v) == 0$ (no unsatisfied prerequisites).
   - While queue is non-empty:
     - Dequeue skill $u$ and append to roadmap stages.
     - For each neighbor $v$ of $u$: decrement $\text{deg}^-(v)$. If $\text{deg}^-(v) == 0$, enqueue $v$.
4. **Tie-Breaking**: If multiple skills have zero in-degree, prioritize by **Career Importance ($W$)** descending.
5. **Cycle Detection**: If processed vertices count $< |V|$, a circular dependency exists; unresolved skills are safely appended at the end.

### Worked Numeric Example
Target skills needing improvement:
- $V_1$: **Docker** (Requires *Linux Basics*, Importance: 4)
- $V_2$: **Linux Basics** (No prerequisite, Importance: 3)
- $V_3$: **Kubernetes** (Requires *Docker*, Importance: 5)
- $V_4$: **PostgreSQL** (No prerequisite, Importance: 4)

**Execution Trace:**
1. In-degrees:
   - $\text{deg}^-(\text{Linux Basics}) = 0$
   - $\text{deg}^-(\text{PostgreSQL}) = 0$
   - $\text{deg}^-(\text{Docker}) = 1$
   - $\text{deg}^-(\text{Kubernetes}) = 1$
2. Queue initially: `[PostgreSQL (W=4), Linux Basics (W=3)]` (sorted by importance).
3. **Stage 1**: Dequeue `PostgreSQL`.
4. **Stage 2**: Dequeue `Linux Basics`. Decrement `Docker` in-degree $\to 0$. Enqueue `Docker`.
5. **Stage 3**: Dequeue `Docker`. Decrement `Kubernetes` in-degree $\to 0$. Enqueue `Kubernetes`.
6. **Stage 4**: Dequeue `Kubernetes`.

**Resulting Roadmap**:
`Stage 1: PostgreSQL` $\to$ `Stage 2: Linux Basics` $\to$ `Stage 3: Docker` $\to$ `Stage 4: Kubernetes`.

---

## 3. Multi-Factor Opportunity Match Scoring

### Purpose
Ranks open internships, hackathons, and projects by computing an explainable compatibility score $S_{match} \in [0, 100]$ based on current skills, developing skills, and missing skills.

### Mathematical Formulation
For an opportunity requiring skills $O_{req} = \{s_1, \dots, s_m\}$, each requiring minimum level $L_{min}(s_j)$:

1. **Skill Contribution Score ($C_j$)**:
   - **Full Match**: If student has $s_j$ with $L_{cur}(s_j) \ge L_{min}(s_j)$:
     $$C_j = 1.0$$
   - **Developing Skill**: If student has $s_j$ with $0 < L_{cur}(s_j) < L_{min}(s_j)$:
     $$C_j = 0.5 \times \frac{L_{cur}(s_j)}{L_{min}(s_j)}$$
   - **Growth Opportunity Bonus**: If student lacks $s_j$ ($L_{cur} == 0$), but $s_j$ is in their career *missing skills* list (opportunity teaches a needed gap):
     $$C_j = +0.25$$
   - **Irrelevant Missing Skill**: If student lacks $s_j$ and it is not in their career gap:
     $$C_j = 0.0$$

2. **Over-Requirement Penalty ($P_j$)**:
   If an opportunity requires advanced mastery far exceeding student ability ($L_{min}(s_j) - L_{cur}(s_j) \ge 3$):
   $$P_j = 0.15$$

3. **Composite Match Score**:
   $$S_{match} = \max\left(0.0, \min\left(100.0, \frac{\sum (C_j - P_j)}{m} \times 100\right)\right)$$

### Worked Numeric Example
Student Skills: `Python (Lv. 3)`, `SQL (Lv. 2)`. Career Missing: `[Docker, AWS]`.

Opportunity: **Backend Engineering Intern** ($m = 3$ required skills):
1. **Python** ($L_{min} = 3$): Student level 3 $\ge$ 3 $\implies$ Full match $\to C_1 = 1.0, P_1 = 0.0$.
2. **SQL** ($L_{min} = 3$): Student level 2 < 3 $\implies$ Developing skill $\to C_2 = 0.5 \times (2/3) \approx 0.333, P_2 = 0.0$.
3. **Docker** ($L_{min} = 2$): Student level 0, but Docker is in career missing skills $\implies$ Growth bonus $\to C_3 = +0.25, P_3 = 0.0$.

$$\sum (C_j - P_j) = 1.0 + 0.333 + 0.25 = 1.583$$
$$S_{match} = \frac{1.583}{3} \times 100 = 52.77\% \approx 53\%$$

**Explanation String Generated:**
*"Strong match on Python (Lv. 3). Opportunity provides practical experience to advance SQL and learn Docker."*
