from fastapi import APIRouter, HTTPException, Query

from graph.path_engine import GraphPathEngine


router = APIRouter(
    prefix="/api/graph",
    tags=["Graph Paths"],
)


path_engine = GraphPathEngine(
    graph_name="novatech"
)


# =========================================================
# EXACT PATH
# =========================================================

@router.get("/path")
def get_graph_path(
    source: str = Query(
        ...,
        min_length=1,
    ),
    target: str | None = Query(
        default=None
    ),
    max_hops: int = Query(
        default=6,
        ge=1,
        le=10,
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
):

    try:

        result = path_engine.find_paths(
            source=source,
            target=target,
            max_hops=max_hops,
            limit=limit,
        )

        paths = path_engine.normalize_path(
            result
        )

        return {
            "success": True,
            "source": source,
            "target": target,
            "max_hops": max_hops,
            "paths": paths,
            "raw": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# GRAPH EXPLORATION
# =========================================================

@router.get("/explore")
def explore_graph(
    entity_name: str = Query(
        ...,
        min_length=1,
    ),
    max_hops: int = Query(
        default=4,
        ge=1,
        le=8,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):

    try:

        result = path_engine.explore(
            entity_name=entity_name,
            max_hops=max_hops,
            limit=limit,
        )

        return {
            "success": True,
            "entity": entity_name,
            "max_hops": max_hops,
            "result": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# HERO PATH
# =========================================================

@router.get("/hero")
def hero_path(
    source: str = Query(
        default="Checkout Service"
    ),
    target: str | None = Query(
        default=None
    ),
    max_hops: int = Query(
        default=8,
        ge=1,
        le=10,
    ),
):

    try:

        result = path_engine.hero_path(
            source=source,
            target=target,
            max_hops=max_hops,
        )

        paths = path_engine.normalize_path(
            result
        )

        return {
            "success": True,
            "source": source,
            "target": target,
            "max_hops": max_hops,
            "paths": paths,
            "raw": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )