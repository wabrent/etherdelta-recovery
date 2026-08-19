"""Скриншоты-пруфы для твит-треда.

Снимает страницы Blockscout (баланс, имя, создатель), таблицы кандидатов
и дамп дизассемблера. Результат: screenshots/tweet*.png

Запуск: python proofshots.py
"""

import csv
import html
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "screenshots"
OUT.mkdir(exist_ok=True)

PAGES = [
    ("tweet3_etherdelta_15214eth", "https://eth.blockscout.com/address/0x8d12A197cB00D4747a1fe03395095ce2A5CC6819"),
    ("tweet4_exchange2016_1513eth", "https://eth.blockscout.com/address/0xecf8f87f810ecf450940c9f60066b4a7a501d6a7"),
    ("tweet5_contract_2015_122eth", "https://eth.blockscout.com/address/0xc4c51de1abf5d60dbd329ec0f999fd8f021ae9fc"),
    ("tweet6_owner_eoa_sleeping", "https://eth.blockscout.com/address/0x87c5b5874a18b4306df8a752a6c8cc3e82dafc19"),
    ("tweet10_next_2480eth", "https://eth.blockscout.com/address/0x4d55f76ce2dbbae7b48661bef9bd144ce0c9091b"),
]


def table_html(title: str, headers: list, rows: list) -> str:
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>" for r in rows
    )
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#0d1117; color:#e6edf3; margin:40px; }}
h1 {{ color:#58a6ff; font-size:26px; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th,td {{ border:1px solid #30363d; padding:8px 12px; text-align:left; white-space:nowrap; }}
th {{ background:#161b22; color:#58a6ff; }}
tr:nth-child(even) {{ background:#161b22; }}
td.mono {{ font-family:Consolas,monospace; }}
</style></head><body>
<h1>{html.escape(title)}</h1>
<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
</body></html>"""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1400})

        for name, url in PAGES:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(6000)
                page.screenshot(path=str(OUT / f"{name}.png"))
                print(f"OK  {name}.png")
            except Exception as e:
                print(f"ERR {name}: {str(e)[:80]}")

        rows = []
        with open(HERE / "results.csv", encoding="utf-8-sig", newline="") as f:
            for i, r in enumerate(csv.DictReader(f)):
                if i >= 15:
                    break
                rows.append([r["address"], f"{float(r['eth']):,.2f}", r["deployed_at"][:10], r["sighashes"][:80]])
        html_doc = table_html("Scanner: top 15 candidates from BigQuery (500 total)", ["address", "ETH", "deployed", "selectors"], rows)
        f_html = OUT / "_candidates.html"
        f_html.write_text(html_doc, encoding="utf-8")
        page.goto(f_html.as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "tweet2_scanner_500_candidates.png"))
        print("OK  tweet2_scanner_500_candidates.png")

        disasm = """<pre>437  JUMPDEST                    // withdraw(uint256 amount)
441  CALLDATALOAD               // amount = calldata[4]
446  SLOAD                      // storage[1]        (owner)
457  AND
458  CALLER                     // msg.sender
462  AND
463  EQ                         // storage[1] == msg.sender ?
467  JUMPI                      // if equal -> continue
471  JUMP  -> 1803              // else -> revert
...
1472  SHA3(CALLER, slot) SLOAD  // balance[msg.sender]
1391  LT ISZERO                 // balance >= amount ? else revert
1461  ...                       // send amount to msg.sender</pre>"""
        dis_html = f"""<!doctype html><html><head><meta charset="utf-8">
<style>body {{ background:#0d1117; color:#e6edf3; font-family:Consolas,monospace; font-size:16px; padding:40px; }}
pre {{ color:#7ee787; white-space:pre; }}
</style></head><body>
<h1 style="color:#58a6ff;font-family:'Segoe UI',Arial,sans-serif;">Contract 0xc4c51de1 (Aug 2015, 122 ETH) - withdraw() disassembly</h1>
{disasm}</body></html>"""
        f_dis = OUT / "_disasm.html"
        f_dis.write_text(dis_html, encoding="utf-8")
        page.goto(f_dis.as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "tweet5_disassembly_withdraw.png"))
        print("OK  tweet5_disassembly_withdraw.png")

        browser.close()

    for f in sorted(OUT.glob("*.png")):
        print(f"{f.name}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
