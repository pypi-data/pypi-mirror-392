"""Unit tests for the Horizon-focused helpers."""

from __future__ import annotations

import asyncio
import types
from decimal import Decimal
from typing import cast
from unittest.mock import AsyncMock

import pytest  # type: ignore[import]
from stellar_sdk import Asset
from stellar_sdk.account import Account
from stellar_sdk.exceptions import BadResponseError
from stellar_sdk.keypair import Keypair
from stellar_sdk.server_async import ServerAsync
from stellar_sdk.transaction_envelope import TransactionEnvelope

from ovrl_sdk import NetworkPresets, OVRLClient
from ovrl_sdk.constants import (
    DEFAULT_USD_ASSET,
    OVRL_ASSET,
    OVRL_CODE,
    OVRL_HOME_DOMAIN,
    OVRL_ISSUER,
    OVRL_ISSUER_LOCKED,
    OVRL_MAX_SUPPLY,
)
from ovrl_sdk.exceptions import FriendbotError, OVRLError
from ovrl_sdk.types import (
    AccountOverview,
    BalanceSnapshot,
    AssetStats,
    FeeStats,
    PathQuote,
    PaymentPage,
    PaymentIntent,
    PaymentRecord,
)


@pytest.mark.asyncio
async def test_get_balance_returns_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    dummy_account = types.SimpleNamespace(
        account_id="GDTESTACCOUNT",
        balances=[
            {
                "asset_code": OVRL_CODE,
                "asset_issuer": OVRL_ISSUER,
                "balance": "42.0000000",
                "limit": "123.0000000",
                "buying_liabilities": "1.0000000",
                "selling_liabilities": "0.0000000",
            }
        ],
    )

    async def fake_load_account(_: str) -> object:
        return dummy_account

    monkeypatch.setattr(client, "load_account", fake_load_account)

    snapshot = await client.get_ovrl_balance(dummy_account.account_id)

    assert snapshot.account_id == dummy_account.account_id
    assert snapshot.balance == Decimal("42.0000000")
    assert snapshot.limit == Decimal("123.0000000")


