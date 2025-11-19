"""Bootstrap an OVRL account and trustline, then inspect the resulting status."""

from __future__ import annotations

import asyncio

from stellar_sdk import Keypair

from examples.shared import optional_env, ovrl_client, require_env


async def main() -> None:
    """Ensure the caller account exists, is funded, and holds the OVRL trustline."""

    secret = require_env("OVRL_SECRET")
    funding_secret = optional_env("OVRL_FUNDING_SECRET")
    keypair = Keypair.from_secret(secret)

    async with ovrl_client() as client:
        metadata = client.asset_metadata()
        print(f"OVRL issuer: {metadata.issuer} | max supply: {metadata.max_supply}")

        before = await client.inspect_account(keypair.public_key)
        print(
            "Before bootstrap -> exists=%s trustline=%s"
            % (before.exists, before.has_trustline)
        )

        status = await client.bootstrap_account(
            account_secret=secret,
            funding_secret=funding_secret,
        )
        print(
            "After bootstrap  -> exists=%s trustline=%s friendbot=%s"
            % (status.exists, status.has_trustline, status.needs_friendbot)
        )

        if status.balance:
            print(
                f"OVRL balance: {status.balance.balance} / limit {status.balance.limit or 'unbounded'}"
            )
        else:
            print("OVRL trustline created; balance 0.0")


if __name__ == "__main__":
    asyncio.run(main())
