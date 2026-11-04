# -*- coding: utf-8 -*-
"""转换逻辑的冒烟测试。

直接加载被测模块，用 fixtures 里的样例名单跑一遍，校验输出的编码、表头、
筛选结果与序号连续性。CI 与本地均可运行：``python tests/test_convert.py``。
"""

import csv
import importlib.util
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_PATH = os.path.join(ROOT, "dmr_contact_converter.py")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "user_sample.csv")

failures = []


def check(condition, message):
    if condition:
        print(f"  [ok] {message}")
    else:
        print(f"  [FAIL] {message}")
        failures.append(message)


def load_module():
    spec = importlib.util.spec_from_file_location("dmr_contact_converter", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load_module()

    print("模块加载与常量：")
    check(module.INPUT_NAME == "user.csv", "输入文件名为 user.csv")
    check(module.OUTPUT_NAME == "china_dmr_ids_final.csv", "输出文件名为 china_dmr_ids_final.csv")
    check(len(module.OUTPUT_HEADER) == 10, "目标表头为 10 列")
    check(module.OUTPUT_HEADER[0] == "序号" and module.OUTPUT_HEADER[9] == "呼叫提示", "目标表头首尾正确")

    print("\n呼号判定：")
    for callsign, expected in [
        ("BD1ABC", True), ("B", True), ("VR2XYZ", True), ("XX9ABC", True),
        ("W1AW", False), ("DL1XYZ", False), ("", False),
        ('"bd1abc"', True),
    ]:
        check(module.is_china_callsign(callsign) is expected, f"{callsign!r} → {expected}")

    print("\n端到端转换：")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "out.csv")
        count = module.convert(FIXTURE, out_path)

        check(count == 3, f"样例中 3 条中国呼号被提取（实际 {count}）")
        check(os.path.isfile(out_path), "输出文件已生成")

        with open(out_path, "r", encoding="gbk") as handle:
            rows = list(csv.reader(handle))

        check(rows[0] == module.OUTPUT_HEADER, "写出表头与常量一致")
        check(len(rows) == 4, f"共 4 行（表头 + 3 条记录），实际 {len(rows)} 行")
        check([r[0] for r in rows[1:]] == ["1", "2", "3"], "序号从 1 连续编号")
        check([r[2] for r in rows[1:]] == ["BD1ABC", "VR2XYZ", "XX9ABC"], "只保留中国呼号")
        check(all(r[8] == "个呼" and r[9] == "无" for r in rows[1:]), "呼叫类型/提示为固定值")
        check(all(r[7] == "" for r in rows[1:]), "备注列为空")

        # 别名应合并姓与名，且不重复呼号
        check(rows[1][3] == "三 张", f"别名合并正确（实际 {rows[1][3]!r}）")

        raw = open(out_path, "rb").read()
        check(b"\xef\xbb\xbf" not in raw, "输出不带 UTF-8 BOM")
        check(raw[:6] != b"RADIO_", "输出不是原版表头")

    print("\n异常输入：")
    with tempfile.TemporaryDirectory() as tmp:
        bad = os.path.join(tmp, "bad.csv")
        with open(bad, "w", encoding="utf-8") as handle:
            handle.write("A,B,C\n1,2,3\n")
        check(module.convert(bad, os.path.join(tmp, "o.csv")) == -1, "表头不符时返回 -1 且不写文件")
        check(not os.path.isfile(os.path.join(tmp, "o.csv")), "表头不符时不产生输出")

    print()
    if failures:
        print(f"FAILED: {len(failures)} 项未通过")
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
