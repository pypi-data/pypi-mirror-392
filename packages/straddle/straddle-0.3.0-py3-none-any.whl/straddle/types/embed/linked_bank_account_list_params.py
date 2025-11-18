# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LinkedBankAccountListParams"]


class LinkedBankAccountListParams(TypedDict, total=False):
    account_id: str
    """The unique identifier of the related account."""

    level: Literal["account", "platform"]

    page_number: int
    """Results page number. Starts at page 1."""

    page_size: int
    """Page size. Max value: 1000"""

    purpose: Literal["charges", "payouts", "billing"]
    """The purpose of the linked bank accounts to return.

    Possible values: 'charges', 'payouts', 'billing'.
    """

    sort_by: str
    """Sort By."""

    sort_order: Literal["asc", "desc"]
    """Sort Order."""

    status: Literal["created", "onboarding", "active", "rejected", "inactive", "canceled"]
    """The status of the linked bank accounts to return.

    Possible values: 'created', 'onboarding', 'active', 'inactive', 'rejected'.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
