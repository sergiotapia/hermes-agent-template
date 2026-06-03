"""Tool handlers for the Nabi care Hermes plugin."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def next_appointment(args: dict, **kwargs) -> str:
    """Fetch the active patient's next appointment from Nabi."""
    del args

    return _post_tool(
        "/api/internal/hermes/care-agent/tools/next-appointment",
        {"hermes_session_id": _hermes_session_id(kwargs)},
        timeout=10,
    )


def patient_context(args: dict, **kwargs) -> str:
    """Fetch bounded patient-care context from Nabi for the active session."""
    body = dict(args or {})
    body["hermes_session_id"] = _hermes_session_id(kwargs)

    return _post_tool(
        "/api/internal/hermes/care-agent/tools/patient-context",
        body,
        timeout=20,
    )


def _post_tool(path: str, body: dict, timeout: int) -> str:
    hermes_session_id = str(body.get("hermes_session_id") or "").strip()
    base_url = os.environ.get("NABI_API_BASE_URL", "").strip().rstrip("/")
    token = os.environ.get("NABI_HERMES_TOOL_TOKEN", "").strip()

    if not hermes_session_id:
        return _json({"ok": False, "error": "missing_hermes_session_id"})
    if not base_url:
        return _json({"ok": False, "error": "missing_nabi_api_base_url"})
    if not token:
        return _json({"ok": False, "error": "missing_nabi_hermes_tool_token"})

    body = {**body, "hermes_session_id": hermes_session_id}
    encoded_body = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=encoded_body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        return _json(
            {
                "ok": False,
                "error": "nabi_tool_http_error",
                "status": exc.code,
                "detail": detail,
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": "nabi_tool_request_failed", "detail": str(exc)})

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return _json({"ok": False, "error": "invalid_nabi_tool_response"})

    return _json(parsed)


def _hermes_session_id(kwargs: dict) -> str:
    return str(
        kwargs.get("task_id")
        or kwargs.get("session_id")
        or kwargs.get("gateway_session_id")
        or ""
    ).strip()


def _json(value: dict) -> str:
    return json.dumps(value, separators=(",", ":"))
