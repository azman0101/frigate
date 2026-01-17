"""Audit Logging API."""

import logging
from functools import reduce
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from peewee import operator

from frigate.api.auth import allow_any_authenticated, get_current_user
from frigate.api.defs.tags import Tags
from frigate.models import AuditLog
from frigate.util.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(tags=[Tags.audit])


@router.get(
    "/audit/logs",
    dependencies=[Depends(allow_any_authenticated())],
    summary="Get audit logs",
)
def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    user: Optional[str] = None,
    type: Optional[str] = None,
    action: Optional[str] = None,
    resource_id: Optional[str] = None,
    after: Optional[float] = None,
    before: Optional[float] = None,
):
    clauses = []

    if user:
        clauses.append(AuditLog.user_id == user)
    if type:
        clauses.append(AuditLog.type == type)
    if action:
        clauses.append(AuditLog.action == action)
    if resource_id:
        clauses.append(AuditLog.resource_id == resource_id)
    if after:
        clauses.append(AuditLog.start_time >= after)
    if before:
        clauses.append(AuditLog.start_time <= before)

    if not clauses:
        clauses.append(True)

    query = (
        AuditLog.select()
        .where(reduce(operator.and_, clauses))
        .order_by(AuditLog.start_time.desc())
        .limit(limit)
        .offset(offset)
        .dicts()
    )

    return JSONResponse(content=list(query))


@router.post(
    "/audit/events",
    dependencies=[Depends(allow_any_authenticated())],
    summary="Log a client-side audit event",
)
async def log_client_event(request: Request):
    """
    Frontend sends:
    {
        "type": "live",
        "action": "view",
        "resource_id": "camera_name",
        "start_time": 1234567890,
        "end_time": 1234567895, # Optional
        "metadata": {}
    }
    """
    current_user = await get_current_user(request)
    if isinstance(current_user, JSONResponse):
        return current_user

    user_id = current_user["username"]

    try:
        body = await request.json()

        log_audit_event(
            user_id=user_id,
            type=body.get("type"),
            action=body.get("action"),
            resource_id=body.get("resource_id"),
            metadata=body.get("metadata"),
            start_time=body.get("start_time"),
            end_time=body.get("end_time"),
        )

        return JSONResponse(content={"success": True})
    except Exception as e:
        logger.error(f"Error logging client event: {e}")
        return JSONResponse(
            content={"success": False, "message": str(e)}, status_code=500
        )
