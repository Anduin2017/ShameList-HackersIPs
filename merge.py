#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
merge_inputs.py

将 input_ips.txt 中的新 IP / 子网，合并到 list 文件中，避免重复或已包含的条目。

用法：
    ./merge_inputs.py [-i INPUT_FILE] [-l LIST_FILE]

默认：
    INPUT_FILE = input_ips.txt
    LIST_FILE  = list
"""

import argparse
import ipaddress
from pathlib import Path
import sys

def load_networks(path):
    """
    从文件中读取每行（IP 或 CIDR），返回 [(原文, ip_network), …]
    忽略空行和格式错误的条目。
    """
    nets = []
    for line in path.read_text().splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            # 单 IP 当成 /32 网络处理
            net = ipaddress.ip_network(text, strict=False)
        except ValueError:
            print(f"[WARN] 跳过无效条目：{text}", file=sys.stderr)
            continue
        nets.append((text, net))
    return nets

def main():
    p = argparse.ArgumentParser(description="Merge new IPs/subnets into a master list")
    p.add_argument('-i','--input', default='input_ips.txt', help="待合并列表（默认 input_ips.txt）")
    p.add_argument('-l','--list',  default='list',           help="主名单文件（默认 list）")
    args = p.parse_args()

    input_path = Path(args.input)
    list_path  = Path(args.list)
    if not input_path.exists() or not list_path.exists():
        print("ERROR: 确保 input 和 list 文件都存在！", file=sys.stderr)
        sys.exit(1)

    # 加载已有条目
    existing = load_networks(list_path)
    existing_nets = [net for _, net in existing]

    # 处理输入
    new_entries = []
    for text, net in load_networks(input_path):
        # 如果 net 是已有任何网络的子网，就跳过
        if any(net.subnet_of(e) for e in existing_nets):
            continue
        # 否则新增
        new_entries.append(text)
        existing_nets.append(net)

    # 写回
    if new_entries:
        with list_path.open('a') as f:
            for entry in new_entries:
                f.write(entry + '\n')
        print(f"[OK] 共新增 {len(new_entries)} 条：")
        print('\n'.join(new_entries))
    else:
        print("[OK] 无需要新增的条目。")

if __name__ == '__main__':
    main()
