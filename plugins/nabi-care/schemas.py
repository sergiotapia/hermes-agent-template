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
