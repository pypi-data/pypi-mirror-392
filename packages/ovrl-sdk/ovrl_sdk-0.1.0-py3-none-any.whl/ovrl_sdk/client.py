"""Async helpers for Horizon/Soroban operations tied to the OVRL asset.

This module implements the high-level `OVRLClient` used for account bootstrap,
payments, quoting, swaps, monitoring, and Soroban contract execution.
License: Apache-2.0. Authors: Overlumens (github.com/overlumens) and
Md Mahedi Zaman Zaber (github.com/zaber-dev).
"""

from __future__ import annotations

import asyncio
import time
import tomllib
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, AsyncIterator, Iterable, List, Optional, Sequence, Tuple, Union

from aiohttp import ClientSession, ClientTimeout
from stellar_sdk import Asset, Keypair, TextMemo, TransactionBuilder, TransactionEnvelope
from stellar_sdk.client.aiohttp_client import AiohttpClient
from stellar_sdk.exceptions import BadResponseError, NotFoundError
from stellar_sdk.server_async import ServerAsync
from stellar_sdk.soroban_server_async import SorobanServerAsync

from .config import NetworkConfig, NetworkPresets
from .constants import (
    DEFAULT_BASE_FEE,
    DEFAULT_TRUSTLINE_LIMIT,
    DEFAULT_USD_ASSET,
    DECIMAL_SCALE,
    OVRL_ASSET,
    OVRL_CODE,
    OVRL_HOME_DOMAIN,
    OVRL_ISSUER,
    OVRL_ISSUER_LOCKED,
    OVRL_MAX_SUPPLY,
)
from .exceptions import FriendbotError, OVRLError, SorobanUnavailableError
from .types import (
    AccountOverview,
    AccountStatus,
    AssetMetadata,
    AssetStats,
    BalanceSnapshot,
    FeeStats,
    PathQuote,
    PaymentIntent,
    PaymentPage,
    PaymentRecord,
    PaymentSummary,
    TransactionResult,
)


MAX_OPERATIONS_PER_TX = 100


