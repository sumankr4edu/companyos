from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.investigations import router as investigations_router
from graph.schema import initialize_schema
from graph.queries import run_cypher
from data_generator.novatech_generator import NovaTechGenerator

from api.chat import router as chat_router
from api.graph import router as graph_router
from api.memory import router as memory_router
from api.algorithms import router as algorithms_router
from api.evidence import router as evidence_router
from api.actions import router as actions_router
from api.action_history import router as action_history_router
from api.path import router as path_router
from api.agents import router as agents_router
from security.middleware import RequestIDMiddleware
from security.headers import SecurityHeadersMiddleware
from api.mcp import router as mcp_router

# ============================================================
# Application
# ============================================================

app = FastAPI(
    title="CompanyOS",
    description="The Graph-Native Company Brain",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Security Middleware
# ============================================================

app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# ============================================================
# API Routers
# ============================================================

app.include_router(chat_router)
app.include_router(graph_router)
app.include_router(memory_router)
app.include_router(algorithms_router)
app.include_router(evidence_router)
app.include_router(actions_router)
app.include_router(action_history_router)
app.include_router(path_router)
app.include_router(investigations_router)
app.include_router(
    mcp_router
)
app.include_router(agents_router)

# ============================================================
# Health
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "companyos",
        "graph": "novatech",
    }


# ============================================================
# Root
# ============================================================

@app.get("/")
async def root():
    return {
        "name": "CompanyOS",
        "description": "The Graph-Native Company Brain",
        "version": "1.0.0",
        "status": "running",
    }


# ============================================================
# Demo Initialization
# ============================================================

@app.post("/api/demo/initialize")
async def initialize_demo():

    schema_result = initialize_schema("novatech")

    generator = NovaTechGenerator("novatech")

    seed_result = generator.generate()

    return {
        "success": True,
        "schema": schema_result,
        "seed": seed_result,
    }


# ============================================================
# Raw Graph Query
# ============================================================

class CypherRequest(BaseModel):
    query: str
    graph_name: str = "novatech"


@app.post("/api/graph/query")
async def graph_query(request: CypherRequest):

    return run_cypher(
        request.query,
        request.graph_name,
    )