@pytest.mark.asyncio
async def test_get_balance_without_trustline(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    dummy_account = types.SimpleNamespace(account_id="GDTEST", balances=[{"asset_code": "USD", "asset_issuer": "else"}])

    async def fake_load_account(_: str) -> object:
        return dummy_account

    monkeypatch.setattr(client, "load_account", fake_load_account)

    with pytest.raises(OVRLError):
        await client.get_ovrl_balance(dummy_account.account_id)


def test_asset_metadata_reports_constants() -> None:
    client = OVRLClient()
    metadata = client.asset_metadata()

    assert metadata.code == OVRL_CODE
    assert metadata.issuer == OVRL_ISSUER
    assert metadata.home_domain == OVRL_HOME_DOMAIN
    assert metadata.issuer_locked is OVRL_ISSUER_LOCKED
    assert metadata.max_supply == OVRL_MAX_SUPPLY


@pytest.mark.asyncio
async def test_create_trustline_builds_and_submits(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    account = Account(account=keypair.public_key, sequence=1)

    monkeypatch.setattr(client, "load_account", AsyncMock(return_value=account))
    submit_mock = AsyncMock(return_value={"hash": "abc123", "envelope_xdr": "AAA", "result_xdr": "BBB"})
    client.server = cast(ServerAsync, types.SimpleNamespace(submit_transaction=submit_mock))

    result = await client.create_trustline(keypair.secret)

    submit_mock.assert_awaited()
    assert result.hash == "abc123"


@pytest.mark.asyncio
async def test_friendbot_requires_configured_url() -> None:
    client = OVRLClient(network=NetworkPresets.PUBLIC)
    with pytest.raises(FriendbotError):
        await client.ensure_friendbot("GDFAKE")


@pytest.mark.asyncio
async def test_ensure_trustline_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    monkeypatch.setattr(client, "has_trustline", AsyncMock(return_value=True))
    create_mock = AsyncMock()
    monkeypatch.setattr(client, "create_trustline", create_mock)

    created = await client.ensure_trustline(keypair.secret)

    assert created is False
    create_mock.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_account_uses_friendbot(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    monkeypatch.setattr(client, "load_account", AsyncMock(side_effect=OVRLError("missing")))
    friendbot_mock = AsyncMock()
    monkeypatch.setattr(client, "ensure_friendbot", friendbot_mock)

    created = await client.ensure_account("GDACCOUNT")

    assert created is True
    friendbot_mock.assert_awaited_with("GDACCOUNT")


@pytest.mark.asyncio
async def test_inspect_account_handles_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    monkeypatch.setattr(client, "get_account_overview", AsyncMock(side_effect=OVRLError("missing")))

    status = await client.inspect_account("GDUNKNOWN")

    assert status.exists is False
    assert status.needs_friendbot is True
    assert status.has_trustline is False


@pytest.mark.asyncio
async def test_inspect_account_reports_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    overview = AccountOverview(
        account_id="GD1",
        sequence="1",
        subentry_count=0,
        last_modified_ledger=1,
        balances=[],
        signers=[],
    )
    balance = BalanceSnapshot(
        account_id="GD1",
        asset_code=OVRL_CODE,
        asset_issuer=OVRL_ISSUER,
        balance=Decimal("10"),
        limit=Decimal("100"),
        buying_liabilities=Decimal("0"),
        selling_liabilities=Decimal("0"),
    )
    monkeypatch.setattr(client, "get_account_overview", AsyncMock(return_value=overview))
    monkeypatch.setattr(client, "get_ovrl_balance", AsyncMock(return_value=balance))

    status = await client.inspect_account("GD1")

    assert status.exists is True
    assert status.has_trustline is True
    assert status.overview == overview
    assert status.balance == balance


@pytest.mark.asyncio
async def test_bootstrap_account_ensures_trustline(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    monkeypatch.setattr(client, "ensure_account", AsyncMock(return_value=True))
    monkeypatch.setattr(client, "ensure_trustline", AsyncMock(return_value=True))
    inspect_mock = AsyncMock()
    monkeypatch.setattr(client, "inspect_account", inspect_mock)

    await client.bootstrap_account(account_secret=keypair.secret)

    inspect_mock.assert_awaited_with(keypair.public_key)


class _FakeBuilder:
    def __init__(self) -> None:
        self.payments = []
        self.memo = None

    def append_payment_op(self, **kwargs):
        self.payments.append(kwargs)
        return self

    def add_memo(self, memo):
        self.memo = memo
        return self

    def set_timeout(self, *_):
        return self

    def build(self):
        class _Envelope:
            def sign(self, *_):
                return None

        return _Envelope()


@pytest.mark.asyncio
async def test_batch_pay_builds_multiple_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    monkeypatch.setattr(client, "load_account", AsyncMock(return_value=Account(account=keypair.public_key, sequence=1)))
    fake_builder = _FakeBuilder()
    monkeypatch.setattr(client, "_builder", lambda *_: fake_builder)
    submit_mock = AsyncMock(return_value={"hash": "multi"})
    client.server = cast(ServerAsync, types.SimpleNamespace(submit_transaction=submit_mock))

    intents = [
        PaymentIntent(destination=Keypair.random().public_key, amount="5"),
        {"destination": Keypair.random().public_key, "amount": "2.5"},
    ]

    result = await client.batch_pay(source_secret=keypair.secret, payouts=intents, memo="Batch")

    assert len(result) == 1
    assert result[0].hash == "multi"
    assert len(fake_builder.payments) == 2
    assert fake_builder.memo is not None


@pytest.mark.asyncio
async def test_batch_pay_chunks_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    account = Account(account=keypair.public_key, sequence=1)
    monkeypatch.setattr(client, "load_account", AsyncMock(return_value=account))

    builders: list[_FakeBuilder] = []

    def builder_factory(*_):
        builder = _FakeBuilder()
        builders.append(builder)
        return builder

    monkeypatch.setattr(client, "_builder", builder_factory)
    submit_mock = AsyncMock(side_effect=[{"hash": "chunk1"}, {"hash": "chunk2"}])
    client.server = cast(ServerAsync, types.SimpleNamespace(submit_transaction=submit_mock))

    payouts = [
        PaymentIntent(destination=Keypair.random().public_key, amount="1"),
        PaymentIntent(destination=Keypair.random().public_key, amount="2"),
    ]

    results = await client.batch_pay(source_secret=keypair.secret, payouts=payouts, chunk_size=1)

    assert len(results) == 2
    assert [result.hash for result in results] == ["chunk1", "chunk2"]
    assert len(builders) == 2
    assert all(len(builder.payments) == 1 for builder in builders)


class _DummyAsyncBuilder:
    def __init__(self, response: dict) -> None:
        self.response = response

    def for_account(self, *_):
        return self

    def limit(self, *_):
        return self

    def order(self, *_):
        return self

    def cursor(self, *_):
        return self

    async def call(self):
        return self.response


class _AssetBuilder:
    def __init__(self, response: dict) -> None:
        self.response = response

    def for_code(self, *_):
        return self

    def for_issuer(self, *_):
        return self

    def limit(self, *_):
        return self

    async def call(self):
        return self.response


class _AccountsBuilder:
    def __init__(self, response: dict) -> None:
        self.response = response

    def for_asset(self, *_):
        return self

    def limit(self, *_):
        return self

    async def call(self):
        return self.response


@pytest.mark.asyncio
async def test_list_payments_filters_to_ovrl(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "type": "payment",
                    "id": "1",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "3",
                    "asset_code": OVRL_CODE,
                    "asset_issuer": OVRL_ISSUER,
                    "created_at": "2024-01-01T00:00:00Z",
                },
                {
                    "type": "payment",
                    "id": "2",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "3",
                    "asset_code": "USD",
                    "asset_issuer": "OTHER",
                    "created_at": "2024-01-01T00:00:00Z",
                },
            ]
        }
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(payments=lambda: _DummyAsyncBuilder(response)))

    payments = await client.list_payments("GD1")

    assert len(payments) == 1
    assert payments[0].id == "1"


@pytest.mark.asyncio
async def test_list_payments_page_returns_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "type": "payment",
                    "id": "1",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "3",
                    "asset_code": OVRL_CODE,
                    "asset_issuer": OVRL_ISSUER,
                    "created_at": "2024-01-01T00:00:00Z",
                    "paging_token": "cursor-ovrl",
                },
                {
                    "type": "payment",
                    "id": "2",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "3",
                    "asset_code": "USD",
                    "asset_issuer": "OTHER",
                    "created_at": "2024-01-01T00:00:00Z",
                    "paging_token": "cursor-non",
                },
            ]
        }
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(payments=lambda: _DummyAsyncBuilder(response)))

    page = await client.list_payments_page("GD1", limit=2, cursor="prev")

    assert page.next_cursor == "cursor-non"
    assert page.record_count == 1
    assert page.total_amount == Decimal("3")
    assert page.records[0].paging_token == "cursor-ovrl"


