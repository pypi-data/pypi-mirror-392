# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.paykeys import review_decision_params
from ...types.paykey_v1 import PaykeyV1
from ...types.paykeys.review_get_response import ReviewGetResponse

__all__ = ["ReviewResource", "AsyncReviewResource"]


class ReviewResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReviewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return ReviewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReviewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return ReviewResourceWithStreamingResponse(self)

    def decision(
        self,
        id: str,
        *,
        status: Literal["active", "rejected"],
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PaykeyV1:
        """
        Update the status of a paykey when in review status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Idempotency-Key": idempotency_key,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._patch(
            f"/v1/paykeys/{id}/review",
            body=maybe_transform({"status": status}, review_decision_params.ReviewDecisionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    def get(
        self,
        id: str,
        *,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReviewGetResponse:
        """
        Get additional details about a paykey.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get(
            f"/v1/paykeys/{id}/review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReviewGetResponse,
        )

    def refresh_review(
        self,
        id: str,
        *,
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PaykeyV1:
        """Updates the decision of a paykey's review validation.

        This endpoint allows you
        to refresh the outcome of a paykey's decision and is useful for correcting or
        updating the status of a paykey's verification.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Idempotency-Key": idempotency_key,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/paykeys/{id}/refresh_review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )


class AsyncReviewResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReviewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncReviewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReviewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncReviewResourceWithStreamingResponse(self)

    async def decision(
        self,
        id: str,
        *,
        status: Literal["active", "rejected"],
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PaykeyV1:
        """
        Update the status of a paykey when in review status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Idempotency-Key": idempotency_key,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._patch(
            f"/v1/paykeys/{id}/review",
            body=await async_maybe_transform({"status": status}, review_decision_params.ReviewDecisionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )

    async def get(
        self,
        id: str,
        *,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReviewGetResponse:
        """
        Get additional details about a paykey.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._get(
            f"/v1/paykeys/{id}/review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReviewGetResponse,
        )

    async def refresh_review(
        self,
        id: str,
        *,
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PaykeyV1:
        """Updates the decision of a paykey's review validation.

        This endpoint allows you
        to refresh the outcome of a paykey's decision and is useful for correcting or
        updating the status of a paykey's verification.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Idempotency-Key": idempotency_key,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/paykeys/{id}/refresh_review",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PaykeyV1,
        )


class ReviewResourceWithRawResponse:
    def __init__(self, review: ReviewResource) -> None:
        self._review = review

        self.decision = to_raw_response_wrapper(
            review.decision,
        )
        self.get = to_raw_response_wrapper(
            review.get,
        )
        self.refresh_review = to_raw_response_wrapper(
            review.refresh_review,
        )


class AsyncReviewResourceWithRawResponse:
    def __init__(self, review: AsyncReviewResource) -> None:
        self._review = review

        self.decision = async_to_raw_response_wrapper(
            review.decision,
        )
        self.get = async_to_raw_response_wrapper(
            review.get,
        )
        self.refresh_review = async_to_raw_response_wrapper(
            review.refresh_review,
        )


class ReviewResourceWithStreamingResponse:
    def __init__(self, review: ReviewResource) -> None:
        self._review = review

        self.decision = to_streamed_response_wrapper(
            review.decision,
        )
        self.get = to_streamed_response_wrapper(
            review.get,
        )
        self.refresh_review = to_streamed_response_wrapper(
            review.refresh_review,
        )


class AsyncReviewResourceWithStreamingResponse:
    def __init__(self, review: AsyncReviewResource) -> None:
        self._review = review

        self.decision = async_to_streamed_response_wrapper(
            review.decision,
        )
        self.get = async_to_streamed_response_wrapper(
            review.get,
        )
        self.refresh_review = async_to_streamed_response_wrapper(
            review.refresh_review,
        )
