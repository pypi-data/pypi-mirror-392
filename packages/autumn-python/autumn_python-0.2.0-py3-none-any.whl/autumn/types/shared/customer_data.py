# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["CustomerData"]


class CustomerData(BaseModel):
    disable_default: Optional[bool] = None

    email: Optional[str] = None
    """Customer's email address"""

    fingerprint: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    name: Optional[str] = None
    """Customer's name"""

    stripe_id: Optional[str] = None
