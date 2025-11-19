# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["PersonaCreateResponse", "Persona"]


class Persona(BaseModel):
    created_at: datetime

    description: Optional[str] = None

    name: str

    persona_id: str

    user_email: Optional[str] = None

    user_id: str

    user_name: Optional[str] = None


class PersonaCreateResponse(BaseModel):
    message: str
    """Success message"""

    persona: Persona
    """The created persona"""
