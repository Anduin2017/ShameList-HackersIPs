#!/usr/bin/env python3
"""
Convert raw IP list to Cloudflare IP List CSV format.

- Auto-fixes CIDR with host bits set (e.g. 1.2.3.4/24 → 1.2.3.0/24)
- Removes duplicates
- Outputs valid Cloudflare-compatible CSV

Usage:
    python3 convert_to_cloudflare.py
    python3 convert_to_cloudflare.py -i input.txt -o output.csv
"""

import argparse
import ipaddress
import sys


def convert(input_path: str, output_path: str, description: str = "blocklist"):
    seen = set()
    fixed = 0
    dup = 0
    invalid = 0
    results = []

    with open(input_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        raw = line.strip()
        if not raw:
            continue

        try:
            if '/' in raw:
                net = ipaddress.ip_network(raw, strict=False)
                normalized = str(net)
            else:
                ip = ipaddress.ip_address(raw)
                normalized = str(ip)

            if normalized in seen:
                dup += 1
                continue
            seen.add(normalized)

            if normalized != raw:
                print(f"  [FIX] line {i}: {raw} -> {normalized}")
                fixed += 1

            results.append(normalized)

        except ValueError:
            print(f"  [SKIP] line {i}: {raw} (invalid)", file=sys.stderr)
            invalid += 1

    with open(output_path, 'w') as f:
        f.write("ip,description\n")
        for ip in results:
            f.write(f"{ip},{description}\n")

    print(f"\nDone: {output_path}")
    print(f"  Valid:      {len(results)}")
    print(f"  Fixed:      {fixed}")
    print(f"  Duplicates: {dup}")
    print(f"  Skipped:    {invalid}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert raw IP list to Cloudflare CSV"
    )
    parser.add_argument(
        "-i", "--input",
        default="list",
        help="Input file (default: list)"
    )
    parser.add_argument(
        "-o", "--output",
        default="cloudflare-list.csv",
        help="Output CSV file (default: cloudflare-list.csv)"
    )
    parser.add_argument(
        "-d", "--description",
        default="blocklist",
        help="Description for all entries (default: blocklist)"
    )
    args = parser.parse_args()

    convert(args.input, args.output, args.description)


if __name__ == "__main__":
    main()
