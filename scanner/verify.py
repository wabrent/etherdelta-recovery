"""Verify a candidate contract via public RPC (no own node).

Run:
    python verify.py 0x9fa8fa61a10ff892e4ebceb7f4e0fc684c2ce0a9
    python verify.py <address> --rpc <rpc_url>

What it does:
    1) balance and code size (if no code — contract is self-destructed, skip);
    2) extracts all PUSH4 selectors from the runtime bytecode;
    3) matches against the list of known "withdrawing" functions (selectors.txt).
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
    """Find 0x63 <4 bytes> (PUSH4) sequences in bytecode."""
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
        sys.exit("RPC unavailable. Try another: https://eth.llamarpc.com")

    addr = w3.to_checksum_address(args.address)
    balance = w3.eth.get_balance(addr)
    code = w3.eth.get_code(addr)

    print(f"Address: {addr}")
    print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
    print(f"Code:    {len(code)} bytes" + ("" if len(code) else "  <- NO CODE (self-destructed), skip"))

    if not len(code):
        return

    names = load_names()
    known = [(s, names[s]) for s in extract_sighashes(code) if s in names]
    if known:
        print(f"\nKnown withdrawal functions ({len(known)}):")
        for sel, name in known:
            print(f"  {sel}  {name}")
        print("\nNext step: open the contract on etherscan.io, read these functions,")
        print("and figure out who can call them (msg.sender / onlyOwner / multisig).")
    else:
        print("\nNo known withdrawal selectors found — funds are probably withdrawn via")
        print("a non-standard function. Inspect the source/decompilation manually.")


if __name__ == "__main__":
    main()
