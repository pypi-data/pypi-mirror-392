"""Send individual and batched OVRL payments, then inspect payment history."""

from __future__ import annotations

import asyncio

from stellar_sdk import Keypair

from ovrl_sdk import PaymentIntent
from examples.shared import ovrl_client, require_env


async def main() -> None:
    """Execute a single payment, a chunked batch, and summarize history."""

    source_secret = require_env("OVRL_SECRET")
    destination = require_env("OVRL_DESTINATION")
    source_keypair = Keypair.from_secret(source_secret)

    async with ovrl_client() as client:
        print("Sending a single payment...")
        payment = await client.pay(
            source_secret=source_secret,
            destination=destination,
            amount="1",
            memo="Example transfer",
        )
        print("Payment hash:", payment.hash)

        print("\nSubmitting a batch payout...")
        payouts = [
            PaymentIntent(destination=destination, amount="0.50"),
            {"destination": destination, "amount": "0.25", "memo": "Bonus"},
        ]
        batch = await client.batch_pay(
            source_secret=source_secret,
            payouts=payouts,
            memo="Weekly rewards",
            chunk_size=1,
        )
        print("Batch hashes:", [result.hash for result in batch])

        print("\nInspecting recent payment history...")
        page = await client.list_payments_page(source_keypair.public_key, limit=5)
        for record in page.records:
            print(f"{record.id} -> {record.destination} amount={record.amount}")
        print("Next cursor:", page.next_cursor)

        summary = await client.summarize_payments(source_keypair.public_key, max_pages=2)
        print(
            f"Across {summary.record_count} records we observed {summary.total_amount} OVRL"
        )


if __name__ == "__main__":
    asyncio.run(main())
