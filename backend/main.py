from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

from security.middleware import RequestIDMiddleware
from security.headers import SecurityHeadersMiddleware


app = FastAPI(
    title="CompanyOS API",
    description="Graph-native AI company brain powered by FalkorDB",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SECURITY MIDDLEWARE
# ============================================================

app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(chat_router)
app.include_router(graph_router)
app.include_router(memory_router)
app.include_router(algorithms_router)
app.include_router(evidence_router)
app.include_router(actions_router)
app.include_router(action_history_router)
app.include_router(path_router)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "companyos-api",
        "version": "0.1.0",
    }


# ============================================================
# DEMO INITIALIZATION
# ============================================================

@app.post("/api/demo/initialize")
async def initialize_demo():
    """
    Initialize the NovaTech demo graph.

    This endpoint:
    1. Creates/initializes the graph schema.
    2. Generates the NovaTech demo company graph.
    """

    schema_result = initialize_schema("novatech")

    generator = NovaTechGenerator("novatech")
    seed_result = generator.generate()

    return {
        "schema": schema_result,
        "seed": seed_result,
    }


# ============================================================
# GRAPH QUERY
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