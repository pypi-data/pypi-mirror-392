# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.response_metadata import ResponseMetadata

__all__ = [
    "ReviewGetResponse",
    "Data",
    "DataPaykeyDetails",
    "DataPaykeyDetailsConfig",
    "DataPaykeyDetailsBalance",
    "DataPaykeyDetailsBankData",
    "DataPaykeyDetailsStatusDetails",
    "DataVerificationDetails",
    "DataVerificationDetailsBreakdown",
    "DataVerificationDetailsBreakdownAccountValidation",
    "DataVerificationDetailsBreakdownNameMatch",
]


class DataPaykeyDetailsConfig(BaseModel):
    processing_method: Optional[Literal["inline", "background", "skip"]] = None

    sandbox_outcome: Optional[Literal["standard", "active", "rejected", "review"]] = None


class DataPaykeyDetailsBalance(BaseModel):
    status: Literal["pending", "completed", "failed"]

    account_balance: Optional[int] = None
    """Account Balance when last retrieved"""

    updated_at: Optional[datetime] = None
    """Last time account balance was updated."""


class DataPaykeyDetailsBankData(BaseModel):
    account_number: str
    """Bank account number.

    This value is masked by default for security reasons. Use the /unmask endpoint
    to access the unmasked value.
    """

    account_type: Literal["checking", "savings"]

    routing_number: str
    """The routing number of the bank account."""


class DataPaykeyDetailsStatusDetails(BaseModel):
    changed_at: datetime
    """The time the status change occurred."""

    message: str
    """A human-readable description of the current status."""

    reason: Literal[
        "insufficient_funds",
        "closed_bank_account",
        "invalid_bank_account",
        "invalid_routing",
        "disputed",
        "payment_stopped",
        "owner_deceased",
        "frozen_bank_account",
        "risk_review",
        "fraudulent",
        "duplicate_entry",
        "invalid_paykey",
        "payment_blocked",
        "amount_too_large",
        "too_many_attempts",
        "internal_system_error",
        "user_request",
        "ok",
        "other_network_return",
        "payout_refused",
    ]

    source: Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]

    code: Optional[str] = None
    """The status code if applicable."""


class DataPaykeyDetails(BaseModel):
    id: str
    """Unique identifier for the paykey."""

    config: DataPaykeyDetailsConfig

    created_at: datetime
    """Timestamp of when the paykey was created."""

    label: str
    """Human-readable label used to represent this paykey in a UI."""

    paykey: str
    """The tokenized paykey value.

    This value is used to create payments and should be stored securely.
    """

    source: Literal["bank_account", "straddle", "mx", "plaid", "tan", "quiltt"]

    status: Literal["pending", "active", "inactive", "rejected", "review"]

    updated_at: datetime
    """Timestamp of the most recent update to the paykey."""

    balance: Optional[DataPaykeyDetailsBalance] = None

    bank_data: Optional[DataPaykeyDetailsBankData] = None

    customer_id: Optional[str] = None
    """Unique identifier of the related customer object."""

    expires_at: Optional[datetime] = None
    """Expiration date and time of the paykey, if applicable."""

    external_id: Optional[str] = None
    """
    Unique identifier for the paykey in your database, used for cross-referencing
    between Straddle and your systems.
    """

    institution_name: Optional[str] = None
    """Name of the financial institution."""

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the paykey in a structured
    format.
    """

    status_details: Optional[DataPaykeyDetailsStatusDetails] = None


class DataVerificationDetailsBreakdownAccountValidation(BaseModel):
    codes: List[str]

    decision: Literal["unknown", "accept", "reject", "review"]

    reason: Optional[str] = None


class DataVerificationDetailsBreakdownNameMatch(BaseModel):
    codes: List[str]

    decision: Literal["unknown", "accept", "reject", "review"]

    correlation_score: Optional[float] = None

    customer_name: Optional[str] = None

    matched_name: Optional[str] = None

    names_on_account: Optional[List[str]] = None

    reason: Optional[str] = None


class DataVerificationDetailsBreakdown(BaseModel):
    account_validation: Optional[DataVerificationDetailsBreakdownAccountValidation] = None

    name_match: Optional[DataVerificationDetailsBreakdownNameMatch] = None


class DataVerificationDetails(BaseModel):
    id: str
    """Unique identifier for the verification details."""

    breakdown: DataVerificationDetailsBreakdown

    created_at: datetime
    """Timestamp of when the verification was initiated."""

    decision: Literal["unknown", "accept", "reject", "review"]

    messages: Dict[str, str]
    """Dictionary of all messages from the paykey verification process."""

    updated_at: datetime
    """Timestamp of the most recent update to the verification details."""


class Data(BaseModel):
    paykey_details: DataPaykeyDetails

    verification_details: Optional[DataVerificationDetails] = None


class ReviewGetResponse(BaseModel):
    data: Data

    meta: ResponseMetadata
    """Metadata about the API request, including an identifier and timestamp."""

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
