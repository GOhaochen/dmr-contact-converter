# -*- coding: utf-8 -*-
"""RadioID DMR-ID 名单 → 如意通 6900DMR 联系人 CSV 转换工具。

输入：从 https://radioid.net 下载的 ``user.csv``（原始名单，UTF-8 带 BOM）。
输出：``china_dmr_ids_final.csv``（GBK/ANSI 编码），可直接由 6900DMR 写频软件导入。

筛选规则：呼号以 ``B``（中国大陆）、``VR2``（香港）、``XX9``（澳门）开头。

用法::

    6900DMR-Contact-Tool.exe                    # 读取同目录下的 user.csv
    6900DMR-Contact-Tool.exe D:\\下载\\user.csv   # 或把 user.csv 拖到 exe 上

本文件是 ``demo.py`` 的打包版：修正了工作目录依赖、Windows 控制台编码、
个人调试信息等不适合分发的内容，转换规则与原版完全一致。
"""

from __future__ import annotations

import csv
import os
import sys

APP_NAME = "6900DMR 联系人转换工具"
INPUT_NAME = "user.csv"
OUTPUT_NAME = "china_dmr_ids_final.csv"

# 写频软件要求的目标表头
OUTPUT_HEADER = ["序号", "对讲机ID", "呼号", "别名", "城市", "省份", "国家", "备注", "呼叫类型", "呼叫提示"]
# RadioID 原版名单的前七列，用于校验文件是否正确
EXPECTED_HEADER = ["RADIO_ID", "CALLSIGN", "FIRST_NAME", "LAST_NAME", "CITY", "STATE", "COUNTRY"]

# 中国大陆 / 香港 / 澳门 的呼号前缀
CHINA_PREFIXES = ("B", "VR2", "XX9")


def base_dir() -> str:
    """程序所在目录。打包成 exe 后取 exe 所在目录，而非当前工作目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def setup_console() -> None:
    """Windows 控制台可能是 GBK 代码页，统一改成 UTF-8 并容错，避免中文输出崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def pause_if_interactive() -> None:
    """双击运行时窗口会一闪而过，故结束时停一下等用户按回车。"""
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            input("\n按回车键退出……")
    except Exception:
        pass


def is_china_callsign(callsign: str) -> bool:
    """判断呼号是否属于中国大陆 / 香港 / 澳门。"""
    if not callsign:
        return False
    cs = str(callsign).upper().strip().replace('"', "").replace("'", "")
    return cs.startswith(CHINA_PREFIXES)


def resolve_input() -> str | None:
    """确定输入文件路径：命令行参数（支持拖拽）→ 程序同目录 → 当前目录。"""
    if len(sys.argv) > 1:
        candidate = sys.argv[1].strip().strip('"')
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
        print(f"[!] 命令行给出的文件不存在：{candidate}")

    for directory in (base_dir(), os.getcwd()):
        candidate = os.path.join(directory, INPUT_NAME)
        if os.path.isfile(candidate):
            return candidate
    return None


def convert(input_path: str, output_path: str) -> int:
    """执行转换，返回写出的记录条数；参数或数据有问题时返回 -1。"""
    print(f"正在读取：{input_path}")

    with open(input_path, mode="r", encoding="utf-8-sig", errors="ignore") as infile:
        reader = csv.reader(infile)
        try:
            header = next(reader)
        except StopIteration:
            print("[x] 文件是空的。")
            return -1

        # 严格核对表头，防止下载到的不是原版名单
        if header[:7] != EXPECTED_HEADER:
            print("[!] 表头不是 RadioID 原版格式，已中止。")
            print(f"    当前表头：{header[:7]}")
            print("    请到 https://radioid.net 重新下载 user.csv。")
            return -1

        count = 0
        skipped_rows = 0

        # 以 GBK 编码写出，确保写频软件能正常显示中文
        with open(output_path, mode="w", encoding="gbk", errors="replace", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(OUTPUT_HEADER)

            for row in reader:
                # 原版名单至少要有 7 列
                if len(row) < 7:
                    skipped_rows += 1
                    continue

                dmr_id = row[0].strip()
                callsign = row[1].strip()

                # 只接受纯数字 ID，防止数据错位
                if not dmr_id.isdigit():
                    skipped_rows += 1
                    continue

                if not is_china_callsign(callsign):
                    continue

                count += 1

                # 别名 = FIRST_NAME + LAST_NAME；若其中重复了呼号则剔除
                alias = f"{row[2].strip()} {row[3].strip()}".strip()
                if alias.upper().startswith(callsign.upper()):
                    alias = alias[len(callsign):].strip()

                writer.writerow([
                    count,          # 序号，从 1 连续编号
                    dmr_id,         # 对讲机ID
                    callsign,       # 呼号
                    alias,          # 别名
                    row[4].strip(),  # 城市
                    row[5].strip(),  # 省份
                    row[6].strip(),  # 国家
                    "",             # 备注（留空）
                    "个呼",          # 呼叫类型
                    "无",            # 呼叫提示
                ])

    print(f"[✓] 共写出 {count} 条中国呼号记录，跳过 {skipped_rows} 行无效数据。")
    print(f"[✓] 输出文件：{output_path}")
    return count


def main() -> int:
    setup_console()
    print("=" * 46)
    print(f"  {APP_NAME}")
    print("=" * 46)

    input_path = resolve_input()
    if input_path is None:
        print(f"[x] 找不到 {INPUT_NAME}。")
        print(f"    请把 {INPUT_NAME} 放在本程序同一目录下，或直接把它拖到本程序图标上。")
        print("    下载地址：https://radioid.net/database/dump/user.csv")
        pause_if_interactive()
        return 2

    # 输出到 user.csv 同目录：结果就在用户放数据的地方，也避免 Program Files 无写权限
    output_path = os.path.join(os.path.dirname(input_path), OUTPUT_NAME)
    try:
        result = convert(input_path, output_path)
        rc = 0 if result >= 0 else 1
    except Exception as exc:  # noqa: BLE001 - 面向最终用户，统一提示
        print(f"[x] 发生错误：{exc}")
        rc = 1

    pause_if_interactive()
    return rc


if __name__ == "__main__":
    sys.exit(main())
