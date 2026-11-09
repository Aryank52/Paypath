import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Structured JSON Logger
class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

logger = logging.getLogger("paypath")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_audit_event(
    action: str,
    actor_type: str,
    actor_id: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> Dict[str, Any]:
    event = {
        "event_type": "AUDIT_LOG",
        "action": action,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    logger.info(f"AUDIT: {action} on {resource_type}:{resource_id} by {actor_type}:{actor_id}", extra=event)
    return event
