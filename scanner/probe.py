"""Ончейн-зонд: вызывает известные getter'ы контракта через публичный RPC.

Запуск:
    python probe.py 0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c [адрес2 ...]
"""

import sys
from pathlib import Path

from web3 import Web3

HERE = Path(__file__).parent
RPC = "https://ethereum-rpc.publicnode.com"

GETTERS = {
    "owner()": "0x8da5cb5b",
    "name()": "0x06fdde03",
    "symbol()": "0x95d89b41",
    "totalSupply()": "0x18160ddd",
    "decimals()": "0x313ce567",
    "mainDAO()": "0xeedcf50a",
    "trustee()": "0xfdf97cb2",
    "weiRaised()": "0x5f7f8ddb",
    "endTime()": "0x3197cbb6",
    "refundEndTime()": "0x8f38f309",
    "locked()": "0xcf805191",
    "paused()": "0x5c975abb",
}


def main() -> None:
    w3 = Web3(Web3.HTTPProvider(RPC))
    targets = [a.lower() for a in sys.argv[1:]]
    for addr in targets:
        w3addr = w3.to_checksum_address(addr)
        code = w3.eth.get_code(w3addr)
        print(f"\n== {addr}  ({len(code)} bytes, {w3.from_wei(w3.eth.get_balance(w3addr), 'ether'):.2f} ETH) ==")
        hexs = code.hex()
        for name, sel in GETTERS.items():
            sel_hex = sel[2:]
            if sel_hex in hexs:
                try:
                    res = w3.eth.call({"to": w3addr, "data": sel})
                    if len(res) == 32:
                        v = int.from_bytes(res, "big")
                        if "(" in name and "address" in name or name in ("owner()", "mainDAO()", "trustee()"):
                            print(f"  {name}: {Web3.to_checksum_address(v.to_bytes(20, 'big').hex())}")
                        elif v < 10**18:
                            print(f"  {name}: {v}")
                        else:
                            print(f"  {name}: {v / 1e18:.4f}")
                    else:
                        print(f"  {name}: 0x{res.hex()}")
                except Exception as e:
                    print(f"  {name}: error {str(e)[:50]}")


if __name__ == "__main__":
    main()
