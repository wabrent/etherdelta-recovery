"""Ранжирование CSV-выгрузки из BigQuery (stuck_contracts.sql).

Запуск:
    python rank.py results.csv [--top 50]

Формат CSV (колонки из SQL):
    address, eth_balance, eth, deployed_at, creator_address, code_fp, sighashes, last_out

Оценка интереса:
    score = eth * возрастной_множитель * селекторный_множитель
    - возраст: чем старше контракт, тем выше (до x3 на 8+ лет)
    - селекторы: refund/claim/withdraw = 0.5, прочие из списка = 0.25
    - спящий контракт (нет last_out) получает флаг DORMANT
"""

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent

# имя -> вес, берём из scanner/selectors.txt
SELECTOR_WEIGHTS = {}
HIGH = {"refund", "claim", "withdraw", "unlock", "release"}


def load_selectors() -> None:
    try:
        with open(HERE / "selectors.txt", encoding="utf-8") as f:
            for line in f:
                sel, sig = line.split(maxsplit=1)
                sig = sig.strip().rstrip("()")
                name = sig.split("(")[0].lower()
                SELECTOR_WEIGHTS[sel] = 0.5 if any(h in name for h in HIGH) else 0.25
    except FileNotFoundError:
        print("selectors.txt не найден — селекторный множитель выключен", file=sys.stderr)


def parse_ts(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace(" UTC", "+00:00").replace("Z", "+00:00"))
    except ValueError:
        return None


def selector_mult(sighashes: str) -> float:
    if not sighashes:
        return 1.0
    return 1.0 + sum(
        SELECTOR_WEIGHTS.get(s.strip(), 0.0) for s in sighashes.split(",")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args()

    load_selectors()

    now = datetime.now(timezone.utc)
    rows = []
    with open(args.csv_file, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                eth = float(row.get("eth") or 0)
            except ValueError:
                continue
            if eth <= 0:
                continue
            deployed = parse_ts(row.get("deployed_at", ""))
            age_mult = 1.0 + min((now - deployed).days / 365, 8) / 4 if deployed else 1.0
            smult = selector_mult(row.get("sighashes", ""))
            dormant = not (row.get("last_out") or "").strip()
            rows.append({
                "address": row.get("address", ""),
                "eth": eth,
                "age_mult": age_mult,
                "smult": smult,
                "dormant": dormant,
                "score": eth * age_mult * smult,
                "deployed": deployed,
                "creator": row.get("creator_address", ""),
                "code_fp": row.get("code_fp", ""),
            })

    rows.sort(key=lambda r: r["score"], reverse=True)

    print(f"{'ADDRESS':<44} {'ETH':>9} {'SCORE':>9} {'AGE':>6} {'CODE_FP':<18} FLAGS")
    print("-" * 100)
    for r in rows[: args.top]:
        flags = ("DORMANT " if r["dormant"] else "") + ("KNOWN-SEL" if r["smult"] > 1.0 else "")
        age = f"{(now - r['deployed']).days // 365}y" if r["deployed"] else "?"
        print(
            f"{r['address']:<44} {r['eth']:9.2f} {r['score']:9.2f} {age:>6} "
            f"{r['code_fp']:<18} {flags}"
        )
    print("-" * 100)
    print("Проверка лидера: python verify.py <address>")
    print("Ссылки: https://etherscan.io/address/<address>")


if __name__ == "__main__":
    main()
