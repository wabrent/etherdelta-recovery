"""Батч-скан балансов контрактов через публичные RPC (без ключей).

Источники адресов:
    --source coingecko        скачать список токенов Ethereum с api.coingecko.com
    --source file:addr.txt    свой список адресов (по одному в строке)

Запуск:
    python scan_batch.py --source coingecko --min-eth 0.25
    python scan_batch.py --source file:list.txt --min-eth 1

Результат: results.csv + кэш в cache.json (повторный запуск продолжает с места).
"""

import argparse
import csv
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from web3 import Web3
from web3.exceptions import Web3Exception

HERE = Path(__file__).parent

RPCS = [
    "https://ethereum-rpc.publicnode.com",
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
    "https://eth.drpc.org",
    "https://1rpc.io/eth",
]

CACHE_FILE = HERE / "cache.json"
OUT_FILE = HERE / "results.csv"

HIGH_HINTS = ("refund", "claim", "withdraw", "unlock", "release")


def load_selector_names() -> dict:
    names = {}
    f = HERE / "selectors.txt"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            sel, sig = line.split(maxsplit=1)
            names[sel.strip()] = sig.strip()
    return names


def extract_sighashes(code: bytes) -> list:
    found = []
    i = 0
    while i < len(code) - 4:
        if code[i] == 0x63:
            found.append("0x" + code[i + 1 : i + 5].hex())
            i += 5
        else:
            i += 1
    return found


def make_web3():
    w3 = Web3(Web3.HTTPProvider(random.choice(RPCS)))
    w3.strict_bytes_type_checking = False
    return w3


class Scanner:
    def __init__(self, min_eth: float):
        self.min_wei = int(min_eth * 1e18)
        self.cache = {}
        if CACHE_FILE.exists():
            self.cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        self.sel_names = load_selector_names()
        self.lock = None

    def save_cache(self):
        CACHE_FILE.write_text(json.dumps(self.cache), encoding="utf-8")

    def scan_one(self, addr: str):
        addr = addr.strip().lower()
        if not addr.startswith("0x") or len(addr) != 42:
            return None
        if addr in self.cache:
            return None
        w3 = make_web3()
        for attempt in range(3):
            try:
                balance = w3.eth.get_balance(addr)
                code = w3.eth.get_code(addr)
                record = {
                    "balance": balance,
                    "code_len": len(code),
                    "selectors": extract_sighashes(code) if len(code) else [],
                }
                self.cache[addr] = record
                return addr, record
            except Web3Exception as e:
                if "429" in str(e) or "limit" in str(e).lower():
                    time.sleep(1.5 * (attempt + 1))
                    w3 = make_web3()
                    continue
                self.cache[addr] = {"balance": 0, "code_len": 0, "selectors": [], "error": str(e)[:80]}
                return None
            except Exception:
                self.cache[addr] = {"balance": 0, "code_len": 0, "selectors": []}
                return None
        self.cache[addr] = {"balance": 0, "code_len": 0, "selectors": []}
        return None

    def run(self, addresses: list, workers: int):
        hits = []
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(self.scan_one, a) for a in addresses]
            for fut in as_completed(futures):
                done += 1
                if done % 200 == 0:
                    self.save_cache()
                    print(f"  проверено {done}/{len(addresses)}", flush=True)
                res = fut.result()
                if res is None:
                    continue
                addr, rec = res
                if rec["balance"] >= self.min_wei and rec["code_len"] > 0:
                    hits.append((addr, rec))
        self.save_cache()
        return hits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="coingecko")
    parser.add_argument("--min-eth", type=float, default=0.25)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    if args.source.startswith("file:"):
        path = Path(args.source.split(":", 1)[1])
        addresses = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        print("Скачиваю список токенов с coingecko...", flush=True)
        import urllib.request

        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/coins/list?include_platform=true",
            headers={"User-Agent": "whitehat-scanner/1.0"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            coins = json.loads(r.read().decode())
        addresses = [
            c["platforms"]["ethereum"]
            for c in coins
            if c.get("platforms", {}).get("ethereum")
        ]
        print(f"Токен-контрактов на Ethereum: {len(addresses)}", flush=True)

    addresses = list(dict.fromkeys(a.lower() for a in addresses))
    print(f"Запускаю проверку {len(addresses)} адресов, порог {args.min_eth} ETH", flush=True)

    scanner = Scanner(args.min_eth)
    hits = scanner.run(addresses, args.workers)

    sel_names = load_selector_names()
    rows = []
    for addr, rec in hits:
        eth = rec["balance"] / 1e18
        known = [s for s in rec["selectors"] if s in sel_names]
        rows.append((addr, eth, len(known), known))

    rows.sort(key=lambda r: -r[1])
    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["address", "eth", "known_selectors", "selectors"])
        for addr, eth, n, known in rows:
            w.writerow([addr, f"{eth:.4f}", n, ";".join(known)])

    print(f"\n=== НАХОДКИ (ETH > {args.min_eth}, контракт жив) === {len(rows)}")
    for addr, eth, n, known in rows[:30]:
        flags = " ".join(sel_names[s] for s in known[:4])
        print(f"{addr}  {eth:9.2f} ETH  [{n}] {flags}")
    print(f"\nСохранено: {OUT_FILE}")


if __name__ == "__main__":
    main()
