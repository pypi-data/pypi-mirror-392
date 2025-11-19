"""Lightweight dataclasses modeling responses for the OVRL SDK.

Defines high-level records for balances, payments, quotes, pagination, and
transaction summaries returned by the async client. License: Apache-2.0.
Authors: Overlumens (github.com/overlumens) and Md Mahedi Zaman Zaber
(github.com/zaber-dev).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Union


@dataclass(slots=True)
class BalanceSnapshot:
    """Represents a point-in-time OVRL balance pulled from Horizon."""

    account_id: str
    asset_code: str
    asset_issuer: str
    balance: Decimal
    limit: Optional[Decimal]
    buying_liabilities: Decimal
    selling_liabilities: Decimal


@dataclass(slots=True)
class PaymentIntent:
    """Declarative payout description consumed by `OVRLClient.batch_pay`."""

    destination: str
    amount: Union[Decimal, str]
    source: Optional[str] = None
    memo: Optional[str] = None


@dataclass(slots=True)
class TransactionResult:
    """Minimal structure describing a submitted transaction hash/XDR blobs."""

    hash: str
    envelope_xdr: Optional[str] = None
    result_xdr: Optional[str] = None


@dataclass(slots=True)
class AccountOverview:
    """Lightweight wrapper around the Horizon account payload."""

    account_id: str
    sequence: str
    subentry_count: int
    last_modified_ledger: Optional[int]
    balances: List[dict]
    signers: List[dict]


@dataclass(slots=True)
class AccountStatus:
    """High-level status report produced by `OVRLClient.inspect_account`."""

    account_id: str
    exists: bool
    has_trustline: bool
    overview: Optional[AccountOverview]
    balance: Optional[BalanceSnapshot]
    needs_friendbot: bool


@dataclass(slots=True)
class PaymentRecord:
    """Typed version of a payment response returned by Horizon."""

    id: str
    source: str
    destination: Optional[str]
    amount: Decimal
    asset_code: str
    asset_issuer: Optional[str]
    created_at: str
    memo: Optional[str] = None
    paging_token: Optional[str] = None


@dataclass(slots=True)
class PathQuote:
    """Normalized strict send/receive path quote for logging or decision making."""

    destination_amount: Decimal
    source_amount: Decimal
    path_assets: Sequence[str] = field(default_factory=list)
    source_asset_code: Optional[str] = None
    source_asset_issuer: Optional[str] = None
    destination_asset_code: Optional[str] = None
    destination_asset_issuer: Optional[str] = None


@dataclass(slots=True)
class AssetMetadata:
    """Static attributes describing the OVRL asset."""

    code: str
    issuer: str
    home_domain: str
    max_supply: Decimal
    issuer_locked: bool
    decimal_scale: int


@dataclass(slots=True)
class AssetStats:
    """Aggregated Horizon stats for OVRL (supply, holders, flags)."""

    amount: Decimal
    num_accounts: int
    num_claimable_balances: int
    claimable_balances_amount: Decimal
    liquidity_pools_amount: Decimal
    num_liquidity_pools: int
    home_domain: Optional[str]
    last_modified_ledger: Optional[int]
    flags: Dict[str, bool]


@dataclass(slots=True)
class PaymentPage:
    """Single page of payment history plus pagination metadata."""

    records: List[PaymentRecord]
    next_cursor: Optional[str]
    record_count: int
    total_amount: Decimal


@dataclass(slots=True)
class PaymentSummary:
    """Aggregate stats produced by `OVRLClient.summarize_payments`."""

    record_count: int
    total_amount: Decimal
    last_cursor: Optional[str]


@dataclass(slots=True)
class FeeStats:
    """Snapshot of Horizon fee percentile metrics."""

    last_ledger: int
    last_ledger_base_fee: int
    ledger_capacity_usage: Decimal
    min_accepted_fee: int
    mode_accepted_fee: int
    p10_accepted_fee: int
    p50_accepted_fee: int
    p95_accepted_fee: int
    p99_accepted_fee: int


__all__ = [
    "AccountOverview",
    "AccountStatus",
    "AssetMetadata",
    "AssetStats",
    "BalanceSnapshot",
    "FeeStats",
    "PathQuote",
    "PaymentIntent",
    "PaymentPage",
    "PaymentRecord",
    "PaymentSummary",
    "TransactionResult",
]
