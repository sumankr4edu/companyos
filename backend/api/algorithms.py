from fastapi import APIRouter, Depends, HTTPException, Query

from graph.algorithms import GraphAlgorithms
from security.context import (
    UserContext,
    get_current_user,
    require_permission,
)
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/graph/algorithms",
    tags=["graph-intelligence"],
)


# =========================================================
# Helper
# =========================================================

def get_algorithms(
    user: UserContext,
) -> GraphAlgorithms:

    graph_name = validate_graph_access(
        user,
        user.graph_name,
    )

    return GraphAlgorithms(
        graph_name=graph_name
    )


# =========================================================
# People expertise
# =========================================================

@router.get("/expertise")
def expertise(
    entity_name: str = Query(
        ...,
        min_length=1,
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.expertise_ranking(
            entity_name=entity_name,
            limit=limit,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Expertise analysis failed: {exc}",
        )


# =========================================================
# Dependency blast radius
# =========================================================

@router.get("/blast-radius")
def blast_radius(
    service_name: str = Query(
        ...,
        min_length=1,
    ),
    max_hops: int = Query(
        4,
        ge=1,
        le=8,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=200,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.dependency_blast_radius(
            service_name=service_name,
            max_hops=max_hops,
            limit=limit,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Blast-radius analysis failed: {exc}",
        )


# =========================================================
# Forward dependencies
# =========================================================

@router.get("/dependencies")
def dependencies(
    service_name: str = Query(
        ...,
        min_length=1,
    ),
    max_hops: int = Query(
        4,
        ge=1,
        le=8,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=200,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.dependencies(
            service_name=service_name,
            max_hops=max_hops,
            limit=limit,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Dependency analysis failed: {exc}",
        )


# =========================================================
# Entity centrality
# =========================================================

@router.get("/centrality")
def centrality(
    entity_name: str = Query(
        ...,
        min_length=1,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.degree_centrality(
            entity_name=entity_name
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Centrality analysis failed: {exc}",
        )


# =========================================================
# People centrality
# =========================================================

@router.get("/people-centrality")
def people_centrality(
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.people_centrality(
            limit=limit
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"People centrality failed: {exc}",
        )


# =========================================================
# System centrality
# =========================================================

@router.get("/systems")
def systems(
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.system_centrality(
            limit=limit
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"System centrality failed: {exc}",
        )


# =========================================================
# Connected component
# =========================================================

@router.get("/component/{entity_name}")
def component(
    entity_name: str,
    max_hops: int = Query(
        6,
        ge=1,
        le=8,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=200,
    ),
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.connected_component(
            entity_name=entity_name,
            max_hops=max_hops,
            limit=limit,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Component analysis failed: {exc}",
        )


# =========================================================
# Relationship statistics
# =========================================================

@router.get("/relationships")
def relationships(
    user: UserContext = Depends(
        get_current_user
    ),
):

    require_permission(
        user,
        "graph:read",
    )

    try:

        algorithms = get_algorithms(
            user
        )

        return algorithms.relationship_counts()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Relationship analysis failed: {exc}",
        )