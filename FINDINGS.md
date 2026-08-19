# Case notes: 2026-08-19 scan for stuck ETH

Pipeline: BigQuery (500 candidates) -> identification (Blockscout) ->
shortlist (369 unidentified contracts with withdrawal functions) ->
manual disassembly of top targets.

## Verified findings

### 1. EtherDelta - 0x8d12a197cb00d4747a1fe03395095ce2a5cc6819 - 15,214 ETH
- 2017 exchange (Zachary Coburn), deposit/withdraw DEX contract.
- The funds are user deposits that were never withdrawn.
- Withdrawal: `withdraw(uint256)` is available to any balance holder
  (second instance: 0x373c55c277b866a69dc047cad488154ab9759466 - 122 ETH).
- IMPORTANT (verified 2026-08-19): the contract is NOT dormant. Every day
  `withdraw()` calls arrive from various addresses (dust bots, 0.008-0.1 ETH,
  receipt=1). Large balances remain unclaimed. Accurate framing:
  "15,214 ETH of residuals in a live contract; dust is being collected by bots".
- METHODOLOGY BUG: the BigQuery dormancy filter (`from_address = contract`)
  is always empty because contracts never appear as transaction originators.
  The DORMANT flag in rank.py was meaningless. Real activity must be checked
  by calls TO the contract (txlist, selector, receipt) and balance changes.

### 2. 0xecf8f87f810ecf450940c9f60066b4a7a501d6a7 - 1,513 ETH (06.2016)
- Tokenized exchange from 2016: totalSupply == contract balance exactly 1:1.
- 1,471 token holders, 27,268 transfers. Any token holder can withdraw ETH
  via withdraw(uint256).
- Path: identify large holders, outreach/guide.

### 3. 0xc4c51de1abf5d60dbd329ec0f999fd8f021ae9fc + 0xd79b4c6791784184e2755b2fc1659eaab0f80456 - 206 ETH (08.2015!)
- Contracts from the first weeks of Ethereum (August 2015).
- Disassembly: `withdraw(uint256)` requires `msg.sender == storage[1]`.
- storage[1] = 0x87C5B5874A18B4306DF8a752a6C8cc3E82daFc19 = deployer = EOA.
- Owner: no labels, 0.001 ETH balance, last tx 2017-05-06. In 2016 moved
  large amounts (3,058 ETH on 2016-07-04).
- Trail: received 100 ETH from 0x326be8f71bfb0379f989aab1cc1fe37f0a771f60 on
  2015-08-12 (full address confirmed), deployed 4 contracts the same day
  (incl. 0xc4c51de1, 0xd79b4c67, 0xb86a36e3 - empty token, 0 ETH).
  Holds 1 WEALTH token (spam).
- Path: try to identify the owner from on-chain traces, white contact,
  agreed fee for outreach/analysis.

### 4. 0x4aea7cf559f67cedcad07e12ae6bc00f07e8cf65 - 221 ETH (08.2016)
- Exchange contract: withdraw by `balances[msg.sender]` (disassembly).
- Funds belong to depositors -> outreach case like EtherDelta.

### 5. 0xed44f3c2081480b08643fe1ca281fab9ed643735 - 50 ETH (12.2015)
- Slot 1 = 0x25980600 (not an address) - different structure, needs separate
  analysis. Queue candidate.

### 6. 0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c - 3,391 ETH (08.2018)
- "Last Winner" (LW): owner = deployer 0xEAe69cADEB04E66767bD69f52e0fFFc28E37d799.
- Owner is alive (holds keys) -> not "lost funds", only a commercial contact
  (unlikely).

### 7. 0x4d55f76ce2dbbae7b48661bef9bd144ce0c9091b - 2,480 ETH (09.2017)
- Same exchange pattern as 0x4aea7cf5: deposit/withdraw by balances[msg.sender].
- Slots 0-1 = deployer 0x4499514831219df01cf5d6b66c76ca9d76ac4f74.
- Owner: last tx 2021-11-22 (small amounts), before that 2019-2020.
  Contract untouched ~5 years. Classification: depositor funds (outreach case).

### 8. Not targets (excluded)
- WithdrawDAO 0xbf4ed7b2 - 81,504 ETH: withdrawal only for DAO token holders,
  residual goes to trustee (A. van de Sande). Known mechanism.
- 0x755cdba6 - 977 ETH: WithdrawDAO clone, same trustee.
- 0x2cc2720e (49 ETH), 0xf0a92466 (37 ETH): self-destructed, code erased,
  ETH burned, unrecoverable.
- WETH9 0xc02aaa39 - 2.28M ETH: infrastructure, not a target.

## Batch 2026-08-19 (batch_probe.py, 15 targets, ~1,450 ETH)

| Address | ETH | Verdict |
| --- | --- | --- |
| 0x4db13686 / 0xc0099b50 / 0x6baec8a0 (553-byte clones) | 83.7 / 75.6 / 69.5 | kill()+collect() collection contracts; owner 0x42dA8a05CB ACTIVE (tx 2026-08-03) - not stuck |
| 0x4d1886da | 107.5 | exchange family (same selectors as 0x4aea7cf5); time lock storage[5]=4587234 long passed; user-claimable balances |
| 0xf058ee35 | 91.2 | withdraw() checks balances[msg.sender] > 0 (disassembly pc 888-970); user-claimable |
| 0xc3c12a9e | 101.3 | owner 0x194AFBF7A5 (last tx 2025-01-09); queue |
| 0xdd637dda / 0x48c128ea / 0x879ae070 / 0xdc260a23 | 138+98+84+92 | staking-template clones (slot0=3); queue |
| 0x05aa2fdf / 0x4fb7d68e / 0x18b59a4d | 120/84/70 | "B4B" family, same creator 0x535b25b00C; queue |
| 0x47663541 / others | 87 | queue |

Pattern: ~90% of "stuck" contracts are exchange residuals (user-claimable).
The only owner-lost cases remain: 2015 pair 0xc4c51de1+0xd79b4c67 (206 ETH).

## Analysis queue (shortlist.csv - 369 addresses)
- 0xab83d96d - 468 ETH (2018, "Gold Apple", withdraw)
- 0xfd71d62a - 73 ETH (2016, claim())
- 0x2387a684 - 55 ETH (2017, getRefund())
- 0x102011cb - 32 ETH (2017, release)
- + 360 addresses in descending balance order

## Tooling (scanner/)
bq_run.py (BigQuery) | rank.py (ranking) | identify.py (identification) |
deepdive.py (activity) | probe.py (on-chain getters) | analyze.py (disassembler) |
shortlist.py (shortlist) | scan_batch.py (RPC scan) | verify.py (verification) |
proofshots.py (proof screenshots)

## Ethics
No contract gives "our" money: funds belong to owners/depositors. Income comes
from an agreed whitehat outreach fee or reputation. Draining other people's
funds is theft.
