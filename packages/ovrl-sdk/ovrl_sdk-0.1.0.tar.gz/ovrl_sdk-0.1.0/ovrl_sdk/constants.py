"""OVRL token metadata and shared constants for the SDK.

Defines canonical asset codes, issuers, limits, default fees, and decimal
precision helpers reused throughout the client. License: Apache-2.0. Authors:
Overlumens (github.com/overlumens) and Md Mahedi Zaman Zaber
(github.com/zaber-dev).
"""

from decimal import Decimal

from stellar_sdk import Asset

OVRL_CODE = "OVRL"
OVRL_ISSUER = "GBZH36ATUXJZKFRMQTAAW42MWNM34SOA4N6E7DQ62V3G5NVITC3QOVRL"
OVRL_HOME_DOMAIN = "overlumens.com"
OVRL_MAX_SUPPLY = Decimal("100000000000")
OVRL_ISSUER_LOCKED = True
OVRL_ASSET = Asset(OVRL_CODE, OVRL_ISSUER)

DEFAULT_USD_CODE = "USDC"
DEFAULT_USD_ISSUER = "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"
DEFAULT_USD_ASSET = Asset(DEFAULT_USD_CODE, DEFAULT_USD_ISSUER)

DEFAULT_TRUSTLINE_LIMIT = "100000000000"
DEFAULT_BASE_FEE = 200
DECIMAL_SCALE = 7

__all__ = [
    "DEFAULT_BASE_FEE",
    "DEFAULT_TRUSTLINE_LIMIT",
    "DEFAULT_USD_ASSET",
    "DEFAULT_USD_CODE",
    "DEFAULT_USD_ISSUER",
    "DECIMAL_SCALE",
    "OVRL_ASSET",
    "OVRL_CODE",
    "OVRL_HOME_DOMAIN",
    "OVRL_ISSUER",
    "OVRL_ISSUER_LOCKED",
    "OVRL_MAX_SUPPLY",
]
