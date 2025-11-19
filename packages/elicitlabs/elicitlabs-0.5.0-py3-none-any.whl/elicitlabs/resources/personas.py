# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import persona_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.persona_list_response import PersonaListResponse
from ..types.persona_create_response import PersonaCreateResponse
from ..types.persona_retrieve_response import PersonaRetrieveResponse

__all__ = ["PersonasResource", "AsyncPersonasResource"]


class PersonasResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PersonasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return PersonasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PersonasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return PersonasResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        description: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaCreateResponse:
        """
        Create a new persona for the authenticated user.

            This endpoint:
            - Creates a new persona with the provided name and description
            - Associates the persona with the authenticated user
            - Returns the created persona with all metadata

            **Authentication**: Requires valid API key or JWT token

        Args:
          name: Persona name

          description: Optional persona description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/personas",
            body=maybe_transform(
                {
                    "name": name,
                    "description": description,
                },
                persona_create_params.PersonaCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaCreateResponse,
        )

    def retrieve(
        self,
        persona_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaRetrieveResponse:
        """
        Retrieve details of a specific persona by its unique identifier.

            This endpoint:
            - Returns full persona information including metadata
            - Includes user information for the persona owner
            - Returns 404 if persona is not found

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not persona_id:
            raise ValueError(f"Expected a non-empty value for `persona_id` but received {persona_id!r}")
        return self._get(
            f"/v1/personas/{persona_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaListResponse:
        """
        Get all personas belonging to the authenticated user.

            This endpoint:
            - Returns all personas created by the authenticated user
            - Includes persona metadata (name, description, creation date)
            - Provides user information for each persona

            **Authentication**: Requires valid API key or JWT token
        """
        return self._get(
            "/v1/personas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaListResponse,
        )


class AsyncPersonasResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPersonasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPersonasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPersonasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return AsyncPersonasResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaCreateResponse:
        """
        Create a new persona for the authenticated user.

            This endpoint:
            - Creates a new persona with the provided name and description
            - Associates the persona with the authenticated user
            - Returns the created persona with all metadata

            **Authentication**: Requires valid API key or JWT token

        Args:
          name: Persona name

          description: Optional persona description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/personas",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "description": description,
                },
                persona_create_params.PersonaCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaCreateResponse,
        )

    async def retrieve(
        self,
        persona_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaRetrieveResponse:
        """
        Retrieve details of a specific persona by its unique identifier.

            This endpoint:
            - Returns full persona information including metadata
            - Includes user information for the persona owner
            - Returns 404 if persona is not found

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not persona_id:
            raise ValueError(f"Expected a non-empty value for `persona_id` but received {persona_id!r}")
        return await self._get(
            f"/v1/personas/{persona_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PersonaListResponse:
        """
        Get all personas belonging to the authenticated user.

            This endpoint:
            - Returns all personas created by the authenticated user
            - Includes persona metadata (name, description, creation date)
            - Provides user information for each persona

            **Authentication**: Requires valid API key or JWT token
        """
        return await self._get(
            "/v1/personas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PersonaListResponse,
        )


class PersonasResourceWithRawResponse:
    def __init__(self, personas: PersonasResource) -> None:
        self._personas = personas

        self.create = to_raw_response_wrapper(
            personas.create,
        )
        self.retrieve = to_raw_response_wrapper(
            personas.retrieve,
        )
        self.list = to_raw_response_wrapper(
            personas.list,
        )


class AsyncPersonasResourceWithRawResponse:
    def __init__(self, personas: AsyncPersonasResource) -> None:
        self._personas = personas

        self.create = async_to_raw_response_wrapper(
            personas.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            personas.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            personas.list,
        )


class PersonasResourceWithStreamingResponse:
    def __init__(self, personas: PersonasResource) -> None:
        self._personas = personas

        self.create = to_streamed_response_wrapper(
            personas.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            personas.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            personas.list,
        )


class AsyncPersonasResourceWithStreamingResponse:
    def __init__(self, personas: AsyncPersonasResource) -> None:
        self._personas = personas

        self.create = async_to_streamed_response_wrapper(
            personas.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            personas.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            personas.list,
        )
