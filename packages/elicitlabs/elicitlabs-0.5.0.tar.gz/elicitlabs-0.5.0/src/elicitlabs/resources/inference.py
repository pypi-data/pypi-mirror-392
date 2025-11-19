# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional

import httpx

from ..types import inference_generate_completion_params, inference_generate_persona_chat_params
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
from ..types.inference_generate_completion_response import InferenceGenerateCompletionResponse
from ..types.inference_generate_persona_chat_response import InferenceGeneratePersonaChatResponse

__all__ = ["InferenceResource", "AsyncInferenceResource"]


class InferenceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return InferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return InferenceResourceWithStreamingResponse(self)

    def generate_completion(
        self,
        *,
        content: Union[str, Iterable[Dict[str, str]]],
        user_id: str,
        disabled_learning: bool | Omit = omit,
        model: str | Omit = omit,
        session_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceGenerateCompletionResponse:
        """
        Generate personalized AI completion using the Elicit Labs Modal System.

            This endpoint:
            - Takes raw messages or user query
            - Retrieves relevant memories and personalizes the context
            - Generates personalized AI response using the specified LLM model
            - Optionally learns from the conversation (disabled_learning=False)
            - Returns formatted messages with AI response

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          content: Content to process

          user_id: User ID

          disabled_learning: Whether to disable learning

          model: LLM model to use for generation

          session_id: Session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/inference/completion",
            body=maybe_transform(
                {
                    "content": content,
                    "user_id": user_id,
                    "disabled_learning": disabled_learning,
                    "model": model,
                    "session_id": session_id,
                },
                inference_generate_completion_params.InferenceGenerateCompletionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceGenerateCompletionResponse,
        )

    def generate_persona_chat(
        self,
        *,
        content: Union[str, Iterable[Dict[str, str]]],
        user_id: str,
        disabled_learning: bool | Omit = omit,
        model: str | Omit = omit,
        session_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceGeneratePersonaChatResponse:
        """
        Generate AI response as a specific persona with Elicit Labs Modal System.

            This endpoint:
            - Retrieves persona information and characteristics
            - Formats messages with persona-specific context and memories
            - Generates response in the persona's unique style and voice
            - Optionally learns from the conversation (disabled_learning=False)
            - Returns synchronous response with formatted messages

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          content: Content to process

          user_id: User ID (persona ID)

          disabled_learning: Whether to disable learning

          model: LLM model to use for generation

          session_id: Session identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/inference/persona-chat",
            body=maybe_transform(
                {
                    "content": content,
                    "user_id": user_id,
                    "disabled_learning": disabled_learning,
                    "model": model,
                    "session_id": session_id,
                },
                inference_generate_persona_chat_params.InferenceGeneratePersonaChatParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceGeneratePersonaChatResponse,
        )


class AsyncInferenceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncInferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/elicitlabs-python-sdk#with_streaming_response
        """
        return AsyncInferenceResourceWithStreamingResponse(self)

    async def generate_completion(
        self,
        *,
        content: Union[str, Iterable[Dict[str, str]]],
        user_id: str,
        disabled_learning: bool | Omit = omit,
        model: str | Omit = omit,
        session_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceGenerateCompletionResponse:
        """
        Generate personalized AI completion using the Elicit Labs Modal System.

            This endpoint:
            - Takes raw messages or user query
            - Retrieves relevant memories and personalizes the context
            - Generates personalized AI response using the specified LLM model
            - Optionally learns from the conversation (disabled_learning=False)
            - Returns formatted messages with AI response

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          content: Content to process

          user_id: User ID

          disabled_learning: Whether to disable learning

          model: LLM model to use for generation

          session_id: Session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/inference/completion",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "user_id": user_id,
                    "disabled_learning": disabled_learning,
                    "model": model,
                    "session_id": session_id,
                },
                inference_generate_completion_params.InferenceGenerateCompletionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceGenerateCompletionResponse,
        )

    async def generate_persona_chat(
        self,
        *,
        content: Union[str, Iterable[Dict[str, str]]],
        user_id: str,
        disabled_learning: bool | Omit = omit,
        model: str | Omit = omit,
        session_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceGeneratePersonaChatResponse:
        """
        Generate AI response as a specific persona with Elicit Labs Modal System.

            This endpoint:
            - Retrieves persona information and characteristics
            - Formats messages with persona-specific context and memories
            - Generates response in the persona's unique style and voice
            - Optionally learns from the conversation (disabled_learning=False)
            - Returns synchronous response with formatted messages

            **Authentication**: Requires valid API key or JWT token in Authorization header

        Args:
          content: Content to process

          user_id: User ID (persona ID)

          disabled_learning: Whether to disable learning

          model: LLM model to use for generation

          session_id: Session identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/inference/persona-chat",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "user_id": user_id,
                    "disabled_learning": disabled_learning,
                    "model": model,
                    "session_id": session_id,
                },
                inference_generate_persona_chat_params.InferenceGeneratePersonaChatParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceGeneratePersonaChatResponse,
        )


class InferenceResourceWithRawResponse:
    def __init__(self, inference: InferenceResource) -> None:
        self._inference = inference

        self.generate_completion = to_raw_response_wrapper(
            inference.generate_completion,
        )
        self.generate_persona_chat = to_raw_response_wrapper(
            inference.generate_persona_chat,
        )


class AsyncInferenceResourceWithRawResponse:
    def __init__(self, inference: AsyncInferenceResource) -> None:
        self._inference = inference

        self.generate_completion = async_to_raw_response_wrapper(
            inference.generate_completion,
        )
        self.generate_persona_chat = async_to_raw_response_wrapper(
            inference.generate_persona_chat,
        )


class InferenceResourceWithStreamingResponse:
    def __init__(self, inference: InferenceResource) -> None:
        self._inference = inference

        self.generate_completion = to_streamed_response_wrapper(
            inference.generate_completion,
        )
        self.generate_persona_chat = to_streamed_response_wrapper(
            inference.generate_persona_chat,
        )


class AsyncInferenceResourceWithStreamingResponse:
    def __init__(self, inference: AsyncInferenceResource) -> None:
        self._inference = inference

        self.generate_completion = async_to_streamed_response_wrapper(
            inference.generate_completion,
        )
        self.generate_persona_chat = async_to_streamed_response_wrapper(
            inference.generate_persona_chat,
        )
