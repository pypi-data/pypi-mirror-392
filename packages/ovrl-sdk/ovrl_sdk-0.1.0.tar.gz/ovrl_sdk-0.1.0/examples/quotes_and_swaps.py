"""Quote OVRL prices, convert balances, and optionally execute swap transactions."""

from __future__ import annotations

import asyncio
import os

from stellar_sdk import Keypair

from ovrl_sdk.constants import DEFAULT_USD_ASSET
from examples.shared import ovrl_client, require_env


async def main() -> None:
    """Show conversion helpers and optional swap execution."""

    secret = require_env("OVRL_SECRET")
    destination = require_env("OVRL_DESTINATION")
    should_swap = os.getenv("OVRL_EXECUTE_SWAPS", "0") == "1"
    keypair = Keypair.from_secret(secret)

    async with ovrl_client() as client:
        price = await client.quote_ovrl_price()
        usd_value = await client.ovrl_to_usd("10")
        inverse = await client.usd_to_ovrl("50")
        print(f"Spot price: {price} (counter asset {DEFAULT_USD_ASSET.code})")
        print("10 OVRL ≈", usd_value, DEFAULT_USD_ASSET.code)
        print("USD 50 buys", inverse, "OVRL")

        quotes = await client.quote_paths_from_ovrl("25")
        if quotes:
            print("\nBest strict-send path for 25 OVRL ->", quotes[0].destination_asset_code)
            print("Path assets:", " → ".join(quotes[0].path_assets) or "direct")
        else:
            print("\nNo swap path available right now")

        if should_swap:
            print("\nSubmitting swap transactions...")
            send_swap = await client.swap_from_ovrl(
                source_secret=secret,
                destination=destination,
                amount="5",
                counter_asset=DEFAULT_USD_ASSET,
            )
            print("swap_from_ovrl hash:", send_swap.hash)

            receive_swap = await client.swap_to_ovrl(
                source_secret=secret,
                destination=keypair.public_key,
                ovrl_amount="5",
                source_asset=DEFAULT_USD_ASSET,
            )
            print("swap_to_ovrl hash:", receive_swap.hash)
        else:
            print(
                "\nSet OVRL_EXECUTE_SWAPS=1 to submit swap transactions after verifying trustlines."
            )


if __name__ == "__main__":
    asyncio.run(main())