@pytest.mark.asyncio
async def test_list_payments_page_accepts_type_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "type": "payment",
                    "id": "1",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "3",
                    "asset_code": OVRL_CODE,
                    "asset_issuer": OVRL_ISSUER,
                    "created_at": "2024-01-01T00:00:00Z",
                    "paging_token": "cursor-ovrl",
                },
                {
                    "type": "path_payment_strict_receive",
                    "id": "3",
                    "from": "GD1",
                    "to": "GD2",
                    "amount": "2",
                    "asset_code": OVRL_CODE,
                    "asset_issuer": OVRL_ISSUER,
                    "created_at": "2024-01-01T00:00:01Z",
                    "paging_token": "cursor-path",
                },
            ]
        }
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(payments=lambda: _DummyAsyncBuilder(response)))

    page = await client.list_payments_page(
        "GD1",
        limit=3,
        payment_types=["path_payment_strict_receive"],
    )

    assert page.record_count == 1
    assert page.records[0].id == "3"
    assert page.total_amount == Decimal("2")


@pytest.mark.asyncio
async def test_get_asset_stats_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "amount": "123.4560000",
                    "num_accounts": 5,
                    "num_claimable_balances": 1,
                    "claimable_balances_amount": "10.5",
                    "liquidity_pools_amount": "0.5",
                    "num_liquidity_pools": 1,
                    "home_domain": OVRL_HOME_DOMAIN,
                    "last_modified_ledger": 1234,
                    "flags": {"auth_required": True},
                }
            ]
        }
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(assets=lambda: _AssetBuilder(response)))

    stats = await client.get_asset_stats()

    assert stats.amount == Decimal("123.4560000")
    assert stats.home_domain == OVRL_HOME_DOMAIN
    assert stats.flags["auth_required"] is True


