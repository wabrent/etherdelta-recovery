"""Глубокая разведка конкретного адреса через Blockscout API.

Запуск:
    python deepdive.py 0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE / "ident_cache.json"


def api(path: str) -> dict:
    url = "https://eth.blockscout.com/api/v2/" + path
    req = urllib.request.Request(url, headers={"User-Agent": "whitehat-scanner/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    addr = sys.argv[1].lower()
    info = load_cache().get(addr) or api(f"addresses/{addr}")

    print(f"== {addr} ==")
    print(f"Name:    {info.get('name') or '?'}")
    print(f"Balance: {int(info['coin_balance']) / 1e18:.2f} ETH")
    print(f"Creator: {info.get('creator_address_hash')}")
    print(f"Created: {info.get('creation_transaction_hash')}")
    print(f"Verified: {info.get('is_verified')}")

    try:
        txs = api(f"addresses/{addr}/transactions?limit=5")
        print("\nПоследние 5 транзакций:")
        for t in txs.get("items", []):
            ts = t.get("timestamp")
            frm = (t.get("from") or {}).get("hash", "?")[:12]
            to = (t.get("to") or {}).get("hash", "?")[:12]
            val = int(t.get("value") or 0) / 1e18
            status = t.get("status")
            print(f"  {ts}  {frm} -> {to}  {val:.4f} ETH  {status}")
    except Exception as e:
        print(f"(tx list error: {e})")

    try:
        tr = api(f"addresses/{addr}/internal-transactions?limit=5")
        print("\nПоследние 5 внутренних транзакций:")
        for t in tr.get("items", []):
            ts = t.get("timestamp")
            frm = (t.get("from") or {}).get("hash", "?")[:12]
            to = (t.get("to") or {}).get("hash", "?")[:12]
            val = int(t.get("value") or 0) / 1e18
            print(f"  {ts}  {frm} -> {to}  {val:.4f} ETH  {t.get('type')}")
    except Exception as e:
        print(f"(internal tx error: {e})")

    try:
        sc = api(f"smart-contracts/{addr}")
        abi = sc.get("abi")
        print(f"\nABI: {'есть' if abi else 'нет'}, сол. версия: {sc.get('compiler_version')}")
        if abi:
            for f in abi:
                if f.get("type") == "function":
                    inputs = ",".join(i.get("type", "") for i in f.get("inputs", []))
                    print(f"  {f.get('name')}({inputs})")
    except Exception as e:
        print(f"(abi error: {e})")


if __name__ == "__main__":
    main()
