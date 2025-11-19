# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from elicitlabs import ElicitClient, AsyncElicitClient
from tests.utils import assert_matches_type
from elicitlabs.types import PersonaListResponse, PersonaCreateResponse, PersonaRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPersonas:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: ElicitClient) -> None:
        persona = client.personas.create(
            name="Creative Writer",
        )
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: ElicitClient) -> None:
        persona = client.personas.create(
            name="Creative Writer",
            description="A persona specialized in creative writing and storytelling",
        )
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: ElicitClient) -> None:
        response = client.personas.with_raw_response.create(
            name="Creative Writer",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = response.parse()
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: ElicitClient) -> None:
        with client.personas.with_streaming_response.create(
            name="Creative Writer",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = response.parse()
            assert_matches_type(PersonaCreateResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: ElicitClient) -> None:
        persona = client.personas.retrieve(
            "persona_id",
        )
        assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: ElicitClient) -> None:
        response = client.personas.with_raw_response.retrieve(
            "persona_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = response.parse()
        assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: ElicitClient) -> None:
        with client.personas.with_streaming_response.retrieve(
            "persona_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = response.parse()
            assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: ElicitClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `persona_id` but received ''"):
            client.personas.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: ElicitClient) -> None:
        persona = client.personas.list()
        assert_matches_type(PersonaListResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: ElicitClient) -> None:
        response = client.personas.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = response.parse()
        assert_matches_type(PersonaListResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: ElicitClient) -> None:
        with client.personas.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = response.parse()
            assert_matches_type(PersonaListResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPersonas:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncElicitClient) -> None:
        persona = await async_client.personas.create(
            name="Creative Writer",
        )
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncElicitClient) -> None:
        persona = await async_client.personas.create(
            name="Creative Writer",
            description="A persona specialized in creative writing and storytelling",
        )
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncElicitClient) -> None:
        response = await async_client.personas.with_raw_response.create(
            name="Creative Writer",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = await response.parse()
        assert_matches_type(PersonaCreateResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncElicitClient) -> None:
        async with async_client.personas.with_streaming_response.create(
            name="Creative Writer",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = await response.parse()
            assert_matches_type(PersonaCreateResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncElicitClient) -> None:
        persona = await async_client.personas.retrieve(
            "persona_id",
        )
        assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncElicitClient) -> None:
        response = await async_client.personas.with_raw_response.retrieve(
            "persona_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = await response.parse()
        assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncElicitClient) -> None:
        async with async_client.personas.with_streaming_response.retrieve(
            "persona_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = await response.parse()
            assert_matches_type(PersonaRetrieveResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncElicitClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `persona_id` but received ''"):
            await async_client.personas.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncElicitClient) -> None:
        persona = await async_client.personas.list()
        assert_matches_type(PersonaListResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncElicitClient) -> None:
        response = await async_client.personas.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        persona = await response.parse()
        assert_matches_type(PersonaListResponse, persona, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncElicitClient) -> None:
        async with async_client.personas.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            persona = await response.parse()
            assert_matches_type(PersonaListResponse, persona, path=["response"])

        assert cast(Any, response.is_closed) is True
