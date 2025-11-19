# Examples

Each script in this directory demonstrates a focused workflow using the OVRL SDK. All
examples rely on the following environment variables:

| Variable | Purpose |
| --- | --- |
| `OVRL_SECRET` | Primary secret key used for signing transactions. |
| `OVRL_DESTINATION` | Destination account for payment-oriented scripts. |
| `OVRL_FUNDING_SECRET` | Optional sponsor secret when Friendbot is unavailable. |
| `OVRL_CONTRACT_ID` | Soroban contract ID for the token example. |
| `OVRL_SPENDER` | Optional spender account for allowances (defaults to destination). |
| `OVRL_WATCH_ACCOUNT` | Optional account ID to monitor payments (defaults to `OVRL_SECRET`). |
| `OVRL_NETWORK` | `PUBLIC`, `TESTNET`, or `FUTURENET` (defaults to `TESTNET`). |
| `OVRL_EXECUTE_SWAPS` | Set to `1` to actually submit swap transactions in the quotes example. |

Run an example with:

```powershell
$env:OVRL_SECRET="SC..."; $env:OVRL_DESTINATION="GD..."; python examples\payments_and_batches.py
```

Available scripts:

- `bootstrap_trustline.py` – ensure an account exists, is funded, and holds the OVRL trustline.
- `payments_and_batches.py` – send individual transfers, chunk batch payouts, and inspect history.
- `quotes_and_swaps.py` – fetch price quotes, conversions, and (optionally) submit swap transactions.
- `monitoring_and_reporting.py` – capture circulating supply, fee stats, and watch live payments.
- `soroban_token_flow.py` – exercise the Soroban token contract (balance, approvals, transfers).

All scripts automatically pick the correct network preset via `OVRL_NETWORK` and cleanly close
network connections when finished.
