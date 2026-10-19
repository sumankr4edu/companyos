[README.md](https://github.com/user-attachments/files/33663831/README.1.md)
# CompanyOS — The Graph-Native Company Brain

> **Your company's knowledge, connected.**  
> **Ask your company. Follow the graph. Get the evidence.**

CompanyOS is a graph-native AI company knowledge system built around **FalkorDB**. It connects people, teams, projects, services, incidents, decisions, documents, ownership, dependencies, memory, and actions into one queryable company graph.

Instead of treating company knowledge as disconnected documents or isolated vector-search results, CompanyOS uses relationships as first-class context. AI agents can traverse those relationships, explain the evidence path, preserve memory, detect contradictions, coordinate work, and turn investigations into auditable actions.

---

## ✨ What CompanyOS Does

CompanyOS answers questions that require connected organizational context:

- Who knows the most about a system?
- Who owns this service?
- What depends on this service?
- What breaks if this service goes down?
- Why was this architecture changed?
- Which people worked on the affected system before?
- Which incidents are connected to this problem?
- What decision caused the current architecture?
- Who should investigate an issue?
- What did we discover in a previous investigation?

The system is designed for **multi-hop graph reasoning**, not simple keyword retrieval.

### Example

> **Checkout failures increased this week. What happened, who worked on the affected system before, what decision caused the current architecture, and who should investigate it?**

A typical reasoning path can connect:

```text
Checkout Service
      │
      └── DEPENDS_ON ──> Payment Service
                              │
                              ├── OWNS ──> Maya Singh
                              │
                              └── PRODUCES <── Payment Service Migration
                                                  │
                                                  ├── IMPLEMENTED_BY ──> Decision
                                                  │                         │
                                                  │                         └── MADE_BY ──> Alice Chen
                                                  │
                                                  └── historical context
```

CompanyOS does **not** invent missing graph relationships. If the graph cannot establish a fact, the response reports the unknown explicitly.

---

# 🧠 Why FalkorDB Is Central

FalkorDB is not a decorative persistence layer. It is the **context and reasoning layer** of CompanyOS.

It is used for:

- Entity relationships
- Multi-hop traversal
- Dependency analysis
- Ownership analysis
- Graph search
- Shortest-path reasoning
- Connected components
- Centrality / PageRank-style analysis
- Organizational memory
- Agent coordination state
- Investigation and action history
- Provenance and evidence
- Tenant-isolated company graphs

```text
                    ┌──────────────────────┐
                    │      User / UI       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   AI Command Center  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Orchestrator     │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ Graph Agent │   │Memory Agent │   │ Action Agent│
      └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │       FalkorDB       │
                    │  Company Knowledge   │
                    │       Graph          │
                    └──────────────────────┘
```

If FalkorDB is removed, the core graph-grounded reasoning capability is removed with it.

---

# 🏗️ Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                         CompanyOS UI                          │
│ Dashboard │ AI Command Center │ Graph Explorer │ Actions     │
└───────────────────────────────┬───────────────────────────────┘
                                │ HTTP
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                       │
│ Chat │ Graph │ Memory │ Actions │ Agents │ MCP                │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         Orchestrator                          │
│ Intent → Entities → Relationships → Cypher → Validation       │
│        → FalkorDB → Evidence → Reasoning → Answer             │
└───────────────┬─────────────────┬─────────────────────────────┘
                │                 │
        ┌───────▼───────┐ ┌──────▼────────┐
        │  Graph Agent  │ │ Memory Agent  │
        └───────┬───────┘ └──────┬────────┘
                │                 │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │    FalkorDB     │
                │ Graph + Memory  │
                │ + Agent State   │
                └────────┬────────┘
                         ▲
                  ┌──────┴──────┐
                  │ Action Agent│
                  └─────────────┘
```

## Controlled Graph Query Planning

```text
User Question
      │
      ▼
Intent Detection
      │
      ▼
Entity Extraction
      │
      ▼
Relationship Planning
      │
      ▼
Cypher Generation
      │
      ▼
Cypher Validation
      │
      ▼
FalkorDB
      │
      ▼
Result Graph
      │
      ▼
Evidence Normalization
      │
      ▼
Reasoning
      │
      ▼
Answer + Evidence + Graph Path
```

The query generator uses bounded, entity-constrained Cypher rather than unrestricted graph scans.

---

# 🕸️ Graph Ontology

## Core entities

```text
Company
Person
Role
Team
Department
Project
Document
Decision
ADR
Policy
SOP
Conversation
Message
Channel
Repository
Service
API
Database
Infrastructure
Deployment
Incident
Ticket
```

## Core relationships

```text
MEMBER_OF       REPORTS_TO       WORKED_ON
OWNS            DEPENDS_ON       PRODUCES
AFFECTS         AUTHORED         REFERENCES
DESCRIBES       MADE_BY          SUPERSEDES
POSTED          MENTIONS         CONTRIBUTED_TO
IMPLEMENTS      CALLS            DEPLOYED
RESOLVED
```

These relationships represent organizational structure, technical architecture, knowledge, decisions, and incident history.

---

# 🔎 Multi-Hop Reasoning

Example:

```text
Checkout Service
      │ DEPENDS_ON
      ▼
Payment Service
      │
      ▼
Payment Service Migration
      │ IMPLEMENTED_BY
      ▼
Architecture Decision
      │ MADE_BY
      ▼
Alice Chen
```

The reasoning layer distinguishes:

- Known facts
- Graph evidence
- Inferred connections
- Unknowns
- Contradictions

This prevents unsupported claims from being presented as graph facts.

---

# 📚 Evidence, Provenance & Explainability

Graph-grounded responses can expose:

```text
Answer
Evidence
Graph Path
Reasoning Summary
Confidence
Unknowns
Contradictions
Freshness
```

Typical provenance fields include:

```text
source_id
source_type
source_url
document_id
author
created_at
updated_at
confidence
```

Evidence is normalized, deduplicated, ranked, and bounded before being returned to the reasoning layer.

---

# ⚠️ Contradiction & Freshness Detection

CompanyOS treats inconsistent data as a useful signal.

For example:

```text
Maya Singh ──OWNS──> Payment Service
Amit Chen  ──OWNS──> Payment Service
```

Rather than silently choosing one owner, the graph layer can identify this as a data-quality contradiction. Duplicate records are deduplicated while distinct conflicting relationships remain visible.

Evidence timestamps such as `updated_at`, `modified_at`, `created_at`, and `timestamp` can be analyzed as **fresh, stale, or unknown**.

---

# 🧠 Persistent Memory

CompanyOS stores memory in the graph instead of treating every chat session as isolated.

### Episodic memory
What happened during a previous interaction or investigation.

### Semantic memory
Facts learned about the company and its entities.

### Procedural memory
Reusable procedures, workflows, and operational knowledge.

```text
Conversation → Memory → Future Question → Graph + Memory → Better Context
```

---

# 🤖 Multi-Agent Coordination

Graph-native coordination uses persistent entities such as:

```text
AgentRun
AgentTask
AgentEvent
AgentMessage
```

Conceptually:

```text
AgentRun
 ├── HAS_TASK ──> AgentTask
 ├── HAS_EVENT ──> AgentEvent
 └── HAS_MESSAGE ──> AgentMessage
```

The coordination layer supports run creation, task creation/update, events, messages, pending tasks, status, resumption, and agent handoff.

---

# 🔌 MCP / Graph Tools

The graph tool layer includes:

```text
falkor_search
falkor_traverse
falkor_cypher
falkor_shortest_path
falkor_neighbors
falkor_subgraph
falkor_write
```

Graph tools follow the application's authorization and Cypher safety model. Arbitrary graph mutation is not treated as an unrestricted client capability.

---

# 📊 Graph Algorithms

CompanyOS supports or is designed around:

- Centrality
- Shortest path
- Community detection
- Connected components
- PageRank-style ranking
- Dependency traversal
- Neighborhood exploration

Example: **"Who knows the most about Payment Service?"** can use graph relationships such as `OWNS`, `WORKED_ON`, and `CONTRIBUTED_TO` instead of relying only on text similarity.

---

# 🔐 Security

## Tenant isolation

Each company uses its own graph namespace:

```text
Company A → graph_a
Company B → graph_b
Company C → graph_c
```

Cross-tenant graph access is rejected.

## Permissions

Example permissions include:

```text
graph:read
graph:write
memory:read
memory:write
actions:read
actions:create
```

## Cypher protection

The validator blocks dangerous operations including:

```text
CREATE, DELETE, DETACH DELETE, SET, REMOVE, MERGE, DROP,
LOAD CSV, CALL DBMS, CALL DB, CALL APOC, FOREACH,
ALTER, GRANT, REVOKE
```

It also rejects multiple statements, comment-based manipulation, oversized queries, and inappropriate non-read graph operations.

## Action authorization

Action actors are derived from the authenticated user context rather than trusted from a client-supplied actor ID.

---

# 🏢 NovaTech Demo Dataset

The project includes a synthetic NovaTech company graph.

| Entity | Count |
|---|---:|
| People | 126 |
| Teams | 24 |
| Projects | 32 |
| Services | 54 |
| Documents | 100 |
| Incidents | 102 |
| Decisions | 202 |
| Relationships | 1338 |

The dataset is synthetic and designed for graph reasoning demonstrations.

---

# 🎯 Demo Questions

The primary demo flow includes:

1. **Who knows the most about the payment system?** — expertise and ownership.
2. **Why was the payment architecture changed?** — decision and implementation lineage.
3. **What happens if Payment Service goes down?** — dependency and blast radius.
4. **Who should investigate the checkout failures?** — incident and ownership context.
5. **Checkout failures increased this week. What happened, who worked on the affected system before, what decision caused the current architecture, and who should investigate it?** — combined multi-hop investigation.

The latest validated demo run completed **5/5 questions successfully**.

---

# 🖥️ Product Interface

The frontend is designed as a futuristic enterprise AI interface with a dark, graph-centric visual language.

Core experiences:

```text
Dashboard
AI Command Center
Graph Explorer
Reasoning Panel
Memory
Actions
```

The interface emphasizes graph visualization, evidence paths, relationship exploration, confidence/unknown states, and auditable actions.

---

# 🚀 Getting Started

## Prerequisites

- Docker Desktop
- Python 3.11+
- Node.js / npm
- Git
- Gemini API key (or another configured LLM provider)

## 1. Start FalkorDB

From the project root:

```powershell
docker compose up -d
docker ps
```

FalkorDB is exposed on `localhost:6379`.

## 2. Backend setup

```powershell
cd C:\Users\KIIT\Downloads\companyOs\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Environment variables

Example:

```env
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=
FALKORDB_PASSWORD=

LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.8-flash
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

Never commit real secrets.

## 4. Seed NovaTech

```powershell
cd C:\Users\KIIT\Downloads\companyOs\backend
python seed_novatech.py
```

Verify the graph:

```powershell
python -c "from graph.client import graph_client; print(graph_client.query('MATCH (n) RETURN count(n) AS count', 'novatech').result_set)"
```

## 5. Start the backend

```powershell
uvicorn main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## 6. Start the frontend

```powershell
cd C:\Users\KIIT\Downloads\companyOs\frontend
npm install
npm run dev
```

Set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# 🧪 Testing

Run the full backend suite:

```powershell
cd C:\Users\KIIT\Downloads\companyOs\backend
pytest -v
```

Phase 28 E2E coverage includes:

```text
Health
Graph connectivity
NovaTech graph
Graph query
Chat orchestrator
Payment multi-hop path
Payment ownership
Agent run creation
Memory endpoint
Actions endpoint
Tenant isolation
Cypher write protection
Multiple statement protection
Read-only authorization
Coordination graph structure
```

Validated result: **15 passed**.

## Performance

```powershell
pytest .\tests\test_phase29_performance.py -v -s
```

Validated results:

```text
Graph query latency:          ~0.0023s
Payment dependency latency:   ~0.0022s
Ownership ranking latency:    ~0.0027s
Bounded multi-hop latency:    ~0.0154s
Chat latency:                 ~11.36s
Bounded graph results:        50 rows maximum in the test
```

The raw FalkorDB operations are fast; natural-language chat latency is primarily LLM/orchestration work.

---

# 🔍 Example Cypher

## Payment Service ownership/expertise

```cypher
MATCH (service:Service {name: 'Payment Service'})
OPTIONAL MATCH
    (person:Person)-[
        r:OWNS|WORKED_ON|CONTRIBUTED_TO
    ]->(service)
RETURN DISTINCT
    person.name AS person,
    type(r) AS relationship,
    service.name AS entity
LIMIT 25
```

## Architecture decision lineage

```cypher
MATCH (service:Service {name:'Payment Service'})
OPTIONAL MATCH
    (migration:Project)-[migration_rel:PRODUCES|IMPLEMENTS|AFFECTS]->(service)
OPTIONAL MATCH
    (migration)-[decision_rel:IMPLEMENTED_BY|PRODUCES|AFFECTS]->(decision:Decision)
OPTIONAL MATCH
    (decision)-[person_rel:MADE_BY|AUTHORED|REFERENCES]->(person:Person)
RETURN DISTINCT
    migration.name AS migration,
    type(migration_rel) AS migration_relationship,
    decision.title AS decision,
    type(decision_rel) AS decision_relationship,
    person.name AS person,
    type(person_rel) AS person_relationship
LIMIT 25
```

The application constrains generated queries by intent, entities, safety validation, and result bounds before execution.

---

# 🔄 API Overview

Important API areas:

### Chat

```text
POST /api/chat
```

### Graph

```text
/api/graph/query
/api/graph/traverse
/api/graph/entity/{id}
/api/graph/path
```

### Companies

```text
/api/companies
/api/companies/{id}/ingest
/api/companies/{id}/overview
/api/companies/{id}/graph
```

### Memory

```text
/api/memory/*
```

### Actions

```text
/api/actions/*
```

### Agent coordination

```text
/api/agents/runs
/api/agents/runs/{run_id}
/api/agents/runs/{run_id}/tasks
/api/agents/runs/{run_id}/events
/api/agents/runs/{run_id}/resume
```

### MCP

```text
/api/mcp/*
```

---

# 🗂️ Project Structure

Representative structure:

```text
companyOs/
│
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── query_planner.py
│   │   ├── cypher_generator.py
│   │   ├── llm.py
│   │   ├── contradiction_agent.py
│   │   ├── freshness_agent.py
│   │   ├── coordination.py
│   │   └── agent_handoff.py
│   │
│   ├── api/
│   │   ├── chat.py
│   │   ├── graph.py
│   │   ├── memory.py
│   │   ├── actions.py
│   │   ├── agents.py
│   │   └── mcp.py
│   │
│   ├── graph/
│   │   ├── client.py
│   │   ├── evidence.py
│   │   └── contradictions.py
│   │
│   ├── security/
│   │   ├── context.py
│   │   ├── tenant.py
│   │   └── cypher_validator.py
│   │
│   ├── mcp/
│   │   ├── registry.py
│   │   ├── graph_tools.py
│   │   └── tool_agent.py
│   │
│   ├── data_generator/
│   │   └── novatech_generator.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_phase28_e2e.py
│   │   └── test_phase29_performance.py
│   │
│   ├── seed_novatech.py
│   └── main.py
│
├── frontend/
├── docker-compose.yml
├── .env
└── README.md
```

---

# 🧭 Engineering Principles

1. **Graph first** — relationships are part of the answer.
2. **Evidence first** — conclusions should be traceable.
3. **Unknowns are valid** — unsupported facts are not invented.
4. **Bounded reasoning** — queries and evidence are bounded.
5. **Secure by default** — tenant isolation, authorization, and Cypher validation.
6. **Persistent state** — memory and coordination survive process boundaries.
7. **Auditable actions** — investigations leave graph state behind.
8. **Visible data quality** — contradictions and stale evidence are surfaced.

---

# 🏆 Hackathon Track Alignment

## Company Brain

CompanyOS is designed as a **Company Brain** that connects:

```text
People + Teams + Projects + Services + Incidents
+ Decisions + Documents + Memory + Actions
```

Traditional enterprise search asks:

> Find documents mentioning Payment Service.

CompanyOS aims to answer:

> Who owns Payment Service, who worked on it before, which systems depend on it, what decision created its current architecture, which incidents affected it, and what should we investigate next?

The graph is the central context layer that makes this possible.

---

# 🎬 3-Minute Demo Script

### 0:00 — Problem

> Company knowledge is fragmented across people, systems, documents, incidents, and decisions.

### 0:20 — Expertise

Ask:

```text
Who knows the most about the payment system?
```

Show people, relationships, and evidence.

### 0:50 — Decision lineage

Ask:

```text
Why was the payment architecture changed?
```

Show:

```text
Payment Service
      ↑
Payment Service Migration
      │
      ▼
Architecture Decision
      │
      ▼
Alice Chen
```

Explain that the graph distinguishes known implementation history from an unsupported rationale.

### 1:20 — Blast radius

Ask:

```text
What happens if Payment Service goes down?
```

Show dependency relationships.

### 1:50 — Investigation

Ask:

```text
Who should investigate the checkout failures?
```

Show incident evidence, ownership context, and explicit uncertainty when no official investigator is recorded.

### 2:15 — Action

Create an investigation task and show that it becomes auditable graph state.

### 2:35 — Memory

Ask:

```text
What did we discover?
```

Demonstrate persistent investigation context.

### 2:50 — Close

> CompanyOS doesn't just search company knowledge. It follows the relationships between people, systems, incidents, decisions, and actions to build an evidence-backed answer.

---

# 📈 Evaluation Philosophy

The system is designed around:

```text
Multi-hop reasoning
Memory
Ownership
Dependencies
Decisions
Contradictions
Actions
```

A useful evaluation set can contain:

```text
30 multi-hop questions
20 memory questions
20 ownership questions
20 dependency questions
10 decision questions
10 contradiction questions
10 action questions
```

Evaluation should measure whether the system:

1. Finds relevant graph entities.
2. Traverses correct relationships.
3. Produces evidence.
4. Preserves uncertainty.
5. Detects contradictions.
6. Uses persistent context.
7. Produces safe, auditable actions.

---

# 🛠️ Demo Reliability Checklist

Before a live demo:

```powershell
docker ps
```

Then:

```powershell
curl http://127.0.0.1:8000/health
```

Run E2E tests:

```powershell
pytest .\tests\test_phase28_e2e.py -v
```

Run performance validation:

```powershell
pytest .\tests\test_phase29_performance.py -v -s
```

Run the demo:

```powershell
python demo_phase30.py
```

Latest validated demo status:

```text
5 questions
5 successful
0 failed
```

---

# 🤖 AI-Assisted Development

AI coding assistants were used during development. Generated code was iteratively tested and verified against the actual CompanyOS architecture, FalkorDB behavior, security model, APIs, graph reasoning, and test suite.

Key areas were manually reviewed and validated, including:

- Graph ontology
- Cypher generation
- Tenant isolation
- Cypher safety
- Evidence normalization
- Contradiction detection
- Freshness analysis
- Agent coordination
- Memory persistence
- Action authorization
- End-to-end tests
- Demo reliability

The intent is to use AI assistance while maintaining understanding and verification of the implementation.

---

# 📜 Data & Privacy

The NovaTech dataset is synthetic. No private company dataset is required for the demo.

Do not commit:

```text
.env
API keys
credentials
private datasets
production secrets
```

Use environment variables for secrets.

---

# 🔮 Future Extensions

Potential extensions include:

- Document and enterprise connector ingestion
- Automatic graph extraction
- Richer graph algorithms
- Automated incident investigation
- Dependency-aware incident prediction
- Decision lineage visualization
- Organizational knowledge maps
- Human approval workflows
- Temporal graph reasoning
- Fine-grained graph authorization
- Production-scale graph partitioning

---

# 👤 Author

**Suman Kumar**

GitHub: https://github.com/sumankr4edu/vibecodearenaai

LinkedIn: https://www.linkedin.com/in/suman-kumar-8698ab249/

---

# ⭐ Final Takeaway

> **CompanyOS turns a company's scattered knowledge into a connected, explainable graph that AI agents can actually reason over.**

```text
Don't just ask the company.

Follow the graph.
Get the evidence.
Understand the context.
Remember what happened.
Act on what you discover.
```

**CompanyOS — Your company's knowledge, connected.**
