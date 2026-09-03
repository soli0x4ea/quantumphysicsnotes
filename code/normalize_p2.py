#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 归档层 · 规范性归一（幂等，可反复重跑）

归一三处实测到的不一致（都是「规范」范畴，不动内容、不推翻架构）：

1. **09 篇分类错误**：第 09 篇《量子态与叠加原理》头部写「第二部分 形式体系工具箱」，
   但权威界定在序.md（第一部分明列 #9 叠加原理、#10 测量理论，各 10 篇），
   应为「第一部分·量子行为与基础概念」。

2. **第二部分名称两版并存**：11/16/18 篇写「形式体系工具箱」，
   12–15/17/19/20 篇写「形式体系与数学结构」。序.md 与依赖关系文档一律用后者，
   以权威文档为准统一。

3. **分隔符混乱**：第一部分/第二部分用空格（第一部分 量子行为…）、
   第三部分/第五部分用间隔号（第三部分·多体…）、第四部分两种并存、
   第六部分用冒号+破折号（第六部分：交叉应用——…）。统一为间隔号。

附带归一：01/02 篇（P1 早期手工样板）的辨析表列头为
「通俗说法 | 严格表述 | 依据」，与 03–47 篇的
「通俗说法 | 严谨表述 | 误区根源」不一致。本脚本把 01/02 转为后者，
并把原「依据」列的引用信息折进严谨表述列（引用是本项目的硬要求，不能丢）。

设计原则：
- 幂等：已归一的篇目跳过；重跑无副作用。
- 保守：只改头部字段与指定表格块，正文一字不动。
- 顶部字段改写不依赖引号字形（01/02 的弯引号不参与匹配）。

用法：python3 code/normalize_p2.py [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# 篇号 -> 权威部分名（依据：序.md 各部分篇数 10/10/8/8/5/6）
CANON = {
    **{n: "第一部分·量子行为与基础概念" for n in range(1, 11)},
    **{n: "第二部分·形式体系与数学结构" for n in range(11, 21)},
    **{n: "第三部分·多体、对称与凝聚态" for n in range(21, 29)},
    **{n: "第四部分·量子信息与量子光学" for n in range(29, 37)},
    **{n: "第五部分·相对论量子理论与前沿" for n in range(37, 42)},
    **{n: "第六部分·交叉应用——量子力学与宝石学" for n in range(42, 48)},
}

# 头部部分字段：从第X部分起，到下一个「· 数学程度」或「· 前置依赖」为止
PART_RE = re.compile(r"第[一二三四五六]部分.*?(?=\s*·\s*(?:数学程度|前置依赖))")
# 01/02 的旧列头
OLD_HEADER = "| 通俗说法 | 严格表述 | 依据 |"
NEW_HEADER = "| 通俗说法 | 严谨表述 | 误区根源 |"

# 01/02 第三列「误区根源」的新文本（按行序）。
# 前两列由脚本从原文搬运（保留引号字形），仅第三列需要人工撰写。
ROOT_CAUSE = {
    "01": [
        "把概率幅干涉当成经典概率相加",
        "把物理探测当成主观意识作用",
        "把第三种行为当成两种经典图像的混合",
    ],
    "02": [
        "把演化与探测两个环节当成客体在切换形态",
        "把概率幅波长当成实体变成波",
        "把历史总括词当成两种图像并存的实在",
    ],
}


def norm_part(no: int, text: str):
    """归一头部部分字段。返回 (新文本, 旧值, 新值) 或 None（无需改）。"""
    want = CANON[no]
    for line in text.split("\n")[:12]:  # 只在头部区域找
        m = PART_RE.search(line)
        if not m:
            continue
        cur = m.group(0).strip()
        if cur == want:
            return None
        new_line = line[: m.start()] + want + line[m.end():]
        # 只替换第一次出现（头部）
        return text.replace(line, new_line, 1), cur, want
    return None


def norm_table(no: str, text: str):
    """把 01/02 的旧辨析表转为统一三列格式。返回新文本或 None。"""
    if OLD_HEADER not in text:
        return None
    lines = text.split("\n")
    i = lines.index(OLD_HEADER)
    # 表格块：表头 -> 分隔行 -> 若干数据行 -> 首个非表格行
    rows, j = [], i + 2
    while j < len(lines) and lines[j].startswith("|"):
        rows.append(lines[j])
        j += 1
    causes = ROOT_CAUSE.get(no, [])
    if len(rows) != len(causes):
        print(f"  ! {no} 篇辨析行数 {len(rows)} 与配置的误区根源数 "
              f"{len(causes)} 不符，跳过表格归一")
        return None
    new_rows = []
    for r, cause in zip(rows, causes):
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) != 3:
            print(f"  ! {no} 篇某行不是 3 列，跳过：{r[:50]}")
            return None
        say, strict, basis = cells
        # 严谨表述 = 原严格表述 + 折进的依据（引用不能丢）
        new_rows.append(f"| {say} | {strict}（依据：{basis}） | {cause} |")
    block = [NEW_HEADER, "|---------|---------|---------|"] + new_rows
    return "\n".join(lines[:i] + block + lines[j:])


def main():
    notes = sorted(ROOT.glob("[0-9][0-9]_*_系统笔记.md"))
    if len(notes) != 47:
        sys.exit(f"扫描到 {len(notes)} 篇，预期 47 篇")
    n_part = n_table = 0
    for p in notes:
        no_txt = p.name[:2]
        no = int(no_txt)
        text = p.read_text(encoding="utf-8")
        orig = text

        r = norm_part(no, text)
        if r:
            text, cur, want = r
            n_part += 1
            print(f"  · {p.name}：{cur}  ->  {want}")

        r2 = norm_table(no_txt, text)
        if r2:
            text = r2
            n_table += 1
            print(f"  · {p.name}：辨析表列头归一（依据折入严谨表述）")

        if text != orig and not DRY:
            p.write_text(text, encoding="utf-8")

    print(f"\n完成：部分字段归一 {n_part} 篇，辨析表归一 {n_table} 篇"
          f"{'（dry-run，未写盘）' if DRY else ''}")


if __name__ == "__main__":
    main()
