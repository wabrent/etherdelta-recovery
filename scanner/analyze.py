"""Дизассемблер контракта: таблица функций + код функции по селектору.

Запуск:
    python analyze.py 0x4aea7cf559f67cedcad07e12ae6bc00f07e8cf65
    python analyze.py <addr> withdraw 0x2e1a7d4d
"""

import sys
from pathlib import Path

import pyevmasm
from web3 import Web3

HERE = Path(__file__).parent
RPC = "https://ethereum-rpc.publicnode.com"


def disassemble(code: bytes):
    return list(pyevmasm.disassemble_all(code))


def main() -> None:
    w3 = Web3(Web3.HTTPProvider(RPC))
    addr = w3.to_checksum_address(sys.argv[1])
    code = w3.eth.get_code(addr)
    print(f"== {sys.argv[1]}  ({len(code)} bytes) ==")

    ops = disassemble(code)
    jumps = set()
    for i, op in enumerate(ops):
        if op.name == "JUMPDEST":
            jumps.add(op.pc)

    dispatchers = []
    for i, op in enumerate(ops):
        if op.name == "PUSH4" and i + 1 < len(ops) and ops[i + 1].name == "EQ":
            sel = "0x" + op.operand.to_bytes(4, "big").hex()
            nxt = next((j for j in range(i + 1, len(ops)) if ops[j].name == "PUSH2"), None)
            dst = ops[nxt].operand if nxt is not None else 0
            dispatchers.append((sel, dst, i))
    if dispatchers:
        print("\nДиспетчер функций:")
        for sel, dst, i in dispatchers:
            print(f"  {sel}  -> {dst}")
    else:
        print("\nPUSH4+EQ-диспетчер не найден (возможно, if-else через CALLDATASIZE)")

    if len(sys.argv) > 2:
        sel = sys.argv[2].lower()
        if not sel.startswith("0x"):
            sel = "0x" + sel
        target = next((d for d in dispatchers if d[0] == sel), None)
        if target:
            dst = target[1]
            print(f"\n--- Код {sel} (начиная с pc={dst}) ---")
            for op in ops:
                if op.pc >= dst:
                    print(f"  {op.pc:6d}  {op.name} {'' if op.operand is None else op.operand}")

    print("\nПолный дамп сохранён? нет. Функции по селекторам смотри выше.")


if __name__ == "__main__":
    main()
