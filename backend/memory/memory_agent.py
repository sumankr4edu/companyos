from __future__ import annotations

from typing import Any, Dict, List, Optional

from memory.conversation_store import ConversationStore


class MemoryAgent:
    """
    CompanyOS persistent memory agent.

    Phase 22 responsibilities:

    - Create conversations
    - Maintain conversation state
    - Persist turns in FalkorDB
    - Search previous investigations
    - Build memory context for the orchestrator
    - Retrieve recent turns
    - Delete conversations
    """

    def __init__(
        self,
        graph_name: str = "novatech",
    ):
        self.graph_name = graph_name

        self.store = ConversationStore(
            graph_name=graph_name
        )

    # ========================================================
    # Conversation
    # ========================================================

    def create_conversation(
        self,
        user_id: str,
        title: str = "New Investigation",
    ) -> Dict[str, Any]:

        return self.store.create_conversation(
            user_id=user_id,
            title=title,
        )

    def ensure_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: str = "New Investigation",
    ) -> Dict[str, Any]:

        return self.store.ensure_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
        )

    def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_turns: bool = True,
    ) -> Optional[Dict[str, Any]]:

        return self.store.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            include_turns=include_turns,
        )

    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        return self.store.list_conversations(
            user_id=user_id,
            limit=limit,
        )

    # ========================================================
    # Turns
    # ========================================================

    def save_turn(
        self,
        conversation_id: str,
        user_id: str,
        question: str,
        answer: str,
        plan: Optional[Dict[str, Any]] = None,
        entities: Optional[List[Any]] = None,
        graph_path: Optional[Dict[str, Any]] = None,
        evidence_count: int = 0,
        confidence: float = 0.0,
        retrieval_mode: str = "graph_first",
    ) -> Dict[str, Any]:

        return self.store.save_turn(
            conversation_id=conversation_id,
            user_id=user_id,
            question=question,
            answer=answer,
            plan=plan,
            entities=entities,
            graph_path=graph_path,
            evidence_count=evidence_count,
            confidence=confidence,
            retrieval_mode=retrieval_mode,
        )

    def recent(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.store.recent_turns(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
        )

    # ========================================================
    # Search
    # ========================================================

    def search(
        self,
        question: str,
        user_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        return self.store.search_memory(
            question=question,
            user_id=user_id,
            limit=limit,
        )

    # ========================================================
    # Context
    # ========================================================

    def build_context(
        self,
        question: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, Any]:

        matches = self.search(
            question=question,
            user_id=user_id,
            limit=limit,
        )

        recent_turns: List[
            Dict[str, Any]
        ] = []

        if conversation_id:
            recent_turns = self.recent(
                conversation_id=conversation_id,
                user_id=user_id,
                limit=limit,
            )

        return {
            "enabled": True,
            "conversation_id": conversation_id,
            "matches": matches,
            "recent_turns": recent_turns,
            "match_count": len(matches),
            "recent_turn_count": len(
                recent_turns
            ),
            "graph_name": self.graph_name,
        }

    # ========================================================
    # Delete
    # ========================================================

    def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        return self.store.delete_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )