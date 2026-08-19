"""Генератор 4-байтовых селекторов (sighash) для функций вывода средств.

Запуск:
    python sighash.py            -> записывает selectors.txt + выводит SQL-фрагмент
    python sighash.py "foo()"    -> выводит селектор для одной сигнатуры
"""

import sys

from Crypto.Hash import keccak

SIGNATURES = [
    "refund()",
    "refund(uint256)",
    "refundAll()",
    "claim()",
    "claim(uint256)",
    "claimTokens()",
    "claimTokens(uint256)",
    "claimAll()",
    "withdraw()",
    "withdraw(uint256)",
    "withdrawAll()",
    "finalize()",
    "finalization()",
    "exit()",
    "kill()",
    "drain()",
    "unlock()",
    "unlockTokens()",
    "release()",
    "releaseTokens()",
    "reclaim()",
    "cashout()",
    "getRefund()",
    "refundMyIcoInvestment()",
    "withdrawRefund()",
    "ownerWithdraw()",
    "ownerWithdraw(uint256)",
    "emergencyWithdraw()",
    "emergencyExit()",
    "rescue()",
    "rescueTokens()",
    "sweep()",
    "sweepTokens()",
    "recoverFunds()",
    "recoverTokens()",
    "collect()",
    "collectTokens()",
    "withdrawEther()",
    "withdrawETH()",
]


def selector(signature: str) -> str:
    k = keccak.new(digest_bits=256)
    k.update(signature.encode())
    return "0x" + k.hexdigest()[:8]


def main() -> None:
    if len(sys.argv) > 1:
        for sig in sys.argv[1:]:
            print(f"{selector(sig)}  {sig}")
        return

    pairs = [(selector(s), s) for s in SIGNATURES]

    with open("selectors.txt", "w", encoding="utf-8") as f:
        for sel, sig in pairs:
            f.write(f"{sel}  {sig}\n")
    print(f"selectors.txt: {len(pairs)} селекторов")

    sql_list = ",\n    ".join(f"'{sel}'" for sel, _ in pairs)
    print("\nSQL-фрагмент для BigQuery (IN-список):\n")
    print(sql_list)


if __name__ == "__main__":
    main()
