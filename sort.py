#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sort_list.py

按网络地址和前缀长度对黑名单列表排序。

用法：
    ./sort_list.py [-l LIST_FILE] [-o OUTPUT_FILE]

默认会就地排序写回 LIST_FILE；如果指定 -o，则写入 OUTPUT_FILE 而保留原文件不变。
"""

import argparse
import ipaddress
from pathlib import Path
import sys

def load_networks(path: Path):
    """从文件中读取每行 IP/CIDR，返回 ip_network 列表，忽略空行和格式错误条目。"""
    nets = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        try:
            # strict=False 会把单 IP 当作 /32 处理
            net = ipaddress.ip_network(text, strict=False)
        except ValueError:
            print(f"[WARN] 跳过第 {lineno} 行无效条目：{text}", file=sys.stderr)
            continue
        nets.append(net)
    return nets

def main():
    p = argparse.ArgumentParser(description="对黑名单列表按 IP/CIDR 排序")
    p.add_argument('-l', '--list', default='list',
                   help="要排序的列表文件（默认 ./list）")
    p.add_argument('-o', '--output',
                   help="排序后写入的文件，默认覆盖原列表")
    args = p.parse_args()

    list_path = Path(args.list)
    if not list_path.exists():
        print(f"ERROR: 列表文件不存在：{list_path}", file=sys.stderr)
        sys.exit(1)

    nets = load_networks(list_path)
    # 排序：先按 network_address，再按 prefixlen（都从小到大）
    nets.sort(key=lambda net: (int(net.network_address), net.prefixlen))

    output_path = Path(args.output) if args.output else list_path
    with output_path.open('w', encoding='utf-8') as f:
        for net in nets:
            f.write(str(net) + "\n")

    print(f"[OK] 排序完成，共处理 {len(nets)} 条，结果写入：{output_path}")

if __name__ == '__main__':
    main()
