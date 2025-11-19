"""Custom exception types for the OVRL SDK (Apache-2.0).

Defines a small hierarchy capturing Friendbot failures, Soroban availability
issues, and transaction rejections. Authors: Overlumens
(github.com/overlumens) and Md Mahedi Zaman Zaber (github.com/zaber-dev).
"""


class OVRLError(Exception):
    """Base exception for the package."""


class FriendbotError(OVRLError):
    """Raised when Friendbot funding fails or is unavailable."""


class SorobanUnavailableError(OVRLError):
    """Raised when Soroban helpers are used without a configured RPC endpoint."""


class SorobanTransactionRejected(OVRLError):
    """Raised when the Soroban RPC reports a terminal failure for a transaction."""


__all__ = [
    "FriendbotError",
    "OVRLError",
    "SorobanTransactionRejected",
    "SorobanUnavailableError",
]
