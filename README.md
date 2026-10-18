[README.md](https://github.com/user-attachments/files/33635263/README.md)
# CompanyOS --- The Graph-Native Company Brain

> **Your company's knowledge, connected.**\
> **Ask your company. Follow the graph. Get the evidence.**

CompanyOS is a graph-native company intelligence platform built around
**FalkorDB**. It connects people, teams, projects, services, incidents,
documents, architectural decisions, dependencies, ownership, and
organizational knowledge into one traversable company graph.

Instead of returning isolated search results, CompanyOS uses graph
traversal, graph algorithms, persistent memory, and agent orchestration
to answer multi-hop questions with **evidence, graph paths, confidence,
contradictions, and unknowns**.

------------------------------------------------------------------------

## Why CompanyOS?

Company knowledge is usually fragmented across documentation, tickets,
repositories, incident reports, conversations, architecture decisions,
and individual expertise.

A question such as:

> "Checkout failures increased. What happened, who worked on the
> affected system, why was the architecture changed, and who should
> investigate?"

is not a simple keyword-search problem.

It requires connecting multiple entities:

``` text
Checkout Service
      ↓ DEPENDS_ON
Payment Service
      ↓ INVOLVES
Incident
      ↓
Payment Migration
      ↓ IMPLEMENTED_BY
Architecture Decision
      ↓ MADE_BY
Engineer
      ↓
Current Owner
```

CompanyOS makes these relationships first-class graph data.

------------------------------------------------------------------------

## Core Features

-   Natural-language company knowledge search
-   Graph-first AI reasoning
-   Multi-hop relationship traversal
-   FalkorDB-powered Cypher queries
-   Expertise and ownership discovery
-   Dependency analysis and blast-radius analysis
-   Centrality and connected-component analysis
-   Architectural decision tracing
-   Incident investigation
-   Persistent agent memory
-   Conversation state
-   Evidence and provenance
-   Contradiction detection
-   Freshness awareness
-   Explainable graph paths
-   Investigation actions and task tracking
-   Multi-agent orchestration
-   Interactive graph visualization
-   Secure Cypher validation
-   Tenant isolation architecture
-   API and end-to-end testing

------------------------------------------------------------------------

# Architecture

``` text
                         ┌─────────────────────────┐
                         │       Next.js UI        │
                         │                         │
                         │ AI Command Center       │
                         │ Graph Explorer          │
                         │ Evidence / Reasoning    │
                         │ Investigation Actions   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │        FastAPI          │
                         │       REST API          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Orchestrator       │
                         └────────────┬────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
      ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
      │ Graph Agent  │        │ Memory Agent │        │ Action Agent │
      └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     ▼
                         ┌─────────────────────────┐
                         │        FalkorDB         │
                         │                         │
                         │ Company Graph           │
                         │ Memory                  │
                         │ Evidence                │
                         │ Actions                 │
                         │ Agent State             │
                         │ Audit Trail             │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
             │  Evidence   │  │  Analysis   │  │Explainability│
             │   Layer     │  │    Agent    │  │    Layer     │
             └─────────────┘  └─────────────┘  └──────────────┘
```

## Graph-First Reasoning Pipeline

``` text
User Question
      ↓
Intent Detection
      ↓
Entity Extraction
      ↓
Relationship Planning
      ↓
Cypher Generation
      ↓
Cypher Validation
      ↓
FalkorDB
      ↓
Graph Evidence
      ↓
Graph Algorithms / Traversal
      ↓
Memory + Context
      ↓
AI Analysis
      ↓
Evidence + Graph Path + Confidence
      ↓
Answer / Action
```

The LLM is used for language understanding and synthesis. **FalkorDB is
the source of connected company evidence.**

------------------------------------------------------------------------

# Why FalkorDB?

FalkorDB is not a decorative database in CompanyOS.

It is the central context and reasoning layer.

The company is represented as a graph of nodes and relationships,
allowing CompanyOS to answer questions that depend on multiple connected
entities.

Examples:

``` text
Person ──WORKED_ON──> Project
Person ──OWNS───────> Service
Service ──DEPENDS_ON─> Service
Service ──INVOLVES──> Incident
Decision ──MADE_BY──> Person
Migration ──PRODUCES─> Service
```

This enables:

-   Multi-hop reasoning
-   Dependency traversal
-   Ownership discovery
-   Expertise ranking
-   Incident investigation
-   Decision tracing
-   Centrality analysis
-   Connected-component exploration
-   Shortest-path analysis
-   Persistent graph-based memory
-   Shared agent state

If FalkorDB were removed, the core reasoning capability of CompanyOS
would no longer work.

------------------------------------------------------------------------

# Graph Ontology

## Main Entities

CompanyOS models entities including:

-   Company
-   Person
-   Role
-   Team
-   Department
-   Project
-   Document
-   Decision
-   ADR
-   Policy
-   SOP
-   Conversation
-   Message
-   Channel
-   Repository
-   Service
-   API
-   Database
-   Infrastructure
-   Deployment
-   Incident
-   Ticket

## Relationships

Important relationships include:

``` text
MEMBER_OF
REPORTS_TO
WORKED_ON
OWNS
DEPENDS_ON
PRODUCES
AFFECTS
AUTHORED
REFERENCES
DESCRIBES
MADE_BY
SUPERSEDES
POSTED
MENTIONS
CONTRIBUTED_TO
IMPLEMENTS
CALLS
DEPLOYED
RESOLVED
```

------------------------------------------------------------------------

# Example Investigation

CompanyOS contains a synthetic NovaTech company graph.

A representative investigation asks:

> "Checkout failures increased this week. What happened, who worked on
> the affected system before, what decision caused the current
> architecture, and who should investigate it?"

The system can establish evidence such as:

``` text
Payment Service
    ├── INVOLVES ──> Checkout failures increased
    ├── DEPENDS_ON ─> Checkout Service
    └── OWNS ──────> Maya Singh

Payment Service Migration
    ├── PRODUCES ───> Payment Service
    └── IMPLEMENTED_BY ─> Architecture Decision

Architecture Decision
    └── MADE_BY ───> Alice Chen
```

CompanyOS deliberately does **not** fabricate relationships that do not
exist in FalkorDB.

For example, if the graph does not establish a direct:

``` text
Incident ──> Migration
```

relationship, the system reports that as an unknown instead of inventing
a path.

------------------------------------------------------------------------

# Graph Intelligence

## Expertise Ranking

CompanyOS can rank people based on graph relationships such as:

``` text
OWNS          → 10
WORKED_ON     → 8
CONTRIBUTED_TO→ 7
INVOLVES      → 5
AUTHORED      → 4
MEMBER_OF     → 1
```

This allows questions such as:

> "Who knows the most about the payment system?"

to be answered using graph evidence.

## Dependency Blast Radius

For:

> "What happens if Payment Service goes down?"

CompanyOS traverses dependency relationships to identify potentially
affected systems.

## Centrality

Centrality can identify highly connected people and systems in the
company graph.

## Connected Components

The system can explore the connected neighborhood around an entity.

## Path Discovery

Graph paths expose how entities are connected rather than returning only
a final answer.

------------------------------------------------------------------------

# Explainability

Every important AI response is designed around:

``` text
ANSWER
EVIDENCE
GRAPH PATH
CONTRADICTIONS
CONFIDENCE
UNKNOWNS
```

Example:

``` text
ANSWER:
Maya Singh is the current owner of Payment Service.

EVIDENCE:
Payment Service → OWNS → Maya Singh

GRAPH PATH:
Payment Service → INVOLVES → Checkout failures increased

CONFIDENCE:
0.91

UNKNOWNS:
No direct Incident → Migration relationship was established.
```

The system exposes concise, auditable reasoning rather than private
model chain-of-thought.

------------------------------------------------------------------------

# Persistent Memory

CompanyOS uses FalkorDB as a persistent context layer for agents.

Memory is organized conceptually into:

``` text
Episodic Memory
    ↓
What happened?

Semantic Memory
    ↓
What do we know?

Procedural Memory
    ↓
How should we do it?
```

Conversation context, useful evidence, investigation outcomes, and agent
state can remain available across sessions.

------------------------------------------------------------------------

# Agent Architecture

CompanyOS separates responsibilities between specialized agents.

``` text
Orchestrator
 ├── Query Planner
 ├── Graph Intelligence Agent
 ├── Graph Path Engine
 ├── Memory Agent
 ├── Evidence Manager
 ├── Analysis Agent
 ├── Explainability Agent
 └── Action Agent
```

The graph acts as the shared context layer.

This prevents every agent from maintaining an isolated view of company
knowledge.

------------------------------------------------------------------------

# Security

CompanyOS includes security controls designed around graph access:

-   Authenticated user context
-   Tenant isolation
-   Graph access authorization
-   Read/write separation
-   Cypher validation
-   Restricted mutation queries
-   Prompt-injection awareness
-   Security headers
-   Request IDs
-   Action authorization
-   Audit-oriented action history

Read-only graph queries are validated before execution.

Dangerous Cypher operations such as unrestricted `CREATE`, `DELETE`,
`DROP`, `MERGE`, `SET`, `REMOVE`, `LOAD CSV`, and sensitive procedure
calls are blocked by the validation layer.

------------------------------------------------------------------------

# Technology Stack

## Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   Interactive graph visualization
-   `react-force-graph-2d`

## Backend

-   Python
-   FastAPI
-   Pydantic
-   Uvicorn

## AI

-   Google Gemini
-   Agent orchestration
-   Natural-language query planning
-   Graph-grounded reasoning

## Graph

-   FalkorDB
-   Redis-compatible graph infrastructure
-   Cypher

## Infrastructure

-   Docker
-   Docker Compose

------------------------------------------------------------------------

# Project Structure

``` text
companyOs/
│
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── query_planner.py
│   │   ├── cypher_generator.py
│   │   ├── analysis_agent.py
│   │   ├── graph_intelligence_agent.py
│   │   ├── explainability.py
│   │   └── hero_reasoning.py
│   │
│   ├── api/
│   │   ├── chat.py
│   │   ├── graph.py
│   │   ├── memory.py
│   │   ├── algorithms.py
│   │   ├── evidence.py
│   │   ├── actions.py
│   │   ├── action_history.py
│   │   └── path.py
│   │
│   ├── graph/
│   │   ├── client.py
│   │   ├── schema.py
│   │   ├── queries.py
│   │   ├── path_engine.py
│   │   ├── evidence.py
│   │   └── algorithms.py
│   │
│   ├── memory/
│   │   └── memory_agent.py
│   │
│   ├── security/
│   │   ├── context.py
│   │   ├── tenant.py
│   │   ├── middleware.py
│   │   ├── headers.py
│   │   └── cypher_validator.py
│   │
│   ├── tools/
│   │   └── query_tools.py
│   │
│   ├── data_generator/
│   │   └── novatech_generator.py
│   │
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── globals.css
│   │
│   ├── components/
│   │   └── GraphExplorer.tsx
│   │
│   └── package.json
│
├── docker-compose.yml
├── .env
└── README.md
```

------------------------------------------------------------------------

# Prerequisites

Install:

-   Docker Desktop
-   Python 3.11+
-   Node.js 20+
-   npm
-   Git

You also need a Gemini API key if using Gemini for the AI reasoning
layer.

------------------------------------------------------------------------

# Quick Start

## 1. Clone the repository

``` powershell
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY>
cd companyOs
```

## 2. Start FalkorDB

``` powershell
docker compose up -d
```

Verify:

``` powershell
docker ps
```

You should see the FalkorDB container running on port `6379`.

------------------------------------------------------------------------

# Backend Setup

``` powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create/update `.env`:

``` env
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=
FALKORDB_PASSWORD=

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.8-flash

NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the backend:

``` powershell
uvicorn main:app --reload --port 8000
```

Backend:

``` text
http://127.0.0.1:8000
```

Health check:

``` text
http://127.0.0.1:8000/health
```

------------------------------------------------------------------------

# Initialize the Demo Graph

Use the demo initialization endpoint:

``` powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://127.0.0.1:8000/api/demo/initialize"
```

This initializes the graph schema and generates the NovaTech demo
company data.

The synthetic graph contains approximately:

``` text
126 People
24 Teams
32 Projects
54 Services
100 Documents
102 Incidents
202 Decisions
1338 Relationships
```

Numbers may change as the generator evolves.

------------------------------------------------------------------------

# Frontend Setup

Open another PowerShell terminal:

``` powershell
cd frontend

npm install
```

Create:

``` text
frontend/.env.local
```

with:

``` env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the frontend:

``` powershell
npm run dev
```

Open:

``` text
http://localhost:3000
```

------------------------------------------------------------------------

# Example Questions

Try:

``` text
Who knows the most about the payment system?
```

``` text
What happens if Payment Service goes down?
```

``` text
What is the blast radius of Payment Service?
```

``` text
Why was the payment architecture changed?
```

``` text
Who owns Payment Service?
```

``` text
Who should investigate the checkout failures?
```

``` text
What systems are connected to Payment Service?
```

``` text
What are the most connected systems?
```

------------------------------------------------------------------------

# API

## Chat

``` http
POST /api/chat
```

Example:

``` json
{
  "question": "Who owns Payment Service?",
  "graph_name": "novatech"
}
```

The response contains fields such as:

``` json
{
  "success": true,
  "answer": "...",
  "plan": {},
  "cypher": "...",
  "entities": [],
  "graph_evidence": [],
  "graph_intelligence": {},
  "graph_path": {},
  "explanation": {},
  "memory": {},
  "provenance": [],
  "freshness": {},
  "contradictions": [],
  "confidence": 0.91,
  "evidence_count": 3,
  "retrieval_mode": "graph_first",
  "graph_first": true
}
```

## Graph

``` text
POST /api/graph/query
POST /api/graph/traverse
GET  /api/graph/entity/{id}
POST /api/graph/path
```

## Algorithms

``` text
GET /api/graph/algorithms/expertise
GET /api/graph/algorithms/blast-radius
GET /api/graph/algorithms/dependencies
GET /api/graph/algorithms/centrality
GET /api/graph/algorithms/people-centrality
GET /api/graph/algorithms/systems
GET /api/graph/algorithms/component/{entity_name}
GET /api/graph/algorithms/relationships
```

------------------------------------------------------------------------

# MCP-Style Graph Tools

The architecture is designed around graph tools such as:

``` text
falkor_search
falkor_traverse
falkor_cypher
falkor_shortest_path
falkor_neighbors
falkor_subgraph
falkor_write
```

These tools expose graph capabilities to agents while keeping FalkorDB
as the underlying source of connected context.

------------------------------------------------------------------------

# Data Model Example

A simplified graph can look like:

``` text
(:Person)-[:OWNS]->(:Service)

(:Service)-[:DEPENDS_ON]->(:Service)

(:Service)-[:INVOLVES]->(:Incident)

(:Decision)-[:MADE_BY]->(:Person)

(:Migration)-[:PRODUCES]->(:Service)

(:Migration)-[:IMPLEMENTED_BY]->(:Decision)

(:Person)-[:WORKED_ON]->(:Project)
```

------------------------------------------------------------------------

# Design Principles

## 1. Graph First

Important organizational answers should be grounded in FalkorDB
evidence.

## 2. Evidence Over Guessing

The system distinguishes observed graph relationships from inference.

## 3. Explainability by Default

Answers expose evidence, graph paths, confidence, contradictions, and
unknowns.

## 4. No Fabricated Relationships

Missing edges remain unknown.

## 5. Agents Share Graph Context

FalkorDB provides a common context layer for multiple agents.

## 6. Actions Become Knowledge

Investigation actions and outcomes can be represented in the graph.

------------------------------------------------------------------------

# Testing

Backend tests can be run with:

``` powershell
cd backend

.\.venv\Scripts\Activate.ps1

pytest -q
```

Individual phase verification scripts can also be run when present:

``` powershell
python test_phase18.py
python test_phase19.py
```

Frontend production build:

``` powershell
cd frontend
npm run build
```

------------------------------------------------------------------------

# Security Notes

Do not commit secrets.

Never commit:

``` text
.env
.env.local
*.key
*.pem
```

Use environment variables for API keys and credentials.

For production deployments, replace demo authentication with a real
identity provider and enforce strict tenant authorization.

------------------------------------------------------------------------

# Hackathon Demo Flow

A recommended three-minute demo:

### 1. Show the company graph

Open the CompanyOS Command Center and demonstrate the connected graph.

### 2. Ask:

> Who knows the most about our payment system?

Show expertise ranking and graph evidence.

### 3. Ask:

> Why was the payment architecture changed?

Show the decision → implementation → service relationship.

### 4. Ask:

> What happens if Payment Service goes down?

Show dependency traversal and blast radius.

### 5. Ask:

> Who should investigate?

Show current ownership and relevant expertise.

### 6. Create an investigation

Create an investigation action associated with the affected service and
incident.

### 7. Show persistence

Return to the conversation and demonstrate that the system retains
useful investigation context.

### 8. Finish with the graph

Show the actual FalkorDB relationship path behind the answer.

------------------------------------------------------------------------

# What Makes CompanyOS Different?

Traditional enterprise search often answers:

> "Here are some documents containing your keywords."

CompanyOS aims to answer:

> "Here is what happened, how the entities are connected, who is
> involved, why the decision was made, what could be affected, and here
> is the graph evidence supporting the answer."

The difference is the **relationship layer**.

------------------------------------------------------------------------

# Learnings

Building CompanyOS highlighted several important lessons:

### Relationships are valuable data

Many enterprise questions are relationship questions rather than
document-search questions.

### The LLM should not own the truth

The graph should establish what is known. The LLM should interpret and
explain it.

### Graph schemas matter

Useful relationships such as `OWNS`, `DEPENDS_ON`, `WORKED_ON`,
`MADE_BY`, and `AFFECTS` make downstream reasoning much stronger.

### Unknowns are important

A trustworthy system should say when the graph cannot establish a
relationship.

### Explainability must be architectural

Evidence needs to flow from the graph through retrieval, reasoning, and
UI.

------------------------------------------------------------------------

# Roadmap

Future improvements include:

-   GitHub ingestion
-   Slack / Teams ingestion
-   Continuous graph synchronization
-   More temporal reasoning
-   Advanced graph algorithms
-   Richer MCP integrations
-   Automated incident investigation
-   Larger evaluation datasets
-   Enterprise authentication
-   Production-scale observability
-   Advanced contradiction resolution

------------------------------------------------------------------------

# Hackathon Track

**Track:** Company Brain

CompanyOS is designed around the idea that a company's knowledge should
be represented as a connected graph and used by agents for reasoning,
memory, investigation, and action.

------------------------------------------------------------------------

# AI Disclosure

AI coding assistants and LLMs were used during development for
implementation assistance, debugging, architecture iteration,
documentation, and code review.

The project architecture, graph model, queries, agent flow, testing,
verification, and integration were reviewed and adapted as part of the
development process.

------------------------------------------------------------------------

# Author

**Suman Kumar**

GitHub: https://github.com/sumankr4edu

LinkedIn: https://www.linkedin.com/in/suman-kumar-8698ab249/

------------------------------------------------------------------------

# Final Message

> **CompanyOS --- Your company's knowledge, connected.**
>
> Ask your company.\
> Follow the graph.\
> Get the evidence.
