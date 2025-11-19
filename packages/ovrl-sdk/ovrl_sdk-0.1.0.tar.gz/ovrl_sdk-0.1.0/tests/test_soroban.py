"""Tests focused on the Soroban helper layer."""

from __future__ import annotations

import types
from decimal import Decimal
from typing import cast
from unittest.mock import AsyncMock

import pytest  # type: ignore[import]
from stellar_sdk import Keypair, scval

from ovrl_sdk import OVRLClient
from ovrl_sdk.soroban import SorobanInvocation, SorobanTokenClient, SorobanToolkit


class _DummySorobanClient:
    soroban_server = object()


@pytest.mark.asyncio
async def test_balance_scales_amount(monkeypatch: pytest.MonkeyPatch) -> None:
    invoker = AsyncMock()
    invocation = SorobanInvocation(
        transaction_hash="hash",
        status="SUCCESS",
        result_meta_xdr=None,
        raw={},
        return_value=scval.to_int128(123_000_000),
    )
    invoker.return_value = invocation
    toolkit = types.SimpleNamespace(invoke_contract=invoker)
    token = SorobanTokenClient(
        cast(OVRLClient, _DummySorobanClient()),
        contract_id="CCOVRL",
        toolkit=cast(SorobanToolkit, toolkit),
    )

    balance = await token.balance(secret=Keypair.random().secret, account_id=Keypair.random().public_key)

    assert balance == Decimal("12.3")


@pytest.mark.asyncio
async def test_transfer_includes_from_and_to_addresses(monkeypatch: pytest.MonkeyPatch) -> None:
    invoker = AsyncMock(return_value=SorobanInvocation(
        transaction_hash="hash",
        status="PENDING",
        result_meta_xdr=None,
        raw={},
        return_value=None,
    ))
    toolkit = types.SimpleNamespace(invoke_contract=invoker)
    token = SorobanTokenClient(
        cast(OVRLClient, _DummySorobanClient()),
        contract_id="CCOVRL",
        toolkit=cast(SorobanToolkit, toolkit),
    )

    sender = Keypair.random()
    destination = Keypair.random().public_key

    await token.transfer(secret=sender.secret, destination=destination, amount="5.5")

    invoker.assert_awaited()
    kwargs = invoker.await_args.kwargs  # type: ignore[union-attr]
    params = kwargs["parameters"]
    assert len(params) == 3
    assert params[0].to_xdr() == scval.to_address(sender.public_key).to_xdr()
    assert params[1].to_xdr() == scval.to_address(destination).to_xdr()


@pytest.mark.asyncio
async def test_allowance_and_approve_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    invoker = AsyncMock(return_value=SorobanInvocation(
        transaction_hash="hash",
        status="SUCCESS",
        result_meta_xdr=None,
        raw={},
        return_value=scval.to_int128(1_000_000),
    ))
    toolkit = types.SimpleNamespace(invoke_contract=invoker)
    token = SorobanTokenClient(
        cast(OVRLClient, _DummySorobanClient()),
        contract_id="CCOVRL",
        toolkit=cast(SorobanToolkit, toolkit),
    )
    owner = Keypair.random()
    spender = Keypair.random().public_key

    balance = await token.allowance(secret=owner.secret, owner=owner.public_key, spender=spender)
    assert balance == Decimal("0.1")

    await token.approve(secret=owner.secret, spender=spender, amount="5", expiration_ledger=123)
    kwargs = invoker.await_args.kwargs  # type: ignore[union-attr]
    assert kwargs["function_name"] == "approve"
    assert len(kwargs["parameters"]) == 4


@pytest.mark.asyncio
async def test_mint_and_burn_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    invoker = AsyncMock(return_value=SorobanInvocation(
        transaction_hash="hash",
        status="PENDING",
        result_meta_xdr=None,
        raw={},
        return_value=None,
    ))
    toolkit = types.SimpleNamespace(invoke_contract=invoker)
    token = SorobanTokenClient(
        cast(OVRLClient, _DummySorobanClient()),
        contract_id="CCOVRL",
        toolkit=cast(SorobanToolkit, toolkit),
    )
    admin = Keypair.random()

    await token.mint(secret=admin.secret, destination=Keypair.random().public_key, amount="10")
    await token.burn(secret=admin.secret, amount="3")

    assert invoker.await_count >= 2
