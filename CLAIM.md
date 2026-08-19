# EtherDelta: how to claim your ETH back (whitehat claim guide)

**Contract:** 0x8d12a197cb00d4747a1fe03395095ce2a5cc6819
(the main EtherDelta exchange contract, deployed 09.02.2017)

**Currently in the contract:** ~15,214 ETH of user deposit balances that were
never withdrawn before the exchange shut down.

Second instance (EtherDelta 2): 0x373c55c277b866a69dc047cad488154ab9759466 - 122 ETH.

## Who this is for

You traded on EtherDelta in 2017-2018 and deposited ETH (via `deposit()`),
but did not withdraw everything before closing. Your balance is still
recorded in the contract's `tokens` mapping and can be withdrawn.

## Step 1. Check your balance (2 minutes, no risk)

1. Open https://etherscan.io/address/0x8d12a197cb00d4747a1fe03395095ce2a5cc6819
2. Tab **Contract** -> **Read Contract**
3. Find `balanceOf(address token, address user)` - ETH balances live in the
   `tokens` mapping under key `token = 0x0000000000000000000000000000000000000000`
4. Enter: `token` = 0x0000000000000000000000000000000000000000, `user` = your address ->
   Query. The value is your balance in wei (divide by 10^18 to get ETH).

Alternative: etherscan **Internal Txns** tab of the contract, filtered by
your address: sum of `Deposit` events minus `Withdraw` events.

## Step 2. Withdraw (one transaction)

1. MetaMask (or any wallet) with the address you used on the exchange.
2. etherscan -> tab **Contract** -> **Write Contract** -> "Connect to Web3".
3. `withdraw(uint256 _amount)` - enter your balance **in wei** (from step 1).
4. Confirm. Gas ~50-100k, costs $2-10.

The contract charges no fee for ETH withdrawals (`feeMake = 0`). You receive
the full amount.

If you also deposited ERC20 tokens (USDT, ZRX, etc.), use
`withdrawToken(address _token, uint256 _amount)` with the token address.
Tokens held by the contract are withdrawn the same way.

## Safety rules

- Withdraw ONLY from your own address, to yourself. Never share keys, no
  "wallet verification" sites, no middlemen.
- Note: in December 2017 EtherDelta was hit by a DNS attack (fake frontend).
  Never approve anything on unknown addresses. Work directly through the
  contract on etherscan.
- If your balance shows 0, you have no remaining balance on this contract.

## Verification

- The contract address in this guide matches the verified source on
  Etherscan (contract name "EtherDelta", Solidity 0.4.9).

_This is a white guide: funds are returned to their owners. No fee is taken,
no third-party address is involved in the withdrawal path._
