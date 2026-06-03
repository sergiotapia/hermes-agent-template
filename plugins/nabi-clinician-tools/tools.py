"""Tool handlers for the Nabi clinician Hermes plugin."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


_VALID_SECTIONS = {"profile", "appointments", "goals", "tracking", "forms", "charting"}


def patient_context(args: dict, **kwargs) -> str:
    """Fetch bounded patient context for a clinician assistant turn."""
    del kwargs

    hermes_session_id = str(args.get("hermes_session_id") or "").strip()
    patient_ref = str(args.get("patient_ref") or "").strip()
    sections = _sections(args.get("sections"))
    intent = str(args.get("intent") or "").strip()
    time_window_days = _time_window_days(args.get("time_window_days"))

    base_url = os.environ.get("NABI_API_BASE_URL", "").strip().rstrip("/")
    token = (
        os.environ.get("NABI_HERMES_TOOL_TOKEN", "").strip()
        or os.environ.get("HERMES_TOOL_TOKEN", "").strip()
    )

    if not hermes_session_id:
        return _json({"ok": False, "error": "missing_hermes_session_id"})
    if not patient_ref:
        return _json({"ok": False, "error": "missing_patient_ref"})
    if not sections:
        return _json({"ok": False, "error": "missing_sections"})
    if not base_url:
        return _json({"ok": False, "error": "missing_nabi_api_base_url"})
    if not token:
        return _json({"ok": False, "error": "missing_nabi_hermes_tool_token"})

    body = {
        "hermes_session_id": hermes_session_id,
        "patient_ref": patient_ref,
        "sections": sections,
        "time_window_days": time_window_days,
    }
    if intent:
        body["intent"] = intent

    request = urllib.request.Request(
        f"{base_url}/api/internal/hermes/clinician-assistant/tools/patient-context",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
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


def _sections(value) -> list[str]:
    if isinstance(value, str):
        raw = value.split(",")
    elif isinstance(value, list):
        raw = value
    else:
        raw = []

    sections: list[str] = []
    for item in raw:
        section = str(item or "").strip().lower()
        if section in _VALID_SECTIONS and section not in sections:
            sections.append(section)

    return sections


def _time_window_days(value) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 30

    return max(1, min(parsed, 180))


def _json(value: dict) -> str:
    return json.dumps(value, separators=(",", ":"))
