# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["InferenceGeneratePersonaChatResponse"]


class InferenceGeneratePersonaChatResponse(BaseModel):
    messages: Optional[List[Dict[str, str]]] = None
    """Formatted messages with memory context"""

    response: Optional[str] = None
    """Generated response content"""
