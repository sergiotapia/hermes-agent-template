"""Tool schemas for the Nabi clinician Hermes plugin."""

PATIENT_CONTEXT = {
    "name": "nabi_clinician_patient_context",
    "description": (
        "Fetch bounded Nabi context for a selected patient in a clinician assistant "
        "session and return concise model context plus UI-ready artifacts. Use this "
        "when the clinician asks about a selected patient's appointment prep, "
        "progress, goals, food/activity tracking, forms, charting, or patient "
        "profile. Do not use for greetings or general questions. The clinician "
        "should have selected a patient reference; use that reference as patient_ref."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "hermes_session_id": {
                "type": "string",
                "description": (
                    "The current Hermes session id supplied in the session instructions."
                ),
            },
            "patient_ref": {
                "type": "string",
                "description": "Selected patient reference, usually patient:<local_patient_id>.",
            },
            "sections": {
                "type": "array",
                "description": (
                    "Only the patient data sections needed for the clinician's question."
                ),
                "items": {
                    "type": "string",
                    "enum": [
                        "profile",
                        "appointments",
                        "goals",
                        "tracking",
                        "forms",
                        "charting",
                    ],
                },
                "minItems": 1,
                "uniqueItems": True,
            },
            "intent": {
                "type": "string",
                "description": "Short description of why this context is being fetched.",
            },
            "time_window_days": {
                "type": "integer",
                "description": "Lookback window for tracking context. Defaults to 30.",
                "minimum": 1,
                "maximum": 180,
            },
        },
        "required": ["hermes_session_id", "patient_ref", "sections"],
        "additionalProperties": False,
    },
}
