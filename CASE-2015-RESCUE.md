# 2015 Rescue Case: 206 ETH stuck in August 2015 contracts

**Target contracts:**
- `0xc4c51de1abf5d60dbd329ec0f999fd8f021ae9fc` - 122.07 ETH (deployed 2015-08-12)
- `0xd79b4c6791784184e2755b2fc1659eaab0f80456` - 83.94 ETH (deployed 2015-08-12)

**Total: 206.01 ETH (~$390k)**

## What these contracts are

Disassembly of `withdraw(uint256)` (0x2e1a7d4d) shows:

```
437 JUMPDEST
441 CALLDATALOAD      // amount
446 SLOAD             // storage[1] (owner)
458 CALLER            // msg.sender
463 EQ                // storage[1] == msg.sender ?
467 JUMPI             // owner-only
468 JUMP -> 1803      // else revert
```

Storage slots 0-1 both hold the owner: `0x87C5B5874A18B4306DF8a752a6C8cc3E82daFc19` (also the deployer).
Only the owner can withdraw. The funds are not accessible to anyone else.

## Owner profile (on-chain)

- Plain EOA, no ENS, no labels, no public mentions
- First tx 2015-08-09 (received 1 ETH), funded with 100 ETH on 2015-08-12 from `0x326be8f71bfb0379f989aab1cc1fe37f0a771f60`
- Deployed 4 contracts on 2015-08-12; the cluster moved ~4,000+ ETH through them that day
- Very active in 2015-2016: 545 calls to its own contracts
- Regular 500-600 ETH inflows from `0x2910543af39aba0cd09dbb2d50200b3e800a63d2` (likely an early mining/venue operator)
- 2016-07-04: swept 3,058.74 ETH to `0x6b13ea57548adef6e333021a27144e88f509b314` (cluster wind-down)
- Last transaction: 2017-05-06 (received 0.001 ETH). Silent for 9+ years.

## Evidence chain

| Date | Event |
| --- | --- |
| 2015-08-09 | owner receives 1 ETH from 0x48cd680b |
| 2015-08-12 | owner receives 100 ETH from 0x326be8f7; deploys contracts incl. 0xc4c51de1, 0xd79b4c67; cluster moves ~4k ETH |
| 2015-08 to 2016-05 | regular 500-600 ETH inflows from 0x2910543af3 |
| 2016-07-04 | owner sends 3,058.74 ETH to 0x6b13ea57 (wind-down) |
| 2017-05-06 | last tx on owner address |
| 2026-08 | 206 ETH still in the two contracts; no activity since 2017 |

## If you are the owner

The contracts are intact and the withdrawal path still works: `withdraw(uint256 amount)`
from your address `0x87C5B5874A18B4306DF8a752a6C8cc3E82daFc19` sends the ETH to you.
You can verify ownership by signing a message with that key and reaching out.

## Contact

- Repo: https://github.com/wabrent/etherdelta-recovery
- Open an issue or reach out via the repo to confirm identity and coordinate.

_White-hat case: no fee is taken unless agreed in advance with the verified owner.
Funds are returned to their rightful owner only._
