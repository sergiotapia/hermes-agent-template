"""Nabi care Hermes plugin."""

from . import schemas, tools


def register(ctx):
    ctx.register_tool(
        name="nabi_care_next_appointment",
        toolset="nabi-care",
        schema=schemas.NEXT_APPOINTMENT,
        handler=tools.next_appointment,
    )
    ctx.register_tool(
        name="nabi_care_patient_context",
        toolset="nabi-care",
        schema=schemas.PATIENT_CONTEXT,
        handler=tools.patient_context,
    )
