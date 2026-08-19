# ICO 2017 Rescue Case: 55.6 ETH blocked in an unactivated refund phase

**Target contract:** `0x2387a684f010936ce7267b0110c980c867533ff6`
- Deployed 2017-10-31 13:52:40 UTC
- Balance: 55.65 ETH (~$105k)
- Unverified source; 25 selectors incl. `getRefund()` (0xb2d5ae44)

## What happened

Disassembly of `getRefund()` (helper at pc 2320):

```
2328 PUSH1 0 SLOAD      // storage[0]
2330 PUSH1 255 AND      // phase = storage[0] & 0xff
2334 PUSH1 3 DUP2 GT ISZERO  // enum bounds check (phase <= 3)
2345 EQ                 // require(phase == 3)
2349 JUMPI ... REVERT   // else revert
2355 CALLER ... SHA3 SLOAD  // balances[caller] check
```

The refund is gated on **phase 3** (refund phase). Current phase: **1**
(`storage[0] = 1`, verified on-chain). `getRefund()` reverts for every
investor until the owner switches the phase. The phase was never activated.

## Owner profile

- Owner/deployer: `0xF17dE20488FEC8100DD294b678c6579516B2232b`
- Last transaction: 2018-06-12 (sent 0.1754 ETH to 0xd5cec41e, calls to 0x611fd421)
- Silent for 8+ years. No ENS, no labels, no public mentions found.

## Evidence chain

| Date | Event |
| --- | --- |
| 2017-10-31 | contract deployed (ICO), ETH deposited by investors |
| 2018-06-12 | owner's last activity |
| 2026-08 | 55.65 ETH still held; storage[0] = 1 (phase 1, not 3); getRefund() blocked |

## Impact

- 55.65 ETH of investor contributions frozen because the refund phase
  was never activated and the owner stopped interacting.
- A single owner transaction (phase switch) would unlock refunds for
  every investor; each investor then calls `getRefund()` for their balance.

## If you are the owner / a contributor

- Owner: verify identity by signing a message with
  `0xF17dE20488FEC8100DD294b678c6579516B2232b` and reach out via the repo.
- Contributors: check the contract's Deposit/Contribution events for your
  address (etherscan -> Internal Txns, filter by your address).

## Contact

- Repo: https://github.com/wabrent/etherdelta-recovery
- Open an issue to coordinate.

_White-hat case: no fee is taken unless agreed in advance with the verified
owner. Funds are returned to their rightful owners only._
