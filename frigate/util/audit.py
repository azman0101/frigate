import logging
import uuid
from datetime import datetime
from typing import Optional
from frigate.models import AuditLog

logger = logging.getLogger(__name__)

def log_audit_event(
    user_id: str,
    type: str,
    action: str,
    resource_id: str,
    metadata: Optional[dict] = None,
    start_time: float = None,
    end_time: float = None,
) -> None:
    """Helper to log audit events."""
    try:
        if start_time is None:
            start_time = datetime.now().timestamp()

        # Ensure we have an ID
        log_id = str(uuid.uuid4()).replace("-", "")[:30]

        AuditLog.create(
            id=log_id,
            user_id=user_id,
            type=type,
            action=action,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            metadata=metadata or {},
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
