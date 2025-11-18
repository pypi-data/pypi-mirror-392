# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BridgeInitializeParams", "Config"]


class BridgeInitializeParams(TypedDict, total=False):
    customer_id: Required[str]
    """
    The Straddle generated unique identifier of the `customer` to create a bridge
    token for.
    """

    config: Config

    external_id: Optional[str]
    """
    Unique identifier for the paykey in your database, used for cross-referencing
    between Straddle and your systems.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class Config(TypedDict, total=False):
    processing_method: Literal["inline", "background", "skip"]

    sandbox_outcome: Literal["standard", "active", "rejected", "review"]
