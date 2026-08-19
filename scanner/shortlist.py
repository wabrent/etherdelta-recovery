"""Шорт-лист целей: неопознанные контракты с выводящими селекторами.

Читает identified.csv (Blockscout) + results.csv (BigQuery) и оставляет
только контракты без названия/верификации, у которых в байткоде есть
refund/claim/withdraw/unlock/release. Это кандидаты, где деньги могут
быть доступны владельцу/держателям.

Запуск: python shortlist.py [--top 40]
"""

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).parent
HIGH = ("refund", "claim", "withdraw", "unlock", "release")


def load_sel_names() -> dict:
    names = {}
    for line in (HERE / "selectors.txt").read_text(encoding="utf-8").splitlines():
        sel, sig = line.split(maxsplit=1)
        names[sel.strip()] = sig.strip()
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--out", default=str(HERE / "shortlist.csv"))
    args = parser.parse_args()

    sel_names = load_sel_names()

    with open(HERE / "identified.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    out = []
    for r in rows:
        if str(r.get("verified", "")).lower() == "true":
            continue
        if not r.get("name"):
            pass
        sighashes = (r.get("sighashes") or "").split(",")
        matched = [sel_names.get(s.strip(), "") for s in sighashes if s.strip() in sel_names]
        high = [m for m in matched if any(h in m.lower() for h in HIGH)]
        out.append({
            "address": r["address"],
            "eth": float(r["eth"]),
            "deployed_at": r.get("deployed_at", ""),
            "high": ";".join(high) if high else "",
            "all_known": ";".join(matched) if matched else "",
        })

    out.sort(key=lambda r: (-(len(r["high"]) > 0), -r["eth"]))

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    print(f"Сохранено: {args.out} ({len(out)} записей)\n")
    print(f"{'ADDRESS':<44} {'ETH':>10} {'DEPLOYED':<20} HIGH-SELECTORS")
    print("-" * 110)
    for r in out[: args.top]:
        flag = "** " if r["high"] else "   "
        print(f"{flag}{r['address']} {r['eth']:10.2f} {r['deployed_at'][:19]:<20} {r['high'][:60]}")


if __name__ == "__main__":
    main()
