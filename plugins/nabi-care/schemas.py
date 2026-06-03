"""Tool schemas for the Nabi care Hermes plugin."""

NEXT_APPOINTMENT = {
    "name": "nabi_care_next_appointment",
    "description": (
        "Fetch the patient's next upcoming Nabi appointment and return a UI-ready "
        "appointment card artifact plus concise context. Use this when the patient "
        "asks about their next appointment, upcoming appointment time, appointment "
        "provider, appointment location, appointment details, or when displaying an "
        "appointment card would make the response clearer. Do not ask the patient "
        "for identifiers; the active Hermes session already scopes the request."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}

PATIENT_CONTEXT = {
    "name": "nabi_care_patient_context",
    "description": (
        "Fetch bounded Nabi care context for the active patient. Use this when the "
        "answer depends on patient-specific care-record facts, prior-session context, "
        "forms or tasks, goals, tracking history, progress, appointments, or care-team "
        "details. Choose only the sections that help the current response. For "
        "emotional-support messages, do not call this reflexively; call it when timing, "
        "recent care context, goals, or safety-relevant patient details would make the "
        "support more grounded. Chart-note context is internal care-record context: "
        "never say it came from chart notes and never quote clinician wording."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sections": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "profile",
                        "care_team",
                        "appointments",
                        "progress",
                        "recent_tracking",
                        "forms",
                        "action_items",
                        "chart_notes",
                    ],
                },
                "description": (
                    "Context sections to fetch. Use appointments for upcoming or recent "
                    "session details, forms for completed/open form requirements, "
                    "action_items for practical next steps, progress/recent_tracking for "
                    "goals and patient-entered data, and chart_notes for prior-session "
                    "care context that should be summarized indirectly."
                ),
                "minItems": 1,
                "uniqueItems": True,
            },
            "detail": {
                "type": "string",
                "enum": ["summary", "standard", "detailed"],
                "description": (
                    "How much bounded detail Nabi should return. Use summary for quick "
                    "grounding, standard for most care questions, and detailed when the "
                    "patient asks for history, trends, or what happened previously."
                ),
            },
            "time_window_days": {
                "type": "integer",
                "minimum": 1,
                "maximum": 180,
                "description": (
                    "Lookback window for progress and recent tracking. Use a wider "
                    "window for trend or progress questions."
                ),
            },
            "appointment_scope": {
                "type": "string",
                "enum": ["next", "recent", "last_completed", "none"],
                "description": (
                    "Use last_completed when answering what happened last session; use "
                    "next when upcoming-session timing may shape the response."
                ),
            },
        },
        "additionalProperties": False,
    },
}