@pytest.mark.asyncio
async def test_get_circulating_supply_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    stats = AssetStats(
        amount=Decimal("20"),
        num_accounts=1,
        num_claimable_balances=0,
        claimable_balances_amount=Decimal("0"),
        liquidity_pools_amount=Decimal("0"),
        num_liquidity_pools=0,
        home_domain=OVRL_HOME_DOMAIN,
        last_modified_ledger=100,
        flags={},
    )
    monkeypatch.setattr(client, "get_asset_stats", AsyncMock(return_value=stats))
    monkeypatch.setattr(client, "fetch_home_domain_toml", AsyncMock(side_effect=OVRLError("toml missing")))

    circulating = await client.get_circulating_supply()

    assert circulating == Decimal("20")


@pytest.mark.asyncio
async def test_get_circulating_supply_excludes_token_wallets(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    stats = AssetStats(
        amount=Decimal("100"),
        num_accounts=2,
        num_claimable_balances=0,
        claimable_balances_amount=Decimal("0"),
        liquidity_pools_amount=Decimal("0"),
        num_liquidity_pools=0,
        home_domain=OVRL_HOME_DOMAIN,
        last_modified_ledger=100,
        flags={},
    )
    monkeypatch.setattr(client, "get_asset_stats", AsyncMock(return_value=stats))
    monkeypatch.setattr(
        client,
        "fetch_home_domain_toml",
        AsyncMock(
            return_value={
                "ACCOUNTS": ["GDINTERNAL"],
                "CURRENCIES": [
                    {"code": "OVRL", "distribution_accounts": ["GDDIST1"]},
                ],
            }
        ),
    )

    async def fake_balance(account_id: str) -> BalanceSnapshot:
        if account_id == "GDDIST1":
            raise OVRLError("missing trustline")
        return BalanceSnapshot(
            account_id=account_id,
            asset_code=OVRL_CODE,
            asset_issuer=OVRL_ISSUER,
            balance=Decimal("10"),
            limit=None,
            buying_liabilities=Decimal("0"),
            selling_liabilities=Decimal("0"),
        )

    monkeypatch.setattr(client, "get_ovrl_balance", fake_balance)

    circulating = await client.get_circulating_supply()

    assert circulating == Decimal("80")


class _DummyPathBuilder:
    def __init__(self, response: dict) -> None:
        self.response = response

    async def call(self):
        return self.response


class _SimpleCallBuilder:
    def __init__(self, response: dict) -> None:
        self.response = response

    async def call(self):
        return self.response


class _PathPaymentBuilder:
    def __init__(self) -> None:
        self.send_ops: list[dict] = []
        self.receive_ops: list[dict] = []
        self.memo = None

    def add_memo(self, memo):
        self.memo = memo
        return self

    def append_path_payment_strict_send_op(self, **kwargs):
        self.send_ops.append(kwargs)
        return self

    def append_path_payment_strict_receive_op(self, **kwargs):
        self.receive_ops.append(kwargs)
        return self

    def set_timeout(self, *_):
        return self

    def build(self):
        class _Envelope:
            def sign(self, *_):
                return None

        return _Envelope()


@pytest.mark.asyncio
async def test_get_ovrl_price_returns_ratio(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    quote = PathQuote(
        destination_amount=Decimal("2"),
        source_amount=Decimal("1"),
        path_assets=[],
        source_asset_code=OVRL_CODE,
        source_asset_issuer=OVRL_ISSUER,
        destination_asset_code="XLM",
        destination_asset_issuer=None,
    )
    monkeypatch.setattr(client, "quote_paths_from_ovrl", AsyncMock(return_value=[quote]))

    price = await client.quote_ovrl_price(counter_asset=Asset.native(), amount="1")

    assert price == Decimal("2")


@pytest.mark.asyncio
async def test_convert_asset_to_ovrl_uses_receive_quote(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    quote = PathQuote(
        destination_amount=Decimal("1"),
        source_amount=Decimal("2"),
        path_assets=[],
        source_asset_code="USD",
        source_asset_issuer="GDUK",
        destination_asset_code=OVRL_CODE,
        destination_asset_issuer=OVRL_ISSUER,
    )
    quote_mock = AsyncMock(return_value=[quote])
    monkeypatch.setattr(client, "quote_paths_to_ovrl", quote_mock)

    amount = await client.quote_asset_to_ovrl("10", source_asset=Asset.native())

    quote_mock.assert_awaited()
    assert amount == Decimal("5")


@pytest.mark.asyncio
async def test_swap_from_ovrl_builds_path_payment(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    eur_issuer = Keypair.random().public_key
    response = {
        "_embedded": {
            "records": [
                {
                    "destination_amount": "4",
                    "path": [
                        {"asset_type": "credit_alphanum4", "asset_code": "EUR", "asset_issuer": eur_issuer}
                    ],
                }
            ]
        }
    }
    submit_mock = AsyncMock(return_value={"hash": "swap"})
    client.server = cast(
        ServerAsync,
        types.SimpleNamespace(
            strict_send_paths=lambda *_, **__: _DummyPathBuilder(response),
            submit_transaction=submit_mock,
        ),
    )
    builder = _PathPaymentBuilder()
    monkeypatch.setattr(client, "_builder", lambda *_: builder)
    monkeypatch.setattr(client, "load_account", AsyncMock(return_value=Account(account=keypair.public_key, sequence=1)))

    result = await client.swap_from_ovrl(
        source_secret=keypair.secret,
        destination="GDDEST",
        amount="5",
        memo="swap",
    )

    submit_mock.assert_awaited()
    assert builder.memo is not None
    assert builder.send_ops[0]["dest_asset"] == DEFAULT_USD_ASSET
    assert builder.send_ops[0]["path"]
    assert result.hash == "swap"


@pytest.mark.asyncio
async def test_swap_to_ovrl_builds_receive_payment(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    keypair = Keypair.random()
    usd_issuer = Keypair.random().public_key
    response = {
        "_embedded": {
            "records": [
                {
                    "source_amount": "6",
                    "path": [
                        {"asset_type": "credit_alphanum4", "asset_code": "USD", "asset_issuer": usd_issuer}
                    ],
                }
            ]
        }
    }
    submit_mock = AsyncMock(return_value={"hash": "swap"})
    client.server = cast(
        ServerAsync,
        types.SimpleNamespace(
            strict_receive_paths=lambda *_, **__: _DummyPathBuilder(response),
            submit_transaction=submit_mock,
        ),
    )
    builder = _PathPaymentBuilder()
    monkeypatch.setattr(client, "_builder", lambda *_: builder)
    monkeypatch.setattr(client, "load_account", AsyncMock(return_value=Account(account=keypair.public_key, sequence=1)))

    result = await client.swap_to_ovrl(
        source_secret=keypair.secret,
        destination="GDDEST",
        ovrl_amount="3",
        memo="swap",
    )

    submit_mock.assert_awaited()
    assert builder.receive_ops[0]["dest_asset"] == OVRL_ASSET
    assert builder.receive_ops[0]["path"]
    assert builder.receive_ops[0]["dest_amount"] == "3"
    assert result.hash == "swap"


def test_format_price_variants() -> None:
    assert OVRLClient.format_price("1.2345", currency="usd", style="symbol", precision=2) == "$1.23"
    assert OVRLClient.format_price("1.2345", currency="usd", style="code", precision=3) == "1.235 USD"
    assert OVRLClient.format_price("1.2345", style="plain", precision=1) == "1.2"
    assert OVRLClient.format_price("1234.5", notation="grouped", precision=1) == "$1,234.5"
    assert OVRLClient.format_price("1250000", notation="compact", precision=1, style="code") == "1.3M USD"
    assert OVRLClient.format_price("-1500", notation="compact", precision=1) == "-$1.5K"
    assert OVRLClient.format_price("100.00", trim_trailing=False) == "$100.00"
    with pytest.raises(OVRLError):
        OVRLClient.format_price("1", style="emoji")
    with pytest.raises(OVRLError):
        OVRLClient.format_price("1", notation="weird")


@pytest.mark.asyncio
async def test_summarize_payments_walks_multiple_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()

    records = [
        PaymentPage(
            records=[
                PaymentRecord(
                    id="1",
                    source="GD1",
                    destination="GD2",
                    amount=Decimal("5"),
                    asset_code=OVRL_CODE,
                    asset_issuer=OVRL_ISSUER,
                    created_at="2024-01-01",
                    paging_token="cursor-1",
                )
            ],
            next_cursor="cursor-1",
            record_count=1,
            total_amount=Decimal("5"),
        ),
        PaymentPage(
            records=[
                PaymentRecord(
                    id="2",
                    source="GD1",
                    destination="GD3",
                    amount=Decimal("7"),
                    asset_code=OVRL_CODE,
                    asset_issuer=OVRL_ISSUER,
                    created_at="2024-01-02",
                    paging_token="cursor-2",
                )
            ],
            next_cursor="cursor-2",
            record_count=1,
            total_amount=Decimal("7"),
        ),
        PaymentPage(records=[], next_cursor=None, record_count=0, total_amount=Decimal("0")),
    ]

    async def fake_page(*_, **__):
        return records.pop(0)

    monkeypatch.setattr(client, "list_payments_page", fake_page)

    summary = await client.summarize_payments("GD1", max_pages=5)

    assert summary.record_count == 2
    assert summary.total_amount == Decimal("12")
    assert summary.last_cursor is None


@pytest.mark.asyncio
async def test_quote_paths_to_ovrl_returns_path(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "source_amount": "10",
                    "destination_amount": "5",
                    "source_asset_code": "USD",
                    "source_asset_issuer": "GDSOURCE",
                    "path": [
                        {"asset_type": "credit_alphanum4", "asset_code": "EUR", "asset_issuer": "GDEUR"}
                    ],
                }
            ]
        }
    }
    client.server = cast(
        ServerAsync,
        types.SimpleNamespace(
        strict_receive_paths=lambda *_, **__: _DummyPathBuilder(response)
        ),
    )

    quotes = await client.quote_paths_to_ovrl("5")

    assert quotes[0].path_assets == ["EUR:GDEUR"]
    assert quotes[0].destination_asset_code == OVRL_CODE
    assert quotes[0].destination_asset_issuer == OVRL_ISSUER


@pytest.mark.asyncio
async def test_quote_paths_from_ovrl_returns_path(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "source_amount": "5",
                    "destination_amount": "7",
                    "destination_asset_code": "USD",
                    "destination_asset_issuer": "GDUSD",
                    "path": [
                        {"asset_type": "credit_alphanum4", "asset_code": "JPY", "asset_issuer": "GDJPY"}
                    ],
                }
            ]
        }
    }
    client.server = cast(
        ServerAsync,
        types.SimpleNamespace(
            strict_send_paths=lambda *_, **__: _DummyPathBuilder(response)
        ),
    )

    quotes = await client.quote_paths_from_ovrl("5")

    assert quotes[0].path_assets == ["JPY:GDJPY"]
    assert quotes[0].destination_asset_code == "USD"




