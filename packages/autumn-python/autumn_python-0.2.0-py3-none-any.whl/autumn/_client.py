# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, Iterable, Optional
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from .types import (
    client_check_params,
    client_query_params,
    client_track_params,
    client_attach_params,
    client_cancel_params,
    client_checkout_params,
    client_setup_payment_params,
    client_billing_portal_params,
)
from ._types import (
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    SequenceNotStr,
    omit,
    not_given,
)
from ._utils import (
    is_given,
    maybe_transform,
    get_async_library,
    async_maybe_transform,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import plans, entities, customers, referrals
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import AutumnError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .types.check_response import CheckResponse
from .types.query_response import QueryResponse
from .types.track_response import TrackResponse
from .types.attach_response import AttachResponse
from .types.cancel_response import CancelResponse
from .types.checkout_response import CheckoutResponse
from .types.setup_payment_response import SetupPaymentResponse
from .types.billing_portal_response import BillingPortalResponse
from .types.shared_params.entity_data import EntityData
from .types.shared_params.customer_data import CustomerData

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Autumn", "AsyncAutumn", "Client", "AsyncClient"]


class Autumn(SyncAPIClient):
    customers: customers.CustomersResource
    plans: plans.PlansResource
    entities: entities.EntitiesResource
    referrals: referrals.ReferralsResource
    with_raw_response: AutumnWithRawResponse
    with_streaming_response: AutumnWithStreamedResponse

    # client options
    secret_key: str
    api_version: str | None

    def __init__(
        self,
        *,
        secret_key: str | None = None,
        api_version: str | None = "2.0.0",
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Autumn client instance.

        This automatically infers the `secret_key` argument from the `AUTUMN_SECRET_KEY` environment variable if it is not provided.
        """
        if secret_key is None:
            secret_key = os.environ.get("AUTUMN_SECRET_KEY")
        if secret_key is None:
            raise AutumnError(
                "The secret_key client option must be set either by passing secret_key to the client or by setting the AUTUMN_SECRET_KEY environment variable"
            )
        self.secret_key = secret_key

        if api_version is None:
            api_version = "2.0.0"
        self.api_version = api_version

        if base_url is None:
            base_url = os.environ.get("AUTUMN_BASE_URL")
        if base_url is None:
            base_url = f"https://api.useautumn.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.customers = customers.CustomersResource(self)
        self.plans = plans.PlansResource(self)
        self.entities = entities.EntitiesResource(self)
        self.referrals = referrals.ReferralsResource(self)
        self.with_raw_response = AutumnWithRawResponse(self)
        self.with_streaming_response = AutumnWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        secret_key = self.secret_key
        return {"Authorization": f"Bearer {secret_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "x-api-version": self.api_version if self.api_version is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        secret_key: str | None = None,
        api_version: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            secret_key=secret_key or self.secret_key,
            api_version=api_version or self.api_version,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def attach(
        self,
        *,
        customer_id: str,
        checkout_session_params: object | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        force_checkout: bool | Omit = omit,
        free_trial: bool | Omit = omit,
        invoice: bool | Omit = omit,
        options: Optional[Iterable[client_attach_params.Option]] | Omit = omit,
        product_id: Optional[str] | Omit = omit,
        product_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        reward: Union[str, SequenceNotStr[str]] | Omit = omit,
        setup_payment: bool | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachResponse:
        """
        Enables a product for a customer and processes payment if their payment method
        is already on file.

        Use this when the customer already has a payment method saved. For new customers
        without payment info, use `checkout` instead.

        @example

        ```typescript
        // Attach a product to a customer
        const response = await client.attach({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/attach Product
        Attachments}

        Args:
          customer_id: Your unique identifier for the customer

          checkout_session_params: Additional parameters to pass onto Stripe when creating the checkout session

          customer_data: If auto creating a customer, the properties from this field will be used.

          entity_data: If attaching a product to an entity and auto creating the entity, the properties
              from this field will be used. feature_id is required.

          entity_id: If attaching a product to an entity, can be used to auto create the entity

          force_checkout: Always return a Stripe Checkout URL, even if the customer's card is already on
              file

          free_trial: If the product has a free trial, this field can be used to disable it when
              attaching (by passing in false)

          options: Pass in quantities for prepaid features

          product_id: Product ID, set when creating the product in the Autumn dashboard

          product_ids: Can be used to attach multiple products to the customer at once. For example,
              attaching a main product and an add-on.

          reward: An Autumn promo_code or reward_id to apply at checkout

          success_url: URL to redirect to after the purchase is successful

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/attach",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "force_checkout": force_checkout,
                    "free_trial": free_trial,
                    "invoice": invoice,
                    "options": options,
                    "product_id": product_id,
                    "product_ids": product_ids,
                    "reward": reward,
                    "setup_payment": setup_payment,
                    "success_url": success_url,
                },
                client_attach_params.ClientAttachParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AttachResponse,
        )

    def billing_portal(
        self,
        *,
        return_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BillingPortalResponse:
        """
        Creates a billing portal session where customers can manage their subscription
        and payment methods.

        Use this to give customers self-service access to view invoices, update payment
        info, and manage subscriptions.

        @example

        ```typescript
        // Open billing portal
        const response = await client.billingPortal({
          customer_id: "cus_123",
          return_url: "https://example.com/account",
        });
        ```

        @param body.return_url - URL to redirect to when back button is clicked in the
        billing portal.

        @see {@link https://docs.useautumn.com/api-reference/core/billing-portal Billing
        Portal}

        Args:
          return_url: URL to redirect to when back button is clicked in the billing portal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/billing_portal",
            body=maybe_transform({"return_url": return_url}, client_billing_portal_params.ClientBillingPortalParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BillingPortalResponse,
        )

    def cancel(
        self,
        *,
        customer_id: str,
        product_id: str,
        cancel_immediately: bool | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        prorate: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CancelResponse:
        """
        Cancel a customer's subscription to a product.

        Use this when a customer wants to stop their subscription. Supports immediate or
        end-of-period cancellation.

        @example

        ```typescript
        // Cancel a subscription
        const response = await client.cancel({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - The ID of the customer @param body.product_id - The ID
        of the product to cancel @param body.entity_id - The ID of the entity (optional)
        @param body.cancel_immediately - Whether to cancel the product immediately or at
        period end @param body.prorate - Whether to prorate the cancellation (defaults
        to true if not specified)

        @see {@link https://docs.useautumn.com/api-reference/core/cancel Cancel
        Subscriptions}

        Args:
          customer_id: The ID of the customer

          product_id: The ID of the product to cancel

          cancel_immediately: Whether to cancel the product immediately or at period end

          entity_id: The ID of the entity (optional)

          prorate: Whether to prorate the cancellation (defaults to true if not specified)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/cancel",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "cancel_immediately": cancel_immediately,
                    "entity_id": entity_id,
                    "prorate": prorate,
                },
                client_cancel_params.ClientCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CancelResponse,
        )

    def check(
        self,
        *,
        customer_id: str,
        feature_id: str,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        properties: Dict[str, object] | Omit = omit,
        required_balance: float | Omit = omit,
        send_event: bool | Omit = omit,
        with_preview: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckResponse:
        """
        Creates a checkout session for a customer to purchase a product with payment
        collection.

        Use this for new customers or when payment info is needed. For customers with
        existing payment methods, use `attach` instead.

        @example

        ```typescript
        // Create a checkout session
        const response = await client.checkout({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/checkout Checkout
        Sessions}

        Args:
          customer_id: ID which you provided when creating the customer

          feature_id: ID of the feature to check access to. Required if product_id is not provided.

          customer_data: Properties used if customer is automatically created. Will also update if the
              name or email is not already set.

          entity_id: If using entity balances (eg, seats), the entity ID to check access for.

          required_balance: If you know the amount of the feature the end user is consuming in advance. If
              their balance is below this quantity, allowed will be false.

          send_event: If true, a usage event will be recorded together with checking access. The
              required_balance field will be used as the usage value.

          with_preview: If true, the response will include a preview object, which can be used to
              display information such as a paywall or upgrade confirmation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/check",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "properties": properties,
                    "required_balance": required_balance,
                    "send_event": send_event,
                    "with_preview": with_preview,
                },
                client_check_params.ClientCheckParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckResponse,
        )

    def checkout(
        self,
        *,
        customer_id: str,
        checkout_session_params: object | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        force_checkout: bool | Omit = omit,
        free_trial: bool | Omit = omit,
        invoice: bool | Omit = omit,
        options: Optional[Iterable[client_checkout_params.Option]] | Omit = omit,
        product_id: Optional[str] | Omit = omit,
        product_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        reward: Union[str, SequenceNotStr[str]] | Omit = omit,
        setup_payment: bool | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckoutResponse:
        """
        Creates a checkout session for a customer to purchase a product with payment
        collection.

        Use this for new customers or when payment info is needed. For customers with
        existing payment methods, use `attach` instead.

        @example

        ```typescript
        // Create a checkout session
        const response = await client.checkout({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/checkout Checkout
        Sessions}

        Args:
          customer_id: Your unique identifier for the customer

          checkout_session_params: Additional parameters to pass onto Stripe when creating the checkout session

          customer_data: If auto creating a customer, the properties from this field will be used.

          entity_data: If attaching a product to an entity and auto creating the entity, the properties
              from this field will be used. feature_id is required.

          entity_id: If attaching a product to an entity, can be used to auto create the entity

          force_checkout: Always return a Stripe Checkout URL, even if the customer's card is already on
              file

          free_trial: If the product has a free trial, this field can be used to disable it when
              attaching (by passing in false)

          options: Pass in quantities for prepaid features

          product_id: Product ID, set when creating the product in the Autumn dashboard

          product_ids: Can be used to attach multiple products to the customer at once. For example,
              attaching a main product and an add-on.

          reward: An Autumn promo_code or reward_id to apply at checkout

          success_url: URL to redirect to after the purchase is successful

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/checkout",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "force_checkout": force_checkout,
                    "free_trial": free_trial,
                    "invoice": invoice,
                    "options": options,
                    "product_id": product_id,
                    "product_ids": product_ids,
                    "reward": reward,
                    "setup_payment": setup_payment,
                    "success_url": success_url,
                },
                client_checkout_params.ClientCheckoutParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckoutResponse,
        )

    def query(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        range: Optional[Literal["24h", "7d", "30d", "90d", "last_cycle"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueryResponse:
        """
        Query usage analytics for a customer's features over a specified time range.

        Use this to retrieve historical usage data for dashboards, reports, or usage
        displays.

        @example

        ```typescript
        // Query 7-day usage
        const response = await client.query({
          customer_id: "cus_123",
          feature_id: "api_calls",
          range: "7d",
        });
        ```

        @param body.customer_id - The ID of the customer to query analytics for @param
        body.feature_id - The feature ID(s) to query @param body.range - Time range for
        the query (defaults to last_cycle if not provided)

        @see {@link https://docs.useautumn.com/api-reference/core/query Analytics
        Queries}

        Args:
          customer_id: The ID of the customer to query analytics for

          feature_id: The feature ID(s) to query

          range: Time range for the query (defaults to last_cycle if not provided)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/query",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "range": range,
                },
                client_query_params.ClientQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueryResponse,
        )

    def setup_payment(
        self,
        *,
        customer_id: str,
        checkout_session_params: Dict[str, object] | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SetupPaymentResponse:
        """
        Creates a session for a customer to add or update their payment method.

        Use this to collect payment information without immediately charging the
        customer.

        @example

        ```typescript
        // Setup payment method
        const response = await client.setupPayment({
          customer_id: "cus_123",
          success_url: "https://example.com/success",
        });
        ```

        @param body.customer_id - The ID of the customer @param body.success_url - URL
        to redirect to after successful payment setup. Must start with either http:// or
        https:// @param body.checkout_session_params - Additional parameters for the
        checkout session

        @see {@link https://docs.useautumn.com/api-reference/core/setup-payment Payment
        Setup}

        Args:
          customer_id: The ID of the customer

          checkout_session_params: Additional parameters for the checkout session

          customer_data: Unique identifier (eg, serial number) to detect duplicate customers and prevent
              free trial abuse

          success_url: URL to redirect to after successful payment setup. Must start with either
              http:// or https://

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/setup_payment",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "success_url": success_url,
                },
                client_setup_payment_params.ClientSetupPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SetupPaymentResponse,
        )

    def track(
        self,
        *,
        customer_id: str,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        event_name: str | Omit = omit,
        feature_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        overage_behavior: Literal["cap", "reject"] | Omit = omit,
        properties: Dict[str, object] | Omit = omit,
        skip_event: bool | Omit = omit,
        timestamp: float | Omit = omit,
        value: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrackResponse:
        """
        Track Event

        Args:
          customer_id: ID which you provided when creating the customer

          customer_data: Additional customer properties. These will be used to create or update the
              customer if they don't exist or their properties are not already set.

          entity_id: If using [entity balances](/features/feature-entities) (eg, seats), the entity
              ID to track usage for.

          event_name: An [event name](/features/tracking-usage#using-event-names) can be used in place
              of feature_id. This can be used if multiple features are tracked in the same
              event.

          feature_id: ID of the feature to track usage for. Required if event_name is not provided.
              Use this for direct feature tracking.

          idempotency_key: Unique key to prevent duplicate event recording. Use this to safely retry
              requests without creating duplicate usage records.

          overage_behavior: How to handle usage when balance is insufficient. 'cap' limits usage to
              available balance, 'reject' prevents the usage entirely.

          properties: Additional properties to attach to this usage event.

          value: The amount of usage to record. Defaults to 1. Can be negative to increase the
              balance (e.g., when removing a seat).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/track",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "event_name": event_name,
                    "feature_id": feature_id,
                    "idempotency_key": idempotency_key,
                    "overage_behavior": overage_behavior,
                    "properties": properties,
                    "skip_event": skip_event,
                    "timestamp": timestamp,
                    "value": value,
                },
                client_track_params.ClientTrackParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrackResponse,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncAutumn(AsyncAPIClient):
    customers: customers.AsyncCustomersResource
    plans: plans.AsyncPlansResource
    entities: entities.AsyncEntitiesResource
    referrals: referrals.AsyncReferralsResource
    with_raw_response: AsyncAutumnWithRawResponse
    with_streaming_response: AsyncAutumnWithStreamedResponse

    # client options
    secret_key: str
    api_version: str | None

    def __init__(
        self,
        *,
        secret_key: str | None = None,
        api_version: str | None = "2.0.0",
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncAutumn client instance.

        This automatically infers the `secret_key` argument from the `AUTUMN_SECRET_KEY` environment variable if it is not provided.
        """
        if secret_key is None:
            secret_key = os.environ.get("AUTUMN_SECRET_KEY")
        if secret_key is None:
            raise AutumnError(
                "The secret_key client option must be set either by passing secret_key to the client or by setting the AUTUMN_SECRET_KEY environment variable"
            )
        self.secret_key = secret_key

        if api_version is None:
            api_version = "2.0.0"
        self.api_version = api_version

        if base_url is None:
            base_url = os.environ.get("AUTUMN_BASE_URL")
        if base_url is None:
            base_url = f"https://api.useautumn.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.customers = customers.AsyncCustomersResource(self)
        self.plans = plans.AsyncPlansResource(self)
        self.entities = entities.AsyncEntitiesResource(self)
        self.referrals = referrals.AsyncReferralsResource(self)
        self.with_raw_response = AsyncAutumnWithRawResponse(self)
        self.with_streaming_response = AsyncAutumnWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        secret_key = self.secret_key
        return {"Authorization": f"Bearer {secret_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "x-api-version": self.api_version if self.api_version is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        secret_key: str | None = None,
        api_version: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            secret_key=secret_key or self.secret_key,
            api_version=api_version or self.api_version,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def attach(
        self,
        *,
        customer_id: str,
        checkout_session_params: object | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        force_checkout: bool | Omit = omit,
        free_trial: bool | Omit = omit,
        invoice: bool | Omit = omit,
        options: Optional[Iterable[client_attach_params.Option]] | Omit = omit,
        product_id: Optional[str] | Omit = omit,
        product_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        reward: Union[str, SequenceNotStr[str]] | Omit = omit,
        setup_payment: bool | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachResponse:
        """
        Enables a product for a customer and processes payment if their payment method
        is already on file.

        Use this when the customer already has a payment method saved. For new customers
        without payment info, use `checkout` instead.

        @example

        ```typescript
        // Attach a product to a customer
        const response = await client.attach({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/attach Product
        Attachments}

        Args:
          customer_id: Your unique identifier for the customer

          checkout_session_params: Additional parameters to pass onto Stripe when creating the checkout session

          customer_data: If auto creating a customer, the properties from this field will be used.

          entity_data: If attaching a product to an entity and auto creating the entity, the properties
              from this field will be used. feature_id is required.

          entity_id: If attaching a product to an entity, can be used to auto create the entity

          force_checkout: Always return a Stripe Checkout URL, even if the customer's card is already on
              file

          free_trial: If the product has a free trial, this field can be used to disable it when
              attaching (by passing in false)

          options: Pass in quantities for prepaid features

          product_id: Product ID, set when creating the product in the Autumn dashboard

          product_ids: Can be used to attach multiple products to the customer at once. For example,
              attaching a main product and an add-on.

          reward: An Autumn promo_code or reward_id to apply at checkout

          success_url: URL to redirect to after the purchase is successful

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/attach",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "force_checkout": force_checkout,
                    "free_trial": free_trial,
                    "invoice": invoice,
                    "options": options,
                    "product_id": product_id,
                    "product_ids": product_ids,
                    "reward": reward,
                    "setup_payment": setup_payment,
                    "success_url": success_url,
                },
                client_attach_params.ClientAttachParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AttachResponse,
        )

    async def billing_portal(
        self,
        *,
        return_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BillingPortalResponse:
        """
        Creates a billing portal session where customers can manage their subscription
        and payment methods.

        Use this to give customers self-service access to view invoices, update payment
        info, and manage subscriptions.

        @example

        ```typescript
        // Open billing portal
        const response = await client.billingPortal({
          customer_id: "cus_123",
          return_url: "https://example.com/account",
        });
        ```

        @param body.return_url - URL to redirect to when back button is clicked in the
        billing portal.

        @see {@link https://docs.useautumn.com/api-reference/core/billing-portal Billing
        Portal}

        Args:
          return_url: URL to redirect to when back button is clicked in the billing portal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/billing_portal",
            body=await async_maybe_transform(
                {"return_url": return_url}, client_billing_portal_params.ClientBillingPortalParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BillingPortalResponse,
        )

    async def cancel(
        self,
        *,
        customer_id: str,
        product_id: str,
        cancel_immediately: bool | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        prorate: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CancelResponse:
        """
        Cancel a customer's subscription to a product.

        Use this when a customer wants to stop their subscription. Supports immediate or
        end-of-period cancellation.

        @example

        ```typescript
        // Cancel a subscription
        const response = await client.cancel({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - The ID of the customer @param body.product_id - The ID
        of the product to cancel @param body.entity_id - The ID of the entity (optional)
        @param body.cancel_immediately - Whether to cancel the product immediately or at
        period end @param body.prorate - Whether to prorate the cancellation (defaults
        to true if not specified)

        @see {@link https://docs.useautumn.com/api-reference/core/cancel Cancel
        Subscriptions}

        Args:
          customer_id: The ID of the customer

          product_id: The ID of the product to cancel

          cancel_immediately: Whether to cancel the product immediately or at period end

          entity_id: The ID of the entity (optional)

          prorate: Whether to prorate the cancellation (defaults to true if not specified)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/cancel",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "cancel_immediately": cancel_immediately,
                    "entity_id": entity_id,
                    "prorate": prorate,
                },
                client_cancel_params.ClientCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CancelResponse,
        )

    async def check(
        self,
        *,
        customer_id: str,
        feature_id: str,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        properties: Dict[str, object] | Omit = omit,
        required_balance: float | Omit = omit,
        send_event: bool | Omit = omit,
        with_preview: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckResponse:
        """
        Creates a checkout session for a customer to purchase a product with payment
        collection.

        Use this for new customers or when payment info is needed. For customers with
        existing payment methods, use `attach` instead.

        @example

        ```typescript
        // Create a checkout session
        const response = await client.checkout({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/checkout Checkout
        Sessions}

        Args:
          customer_id: ID which you provided when creating the customer

          feature_id: ID of the feature to check access to. Required if product_id is not provided.

          customer_data: Properties used if customer is automatically created. Will also update if the
              name or email is not already set.

          entity_id: If using entity balances (eg, seats), the entity ID to check access for.

          required_balance: If you know the amount of the feature the end user is consuming in advance. If
              their balance is below this quantity, allowed will be false.

          send_event: If true, a usage event will be recorded together with checking access. The
              required_balance field will be used as the usage value.

          with_preview: If true, the response will include a preview object, which can be used to
              display information such as a paywall or upgrade confirmation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/check",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "properties": properties,
                    "required_balance": required_balance,
                    "send_event": send_event,
                    "with_preview": with_preview,
                },
                client_check_params.ClientCheckParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckResponse,
        )

    async def checkout(
        self,
        *,
        customer_id: str,
        checkout_session_params: object | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        force_checkout: bool | Omit = omit,
        free_trial: bool | Omit = omit,
        invoice: bool | Omit = omit,
        options: Optional[Iterable[client_checkout_params.Option]] | Omit = omit,
        product_id: Optional[str] | Omit = omit,
        product_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        reward: Union[str, SequenceNotStr[str]] | Omit = omit,
        setup_payment: bool | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckoutResponse:
        """
        Creates a checkout session for a customer to purchase a product with payment
        collection.

        Use this for new customers or when payment info is needed. For customers with
        existing payment methods, use `attach` instead.

        @example

        ```typescript
        // Create a checkout session
        const response = await client.checkout({
          customer_id: "cus_123",
          product_id: "pro_plan",
        });
        ```

        @param body.customer_id - Your unique identifier for the customer @param
        body.product_id - Product ID, set when creating the product in the Autumn
        dashboard @param body.entity_id - If attaching a product to an entity, can be
        used to auto create the entity @param body.customer_data - If auto creating a
        customer, the properties from this field will be used. @param body.entity_data -
        If attaching a product to an entity and auto creating the entity, the properties
        from this field will be used. feature_id is required. @param body.product_ids -
        Can be used to attach multiple products to the customer at once. For example,
        attaching a main product and an add-on. @param body.options - Pass in quantities
        for prepaid features @param body.free_trial - If the product has a free trial,
        this field can be used to disable it when attaching (by passing in false) @param
        body.success_url - URL to redirect to after the purchase is successful @param
        body.force_checkout - Always return a Stripe Checkout URL, even if the
        customer's card is already on file @param body.checkout_session_params -
        Additional parameters to pass onto Stripe when creating the checkout session
        @param body.reward - An Autumn promo_code or reward_id to apply at checkout

        @see {@link https://docs.useautumn.com/api-reference/core/checkout Checkout
        Sessions}

        Args:
          customer_id: Your unique identifier for the customer

          checkout_session_params: Additional parameters to pass onto Stripe when creating the checkout session

          customer_data: If auto creating a customer, the properties from this field will be used.

          entity_data: If attaching a product to an entity and auto creating the entity, the properties
              from this field will be used. feature_id is required.

          entity_id: If attaching a product to an entity, can be used to auto create the entity

          force_checkout: Always return a Stripe Checkout URL, even if the customer's card is already on
              file

          free_trial: If the product has a free trial, this field can be used to disable it when
              attaching (by passing in false)

          options: Pass in quantities for prepaid features

          product_id: Product ID, set when creating the product in the Autumn dashboard

          product_ids: Can be used to attach multiple products to the customer at once. For example,
              attaching a main product and an add-on.

          reward: An Autumn promo_code or reward_id to apply at checkout

          success_url: URL to redirect to after the purchase is successful

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/checkout",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "force_checkout": force_checkout,
                    "free_trial": free_trial,
                    "invoice": invoice,
                    "options": options,
                    "product_id": product_id,
                    "product_ids": product_ids,
                    "reward": reward,
                    "setup_payment": setup_payment,
                    "success_url": success_url,
                },
                client_checkout_params.ClientCheckoutParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckoutResponse,
        )

    async def query(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        range: Optional[Literal["24h", "7d", "30d", "90d", "last_cycle"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueryResponse:
        """
        Query usage analytics for a customer's features over a specified time range.

        Use this to retrieve historical usage data for dashboards, reports, or usage
        displays.

        @example

        ```typescript
        // Query 7-day usage
        const response = await client.query({
          customer_id: "cus_123",
          feature_id: "api_calls",
          range: "7d",
        });
        ```

        @param body.customer_id - The ID of the customer to query analytics for @param
        body.feature_id - The feature ID(s) to query @param body.range - Time range for
        the query (defaults to last_cycle if not provided)

        @see {@link https://docs.useautumn.com/api-reference/core/query Analytics
        Queries}

        Args:
          customer_id: The ID of the customer to query analytics for

          feature_id: The feature ID(s) to query

          range: Time range for the query (defaults to last_cycle if not provided)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/query",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "range": range,
                },
                client_query_params.ClientQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueryResponse,
        )

    async def setup_payment(
        self,
        *,
        customer_id: str,
        checkout_session_params: Dict[str, object] | Omit = omit,
        customer_data: CustomerData | Omit = omit,
        success_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SetupPaymentResponse:
        """
        Creates a session for a customer to add or update their payment method.

        Use this to collect payment information without immediately charging the
        customer.

        @example

        ```typescript
        // Setup payment method
        const response = await client.setupPayment({
          customer_id: "cus_123",
          success_url: "https://example.com/success",
        });
        ```

        @param body.customer_id - The ID of the customer @param body.success_url - URL
        to redirect to after successful payment setup. Must start with either http:// or
        https:// @param body.checkout_session_params - Additional parameters for the
        checkout session

        @see {@link https://docs.useautumn.com/api-reference/core/setup-payment Payment
        Setup}

        Args:
          customer_id: The ID of the customer

          checkout_session_params: Additional parameters for the checkout session

          customer_data: Unique identifier (eg, serial number) to detect duplicate customers and prevent
              free trial abuse

          success_url: URL to redirect to after successful payment setup. Must start with either
              http:// or https://

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/setup_payment",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "checkout_session_params": checkout_session_params,
                    "customer_data": customer_data,
                    "success_url": success_url,
                },
                client_setup_payment_params.ClientSetupPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SetupPaymentResponse,
        )

    async def track(
        self,
        *,
        customer_id: str,
        customer_data: CustomerData | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        event_name: str | Omit = omit,
        feature_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        overage_behavior: Literal["cap", "reject"] | Omit = omit,
        properties: Dict[str, object] | Omit = omit,
        skip_event: bool | Omit = omit,
        timestamp: float | Omit = omit,
        value: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrackResponse:
        """
        Track Event

        Args:
          customer_id: ID which you provided when creating the customer

          customer_data: Additional customer properties. These will be used to create or update the
              customer if they don't exist or their properties are not already set.

          entity_id: If using [entity balances](/features/feature-entities) (eg, seats), the entity
              ID to track usage for.

          event_name: An [event name](/features/tracking-usage#using-event-names) can be used in place
              of feature_id. This can be used if multiple features are tracked in the same
              event.

          feature_id: ID of the feature to track usage for. Required if event_name is not provided.
              Use this for direct feature tracking.

          idempotency_key: Unique key to prevent duplicate event recording. Use this to safely retry
              requests without creating duplicate usage records.

          overage_behavior: How to handle usage when balance is insufficient. 'cap' limits usage to
              available balance, 'reject' prevents the usage entirely.

          properties: Additional properties to attach to this usage event.

          value: The amount of usage to record. Defaults to 1. Can be negative to increase the
              balance (e.g., when removing a seat).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/track",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "customer_data": customer_data,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "event_name": event_name,
                    "feature_id": feature_id,
                    "idempotency_key": idempotency_key,
                    "overage_behavior": overage_behavior,
                    "properties": properties,
                    "skip_event": skip_event,
                    "timestamp": timestamp,
                    "value": value,
                },
                client_track_params.ClientTrackParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrackResponse,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AutumnWithRawResponse:
    def __init__(self, client: Autumn) -> None:
        self.customers = customers.CustomersResourceWithRawResponse(client.customers)
        self.plans = plans.PlansResourceWithRawResponse(client.plans)
        self.entities = entities.EntitiesResourceWithRawResponse(client.entities)
        self.referrals = referrals.ReferralsResourceWithRawResponse(client.referrals)

        self.attach = to_raw_response_wrapper(
            client.attach,
        )
        self.billing_portal = to_raw_response_wrapper(
            client.billing_portal,
        )
        self.cancel = to_raw_response_wrapper(
            client.cancel,
        )
        self.check = to_raw_response_wrapper(
            client.check,
        )
        self.checkout = to_raw_response_wrapper(
            client.checkout,
        )
        self.query = to_raw_response_wrapper(
            client.query,
        )
        self.setup_payment = to_raw_response_wrapper(
            client.setup_payment,
        )
        self.track = to_raw_response_wrapper(
            client.track,
        )


class AsyncAutumnWithRawResponse:
    def __init__(self, client: AsyncAutumn) -> None:
        self.customers = customers.AsyncCustomersResourceWithRawResponse(client.customers)
        self.plans = plans.AsyncPlansResourceWithRawResponse(client.plans)
        self.entities = entities.AsyncEntitiesResourceWithRawResponse(client.entities)
        self.referrals = referrals.AsyncReferralsResourceWithRawResponse(client.referrals)

        self.attach = async_to_raw_response_wrapper(
            client.attach,
        )
        self.billing_portal = async_to_raw_response_wrapper(
            client.billing_portal,
        )
        self.cancel = async_to_raw_response_wrapper(
            client.cancel,
        )
        self.check = async_to_raw_response_wrapper(
            client.check,
        )
        self.checkout = async_to_raw_response_wrapper(
            client.checkout,
        )
        self.query = async_to_raw_response_wrapper(
            client.query,
        )
        self.setup_payment = async_to_raw_response_wrapper(
            client.setup_payment,
        )
        self.track = async_to_raw_response_wrapper(
            client.track,
        )


class AutumnWithStreamedResponse:
    def __init__(self, client: Autumn) -> None:
        self.customers = customers.CustomersResourceWithStreamingResponse(client.customers)
        self.plans = plans.PlansResourceWithStreamingResponse(client.plans)
        self.entities = entities.EntitiesResourceWithStreamingResponse(client.entities)
        self.referrals = referrals.ReferralsResourceWithStreamingResponse(client.referrals)

        self.attach = to_streamed_response_wrapper(
            client.attach,
        )
        self.billing_portal = to_streamed_response_wrapper(
            client.billing_portal,
        )
        self.cancel = to_streamed_response_wrapper(
            client.cancel,
        )
        self.check = to_streamed_response_wrapper(
            client.check,
        )
        self.checkout = to_streamed_response_wrapper(
            client.checkout,
        )
        self.query = to_streamed_response_wrapper(
            client.query,
        )
        self.setup_payment = to_streamed_response_wrapper(
            client.setup_payment,
        )
        self.track = to_streamed_response_wrapper(
            client.track,
        )


class AsyncAutumnWithStreamedResponse:
    def __init__(self, client: AsyncAutumn) -> None:
        self.customers = customers.AsyncCustomersResourceWithStreamingResponse(client.customers)
        self.plans = plans.AsyncPlansResourceWithStreamingResponse(client.plans)
        self.entities = entities.AsyncEntitiesResourceWithStreamingResponse(client.entities)
        self.referrals = referrals.AsyncReferralsResourceWithStreamingResponse(client.referrals)

        self.attach = async_to_streamed_response_wrapper(
            client.attach,
        )
        self.billing_portal = async_to_streamed_response_wrapper(
            client.billing_portal,
        )
        self.cancel = async_to_streamed_response_wrapper(
            client.cancel,
        )
        self.check = async_to_streamed_response_wrapper(
            client.check,
        )
        self.checkout = async_to_streamed_response_wrapper(
            client.checkout,
        )
        self.query = async_to_streamed_response_wrapper(
            client.query,
        )
        self.setup_payment = async_to_streamed_response_wrapper(
            client.setup_payment,
        )
        self.track = async_to_streamed_response_wrapper(
            client.track,
        )


Client = Autumn

AsyncClient = AsyncAutumn
