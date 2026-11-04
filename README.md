# 6900DMR 联系人转换工具

[![Build](https://github.com/GOhaochen/dmr-contact-converter/actions/workflows/build.yml/badge.svg)](https://github.com/GOhaochen/dmr-contact-converter/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/GOhaochen/dmr-contact-converter)](https://github.com/GOhaochen/dmr-contact-converter/releases)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

把 [RadioID.net](https://radioid.net) 的 DMR-ID 原始名单 `user.csv`，转换成**如意通 6900DMR**
写频软件可直接导入的联系人表 `china_dmr_ids_final.csv`。

只保留中国大陆（呼号 `B` 开头）、香港（`VR2`）、澳门（`XX9`）的记录。

## 快速开始

### 1. 下载

到 [Releases](https://github.com/GOhaochen/dmr-contact-converter/releases) 下载
`6900DMR-Contact-Tool.exe`（Windows 64 位单文件，**无需安装 Python**）。

### 2. 准备数据

到 <https://radioid.net/database/dump/user.csv> 下载最新名单（约 20 MB）。

### 3. 转换

两种方式任选：

- **拖拽**：把 `user.csv` 直接拖到 `6900DMR-Contact-Tool.exe` 图标上；
- **双击**：把 `user.csv` 和 exe 放在同一目录，双击 exe。

结果 `china_dmr_ids_final.csv` 会生成在 **`user.csv` 所在目录**。

命令行输出示例：

```
==============================================
  6900DMR 联系人转换工具
==============================================
正在读取：D:\下载\user.csv
[✓] 共写出 48213 条中国呼号记录，跳过 0 行无效数据。
[✓] 输出文件：D:\下载\china_dmr_ids_final.csv
```

### 4. 导入写频软件

用 6900DMR 写频软件的「联系人 → 导入」功能载入 `china_dmr_ids_final.csv`。
文件以 **GBK/ANSI** 编码保存，正是写频软件要求的编码，中文不会乱码。

## 输出格式

| 列 | 内容 |
| --- | --- |
| 序号 | 从 1 连续编号 |
| 对讲机ID | DMR ID |
| 呼号 | CALLSIGN |
| 别名 | `FIRST_NAME LAST_NAME` 合并；若其中重复了呼号则自动剔除 |
| 城市 | CITY |
| 省份 | STATE |
| 国家 | COUNTRY |
| 备注 | 留空 |
| 呼叫类型 | 固定为「个呼」 |
| 呼叫提示 | 固定为「无」 |

## 处理规则

| 规则 | 说明 |
| --- | --- |
| 表头校验 | 前七列必须是 `RADIO_ID, CALLSIGN, FIRST_NAME, LAST_NAME, CITY, STATE, COUNTRY`，否则中止——防止误用被改过的文件 |
| ID 校验 | `RADIO_ID` 必须是纯数字，否则该行跳过（防数据错位） |
| 编码 | 输入按 `utf-8-sig` 读（兼容 BOM），输出按 `gbk` 写 |
| 呼号判定 | 不区分大小写，自动剥离引号与空格 |

## 从源码运行 / 自行打包

源码只有一个文件，纯标准库，无第三方依赖：

```bash
python dmr_contact_converter.py                 # 读取同目录 user.csv
python dmr_contact_converter.py path/to/user.csv # 指定文件
python tests/test_convert.py                     # 跑冒烟测试
```

在 Windows 上自行打包：

```bat
build.bat
```

产物为 `dist\6900DMR-Contact-Tool.exe`。

## 自动构建

仓库已配置 GitHub Actions：每次推送到 `main` 会构建并上传产物；推送 `v*` 标签会自动创建
Release 并附上 exe。构建全部在 GitHub 的 `windows-latest` 上完成，因此不需要本地 Windows 环境。

## 常见问题

**Q：提示「找不到 user.csv」？**
把 `user.csv` 放在 exe 同目录，或直接把 `user.csv` 拖到 exe 上运行。

**Q：提示「表头不是 RadioID 原版格式」？**
你用的不是官网原始文件（例如已经用 Excel 另存过、或被别的工具改过列序）。
请重新到 <https://radioid.net> 下载。

**Q：导入后中文乱码？**
确认导入的是本工具生成的 `china_dmr_ids_final.csv`（GBK 编码），而不是原始的 `user.csv`。

**Q：杀毒软件报毒？**
PyInstaller 打包的单文件 exe 常被启发式引擎误报。源码完全公开，可自行审阅并本地打包；
也可直接运行 `python dmr_contact_converter.py`，效果相同。

## 免责声明

- 本项目为个人工具，与 RadioID.net、如意通及任何厂商均无关联。
- 名单数据由 RadioID.net 提供，其版权与使用条款归原站点所有；本仓库**不附带任何名单数据**。
- 请遵守当地关于无线电使用的法律法规与执照要求。

## 许可

[GNU General Public License v3.0](LICENSE)。

Copyright (C) 2026 GOhaochen
