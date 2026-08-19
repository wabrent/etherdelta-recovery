"""Проверка контракта-кандидата через публичный RPC (без своего нода).

Запуск:
    python verify.py 0x9fa8fa61a10ff892e4ebceb7f4e0fc684c2ce0a9
    python verify.py <address> --rpc <rpc_url>

Что делает:
    1) баланс и размер кода (если кода нет — контракт self-destructed, пропуск);
    2) вытаскивает все PUSH4-селекторы из runtime-байткода;
    3) сверяет со списком известных "выводящих" функций (selectors.txt).
"""

import argparse
import sys
from pathlib import Path

from web3 import Web3

DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
HERE = Path(__file__).parent


def load_names() -> dict:
    names = {}
    try:
        with open(HERE / "selectors.txt", encoding="utf-8") as f:
            for line in f:
                sel, sig = line.split(maxsplit=1)
                names[sel.strip()] = sig.strip()
    except FileNotFoundError:
        pass
    return names


def extract_sighashes(code: bytes) -> list:
    """Ищет последовательности 0x63 <4 байта> (PUSH4) в байткоде."""
    found = set()
    i = 0
    while i < len(code) - 4:
        if code[i] == 0x63:  # PUSH4
            found.add("0x" + code[i + 1 : i + 5].hex())
            i += 5
        else:
            i += 1
    return sorted(found)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("address")
    parser.add_argument("--rpc", default=DEFAULT_RPC)
    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(args.rpc))
    if not w3.is_connected():
        sys.exit("RPC недоступен. Попробуй другой: https://eth.llamarpc.com")

    addr = w3.to_checksum_address(args.address)
    balance = w3.eth.get_balance(addr)
    code = w3.eth.get_code(addr)

    print(f"Адрес:   {addr}")
    print(f"Баланс:  {w3.from_wei(balance, 'ether')} ETH")
    print(f"Код:     {len(code)} байт" + ("" if len(code) else "  <- КОДА НЕТ (self-destructed), пропуск"))

    if not len(code):
        return

    names = load_names()
    known = [(s, names[s]) for s in extract_sighashes(code) if s in names]
    if known:
        print(f"\nИзвестные функции вывода ({len(known)}):")
        for sel, name in known:
            print(f"  {sel}  {name}")
        print("\nСледующий шаг: открыть контракт на etherscan.io, прочитать эти функции,")
        print("понять кто может их вызвать (msg.sender / onlyOwner / multisig).")
    else:
        print("\nИзвестных селекторов вывода не найдено — вероятно, вывод через")
        print("нестандартную функцию. Смотреть исходник/декомпиляцию вручную.")


if __name__ == "__main__":
    main()
