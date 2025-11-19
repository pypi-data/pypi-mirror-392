# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.auth import key_create_params
from ..._base_client import make_request_options
from ...types.auth.key_list_response import KeyListResponse
from ...types.auth.key_create_response import KeyCreateResponse
from ...types.auth.key_revoke_response import KeyRevokeResponse

__all__ = ["KeysResource", "AsyncKeysResource"]


class KeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return KeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return KeysResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        label: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyCreateResponse:
        """
        Create a new API key for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Creates a new API key for the same user/organization
            - Returns the new API key (only shown once)
            - Supports optional labeling for key management

            **Authentication**: Requires valid API key in Authorization header

        Args:
          label: Optional label for the API key

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/auth/keys",
            body=maybe_transform({"label": label}, key_create_params.KeyCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyCreateResponse,
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
    ) -> KeyListResponse:
        """
        Retrieve all API keys for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Returns list of all API keys for the user (without the actual key values)
            - Includes metadata like creation time and last usage

            **Authentication**: Requires valid API key in Authorization header
        """
        return self._get(
            "/v1/auth/keys",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyListResponse,
        )

    def revoke(
        self,
        api_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyRevokeResponse:
        """
        Revoke (delete) an API key for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Revokes the specified API key (if it belongs to the user)
            - Returns confirmation of revocation

            **Authentication**: Requires valid API key in Authorization header

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._delete(
            f"/v1/auth/keys/{api_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyRevokeResponse,
        )


class AsyncKeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return AsyncKeysResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        label: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyCreateResponse:
        """
        Create a new API key for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Creates a new API key for the same user/organization
            - Returns the new API key (only shown once)
            - Supports optional labeling for key management

            **Authentication**: Requires valid API key in Authorization header

        Args:
          label: Optional label for the API key

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/auth/keys",
            body=await async_maybe_transform({"label": label}, key_create_params.KeyCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyCreateResponse,
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
    ) -> KeyListResponse:
        """
        Retrieve all API keys for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Returns list of all API keys for the user (without the actual key values)
            - Includes metadata like creation time and last usage

            **Authentication**: Requires valid API key in Authorization header
        """
        return await self._get(
            "/v1/auth/keys",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyListResponse,
        )

    async def revoke(
        self,
        api_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyRevokeResponse:
        """
        Revoke (delete) an API key for the authenticated user.

            This endpoint:
            - Validates the current API key authentication
            - Revokes the specified API key (if it belongs to the user)
            - Returns confirmation of revocation

            **Authentication**: Requires valid API key in Authorization header

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._delete(
            f"/v1/auth/keys/{api_key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyRevokeResponse,
        )


class KeysResourceWithRawResponse:
    def __init__(self, keys: KeysResource) -> None:
        self._keys = keys

        self.create = to_raw_response_wrapper(
            keys.create,
        )
        self.list = to_raw_response_wrapper(
            keys.list,
        )
        self.revoke = to_raw_response_wrapper(
            keys.revoke,
        )


class AsyncKeysResourceWithRawResponse:
    def __init__(self, keys: AsyncKeysResource) -> None:
        self._keys = keys

        self.create = async_to_raw_response_wrapper(
            keys.create,
        )
        self.list = async_to_raw_response_wrapper(
            keys.list,
        )
        self.revoke = async_to_raw_response_wrapper(
            keys.revoke,
        )


class KeysResourceWithStreamingResponse:
    def __init__(self, keys: KeysResource) -> None:
        self._keys = keys

        self.create = to_streamed_response_wrapper(
            keys.create,
        )
        self.list = to_streamed_response_wrapper(
            keys.list,
        )
        self.revoke = to_streamed_response_wrapper(
            keys.revoke,
        )


class AsyncKeysResourceWithStreamingResponse:
    def __init__(self, keys: AsyncKeysResource) -> None:
        self._keys = keys

        self.create = async_to_streamed_response_wrapper(
            keys.create,
        )
        self.list = async_to_streamed_response_wrapper(
            keys.list,
        )
        self.revoke = async_to_streamed_response_wrapper(
            keys.revoke,
        )
