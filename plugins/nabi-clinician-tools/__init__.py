"""Nabi clinician Hermes plugin."""

from . import schemas, tools


def register(ctx):
    ctx.register_tool(
        name="nabi_clinician_patient_context",
        toolset="nabi-clinician-tools",
        schema=schemas.PATIENT_CONTEXT,
        handler=tools.patient_context,
    )
