# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["CustomerListResponse"]


class CustomerListResponse(BaseModel):
    limit: int
    """Maximum number of customers returned"""

    list: List[object]
    """List of customers"""

    offset: int
    """Number of customers skipped before returning results"""

    total: int
    """Total number of customers available"""
