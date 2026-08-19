"""Batch probe: storage slots + getters + creator for the next targets.

Usage: python batch_probe.py [--top 15] [--skip ADDR,ADDR]
Reads scanner/shortlist.csv, probes each address via public RPC.
"""

import argparse
import csv
import json
from pathlib import Path

from web3 import Web3

HERE = Path(__file__).parent
RPC = "https://ethereum-rpc.publicnode.com"

DONE = {
    "0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c",
    "0x4d55f76ce2dbbae7b48661bef9bd144ce0c9091b",
    "0xecf8f87f810ecf450940c9f60066b4a7a501d6a7",
    "0x755cdba6ae4f479f7164792b318b2a06c759833b",
    "0xab83d96de35bad6f234178fbb6507203488e9626",
    "0x4aea7cf559f67cedcad07e12ae6bc00f07e8cf65",
    "0xc4c51de1abf5d60dbd329ec0f999fd8f021ae9fc",
    "0xd79b4c6791784184e2755b2fc1659eaab0f80456",
    "0xed44f3c2081480b08643fe1ca281fab9ed643735",
}

GETTERS = {
    "owner()": "0x8da5cb5b",
    "name()": "0x06fdde03",
    "symbol()": "0x95d89b41",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(RPC))
    cache = {}
    f = HERE / "ident_cache.json"
    if f.exists():
        cache = json.loads(f.read_text(encoding="utf-8"))

    with open(HERE / "shortlist.csv", encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("eth") and r["address"] not in DONE]
    rows.sort(key=lambda r: float(r["eth"]), reverse=True)

    print(f"{'ADDRESS':<44} {'ETH':>8} {'CODE':>6} {'SLOT0':<12} {'SLOT1':<12} NAME/OWNER")
    print("-" * 120)
    for r in rows[: args.top]:
        addr = r["address"]
        a = w3.to_checksum_address(addr)
        try:
            code = w3.eth.get_code(a)
            s0 = w3.eth.get_storage_at(a, 0).hex()
            s1 = w3.eth.get_storage_at(a, 1).hex()
        except Exception as e:
            print(f"{addr}  ERR {str(e)[:40]}")
            continue
        s0v = s0[-40:] if s0 != "0x" + "00" * 32 else ""
        s1v = s1[-40:] if s1 != "0x" + "00" * 32 else ""
        name = owner = ""
        for gname, sel in GETTERS.items():
            if sel[2:] in code.hex():
                try:
                    res = w3.eth.call({"to": a, "data": sel})
                    if gname == "owner()" and len(res) == 32:
                        owner = Web3.to_checksum_address(res[-20:].hex())
                    elif gname in ("name()", "symbol()") and len(res) > 32:
                        ln = int.from_bytes(res[32:64], "big")
                        name = res[64:64 + ln].decode(errors="ignore")
                except Exception:
                    pass
        info = cache.get(addr.lower(), {})
        creator = (info.get("creator_address_hash") or "")[:12]
        print(f"{addr} {float(r['eth']):8.2f} {len(code):6d} {s0v:<12} {s1v:<12} {name[:14]} own={owner[:14]} cr={creator}")


if __name__ == "__main__":
    main()
