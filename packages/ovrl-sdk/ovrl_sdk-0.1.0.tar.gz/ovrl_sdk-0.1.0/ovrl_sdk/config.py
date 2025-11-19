"""Network presets and configuration objects for the OVRL SDK.

Provides immutable structures describing Horizon/Soroban endpoints for public,
testnet, Futurenet, or custom deployments. License: Apache-2.0. Authors:
Overlumens (github.com/overlumens) and Md Mahedi Zaman Zaber
(github.com/zaber-dev).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from stellar_sdk import Network


@dataclass(frozen=True)
class NetworkConfig:
    """Connection bundle describing Horizon/Soroban endpoints for a network.

    Instantiate this directly when you need to point the SDK at a custom Horizon or
    Soroban RPC URL; otherwise prefer the presets below.
    """

    name: str
    horizon_url: str
    passphrase: str
    soroban_rpc_url: Optional[str] = None
    friendbot_url: Optional[str] = None


class NetworkPresets:
    """Ready-to-use `NetworkConfig` values for public, testnet, and Futurenet."""

    PUBLIC = NetworkConfig(
        name="public",
        horizon_url="https://horizon.stellar.org",
        passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
        soroban_rpc_url="https://rpc-mainnet.stellar.org",
    )

    TESTNET = NetworkConfig(
        name="testnet",
        horizon_url="https://horizon-testnet.stellar.org",
        passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        soroban_rpc_url="https://rpc-testnet.stellar.org",
        friendbot_url="https://friendbot.stellar.org",
    )

    FUTURENET = NetworkConfig(
        name="futurenet",
        horizon_url="https://horizon-futurenet.stellar.org",
        passphrase=Network.FUTURENET_NETWORK_PASSPHRASE,
        soroban_rpc_url="https://rpc-futurenet.stellar.org",
        friendbot_url="https://friendbot-futurenet.stellar.org",
    )

    @staticmethod
    def custom(
        *,
        name: str,
        horizon_url: str,
        passphrase: str,
        soroban_rpc_url: Optional[str] = None,
        friendbot_url: Optional[str] = None,
    ) -> NetworkConfig:
        """Build a :class:`NetworkConfig` from manually supplied endpoints.
        
        :param name: Human-readable identifier for the network (used in logs).
        :param horizon_url: Horizon base URL.
        :param passphrase: Network passphrase (PUBLIC, TESTNET, etc.).
        :param soroban_rpc_url: Optional Soroban RPC endpoint.
        :param friendbot_url: Optional Friendbot endpoint when available.
        :returns: Fully populated :class:`NetworkConfig` instance.
        """
        return NetworkConfig(
            name=name,
            horizon_url=horizon_url,
            passphrase=passphrase,
            soroban_rpc_url=soroban_rpc_url,
            friendbot_url=friendbot_url,
        )


__all__ = ["NetworkConfig", "NetworkPresets"]
