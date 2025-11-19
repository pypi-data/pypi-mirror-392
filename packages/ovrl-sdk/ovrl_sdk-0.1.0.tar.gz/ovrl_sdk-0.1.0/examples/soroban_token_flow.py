"""Interact with the OVRL Soroban token contract using :class:`SorobanTokenClient`."""

from __future__ import annotations

import asyncio

from stellar_sdk import Keypair

from examples.shared import optional_env, ovrl_client, require_env
from ovrl_sdk import SorobanTokenClient


async def main() -> None:
    """Read balances, approvals, and send transfers via Soroban."""

    secret = require_env("OVRL_SECRET")
    destination = require_env("OVRL_DESTINATION")
    contract_id = require_env("OVRL_CONTRACT_ID")
    spender = optional_env("OVRL_SPENDER") or destination
    keypair = Keypair.from_secret(secret)

    async with ovrl_client() as client:
        token = SorobanTokenClient(client, contract_id=contract_id)

        balance = await token.balance(secret=secret, account_id=keypair.public_key)
        print("Current contract balance:", balance)

        print("Approving spender for 10 tokens...")
        approval = await token.approve(
            secret=secret,
            spender=spender,
            amount="10",
        )
        print("Approval hash:", approval.transaction_hash)

        allowance = await token.allowance(secret=secret, owner=keypair.public_key, spender=spender)
        print(f"Allowance for {spender}: {allowance}")

        print("Transferring 1 token via Soroban...")
        transfer = await token.transfer(secret=secret, destination=destination, amount="1")
        print("Transfer hash:", transfer.transaction_hash)


if __name__ == "__main__":
    asyncio.run(main())
