# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr
from .shared_params.entity_data import EntityData
from .shared_params.customer_data import CustomerData

__all__ = ["ClientCheckoutParams", "Option"]


class ClientCheckoutParams(TypedDict, total=False):
    customer_id: Required[str]
    """Your unique identifier for the customer"""

    checkout_session_params: object
    """Additional parameters to pass onto Stripe when creating the checkout session"""

    customer_data: CustomerData
    """If auto creating a customer, the properties from this field will be used."""

    entity_data: EntityData
    """
    If attaching a product to an entity and auto creating the entity, the properties
    from this field will be used. feature_id is required.
    """

    entity_id: Optional[str]
    """If attaching a product to an entity, can be used to auto create the entity"""

    force_checkout: bool
    """
    Always return a Stripe Checkout URL, even if the customer's card is already on
    file
    """

    free_trial: bool
    """
    If the product has a free trial, this field can be used to disable it when
    attaching (by passing in false)
    """

    invoice: bool

    options: Optional[Iterable[Option]]
    """Pass in quantities for prepaid features"""

    product_id: Optional[str]
    """Product ID, set when creating the product in the Autumn dashboard"""

    product_ids: Optional[SequenceNotStr[str]]
    """Can be used to attach multiple products to the customer at once.

    For example, attaching a main product and an add-on.
    """

    reward: Union[str, SequenceNotStr[str]]
    """An Autumn promo_code or reward_id to apply at checkout"""

    setup_payment: bool

    success_url: str
    """URL to redirect to after the purchase is successful"""


class Option(TypedDict, total=False):
    feature_id: Required[str]

    quantity: Required[float]

    adjustable_quantity: Optional[bool]

    internal_feature_id: Optional[str]

    upcoming_quantity: Optional[float]
