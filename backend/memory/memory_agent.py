from datetime import datetime, timezone

from graph.queries import run_cypher


class MemoryAgent:
    """
    Persistent CompanyOS memory stored in FalkorDB.

    Memory types:
    - episodic: what happened during previous interactions
    - semantic: facts learned about the company
    - procedural: how a task/process should be performed
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    def remember(
        self,
        content: str,
        memory_type: str = "episodic",
        entity_name: str | None = None,
        importance: float = 0.5,
    ):
        """
        Store a memory in FalkorDB and optionally connect it
        to an existing company entity.
        """

        if memory_type not in {
            "episodic",
            "semantic",
            "procedural",
        }:
            raise ValueError(
                "memory_type must be episodic, semantic, or procedural"
            )

        if not 0 <= importance <= 1:
            raise ValueError(
                "importance must be between 0 and 1"
            )

        safe_content = content.replace("'", "\\'")

        safe_entity = (
            entity_name.replace("'", "\\'")
            if entity_name
            else None
        )

        timestamp = datetime.now(timezone.utc).isoformat()

        memory_id = f"memory-{timestamp}"

        # ---------------------------------------------------------
        # CASE 1: Memory without an entity relationship
        # ---------------------------------------------------------
        if not safe_entity:
            query = f"""
            CREATE (m:Memory {{
                id: '{memory_id}',
                content: '{safe_content}',
                memory_type: '{memory_type}',
                importance: {importance},
                created_at: '{timestamp}'
            }})

            RETURN
                m.id AS id,
                m.content AS content,
                m.memory_type AS memory_type,
                m.importance AS importance,
                m.created_at AS created_at
            """

            return run_cypher(
                query,
                self.graph_name,
            )

        # ---------------------------------------------------------
        # CASE 2: Memory connected to an existing entity
        # ---------------------------------------------------------
        query = f"""
        MATCH (entity)
        WHERE entity.name = '{safe_entity}'

        CREATE (m:Memory {{
            id: '{memory_id}',
            content: '{safe_content}',
            memory_type: '{memory_type}',
            importance: {importance},
            created_at: '{timestamp}'
        }})

        CREATE (m)-[:ABOUT]->(entity)

        RETURN
            m.id AS id,
            m.content AS content,
            m.memory_type AS memory_type,
            m.importance AS importance,
            m.created_at AS created_at,
            entity.name AS entity
        """

        return run_cypher(
            query,
            self.graph_name,
        )

    def search(
        self,
        query_text: str,
        memory_type: str | None = None,
        limit: int = 10,
    ):
        """
        Search previously stored memories.
        """

        safe_query = query_text.replace("'", "\\'")

        type_filter = ""

        if memory_type:
            safe_type = memory_type.replace("'", "\\'")
            type_filter = (
                f"AND m.memory_type = '{safe_type}'"
            )

        cypher = f"""
        MATCH (m:Memory)
        WHERE toLower(m.content)
              CONTAINS
              toLower('{safe_query}')
        {type_filter}

        RETURN
            m.id AS id,
            m.content AS content,
            m.memory_type AS memory_type,
            m.importance AS importance,
            m.created_at AS created_at

        ORDER BY m.importance DESC
        LIMIT {limit}
        """

        return run_cypher(
            cypher,
            self.graph_name,
        )

    def recent(self, limit: int = 10):
        """
        Return recent memories.
        """

        cypher = f"""
        MATCH (m:Memory)

        RETURN
            m.id AS id,
            m.content AS content,
            m.memory_type AS memory_type,
            m.importance AS importance,
            m.created_at AS created_at

        ORDER BY m.created_at DESC
        LIMIT {limit}
        """

        return run_cypher(
            cypher,
            self.graph_name,
        )

    def related_to(self, entity_name: str):
        """
        Retrieve memories associated with a company entity.
        """

        safe_entity = entity_name.replace("'", "\\'")

        cypher = f"""
        MATCH (m:Memory)-[:ABOUT]->(entity)
        WHERE entity.name = '{safe_entity}'

        RETURN
            m.id AS id,
            m.content AS content,
            m.memory_type AS memory_type,
            m.importance AS importance,
            m.created_at AS created_at,
            entity.name AS entity

        ORDER BY m.importance DESC
        """

        return run_cypher(
            cypher,
            self.graph_name,
        )