"""Shared helpers for the example scripts.

Set the following environment variables before running an example:

* ``OVRL_SECRET`` – primary secret key used as the source account.
* ``OVRL_DESTINATION`` – optional destination account for payment examples.
* ``OVRL_FUNDING_SECRET`` – optional sponsor for bootstrap flows when Friendbot is unavailable.
* ``OVRL_NETWORK`` – one of ``PUBLIC``, ``TESTNET``, or ``FUTURENET`` (defaults to ``TESTNET``).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from ovrl_sdk import NetworkConfig, NetworkPresets, OVRLClient

_NETWORKS: Dict[str, NetworkConfig] = {
    "PUBLIC": NetworkPresets.PUBLIC,
    "TESTNET": NetworkPresets.TESTNET,
    "FUTURENET": NetworkPresets.FUTURENET,
}


def resolve_network() -> NetworkConfig:
    """Return the configured network preset based on ``OVRL_NETWORK``.

    :returns: Network configuration object used by the examples.
    """

    key = os.getenv("OVRL_NETWORK", "TESTNET").upper()
    return _NETWORKS.get(key, NetworkPresets.TESTNET)


def require_env(name: str) -> str:
    """Return a required environment variable or exit with instructions.

    :param name: Name of the variable to load.
    :returns: Resolved value.
    :raises SystemExit: If the variable is not provided.
    """

    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Set the {name} environment variable before running this example.")
    return value


def optional_env(name: str) -> str | None:
    """Return an optional environment variable when present.

    :param name: Name of the variable to read.
    :returns: Value or ``None`` when missing.
    """

    value = os.getenv(name)
    return value or None


@asynccontextmanager
async def ovrl_client() -> AsyncIterator[OVRLClient]:
    """Instantiate an :class:`OVRLClient` configured from the environment.

    :yields: A ready-to-use client that auto-closes when the context exits.
    """

    client = OVRLClient(network=resolve_network())
    try:
        yield client
    finally:
        await client.close()
