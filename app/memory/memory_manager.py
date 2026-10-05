from datetime import datetime
from typing import Any


class MemoryManager:
    """
    Manages short-term conversational memory and
    long-term enterprise workflow memory.
    """

    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = []

    # ---------------------------------------------------------
    # SHORT-TERM MEMORY
    # ---------------------------------------------------------

    def add_message(
        self,
        employee_id: int,
        role: str,
        content: str
    ):
        """
        Store a conversation message for the current session.
        """

        if employee_id not in self.short_term_memory:
            self.short_term_memory[employee_id] = []

        self.short_term_memory[employee_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation(
        self,
        employee_id: int
    ) -> list:

        return self.short_term_memory.get(
            employee_id,
            []
        )

    def clear_conversation(
        self,
        employee_id: int
    ):
        self.short_term_memory.pop(
            employee_id,
            None
        )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    def store_workflow(
        self,
        employee_id: int,
        request: str,
        decision: Any
    ):
        """
        Store important workflow outcomes for future
        context-aware processing.
        """

        self.long_term_memory.append({
            "employee_id": employee_id,
            "request": request,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })

    def get_employee_history(
        self,
        employee_id: int
    ) -> list:

        return [
            record
            for record in self.long_term_memory
            if record["employee_id"] == employee_id
        ]

    def get_recent_workflows(
        self,
        limit: int = 10
    ) -> list:

        return self.long_term_memory[-limit:]


memory_manager = MemoryManager()