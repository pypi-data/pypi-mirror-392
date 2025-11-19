"""Inspect circulating supply, fee stats, and watch payments for a target account."""

from __future__ import annotations

import asyncio

from stellar_sdk import Keypair

from examples.shared import optional_env, ovrl_client, require_env


async def main() -> None:
    """Pull asset intelligence and stream a page of payments."""

    watch_account = optional_env("OVRL_WATCH_ACCOUNT")
    fallback_secret = optional_env("OVRL_SECRET")
    if not watch_account:
        if not fallback_secret:
            raise SystemExit("Set OVRL_WATCH_ACCOUNT or OVRL_SECRET to determine which account to inspect.")
        watch_account = Keypair.from_secret(fallback_secret).public_key

    async with ovrl_client() as client:
        stats = await client.get_asset_stats()
        circulating = await client.get_circulating_supply()
        fee_stats = await client.get_fee_stats()
        holders = await client.list_top_holders(limit=5)

        print(f"Circulating supply (excl. treasury): {circulating}")
        print(
            f"On-ledger stats -> amount={stats.amount} holders={stats.num_accounts} last ledger={stats.last_modified_ledger}"
        )
        print(
            "Fee percentiles -> base=%s p50=%s p95=%s"
            % (fee_stats.min_accepted_fee, fee_stats.p50_accepted_fee, fee_stats.p95_accepted_fee)
        )
        print("Top holders:")
        for snapshot in holders:
            print(f" - {snapshot.account_id}: {snapshot.balance}")

        summary = await client.summarize_payments(watch_account, limit=20, max_pages=2)
        print(
            f"Recent payments for {watch_account}: count={summary.record_count} total={summary.total_amount}"
        )

        print("\nWatching for the next page of payments (single poll)...")
        async for record in client.payment_watcher(
            watch_account,
            max_rounds=1,
            limit=5,
            replay_most_recent=False,
        ):
            print(f"Observed payment {record.id} amount={record.amount} from {record.source}")
            break


if __name__ == "__main__":
    asyncio.run(main())
