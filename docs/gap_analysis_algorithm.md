# Skill Gap Analysis & Roadmap Generation Algorithm

SkillBridge utilizes a **fully deterministic, transparent, and explainable rule-based engine** for student readiness scoring and learning roadmap synthesis.

---

## 1. Skill Gap Classification

For each skill $i$ defined in the target career path:
- $L_{\text{target}, i} \in [1, 5]$: Required proficiency level
- $W_i \in [1, 5]$: Importance weight
- $L_{\text{student}, i} \in [0, 5]$: Student's current proficiency level (0 if the skill is not currently in student profile)

Each skill is categorized into one of three discrete states:

1. **MATCHED**:
   $$\text{Condition: } L_{\text{student}, i} \ge L_{\text{target}, i}$$
   The student has met or exceeded the industry threshold. Gap size = 0.

2. **DEVELOPING**:
   $$\text{Condition: } 0 < L_{\text{student}, i} < L_{\text{target}, i}$$
   The student has initiated learning, but has not achieved the required mastery.
   $$\text{Gap Size} = L_{\text{target}, i} - L_{\text{student}, i}$$

3. **MISSING**:
   $$\text{Condition: } L_{\text{student}, i} = 0$$
   The student lacks exposure to this skill entirely.
   $$\text{Gap Size} = L_{\text{target}, i}$$

---

## 2. Overall Career Readiness Score

The overall readiness score $R \in [0, 100]\%$ measures how prepared a student is for a selected career goal, weighted by the relative importance of each skill:

$$R = \left( \frac{\sum_{i=1}^{N} W_i \cdot \min\left( \frac{L_{\text{student}, i}}{L_{\text{target}, i}}, 1.0 \right)}{\sum_{i=1}^{N} W_i} \right) \times 100$$

### Properties:
- **Monotonicity**: Increasing any student skill level will strictly increase or maintain $R$.
- **Bounded**: Always ranges between $0.0\%$ (no skills acquired) to $100.0\%$ (all requirements satisfied).
- **Proportional Credit**: Partial progress in a high-importance skill yields proportional fractional points.

---

## 3. Category Breakdown (Radar Chart Scores)

For each distinct skill category $C$ (e.g., *Frontend*, *Machine Learning*, *DevOps*):

$$R_C = \left( \frac{\sum_{i \in C} W_i \cdot \min\left( \frac{L_{\text{student}, i}}{L_{\text{target}, i}}, 1.0 \right)}{\sum_{i \in C} W_i} \right) \times 100$$

This produces normalized percentages per category, designed specifically for radial / radar visualization in the UI.

---

## 4. Priority Recommendation Ordering

To determine which skills a student should focus on first, remaining gap skills are sorted using a multi-factor priority comparator:
1. **Status Group**: `MISSING` skills are prioritized before `DEVELOPING` skills to encourage holistic foundational coverage.
2. **Importance Weight**: Within each group, skills with higher $W_i$ appear first.
3. **Gap Size**: If importance is identical, skills with larger gaps ($L_{\text{target}} - L_{\text{student}}$) are given precedence.

---

## 5. Prerequisite-Aware Roadmap Generation (Topological Sort)

A linear learning roadmap must guarantee that prerequisite concepts are mastered before advanced technologies are introduced (e.g., *Python* before *PyTorch*).

### Directed Acyclic Graph (DAG) Model:
- **Nodes**: All skills in `MISSING` $\cup$ `DEVELOPING`.
- **Directed Edges**: An edge $(u \to v)$ indicates skill $u$ is a prerequisite for skill $v$.

### Algorithm (Kahn's BFS):
1. Compute the in-degree $\text{deg}^-(v)$ for every skill in the candidate set (counting only edges between skills that currently have a gap).
2. Initialize queue $Q$ with all skills having $\text{deg}^-(v) = 0$.
3. While $Q$ is not empty:
   - Dequeue skill $u$ and append to roadmap sequence.
   - For each neighbor $v$ dependent on $u$:
     - Decrement $\text{deg}^-(v)$.
     - If $\text{deg}^-(v) = 0$, add $v$ to $Q$.
4. Within each topological depth layer, skills are ordered by $(W_i \text{ DESC}, \text{Gap Size } \text{DESC})$.
5. Any remaining cycle nodes (if circular dependencies ever occur) are safely resolved and appended.

---

## 6. Effort Estimation & Resource Assignment

Each generated stage is assigned:
- **Estimated Weeks**:
  $$\text{Weeks} = f(\text{Gap Size})$$
  $$\{1 \to 2 \text{ weeks}, 2 \to 4 \text{ weeks}, 3 \to 7 \text{ weeks}, 4 \to 11 \text{ weeks}, 5 \to 16 \text{ weeks}\}$$
- **Curated Resources**: 3 vetted learning resources (tutorials, official documentation, video courses) matched from `resources_catalog.json`.
