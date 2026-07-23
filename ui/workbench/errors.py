"""Stable machine-readable errors for the browser/backend boundary."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ErrorCode:
    ROUTE_NOT_FOUND = "request.route_not_found"
    HOST_DENIED = "request.host_denied"
    ORIGIN_DENIED = "request.origin_denied"
    UNSUPPORTED_MEDIA_TYPE = "request.unsupported_media_type"
    INVALID_SIZE = "request.invalid_size"
    INVALID_JSON = "request.invalid_json"
    INVALID_FIELD = "request.invalid_field"
    SKILL_NOT_FOUND = "skill.not_found"
    MODE_DENIED = "workspace.mode_denied"
    TASK_NOT_FOUND = "task.not_found"
    TASK_NOT_CANCELLABLE = "task.not_cancellable"
    TASK_CAPACITY = "task.capacity_exceeded"


def error_payload(
    code: str,
    message: str,
    request_id: str,
    *,
    retryable: bool = False,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the stable HTTP error envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
            "request_id": request_id,
            "details": details or {},
        }
    }