class OVRLClient:
    """Async-first helper that wraps Horizon/Soroban flows for the OVRL token.

    The client wires up the correct network endpoints, asset metadata, quoting helpers,
    and transaction builders so developers can bootstrap accounts, create trustlines,
    send payments, inspect history, and perform swaps without re-learning the raw
    `stellar-sdk` surface. Instantiate it with a `NetworkPresets` value (or custom
    config) and reuse the object across your async tasks.
    """

    def __init__(
        self,
        *,
        network: NetworkConfig = NetworkPresets.TESTNET,
        base_fee: int = DEFAULT_BASE_FEE,
        aiohttp_client: Optional[AiohttpClient] = None,
    ) -> None:
        """Create a client bound to a specific network and fee configuration.
        
        :param network: Network configuration or preset describing Horizon/Soroban URLs.
        :param base_fee: Default base fee (in stroops) for built transactions.
        :param aiohttp_client: Optional shared HTTP client; one will be created when omitted.
        """

        self.network = network
        self.base_fee = base_fee
        self._owns_client = aiohttp_client is None
        self._http_client = aiohttp_client or AiohttpClient()
        self.server = ServerAsync(network.horizon_url, client=self._http_client)
        self.soroban_server = (
            SorobanServerAsync(network.soroban_rpc_url, client=self._http_client)
            if network.soroban_rpc_url
            else None
        )
        self._soroban_toolkit = None

    async def close(self) -> None:
        """Dispose the internally owned HTTP client, if any.
        
        :returns: None. Provided for symmetry with async context managers.
        """

        if self._owns_client:
            await self._http_client.close()

    async def load_account(self, account_id: str):
        """Load an account from Horizon or raise :class:`OVRLError` if missing.
        
        :param account_id: Public key to fetch from Horizon.
        :returns: The Horizon account wrapper returned by `stellar-sdk`.
        :raises OVRLError: When the account cannot be found.
        """

        try:
            return await self.server.load_account(account_id)
        except NotFoundError as exc:  # pragma: no cover - passthrough
            raise OVRLError(f"Account {account_id} was not found") from exc

    async def ensure_friendbot(self, account_id: str) -> dict[str, Any]:
        """Invoke the configured Friendbot endpoint for a target account.
        
        :param account_id: Public key that should receive the Friendbot funding.
        :returns: Parsed JSON response from Friendbot (status, tx hash, etc.).
        :raises FriendbotError: If Friendbot is unavailable or responds with an error.
        """

        if not self.network.friendbot_url:
            raise FriendbotError("Friendbot is not configured for this network")
        async with ClientSession() as session:
            async with session.get(self.network.friendbot_url, params={"addr": account_id}) as response:
                if response.status >= 400:
                    body = await response.text()
                    raise FriendbotError(f"Friendbot failed with {response.status}: {body}")
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return await response.json()
                return {"message": await response.text()}

    async def inspect_account(self, account_id: str) -> AccountStatus:
        """Return summarized account status including trustline and balance details.
        
        :param account_id: Public key to inspect.
        :returns: AccountStatus snapshot describing existence, trustline, and balance.
        """

        overview: Optional[AccountOverview]
        balance: Optional[BalanceSnapshot] = None
        exists = True
        try:
            overview = await self.get_account_overview(account_id)
        except OVRLError:
            exists = False
            overview = None

        has_trustline = False
        if exists:
            try:
                balance = await self.get_ovrl_balance(account_id)
                has_trustline = True
            except OVRLError:
                balance = None

        needs_friendbot = not exists and self.network.friendbot_url is not None
        return AccountStatus(
            account_id=account_id,
            exists=exists,
            has_trustline=has_trustline,
            overview=overview,
            balance=balance,
            needs_friendbot=needs_friendbot,
        )

    def asset_metadata(self) -> AssetMetadata:
        """Return static metadata describing the OVRL asset.
        
        :returns: AssetMetadata with code, issuer, max supply, decimals, etc.
        """

        return AssetMetadata(
            code=OVRL_CODE,
            issuer=OVRL_ISSUER,
            home_domain=OVRL_HOME_DOMAIN,
            max_supply=OVRL_MAX_SUPPLY,
            issuer_locked=OVRL_ISSUER_LOCKED,
            decimal_scale=DECIMAL_SCALE,
        )

    async def get_ovrl_balance(self, account_id: str) -> BalanceSnapshot:
        """Fetch the OVRL balance snapshot for the given Stellar account.
        
        :param account_id: Public key whose OVRL balance should be fetched.
        :returns: BalanceSnapshot describing limit, balance, and liabilities.
        :raises OVRLError: If the account lacks an OVRL trustline.
        """

        account = await self.load_account(account_id)
        balances = getattr(account, "balances", [])
        for balance in balances:
            if balance.get("asset_code") == OVRL_CODE and balance.get("asset_issuer") == OVRL_ISSUER:
                return BalanceSnapshot(
                    account_id=getattr(account, "account_id", account_id),
                    asset_code=OVRL_CODE,
                    asset_issuer=OVRL_ISSUER,
                    balance=Decimal(balance["balance"]),
                    limit=Decimal(balance["limit"]) if balance.get("limit") else None,
                    buying_liabilities=Decimal(balance.get("buying_liabilities", "0")),
                    selling_liabilities=Decimal(balance.get("selling_liabilities", "0")),
                )
        raise OVRLError("Account does not have an OVRL balance yet. Create a trustline first.")

    async def get_asset_stats(self) -> AssetStats:
        """Retrieve Horizon-reported aggregate statistics for OVRL.
        
        :returns: AssetStats representing supply, holders, liquidity pools, etc.
        """

        builder = self.server.assets().for_code(OVRL_CODE).for_issuer(OVRL_ISSUER).limit(1)
        response = await builder.call()
        records = self._embedded_records(response)
        if not records:
            raise OVRLError("Asset stats for OVRL are not available on Horizon")
        record = records[0]
        last_modified = record.get("last_modified_ledger")
        return AssetStats(
            amount=Decimal(record.get("amount", "0")),
            num_accounts=int(record.get("num_accounts", 0)),
            num_claimable_balances=int(record.get("num_claimable_balances", 0)),
            claimable_balances_amount=Decimal(record.get("claimable_balances_amount", "0")),
            liquidity_pools_amount=Decimal(record.get("liquidity_pools_amount", "0")),
            num_liquidity_pools=int(record.get("num_liquidity_pools", 0)),
            home_domain=record.get("home_domain"),
            last_modified_ledger=int(last_modified) if last_modified is not None else None,
            flags=record.get("flags", {}),
        )

    async def get_circulating_supply(self) -> Decimal:
        """Compute circulating supply after subtracting token-owned wallets.
        
        :returns: Decimal supply excluding issuer-controlled holdings.
        """

        stats = await self.get_asset_stats()
        try:
            toml_data = await self.fetch_home_domain_toml()
        except OVRLError:
            return stats.amount
        internal_accounts = self._token_owned_accounts(toml_data)
        if not internal_accounts:
            return stats.amount
        internal_holdings = await self._sum_internal_holdings(internal_accounts)
        circulating = stats.amount - internal_holdings
        return circulating if circulating > Decimal("0") else Decimal("0")

    async def has_trustline(self, account_id: str) -> bool:
        """Check whether the account already holds a trustline for OVRL.
        
        :param account_id: Public key to inspect.
        :returns: True if the trustline exists, otherwise False.
        """

        account = await self.load_account(account_id)
        balances = getattr(account, "balances", [])
        return any(bal.get("asset_code") == OVRL_CODE and bal.get("asset_issuer") == OVRL_ISSUER for bal in balances)

    async def ensure_trustline(self, secret: str, *, limit: str = DEFAULT_TRUSTLINE_LIMIT) -> bool:
        """Create a trustline if missing and return whether one was added.
        
        :param secret: Secret key that should sign the change-trust operation.
        :param limit: Optional limit to apply to the trustline.
        :returns: True if a new trustline was created, False when it already existed.
        """

        keypair = Keypair.from_secret(secret)
        if await self.has_trustline(keypair.public_key):
            return False
        await self.create_trustline(secret, limit=limit)
        return True

    async def bootstrap_account(
        self,
        *,
        account_secret: str,
        funding_secret: Optional[str] = None,
        starting_balance: str = "2",
        trustline_limit: str = DEFAULT_TRUSTLINE_LIMIT,
    ) -> AccountStatus:
        """Ensure the account exists, is funded, and has the OVRL trustline.
        
        :param account_secret: Secret for the account to initialize.
        :param funding_secret: Optional sponsor for account creation when Friendbot is absent.
        :param starting_balance: Lumens sent when creating the account.
        :param trustline_limit: Limit applied to the OVRL trustline.
        :returns: AccountStatus after the bootstrap workflow completes.
        """

        keypair = Keypair.from_secret(account_secret)
        await self.ensure_account(
            keypair.public_key,
            funding_secret=funding_secret,
            starting_balance=starting_balance,
        )
        await self.ensure_trustline(account_secret, limit=trustline_limit)
        return await self.inspect_account(keypair.public_key)

    async def create_trustline(self, secret: str, *, limit: str = DEFAULT_TRUSTLINE_LIMIT) -> TransactionResult:
        """Submit a change-trust operation for OVRL with the specified limit.
        
        :param secret: Secret key that will sign the transaction.
        :param limit: Maximum OVRL balance allowed on the trustline.
        :returns: TransactionResult describing the submitted envelope.
        """

        keypair = Keypair.from_secret(secret)
        account = await self.load_account(keypair.public_key)
        builder = self._builder(account)
        builder.append_change_trust_op(asset=OVRL_ASSET, limit=limit)
        envelope = builder.set_timeout(300).build()
        envelope.sign(keypair)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def create_account(
        self,
        *,
        funding_secret: str,
        destination: str,
        starting_balance: str = "2",
    ) -> TransactionResult:
        """Create and fund a new Stellar account via a direct create-account op.
        
        :param funding_secret: Secret key that pays for the new account.
        :param destination: Public key to create.
        :param starting_balance: Lumens to send in the create-account op.
        :returns: TransactionResult describing the submitted envelope.
        """

        sponsor = Keypair.from_secret(funding_secret)
        account = await self.load_account(sponsor.public_key)
        builder = self._builder(account)
        builder.append_create_account_op(destination=destination, starting_balance=starting_balance)
        envelope = builder.set_timeout(300).build()
        envelope.sign(sponsor)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def ensure_account(
        self,
        account_id: str,
        *,
        funding_secret: Optional[str] = None,
        starting_balance: str = "2",
    ) -> bool:
        """Guarantee that an on-ledger account exists via Friendbot or a funding key.
        
        :param account_id: Public key that must exist.
        :param funding_secret: Optional sponsor secret when Friendbot is unavailable.
        :param starting_balance: Lumens used if a create-account operation is required.
        :returns: True when a new account was created, False if it already existed.
        """

        try:
            await self.load_account(account_id)
            return False
        except OVRLError:
            pass

        if self.network.friendbot_url and funding_secret is None:
            await self.ensure_friendbot(account_id)
            return True

        if not funding_secret:
            raise OVRLError("Account is missing. Provide funding_secret or use a network with Friendbot enabled.")

        await self.create_account(
            funding_secret=funding_secret,
            destination=account_id,
            starting_balance=starting_balance,
        )
        return True

    async def pay(
        self,
        *,
        source_secret: str,
        destination: str,
        amount: str,
        memo: Optional[str] = None,
    ) -> TransactionResult:
        """Send a simple OVRL payment with an optional memo.
        
        :param source_secret: Secret key that signs and pays for the transfer.
        :param destination: Recipient account ID.
        :param amount: Amount of OVRL to send (string amount for Stellar SDK).
        :param memo: Optional text memo.
        :returns: TransactionResult for the submitted payment transaction.
        """

        keypair = Keypair.from_secret(source_secret)
        account = await self.load_account(keypair.public_key)
        builder = self._builder(account)
        memo_obj = TextMemo(memo) if memo else None
        if memo_obj:
            builder.add_memo(memo_obj)
        builder.append_payment_op(destination=destination, amount=amount, asset=OVRL_ASSET)
        envelope = builder.set_timeout(300).build()
        envelope.sign(keypair)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def send_path_payment(
        self,
        *,
        source_secret: str,
        destination: str,
        send_max: str,
        dest_amount: str,
        path: Optional[Iterable[Asset]] = None,
    ) -> TransactionResult:
        """Send OVRL through a strict-receive path payment.
        
        :param source_secret: Secret key that signs the transaction.
        :param destination: Recipient account ID.
        :param send_max: Maximum OVRL you are willing to spend.
        :param dest_amount: Destination amount that must be received.
        :param path: Optional iterable of intermediary :class:`Asset` hops.
        :returns: TransactionResult for the submitted swap transaction.
        """

        keypair = Keypair.from_secret(source_secret)
        account = await self.load_account(keypair.public_key)
        builder = self._builder(account)
        builder.append_path_payment_strict_receive_op(
            send_asset=OVRL_ASSET,
            send_max=send_max,
            destination=destination,
            dest_asset=OVRL_ASSET,
            dest_amount=dest_amount,
            path=list(path or []),
        )
        envelope = builder.set_timeout(300).build()
        envelope.sign(keypair)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def batch_pay(
        self,
        *,
        source_secret: str,
        payouts: Sequence[Union[PaymentIntent, dict]],
        memo: Optional[str] = None,
        chunk_size: int = MAX_OPERATIONS_PER_TX,
    ) -> List[TransactionResult]:
        """Chunk and submit multiple payment operations in batches.
        
        :param source_secret: Secret key funding the batched operations.
        :param payouts: Sequence of dicts or :class:`PaymentIntent` objects.
        :param memo: Optional memo applied to each batch transaction.
        :param chunk_size: Maximum payment operations per transaction (<=100).
        :returns: List of TransactionResult objects, one per submitted transaction.
        """

        if not payouts:
            raise OVRLError("Provide at least one payment intent.")
        if chunk_size <= 0 or chunk_size > MAX_OPERATIONS_PER_TX:
            raise OVRLError("chunk_size must be between 1 and 100 operations")

        keypair = Keypair.from_secret(source_secret)
        intents = [self._normalize_intent(intent, default_source=keypair.public_key) for intent in payouts]
        builder_memo = memo or next((intent.memo for intent in intents if intent.memo), None)

        results: List[TransactionResult] = []
        for chunk in _chunked(intents, chunk_size):
            account = await self.load_account(keypair.public_key)
            builder = self._builder(account)
            if builder_memo:
                builder.add_memo(TextMemo(builder_memo))

            for intent in chunk:
                builder.append_payment_op(
                    destination=intent.destination,
                    amount=_string_amount(intent.amount),
                    asset=OVRL_ASSET,
                    source=intent.source,
                )

            envelope = builder.set_timeout(600).build()
            envelope.sign(keypair)
            response = await self.server.submit_transaction(envelope)
            results.append(
                TransactionResult(
                    hash=response["hash"],
                    envelope_xdr=response.get("envelope_xdr"),
                    result_xdr=response.get("result_xdr"),
                )
            )

        return results

    async def list_payments_page(
        self,
        account_id: str,
        *,
        limit: int = 10,
        only_ovrl: bool = True,
        order: str = "desc",
        cursor: Optional[str] = None,
        payment_types: Optional[Sequence[str]] = None,
    ) -> PaymentPage:
        """Return a single page of payments for the account with cursor metadata.
        
        :param account_id: Account whose payment history should be fetched.
        :param limit: Number of records per page (max 200 per Horizon).
        :param only_ovrl: Filter to OVRL payments only when True.
        :param order: "asc" or "desc" order for paging.
        :param cursor: Optional paging token to resume from.
        :param payment_types: Optional Horizon type filters.
        :returns: PaymentPage containing typed records and the next cursor.
        """

        normalized_order = order.lower()
        if normalized_order not in {"asc", "desc"}:
            raise OVRLError("order must be 'asc' or 'desc'")
        is_desc = normalized_order == "desc"
        builder = self.server.payments().for_account(account_id).limit(limit).order(is_desc)
        if cursor:
            builder = builder.cursor(cursor)
        response = await builder.call()
        raw_records = self._embedded_records(response)
        next_cursor = raw_records[-1].get("paging_token") if raw_records else cursor
        allowed_types: Tuple[str, ...] = tuple(payment_types) if payment_types else ("payment",)
        payments: List[PaymentRecord] = []
        total_amount = Decimal("0")
        for record in raw_records:
            if record.get("type") not in allowed_types:
                continue
            asset_code = record.get("asset_code") or ("XLM" if record.get("asset_type") == "native" else None)
            asset_issuer = record.get("asset_issuer")
            if only_ovrl and not (
                asset_code == OVRL_CODE and asset_issuer == OVRL_ISSUER
            ):
                continue
            amount = Decimal(record.get("amount", "0"))
            payments.append(
                PaymentRecord(
                    id=record.get("id", ""),
                    source=record.get("from") or record.get("source_account", ""),
                    destination=record.get("to") or record.get("account"),
                    amount=amount,
                    asset_code=asset_code or OVRL_CODE,
                    asset_issuer=asset_issuer,
                    created_at=record.get("created_at", ""),
                    memo=record.get("memo"),
                    paging_token=record.get("paging_token"),
                )
            )
            total_amount += amount
        return PaymentPage(
            records=payments,
            next_cursor=next_cursor,
            record_count=len(payments),
            total_amount=total_amount,
        )

    async def list_payments(
        self,
        account_id: str,
        *,
        limit: int = 10,
        only_ovrl: bool = True,
        order: str = "desc",
        cursor: Optional[str] = None,
        payment_types: Optional[Sequence[str]] = None,
    ) -> List[PaymentRecord]:
        """Return payment records without pagination metadata.
        
        :param account_id: Account whose payment history will be read.
        :param limit: Maximum records per fetch (<=200 per Horizon).
        :param only_ovrl: When True, filter records to OVRL payments.
        :param order: "asc" or "desc" ordering.
        :param cursor: Optional paging token to resume from.
        :param payment_types: Optional Horizon payment type filters.
        :returns: List of :class:`PaymentRecord` objects.
        """

        page = await self.list_payments_page(
            account_id,
            limit=limit,
            only_ovrl=only_ovrl,
            order=order,
            cursor=cursor,
            payment_types=payment_types,
        )
        return page.records

    async def summarize_payments(
        self,
        account_id: str,
        *,
        limit: int = 100,
        only_ovrl: bool = True,
        payment_types: Optional[Sequence[str]] = None,
        max_pages: int = 10,
        cursor: Optional[str] = None,
    ) -> PaymentSummary:
        """Summarize total count/amount across multiple payment pages.
        
        :param account_id: Public key whose history should be summarized.
        :param limit: Page size forwarded to Horizon.
        :param only_ovrl: Restrict to OVRL-denominated payments.
        :param payment_types: Optional Horizon payment type filters.
        :param max_pages: Maximum number of pages to fetch.
        :param cursor: Optional paging token to resume from.
        :returns: Aggregated :class:`PaymentSummary` value.
        """

        total_amount = Decimal("0")
        total_records = 0
        current_cursor = cursor
        pages = 0
        while pages < max_pages:
            page = await self.list_payments_page(
                account_id,
                limit=limit,
                only_ovrl=only_ovrl,
                order="asc",
                cursor=current_cursor,
                payment_types=payment_types,
            )
            total_records += page.record_count
            total_amount += page.total_amount
            pages += 1
            if not page.next_cursor or page.record_count == 0:
                current_cursor = page.next_cursor
                break
            current_cursor = page.next_cursor
        return PaymentSummary(record_count=total_records, total_amount=total_amount, last_cursor=current_cursor)

    async def list_top_holders(self, *, limit: int = 10) -> List[BalanceSnapshot]:
        """Return the richest OVRL accounts along with their balances.
        
        :param limit: Maximum number of holders to return.
        :returns: Sorted list of :class:`BalanceSnapshot` objects.
        """

        builder = self.server.accounts().for_asset(OVRL_ASSET).limit(limit)
        response = await builder.call()
        records = self._embedded_records(response)
        holders: List[BalanceSnapshot] = []
        for record in records:
            account_id = record.get("account_id", "")
            for balance in record.get("balances", []):
                if balance.get("asset_code") == OVRL_CODE and balance.get("asset_issuer") == OVRL_ISSUER:
                    holders.append(
                        BalanceSnapshot(
                            account_id=account_id,
                            asset_code=OVRL_CODE,
                            asset_issuer=OVRL_ISSUER,
                            balance=Decimal(balance.get("balance", "0")),
                            limit=Decimal(balance.get("limit")) if balance.get("limit") else None,
                            buying_liabilities=Decimal(balance.get("buying_liabilities", "0")),
                            selling_liabilities=Decimal(balance.get("selling_liabilities", "0")),
                        )
                    )
                    break
        holders.sort(key=lambda snapshot: snapshot.balance, reverse=True)
        return holders

    async def payment_watcher(
        self,
        account_id: str,
        *,
        only_ovrl: bool = True,
        poll_interval: float = 5.0,
        limit: int = 10,
        max_rounds: Optional[int] = None,
        start_cursor: Optional[str] = None,
        replay_most_recent: bool = True,
        payment_types: Optional[Sequence[str]] = None,
    ) -> AsyncIterator[PaymentRecord]:
        """Poll for new payments, yielding records incrementally.
        
        :param account_id: Account to watch.
        :param only_ovrl: When True, skip non-OVRL payments.
        :param poll_interval: Seconds to sleep between Horizon polls.
        :param limit: Page size per poll.
        :param max_rounds: Optional number of polls before stopping.
        :param start_cursor: Optional cursor to resume from.
        :param replay_most_recent: Whether to emit the latest page before polling forward.
        :param payment_types: Optional Horizon payment type filters.
        :yields: PaymentRecord objects as new payments appear.
        """

        cursor = start_cursor
        rounds = 0
        warmup_done = start_cursor is not None or not replay_most_recent
        while True:
            if not warmup_done:
                page = await self.list_payments_page(
                    account_id,
                    limit=limit,
                    only_ovrl=only_ovrl,
                    order="desc",
                    payment_types=payment_types,
                )
                records = list(reversed(page.records))
                if not replay_most_recent and start_cursor is None:
                    records = []
                if page.next_cursor:
                    cursor = page.next_cursor
                warmup_done = True
            else:
                page = await self.list_payments_page(
                    account_id,
                    limit=limit,
                    only_ovrl=only_ovrl,
                    order="asc",
                    cursor=cursor,
                    payment_types=payment_types,
                )
                records = page.records
                if page.next_cursor:
                    cursor = page.next_cursor

            for record in records:
                cursor = record.paging_token or cursor
                yield record

            rounds += 1
            if max_rounds is not None and rounds >= max_rounds:
                break
            await asyncio.sleep(poll_interval)

    async def get_account_overview(self, account_id: str) -> AccountOverview:
        """Fetch raw account JSON from Horizon and normalize into :class:`AccountOverview`.
        
        :param account_id: Public key to load via Horizon.
        :returns: AccountOverview representing the latest Horizon payload.
        """

        response = await self.server.accounts().account_id(account_id).call()
        last_modified = response.get("last_modified_ledger")
        return AccountOverview(
            account_id=response.get("account_id", account_id),
            sequence=response.get("sequence", "0"),
            subentry_count=int(response.get("subentry_count", 0)),
            last_modified_ledger=int(last_modified) if last_modified is not None else None,
            balances=response.get("balances", []),
            signers=response.get("signers", []),
        )

    async def quote_paths_to_ovrl(
        self,
        destination_amount: str,
        *,
        source_assets: Optional[Sequence[Asset]] = None,
    ) -> List[PathQuote]:
        """Enumerate strict-receive paths that deliver the requested OVRL amount.
        
        :param destination_amount: Desired amount of OVRL (string amount accepted by Horizon).
        :param source_assets: Optional list of assets to use when sourcing the payment.
        :returns: List of PathQuote objects ordered by efficiency.
        """

        assets_param: Union[str, List[Asset]] = list(source_assets) if source_assets else "native"
        builder = self.server.strict_receive_paths(assets_param, OVRL_ASSET, destination_amount)
        response = await builder.call()
        records = self._embedded_records(response)
        quotes: List[PathQuote] = []
        for record in records:
            path_assets = [
                _describe_asset(asset)
                for asset in record.get("path", [])
            ]
            quotes.append(
                PathQuote(
                    destination_amount=Decimal(record.get("destination_amount", "0")),
                    source_amount=Decimal(record.get("source_amount", "0")),
                    path_assets=path_assets,
                    source_asset_code=record.get("source_asset_code"),
                    source_asset_issuer=record.get("source_asset_issuer"),
                    destination_asset_code=record.get("destination_asset_code") or OVRL_CODE,
                    destination_asset_issuer=record.get("destination_asset_issuer") or OVRL_ISSUER,
                )
            )
        return quotes

    async def quote_paths_from_ovrl(
        self,
        send_amount: str,
        *,
        destination_assets: Optional[Sequence[Asset]] = None,
    ) -> List[PathQuote]:
        """Enumerate strict-send paths that spend OVRL into target assets.
        
        :param send_amount: Amount of OVRL to spend.
        :param destination_assets: Optional asset whitelist for the destination.
        :returns: List of PathQuote objects ordered by destination amount.
        """

        assets_param: Union[str, List[Asset]] = list(destination_assets) if destination_assets else "native"
        builder = self.server.strict_send_paths(OVRL_ASSET, send_amount, assets_param)
        response = await builder.call()
        records = self._embedded_records(response)
        quotes: List[PathQuote] = []
        for record in records:
            path_assets = [_describe_asset(asset) for asset in record.get("path", [])]
            quotes.append(
                PathQuote(
                    destination_amount=Decimal(record.get("destination_amount", "0")),
                    source_amount=Decimal(record.get("source_amount", "0")),
                    path_assets=path_assets,
                    source_asset_code=record.get("source_asset_code"),
                    source_asset_issuer=record.get("source_asset_issuer"),
                    destination_asset_code=record.get("destination_asset_code"),
                    destination_asset_issuer=record.get("destination_asset_issuer"),
                )
            )
        return quotes

    async def get_transaction(self, tx_hash: str) -> dict[str, Any]:
        """Fetch a transaction via Horizon or raise if not found.
        
        :param tx_hash: Transaction hash to retrieve.
        :returns: Parsed Horizon transaction JSON payload.
        :raises OVRLError: If the transaction cannot be found.
        """
        try:
            return await self.server.transactions().transaction(tx_hash).call()
        except NotFoundError as exc:  # pragma: no cover - passthrough
            raise OVRLError(f"Transaction {tx_hash} was not found") from exc

    async def wait_for_transaction(
        self,
        tx_hash: str,
        *,
        timeout: float = 30,
        poll_interval: float = 2,
    ) -> dict[str, Any]:
        """Poll Horizon until the transaction appears or timeout occurs.
        
        :param tx_hash: Transaction hash to wait for.
        :param timeout: Maximum seconds to wait.
        :param poll_interval: Delay between consecutive polls.
        :returns: Horizon transaction JSON once the record is available.
        :raises OVRLError: If the timeout elapses before the transaction is found.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                return await self.get_transaction(tx_hash)
            except OVRLError:
                await asyncio.sleep(poll_interval)
        raise OVRLError(f"Timed out waiting for transaction {tx_hash}")

    async def submit_envelope_xdr(self, envelope_xdr: str) -> TransactionResult:
        """Submit a base64-encoded envelope XDR using Horizon.
        
        :param envelope_xdr: Base64-encoded transaction envelope.
        :returns: :class:`TransactionResult` describing Horizon's response.
        """
        envelope = TransactionEnvelope.from_xdr(envelope_xdr, self.network.passphrase)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def submit_with_retry(
        self,
        envelope: TransactionEnvelope,
        *,
        attempts: int = 3,
        backoff_seconds: float = 2.0,
    ) -> TransactionResult:
        """Submit a built envelope with retry/backoff semantics.
        
        :param envelope: Prepared envelope to submit.
        :param attempts: Number of submission attempts before failing.
        :param backoff_seconds: Base backoff used between retries.
        :returns: :class:`TransactionResult` on success.
        :raises OVRLError: If attempts is invalid or submission ultimately fails.
        """
        if attempts <= 0:
            raise OVRLError("attempts must be >= 1")
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                response = await self.server.submit_transaction(envelope)
                return TransactionResult(
                    hash=response["hash"],
                    envelope_xdr=response.get("envelope_xdr"),
                    result_xdr=response.get("result_xdr"),
                )
            except (BadResponseError, OVRLError) as exc:
                last_error = exc
                if attempt < attempts:
                    await asyncio.sleep(backoff_seconds * attempt)
        if last_error:
            raise last_error
        raise OVRLError("Failed to submit transaction after retries")

    async def fetch_home_domain_toml(self) -> dict[str, Any]:
        """Download and parse the asset home-domain stellar.toml.
        
        :returns: Parsed TOML dictionary.
        :raises OVRLError: When the file cannot be fetched or parsed.
        """
        url = f"https://{OVRL_HOME_DOMAIN}/.well-known/stellar.toml"
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    body = await response.text()
                    raise OVRLError(f"Failed to fetch stellar.toml from {url}: {response.status} {body}")
                content = await response.read()
        try:
            return tomllib.loads(content.decode("utf-8"))
        except tomllib.TOMLDecodeError as exc:  # pragma: no cover - depends on remote file
            raise OVRLError("stellar.toml returned invalid TOML") from exc

    async def validate_home_domain(self) -> bool:
        """Ensure Horizon's recorded home domain matches the TOML contents.
        
        :returns: True when the home domain configuration is valid.
        :raises OVRLError: When Horizon or TOML data disagree.
        """
        stats = await self.get_asset_stats()
        recorded_home = (stats.home_domain or "").lower()
        if recorded_home and recorded_home != OVRL_HOME_DOMAIN:
            raise OVRLError(
                f"Home domain mismatch: Horizon reports {recorded_home}, expected {OVRL_HOME_DOMAIN}"
            )
        toml_data = await self.fetch_home_domain_toml()
        currencies = toml_data.get("CURRENCIES") or toml_data.get("currencies") or []
        for entry in currencies:
            code = str(entry.get("code", "")).upper()
            issuer = entry.get("issuer")
            if code == OVRL_CODE and issuer == OVRL_ISSUER:
                return True
        raise OVRLError("OVRL is missing from the home-domain stellar.toml")

    async def get_fee_stats(self) -> FeeStats:
        """Return the latest Horizon-reported fee statistics.
        
        :returns: :class:`FeeStats` parsed from Horizon.
        """
        response = await self.server.fee_stats().call()
        return FeeStats(
            last_ledger=int(response.get("last_ledger", 0)),
            last_ledger_base_fee=int(response.get("last_ledger_base_fee", 0)),
            ledger_capacity_usage=Decimal(response.get("ledger_capacity_usage", "0")),
            min_accepted_fee=int(response.get("min_accepted_fee", 0)),
            mode_accepted_fee=int(response.get("mode_accepted_fee", 0)),
            p10_accepted_fee=int(response.get("p10_accepted_fee", 0)),
            p50_accepted_fee=int(response.get("p50_accepted_fee", 0)),
            p95_accepted_fee=int(response.get("p95_accepted_fee", 0)),
            p99_accepted_fee=int(response.get("p99_accepted_fee", 0)),
        )

    async def quote_ovrl_price(
        self,
        *,
        counter_asset: Asset = DEFAULT_USD_ASSET,
        amount: Union[str, Decimal] = "1",
    ) -> Decimal:
        """Return the per-unit counter-asset value for OVRL.
        
        :param counter_asset: Asset used to price OVRL (defaults to USD).
        :param amount: Amount of OVRL used to compute the quote.
        :returns: Decimal price per OVRL (counter_asset / OVRL).
        """

        amount_str = _string_amount(amount)
        value = await self.quote_ovrl_to_asset(amount_str, counter_asset=counter_asset)
        base_amount = Decimal(amount_str)
        if base_amount <= 0:
            raise OVRLError("amount must be greater than zero")
        return value / base_amount


    async def quote_ovrl_to_asset(
        self,
        amount: Union[str, Decimal],
        *,
        counter_asset: Asset = DEFAULT_USD_ASSET,
    ) -> Decimal:
        """Quote how much of the counter asset is received for the OVRL amount.
        
        :param amount: Amount of OVRL to convert.
        :param counter_asset: Asset that should be received.
        :returns: Decimal representing the destination amount.
        """

        amount_str = _string_amount(amount)
        quotes = await self.quote_paths_from_ovrl(amount_str, destination_assets=[counter_asset])
        if not quotes:
            raise OVRLError("No conversion path found for OVRL -> target asset")
        return quotes[0].destination_amount

    async def quote_asset_to_ovrl(
        self,
        amount: Union[str, Decimal],
        *,
        source_asset: Asset = DEFAULT_USD_ASSET,
    ) -> Decimal:
        """Quote how much OVRL can be received for a counter-asset amount.
        
        :param amount: Counter asset amount to spend.
        :param source_asset: Asset being sold.
        :returns: Decimal amount of OVRL that can be purchased.
        """

        quotes = await self.quote_paths_to_ovrl("1", source_assets=[source_asset])
        if not quotes:
            raise OVRLError("No conversion path found for asset -> OVRL")
        per_unit_source = quotes[0].source_amount
        if per_unit_source <= 0:
            raise OVRLError("Received an invalid quote for asset -> OVRL")
        return Decimal(_string_amount(amount)) / per_unit_source


    async def ovrl_to_usd(self, amount: Union[str, Decimal]) -> Decimal:
        """Convert an OVRL amount into the default USD asset.
        
        :param amount: OVRL amount to convert.
        :returns: Decimal amount of USD received.
        """
        return await self.quote_ovrl_to_asset(amount, counter_asset=DEFAULT_USD_ASSET)

    async def usd_to_ovrl(self, amount: Union[str, Decimal]) -> Decimal:
        """Convert the default USD asset amount into OVRL.
        
        :param amount: USD amount to convert.
        :returns: Decimal representing how much OVRL can be purchased.
        """
        return await self.quote_asset_to_ovrl(amount, source_asset=DEFAULT_USD_ASSET)

    async def swap_from_ovrl(
        self,
        *,
        source_secret: str,
        destination: str,
        amount: Union[str, Decimal],
        counter_asset: Asset = DEFAULT_USD_ASSET,
        memo: Optional[str] = None,
    ) -> TransactionResult:
        """Execute a strict-send swap spending OVRL into a counter asset.
        
        :param source_secret: Secret key authorizing the payment.
        :param destination: Recipient account for the destination asset.
        :param amount: Amount of OVRL to swap.
        :param counter_asset: Asset that should be received.
        :param memo: Optional memo text.
        :returns: :class:`TransactionResult` referencing the submitted transaction.
        """
        amount_str = _string_amount(amount)
        response = await self.server.strict_send_paths(OVRL_ASSET, amount_str, [counter_asset]).call()
        records = self._embedded_records(response)
        if not records:
            raise OVRLError("No swap path found for OVRL -> target asset")
        record = records[0]
        path_assets = self._path_assets_from_record(record.get("path", []))
        dest_min = _string_amount(record.get("destination_amount", "0"))

        keypair = Keypair.from_secret(source_secret)
        account = await self.load_account(keypair.public_key)
        builder = self._builder(account)
        if memo:
            builder.add_memo(TextMemo(memo))
        builder.append_path_payment_strict_send_op(
            send_asset=OVRL_ASSET,
            send_amount=amount_str,
            destination=destination,
            dest_asset=counter_asset,
            dest_min=dest_min,
            path=path_assets,
        )
        envelope = builder.set_timeout(300).build()
        envelope.sign(keypair)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    async def swap_to_ovrl(
        self,
        *,
        source_secret: str,
        destination: str,
        ovrl_amount: Union[str, Decimal],
        source_asset: Asset = DEFAULT_USD_ASSET,
        memo: Optional[str] = None,
    ) -> TransactionResult:
        """Execute a strict-receive swap delivering OVRL.
        
        :param source_secret: Secret key authorizing the payment.
        :param destination: Recipient account for the OVRL.
        :param ovrl_amount: Amount of OVRL required at destination.
        :param source_asset: Asset to spend.
        :param memo: Optional memo text.
        :returns: :class:`TransactionResult` referencing the submitted transaction.
        """
        amount_str = _string_amount(ovrl_amount)
        response = await self.server.strict_receive_paths([source_asset], OVRL_ASSET, amount_str).call()
        records = self._embedded_records(response)
        if not records:
            raise OVRLError("No swap path found for asset -> OVRL")
        record = records[0]
        path_assets = self._path_assets_from_record(record.get("path", []))
        send_max = _string_amount(record.get("source_amount", "0"))

        keypair = Keypair.from_secret(source_secret)
        account = await self.load_account(keypair.public_key)
        builder = self._builder(account)
        if memo:
            builder.add_memo(TextMemo(memo))
        builder.append_path_payment_strict_receive_op(
            send_asset=source_asset,
            send_max=send_max,
            destination=destination,
            dest_asset=OVRL_ASSET,
            dest_amount=amount_str,
            path=path_assets,
        )
        envelope = builder.set_timeout(300).build()
        envelope.sign(keypair)
        response = await self.server.submit_transaction(envelope)
        return TransactionResult(
            hash=response["hash"],
            envelope_xdr=response.get("envelope_xdr"),
            result_xdr=response.get("result_xdr"),
        )

    @staticmethod
    def format_price(
        amount: Union[str, Decimal],
        *,
        currency: str = "USD",
        style: str = "symbol",
        precision: int = 2,
        notation: str = "standard",
        trim_trailing: bool = True,
    ) -> str:
        """Format a numeric value with currency styling and optional grouped/compact notation.
        
        :param amount: Numeric amount (string or Decimal) to format.
        :param currency: ISO currency code used for symbol/code output.
        :param style: ``symbol`` (default), ``code``, or ``plain`` text rendering.
        :param precision: Decimal places to display (>=0).
        :param notation: ``standard``, ``grouped``, or ``compact`` for thousands abbreviations.
        :param trim_trailing: When True, drop redundant trailing zeros.
        :returns: Formatted currency string.
        :raises OVRLError: If unsupported precision/style/notation values are provided.
        """

        value = Decimal(_string_amount(amount))
        if precision < 0:
            raise OVRLError("precision must be >= 0")

        currency_code = currency.upper()
        notation_key = notation.lower()
        style_key = style.lower()

        def _trim(number_str: str) -> str:
            if "." not in number_str:
                return number_str
            head, tail = number_str.split(".", 1)
            tail = tail.rstrip("0")
            if not tail:
                return head
            return f"{head}.{tail}"

        quant = Decimal(1).scaleb(-precision) if precision else Decimal(1)

        def _format_decimal(value: Decimal, *, grouped: bool = False) -> str:
            quantized = value.quantize(quant, rounding=ROUND_HALF_UP)
            fmt = f",.{precision}f" if grouped else f".{precision}f"
            return format(quantized, fmt)

        formatted: str
        if notation_key == "compact":
            thresholds = (
                (Decimal("1e12"), "T"),
                (Decimal("1e9"), "B"),
                (Decimal("1e6"), "M"),
                (Decimal("1e3"), "K"),
            )
            abs_value = abs(value)
            for threshold, suffix in thresholds:
                if abs_value >= threshold:
                    scaled = value / threshold
                    formatted = _format_decimal(scaled)
                    if trim_trailing:
                        formatted = _trim(formatted)
                    formatted = f"{formatted}{suffix}"
                    break
            else:
                formatted = _format_decimal(value)
                if trim_trailing:
                    formatted = _trim(formatted)
        elif notation_key == "grouped":
            formatted = _format_decimal(value, grouped=True)
            if trim_trailing:
                formatted = _trim(formatted)
        elif notation_key == "standard":
            formatted = _format_decimal(value)
            if trim_trailing:
                formatted = _trim(formatted)
        else:
            raise OVRLError("notation must be 'standard', 'grouped', or 'compact'")

        if style_key == "plain":
            return formatted
        if style_key == "code":
            return f"{formatted} {currency_code}"
        if style_key == "symbol":
            symbol = "$" if currency_code in {"USD", "USDC"} else ""
            if not symbol:
                return formatted
            if formatted.startswith("-"):
                return f"-{symbol}{formatted[1:]}"
            return f"{symbol}{formatted}"
        raise OVRLError("style must be 'symbol', 'code', or 'plain'")

    def soroban(self):
        """Return a lazy-initialized Soroban toolkit tied to this client.
        
        :returns: SorobanToolkit wired to the client's network configuration.
        :raises SorobanUnavailableError: If the current network lacks a Soroban RPC endpoint.
        """
        if self.soroban_server is None:
            raise SorobanUnavailableError("This network does not have a Soroban RPC endpoint configured")
        if self._soroban_toolkit is None:
            from .soroban import SorobanToolkit

            self._soroban_toolkit = SorobanToolkit(self)
        return self._soroban_toolkit

    def _builder(self, account: Any) -> TransactionBuilder:
        """Create a transaction builder configured with the client's base fee and passphrase.
        
        :param account: Loaded account returned by Horizon used as the transaction source.
        :returns: Configured :class:`TransactionBuilder` ready for operations.
        """
        return TransactionBuilder(
            source_account=account,
            network_passphrase=self.network.passphrase,
            base_fee=self.base_fee,
        )

    @staticmethod
    def _path_assets_from_record(path_entries: Sequence[dict]) -> List[Asset]:
        """Convert Horizon path entries into :class:`Asset` objects.
        
        :param path_entries: Sequence of Horizon path step dictionaries.
        :returns: List of instantiated :class:`Asset` objects representing the path.
        """
        assets: List[Asset] = []
        for entry in path_entries:
            asset_type = entry.get("asset_type")
            if asset_type == "native":
                assets.append(Asset.native())
            else:
                code = entry.get("asset_code")
                issuer = entry.get("asset_issuer")
                if not code or not issuer:
                    continue
                assets.append(Asset(code, issuer))
        return assets

    @staticmethod
    def _normalize_intent(intent: Union[PaymentIntent, dict], *, default_source: str) -> PaymentIntent:
        """Normalize dict-based payouts into :class:`PaymentIntent` instances.
        
        :param intent: Either a :class:`PaymentIntent` or bare dict describing a payout.
        :param default_source: Source account to fall back to when one is not provided.
        :returns: Normalized :class:`PaymentIntent` for downstream payment batching.
        :raises OVRLError: If required keys are missing in the dict payload.
        """
        if isinstance(intent, PaymentIntent):
            return PaymentIntent(
                destination=intent.destination,
                amount=intent.amount,
                source=intent.source or default_source,
                memo=intent.memo,
            )
        payload = {**intent}
        destination = payload.get("destination")
        amount = payload.get("amount")
        if destination is None or amount is None:
            raise OVRLError("Each payment intent must include destination and amount")
        return PaymentIntent(
            destination=destination,
            amount=amount,
            source=payload.get("source") or default_source,
            memo=payload.get("memo"),
        )

    @staticmethod
    def _embedded_records(payload: dict[str, Any]) -> List[dict]:
        """Return `_embedded.records` from a Horizon response.
        
        :param payload: Horizon response JSON.
        :returns: List of embedded record dictionaries (possibly empty).
        """
        return payload.get("_embedded", {}).get("records", [])

    @staticmethod
    def _token_owned_accounts(toml_data: dict[str, Any]) -> List[str]:
        """Extract issuer-controlled accounts from the TOML payload.
        
        :param toml_data: Parsed stellar.toml dictionary.
        :returns: List of uppercase account IDs controlled by the issuer.
        """
        accounts = {str(item).strip().upper() for item in toml_data.get("ACCOUNTS", []) if item}
        currencies = toml_data.get("CURRENCIES") or toml_data.get("currencies") or []
        for entry in currencies:
            if str(entry.get("code", "")).upper() != OVRL_CODE:
                continue
            for key in (
                "issuer",
                "distribution_account",
                "distribution_accounts",
                "org_wallet",
                "org_wallets",
            ):
                value = entry.get(key)
                if isinstance(value, str):
                    accounts.add(value.strip().upper())
                elif isinstance(value, list):
                    accounts.update(str(item).strip().upper() for item in value if item)
        accounts.add(OVRL_ISSUER.upper())
        return [account for account in accounts if account]

    async def _sum_internal_holdings(self, account_ids: Sequence[str]) -> Decimal:
        """Aggregate OVRL balances for issuer-controlled accounts.
        
        :param account_ids: Sequence of account IDs to inspect.
        :returns: Decimal sum of balances across the provided accounts.
        """
        if not account_ids:
            return Decimal("0")
        coroutines = [self.get_ovrl_balance(account_id) for account_id in account_ids]
        snapshots = await asyncio.gather(*coroutines, return_exceptions=True)
        total = Decimal("0")
        for snapshot in snapshots:
            if not isinstance(snapshot, BalanceSnapshot):
                continue
            total += snapshot.balance
        return total


def _string_amount(value: Union[str, Decimal]) -> str:
    """Return a plain string representation for Horizon-bound amount fields.
    
    :param value: Decimal or string amount provided by the caller.
    :returns: String form suitable for the Stellar SDK.
    """
    return format(value, "f") if isinstance(value, Decimal) else str(value)


def _describe_asset(asset: dict) -> str:
    """Summarize a Horizon asset dict into a human-readable code/issuer string.
    
    :param asset: Horizon asset representation.
    :returns: Asset string such as ``XLM`` or ``CODE:ISSUER``.
    """
    if asset.get("asset_type") == "native":
        return "XLM"
    code = asset.get("asset_code") or ""
    issuer = asset.get("asset_issuer")
    return f"{code}:{issuer}" if issuer else code


def _chunked(items: Sequence[PaymentIntent], size: int) -> Iterable[Sequence[PaymentIntent]]:
    """Yield successive slices of ``items`` with the requested chunk size.
    
    :param items: Sequence to iterate over.
    :param size: Max number of entries per chunk.
    :yields: Subsequences preserving order.
    """
    for index in range(0, len(items), size):
        yield items[index:index + size]


__all__ = ["OVRLClient"]
