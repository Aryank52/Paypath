import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def create_trace_step(
        self,
        action: str,
        summary: str,
        status: str = "COMPLETED",
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        return {
            "step_id": f"step_{uuid.uuid4().hex[:6]}",
            "agent_name": self.name,
            "role": self.role,
            "action": action,
            "summary": summary,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
