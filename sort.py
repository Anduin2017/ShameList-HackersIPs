#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sort_list_preserve_format.py

对 list 文件里的 IP/CIDR 按网络地址和前缀长度排序，
输出时保留原始文本格式（不会把单 IP 自动加 /32）。

用法：
    ./sort_list_preserve_format.py [-l LIST_FILE] [-o OUTPUT_FILE]

默认就地覆盖 LIST_FILE；指定 -o 则写到 OUTPUT_FILE，保留原文件不变。
"""

import argparse
import ipaddress
from pathlib import Path
import sys

def load_entries(path: Path):
    """
    从文件读取每行（IP 或 CIDR），返回 [(原文, IPv4Network/IPv6Network), …]
    跳过空行和无效条目，并在 stderr 打个 warning。
    """
    entries = []
    for idx, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        try:
            net = ipaddress.ip_network(text, strict=False)
        except ValueError:
            print(f"[WARN] 第 {idx} 行无效，跳过：{text}", file=sys.stderr)
            continue
        entries.append((text, net))
    return entries

def main():
    p = argparse.ArgumentParser(description="对黑名单列表排序，保留原格式")
    p.add_argument('-l', '--list', default='list',
                   help="要排序的列表文件（默认 ./list）")
    p.add_argument('-o', '--output',
                   help="排序结果写入的文件，默认覆盖原列表")
    args = p.parse_args()

    list_path = Path(args.list)
    if not list_path.exists():
        print(f"ERROR: 列表文件不存在：{list_path}", file=sys.stderr)
        sys.exit(1)

    entries = load_entries(list_path)
    # 按网络起始地址（int）和前缀长度排序
    entries.sort(key=lambda item: (int(item[1].network_address), item[1].prefixlen))

    out_path = Path(args.output) if args.output else list_path
    with out_path.open('w', encoding='utf-8') as f:
        for text, _ in entries:
            f.write(text + "\n")

    print(f"[OK] 排序完成，共处理 {len(entries)} 条，写入：{out_path}")

if __name__ == '__main__':
    main()
