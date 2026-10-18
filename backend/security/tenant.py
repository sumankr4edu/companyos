from fastapi import HTTPException

from security.context import UserContext


def validate_graph_access(
    user: UserContext,
    requested_graph: str,
) -> str:

    if not requested_graph:
        return user.graph_name

    if requested_graph != user.graph_name:
        raise HTTPException(
            status_code=403,
            detail="Cross-tenant graph access denied.",
        )

    return requested_graph