@pytest.mark.asyncio
async def test_payment_watcher_yields_new_records(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    first_page = PaymentPage(
        records=[
            PaymentRecord(
                id="1",
                source="GD1",
                destination="GD2",
                amount=Decimal("1"),
                asset_code=OVRL_CODE,
                asset_issuer=OVRL_ISSUER,
                created_at="2024-01-01",
                paging_token="cursor-1",
            )
        ],
        next_cursor="cursor-1",
        record_count=1,
        total_amount=Decimal("1"),
    )
    second_page = PaymentPage(
        records=[
            PaymentRecord(
                id="2",
                source="GD3",
                destination="GD4",
                amount=Decimal("2"),
                asset_code=OVRL_CODE,
                asset_issuer=OVRL_ISSUER,
                created_at="2024-01-02",
                paging_token="cursor-2",
            )
        ],
        next_cursor="cursor-2",
        record_count=1,
        total_amount=Decimal("2"),
    )
    responses = [first_page, second_page]

    async def fake_list_payments_page(*_, **__):
        return responses.pop(0)

    monkeypatch.setattr(client, "list_payments_page", fake_list_payments_page)

    emitted: list[PaymentRecord] = []

    async for record in client.payment_watcher("GD", poll_interval=0, max_rounds=2):
        emitted.append(record)

    assert [record.id for record in emitted] == ["1", "2"]


@pytest.mark.asyncio
async def test_payment_watcher_resumes_from_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    expected_page = PaymentPage(
        records=[
            PaymentRecord(
                id="2",
                source="GD1",
                destination="GD2",
                amount=Decimal("2"),
                asset_code=OVRL_CODE,
                asset_issuer=OVRL_ISSUER,
                created_at="2024-01-02",
                paging_token="cursor-2",
            )
        ],
        next_cursor="cursor-2",
        record_count=1,
        total_amount=Decimal("2"),
    )

    calls: list[dict] = []

    async def fake_list_payments_page(*_, **kwargs):
        calls.append(kwargs)
        return expected_page

    monkeypatch.setattr(client, "list_payments_page", fake_list_payments_page)

    emitted: list[PaymentRecord] = []

    async for record in client.payment_watcher(
        "GD",
        start_cursor="cursor-1",
        poll_interval=0,
        max_rounds=1,
    ):
        emitted.append(record)

    assert calls[0]["order"] == "asc"
    assert calls[0]["cursor"] == "cursor-1"
    assert [record.id for record in emitted] == ["2"]


@pytest.mark.asyncio
async def test_submit_with_retry_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    envelope = cast(TransactionEnvelope, types.SimpleNamespace())
    failures = [OVRLError("fail"), OVRLError("fail again")]

    async def fake_submit(*_, **__):
        if failures:
            raise failures.pop(0)
        return {"hash": "ok"}

    monkeypatch.setattr(client.server, "submit_transaction", fake_submit)

    result = await client.submit_with_retry(envelope, attempts=3, backoff_seconds=0)

    assert result.hash == "ok"


@pytest.mark.asyncio
async def test_list_top_holders_extracts_balances(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    response = {
        "_embedded": {
            "records": [
                {
                    "account_id": "GD2",
                    "balances": [
                        {
                            "asset_code": OVRL_CODE,
                            "asset_issuer": OVRL_ISSUER,
                            "balance": "30",
                            "limit": "100",
                            "buying_liabilities": "0",
                            "selling_liabilities": "0",
                        }
                    ],
                },
                {
                    "account_id": "GD1",
                    "balances": [
                        {
                            "asset_code": OVRL_CODE,
                            "asset_issuer": OVRL_ISSUER,
                            "balance": "50",
                            "limit": "100",
                            "buying_liabilities": "0",
                            "selling_liabilities": "0",
                        }
                    ],
                },
            ]
        }
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(accounts=lambda: _AccountsBuilder(response)))

    holders = await client.list_top_holders(limit=2)

    assert [holder.account_id for holder in holders] == ["GD1", "GD2"]
    assert holders[0].balance == Decimal("50")


@pytest.mark.asyncio
async def test_get_fee_stats_parses_numbers() -> None:
    client = OVRLClient()
    response = {
        "last_ledger": "123456",
        "last_ledger_base_fee": "100",
        "ledger_capacity_usage": "0.98",
        "min_accepted_fee": "100",
        "mode_accepted_fee": "200",
        "p10_accepted_fee": "120",
        "p50_accepted_fee": "200",
        "p95_accepted_fee": "300",
        "p99_accepted_fee": "400",
    }
    client.server = cast(ServerAsync, types.SimpleNamespace(fee_stats=lambda: _SimpleCallBuilder(response)))

    stats = await client.get_fee_stats()

    assert stats.last_ledger == 123456
    assert stats.ledger_capacity_usage == Decimal("0.98")
    assert stats.p99_accepted_fee == 400


@pytest.mark.asyncio
async def test_validate_home_domain_checks_toml(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    stats = AssetStats(
        amount=Decimal("20"),
        num_accounts=1,
        num_claimable_balances=0,
        claimable_balances_amount=Decimal("0"),
        liquidity_pools_amount=Decimal("0"),
        num_liquidity_pools=0,
        home_domain=OVRL_HOME_DOMAIN,
        last_modified_ledger=100,
        flags={},
    )
    monkeypatch.setattr(client, "get_asset_stats", AsyncMock(return_value=stats))
    monkeypatch.setattr(
        client,
        "fetch_home_domain_toml",
        AsyncMock(return_value={"CURRENCIES": [{"code": OVRL_CODE, "issuer": OVRL_ISSUER}]}),
    )

    assert await client.validate_home_domain() is True


@pytest.mark.asyncio
async def test_validate_home_domain_raises_for_missing_currency(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OVRLClient()
    stats = AssetStats(
        amount=Decimal("20"),
        num_accounts=1,
        num_claimable_balances=0,
        claimable_balances_amount=Decimal("0"),
        liquidity_pools_amount=Decimal("0"),
        num_liquidity_pools=0,
        home_domain=OVRL_HOME_DOMAIN,
        last_modified_ledger=100,
        flags={},
    )
    monkeypatch.setattr(client, "get_asset_stats", AsyncMock(return_value=stats))
    monkeypatch.setattr(client, "fetch_home_domain_toml", AsyncMock(return_value={"CURRENCIES": []}))

    with pytest.raises(OVRLError):
        await client.validate_home_domain()
