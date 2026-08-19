"""Идентификация кандидатов из results.csv через Blockscout API (без ключа).

Запуск:
    python identify.py [--top 40] [--csv scanner/results.csv]
"""

import argparse
import csv
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE / "ident_cache.json"

BASE = "https://eth.blockscout.com/api/v2/addresses/{}"


def fetch(address: str) -> dict:
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        cache = {}
    key = address.lower()
    if key in cache:
        return cache[key]
    req = urllib.request.Request(
        BASE.format(address), headers={"User-Agent": "whitehat-scanner/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        data = {"error": str(e)[:60]}
    cache[key] = data
    try:
        CACHE.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass
    time.sleep(0.25)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(HERE / "results.csv"))
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--out", default=str(HERE / "identified.csv"))
    args = parser.parse_args()

    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("eth")]

    rows.sort(key=lambda r: float(r["eth"]), reverse=True)
    out = []
    for r in rows[: args.top]:
        info = fetch(r["address"])
        rec = {
            "address": r["address"],
            "eth": float(r["eth"]),
            "deployed_at": r.get("deployed_at", ""),
            "sighashes": r.get("sighashes", ""),
            "name": info.get("name") or "",
            "verified": info.get("is_verified", False),
            "creator": info.get("creator_address_hash") or "",
            "creation_tx": info.get("creation_transaction_hash") or "",
        }
        out.append(rec)

    if args.out:
        with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
        print(f"Сохранено: {args.out} ({len(out)} записей)")

    print(f"{'ADDRESS':<44} {'ETH':>10} {'NAME':<26} VERIFIED")
    print("-" * 90)
    for r in out:
        print(f"{r['address']:<44} {r['eth']:10.2f} {(r['name'] or '?')[:26]:<26} {str(r['verified']):<8}")


if __name__ == "__main__":
    main()
