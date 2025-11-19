"""Soroban-specific helpers for contract workflows in the OVRL SDK.

Contains the RPC toolkit wrapper, invocation result types, and token client
utilities used to interact with Soroban token contracts. License: Apache-2.0.
Authors: Overlumens (github.com/overlumens) and Md Mahedi Zaman Zaber
(github.com/zaber-dev).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Optional, Sequence, TYPE_CHECKING, Union

from stellar_sdk import Keypair, scval, soroban_rpc
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban_server_async import SorobanServerAsync

from .constants import DECIMAL_SCALE
from .exceptions import SorobanTransactionRejected, SorobanUnavailableError

if TYPE_CHECKING:  # pragma: no cover
    from .client import OVRLClient


@dataclass(slots=True)
class SorobanInvocation:
    """Result envelope for a Soroban contract call with metadata for debugging."""

    transaction_hash: str
    status: str
    result_meta_xdr: Optional[str]
    raw: object
    return_value: Optional[stellar_xdr.SCVal]


class SorobanToolkit:
    """Thin wrapper around Soroban RPC to prepare, send, and poll transactions."""

    def __init__(self, client: "OVRLClient") -> None:
        """Wire the toolkit to an existing :class:`OVRLClient`.
        
        :param client: Configured OVRLClient with Soroban RPC support enabled.
        :raises SorobanUnavailableError: If the client lacks a Soroban RPC endpoint.
        """
        if client.soroban_server is None:
            raise SorobanUnavailableError("Soroban RPC is not configured for this client")
        self._client = client
        self._rpc: SorobanServerAsync = client.soroban_server

    async def invoke_contract(
        self,
        *,
        secret: str,
        contract_id: str,
        function_name: str,
        parameters: Optional[Sequence[stellar_xdr.SCVal]] = None,
        timeout: int = 300,
    ) -> SorobanInvocation:
        """Submit a contract invocation and wait for confirmation.
        
        :param secret: Secret key authorizing the transaction.
        :param contract_id: Soroban contract identifier.
        :param function_name: Exported contract function to call.
        :param parameters: Optional sequence of serialized ``SCVal`` parameters.
        :param timeout: Transaction timeout in seconds.
        :returns: :class:`SorobanInvocation` describing the finalized transaction.
        :raises SorobanTransactionRejected: If Soroban rejects or never finalizes the tx.
        """
        keypair = Keypair.from_secret(secret)
        account = await self._client.load_account(keypair.public_key)
        builder = self._client._builder(account)
        builder.append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name=function_name,
            parameters=list(parameters or []),
        )
        envelope = builder.set_timeout(timeout).build()
        envelope.sign(keypair)
        prepared = await self._rpc.prepare_transaction(envelope)
        send_response: soroban_rpc.SendTransactionResponse = await self._rpc.send_transaction(prepared)
        if send_response.status not in {
            soroban_rpc.SendTransactionStatus.PENDING,
            soroban_rpc.SendTransactionStatus.DUPLICATE,
        }:
            raise SorobanTransactionRejected(f"Soroban RPC rejected the tx with status {send_response.status}")
        tx_hash = send_response.hash
        final = await self._wait_for_result(tx_hash)
        return final

    async def _wait_for_result(self, tx_hash: str, *, poll_interval: float = 2, attempts: int = 10) -> SorobanInvocation:
        """Poll the Soroban RPC until the transaction succeeds or fails.
        
        :param tx_hash: Transaction hash returned by ``send_transaction``.
        :param poll_interval: Seconds to sleep between polls.
        :param attempts: Maximum number of poll attempts before timing out.
        :returns: Finalized :class:`SorobanInvocation` record.
        :raises SorobanTransactionRejected: If the transaction never finalizes within the attempts.
        """
        for _ in range(attempts):
            result: soroban_rpc.GetTransactionResponse = await self._rpc.get_transaction(tx_hash)
            if result.status in {
                soroban_rpc.GetTransactionStatus.SUCCESS,
                soroban_rpc.GetTransactionStatus.FAILED,
            }:
                return SorobanInvocation(
                    transaction_hash=tx_hash,
                    status=result.status.value,
                    result_meta_xdr=result.result_meta_xdr,
                    raw=result,
                    return_value=_extract_return_value(result.result_meta_xdr),
                )
            await asyncio.sleep(poll_interval)
        raise SorobanTransactionRejected("Timed out waiting for Soroban transaction to finalize")


class SorobanTokenClient:
    """High-level helpers for invoking the Soroban token interface (balance/transfer/etc)."""

    def __init__(
        self,
        client: "OVRLClient",
        contract_id: str,
        *,
        scale: int = DECIMAL_SCALE,
        toolkit: Optional[SorobanToolkit] = None,
    ) -> None:
        """Create a token helper bound to a specific Soroban token contract.
        
        :param client: Parent :class:`OVRLClient` providing signing/building helpers.
        :param contract_id: Soroban token contract identifier.
        :param scale: Decimal scale used by the contract (defaults to OVRL scale).
        :param toolkit: Optional preconfigured :class:`SorobanToolkit`.
        :raises SorobanUnavailableError: If Soroban RPC is not configured.
        """
        if client.soroban_server is None:
            raise SorobanUnavailableError("Soroban RPC is not configured for this client")
        self._toolkit = toolkit or SorobanToolkit(client)
        self._contract_id = contract_id
        self._scale = scale

    async def balance(self, *, secret: str, account_id: str) -> Optional[Decimal]:
        """Return the contract-level token balance for ``account_id``.
        
        :param secret: Secret key used for authentication (read-only call still signs).
        :param account_id: Account whose balance should be returned.
        :returns: Decimal balance using the configured scale, or None when unset.
        """
        result = await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="balance",
            parameters=[_address_scval(account_id)],
        )
        raw = _scval_to_int(result.return_value)
        return _descale(raw, self._scale)

    async def transfer(self, *, secret: str, destination: str, amount: str) -> SorobanInvocation:
        """Transfer tokens from the caller to ``destination`` using Soroban.
        
        :param secret: Secret key initiating the transfer.
        :param destination: Recipient Stellar address.
        :param amount: Human-readable token amount respecting the configured scale.
        :returns: :class:`SorobanInvocation` describing the submitted transaction.
        """
        amount_val = _amount_to_scval(amount, self._scale)
        source_address = Keypair.from_secret(secret).public_key
        return await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="transfer",
            parameters=[_address_scval(source_address), _address_scval(destination), amount_val],
        )

    async def allowance(self, *, secret: str, owner: str, spender: str) -> Optional[Decimal]:
        """Return the approved allowance between ``owner`` and ``spender``.
        
        :param secret: Secret key used to authorize the simulation request.
        :param owner: Account that granted allowance.
        :param spender: Account allowed to spend on behalf of ``owner``.
        :returns: Decimal allowance or ``None`` when no approval exists.
        """
        result = await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="allowance",
            parameters=[_address_scval(owner), _address_scval(spender)],
        )
        return _descale(_scval_to_int(result.return_value), self._scale)

    async def approve(
        self,
        *,
        secret: str,
        spender: str,
        amount: Union[str, Decimal],
        expiration_ledger: Optional[int] = None,
    ) -> SorobanInvocation:
        """Approve the ``spender`` to withdraw up to ``amount`` tokens.
        
        :param secret: Owner's secret key.
        :param spender: Account that will receive the allowance.
        :param amount: Maximum amount the spender can withdraw.
        :param expiration_ledger: Optional ledger after which the approval expires.
        :returns: :class:`SorobanInvocation` describing the approval transaction.
        """
        owner = Keypair.from_secret(secret).public_key
        params = [
            _address_scval(owner),
            _address_scval(spender),
            _amount_to_scval(amount, self._scale),
        ]
        if expiration_ledger is not None:
            params.append(scval.to_uint32(expiration_ledger))
        return await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="approve",
            parameters=params,
        )

    async def mint(self, *, secret: str, destination: str, amount: Union[str, Decimal]) -> SorobanInvocation:
        """Mint new tokens to ``destination`` (requires contract permissions).
        
        :param secret: Secret key with mint authority.
        :param destination: Recipient account for the minted amount.
        :param amount: Amount to mint (string or Decimal).
        :returns: :class:`SorobanInvocation` referencing the mint transaction.
        """
        return await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="mint",
            parameters=[_address_scval(destination), _amount_to_scval(amount, self._scale)],
        )

    async def burn(self, *, secret: str, amount: Union[str, Decimal]) -> SorobanInvocation:
        """Burn tokens from the caller's balance.
        
        :param secret: Secret key whose balance will decrease.
        :param amount: Amount to burn.
        :returns: :class:`SorobanInvocation` referencing the burn transaction.
        """
        owner = Keypair.from_secret(secret).public_key
        return await self._toolkit.invoke_contract(
            secret=secret,
            contract_id=self._contract_id,
            function_name="burn",
            parameters=[_address_scval(owner), _amount_to_scval(amount, self._scale)],
        )


def _address_scval(address: str) -> stellar_xdr.SCVal:
    """Convert a Stellar address into the Soroban SCVal address representation."""
    addr = scval.to_address(address)
    return addr


def _amount_to_scval(amount: Union[str, Decimal], scale: int) -> stellar_xdr.SCVal:
    """Scale a human-readable amount into the integer ``SCVal`` Soroban expects."""
    decimals = Decimal(str(amount))
    scaled = int((decimals * (Decimal(10) ** scale)).to_integral_value(rounding=ROUND_DOWN))
    return scval.to_int128(scaled)


def _extract_return_value(result_meta_xdr: Optional[str]) -> Optional[stellar_xdr.SCVal]:
    """Extract the return ``SCVal`` from the transaction meta XDR, if present."""
    if not result_meta_xdr:
        return None
    meta = stellar_xdr.TransactionMeta.from_xdr(result_meta_xdr)
    if meta.v3 and meta.v3.soroban_meta and meta.v3.soroban_meta.return_value:
        return meta.v3.soroban_meta.return_value
    return None


def _scval_to_int(value: Optional[stellar_xdr.SCVal]) -> Optional[int]:
    """Convert an ``SCVal`` (i64/i128) into a Python integer."""
    if value is None:
        return None
    if value.type == stellar_xdr.SCValType.SCV_I128:
        high = value.i128.hi.int64
        low = value.i128.lo.uint64
        return (high << 64) + low
    if value.type == stellar_xdr.SCValType.SCV_I64:
        return value.i64.int64
    return None


def _descale(value: Optional[int], scale: int) -> Optional[Decimal]:
    """Convert the scaled integer back into a Decimal using ``scale`` places."""
    if value is None:
        return None
    divisor = Decimal(10) ** scale
    return Decimal(value) / divisor


__all__ = ["SorobanInvocation", "SorobanTokenClient", "SorobanToolkit"]
