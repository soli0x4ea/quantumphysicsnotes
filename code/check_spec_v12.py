#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 归档层 · 规范符合性校验（规范 v1.2 的可执行部分）

**为什么必须有这个脚本**：通识讲义改造前的教训是「制度悬空」——序.md 第 4 条
写了「科普比喻须去魅」，规范里也列了 281 行检查清单，但全库只有 16 篇 1 处落地，
「误区」一词 0 篇，**落地率 2%**。原因就是那些要求无法机械校验，只能靠自觉。
规范 v1.2 的每一条新增要求，都必须能被本脚本判成败。

检查项（任一失败则退出码非 0，可直接挂 CI）：
  1. 篇数 = 47，编号 01–47 连续无缺
  2. 八节结构完整（一~八，标题字面一致）
  3. 头部元数据齐全：数学程度、前置依赖、验证依据
  4. **三件套**：三层阅读指引 / 一句话结论 / 通俗说法辨析，各 47/47
  5. 一句话结论 ≤ 50 字（方案原定 40 字；实测 P1 撰写中位 61 字、最长 84 字，
     全部不达标。P2 取 50 字为「一眼可扫完」与「保留判据/边界」的平衡点——
     本套笔记大量结论必须带判据（如「不超光速」「DFT 带隙须 GW/BSE 修正」），
     压到 40 会牺牲严谨性。结论内禁用 LaTeX，改用 Unicode，
     否则源码字符数会把公式多的篇目判虚高。收紧过程见 tighten_conclusions.py）
  6. 辨析表：列头字面统一、≥1 条、每行严格 3 列、单元格非空
  7. 部分字段 = 权威定义（CANON，导入自 normalize_p2，单一真源）
  8. 辨析表位于 §一 内、且在 §二 之前（保证零门槛读者第一屏就看得到）

边界（诚实原则）：
  - 本脚本只判**可机械判定的形式要求**。一句话结论写得准不准、辨析对不对，
    属语义判断，脚本不假装能判，留给人工与交叉审校。

用法：python3 code/check_spec_v12.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_p2 import CANON  # 权威部分定义，单一真源

ROOT = Path(__file__).resolve().parent.parent

SECTIONS = [
    "一、概念与定位", "二、数学结构", "三、物理量与特征尺度",
    "四、实验基础与观测证据", "五、分类体系与物理机制",
    "六、典型系统与可解模型", "七、历史脉络与学术争议", "八、参考文献",
]
MARK_GUIDE = "## 阅读指引（三层）"
MARK_CONCL = "**一句话结论**"
MARK_TABLE = "### 通俗说法辨析"
HEADER_TABLE = "| 通俗说法 | 严谨表述 | 误区根源 |"
PART_RE = re.compile(r"第[一二三四五六]部分.*?(?=\s*·\s*(?:数学程度|前置依赖))")
CONCL_RE = re.compile(r"^>\s*\*\*一句话结论\*\*[：:]\s*(.+?)\s*$", re.M)
MAX_CONCL = 50


def check_file(no: int, p: Path):
    """返回问题列表（空 = 通过）。"""
    bad = []
    text = p.read_text(encoding="utf-8")
    tag = f"{p.name}"

    # 2. 八节
    for s in SECTIONS:
        if f"## {s}" not in text:
            bad.append(f"缺 §{s}")

    # 3. 头部元数据
    for field in ("数学程度", "前置依赖", "验证依据"):
        if field not in text[:2000]:
            bad.append(f"头部缺「{field}」")

    # 4. 三件套
    if MARK_GUIDE not in text:
        bad.append("缺三层阅读指引")
    m = CONCL_RE.search(text)
    if not m:
        bad.append("缺一句话结论")
    else:
        # 5. 字数
        n = len(m.group(1))
        if n > MAX_CONCL:
            bad.append(f"一句话结论 {n} 字，超过 {MAX_CONCL} 字上限")
        if "$" in m.group(1):
            bad.append("一句话结论含 LaTeX，应改用 Unicode（源码字符数会把公式判虚高）")
    if MARK_TABLE not in text:
        bad.append("缺通俗说法辨析表")
    else:
        # 6. 辨析表格式
        if HEADER_TABLE not in text:
            bad.append(f"辨析表列头不是统一格式（应为 {HEADER_TABLE}）")
        rows = table_rows(text)
        if not rows:
            bad.append("辨析表无数据行")
        for i, r in enumerate(rows, 1):
            cells = split_row(r)
            if len(cells) != 3:
                bad.append(f"辨析表第 {i} 行 {len(cells)} 列（应为 3 列）")
            elif any(not c for c in cells):
                bad.append(f"辨析表第 {i} 行有空单元格")
        # 8. 位置
        i1 = text.find("## 一、概念与定位")
        i2 = text.find("## 二、数学结构")
        it = text.find(MARK_TABLE)
        if not (i1 < it < i2):
            bad.append("辨析表不在 §一 内 / 不在 §二 之前")

    # 7. 部分字段
    hit = PART_RE.search(text[:2000])
    if not hit:
        bad.append("头部未找到部分字段")
    elif hit.group(0).strip() != CANON[no]:
        bad.append(f"部分字段「{hit.group(0).strip()}」≠ 权威「{CANON[no]}」")

    return [f"{tag}: {b}" for b in bad]


def split_row(row: str):
    """按「未转义的竖线」切分表格行。

    Markdown 表格里 `\\|` 是字面竖线（如 bra-ket 记号 α\\|0⟩+β\\|1⟩），
    不是单元格分隔符。按 `|` 无脑切分会把这类行误判为列数错误——
    这是校验器第一版自身的 bug，不是笔记的问题。
    """
    parts = re.split(r"(?<!\\)\|", row.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def table_rows(text: str):
    """取辨析表数据行（表头 + 分隔行之后，直到首个非表格行）。"""
    lines = text.split("\n")
    if MARK_TABLE not in lines:
        return []
    i = lines.index(MARK_TABLE)
    # 跳过表头与分隔行
    j = i + 1
    while j < len(lines) and not lines[j].startswith("|"):
        j += 1
    j += 2
    rows = []
    while j < len(lines) and lines[j].startswith("|"):
        rows.append(lines[j])
        j += 1
    return rows


def main():
    notes = sorted(ROOT.glob("[0-9][0-9]_*_系统笔记.md"))
    problems = []

    # 1. 篇数与连续编号
    if len(notes) != 47:
        problems.append(f"篇数 {len(notes)}，预期 47")
    nos = [int(p.name[:2]) for p in notes]
    missing = sorted(set(range(1, 48)) - set(nos))
    if missing:
        problems.append(f"编号缺失：{missing}")

    for p in notes:
        problems += check_file(int(p.name[:2]), p)

    # 汇总输出
    if problems:
        print(f"✗ 规范 v1.2 校验未通过，共 {len(problems)} 项：\n")
        for x in problems:
            print(f"  - {x}")
        sys.exit(1)

    # 通过：给统计
    total_rows = sum(len(table_rows(p.read_text(encoding="utf-8"))) for p in notes)
    lens = []
    for p in notes:
        m = CONCL_RE.search(p.read_text(encoding="utf-8"))
        if m:
            lens.append(len(m.group(1)))
    print("✓ 规范 v1.2 校验全部通过（47/47 篇）")
    print(f"  · 八节结构 / 三件套 / 辨析表格式 / 部分字段：全部符合")
    print(f"  · 辨析条目合计 {total_rows} 条"
          f"（每篇 {min(len(table_rows(p.read_text(encoding='utf-8'))) for p in notes)}"
          f"–{max(len(table_rows(p.read_text(encoding='utf-8'))) for p in notes)} 条）")
    print(f"  · 一句话结论字数：中位 {sorted(lens)[len(lens)//2]} 字，"
          f"最长 {max(lens)} 字（上限 {MAX_CONCL}）")
    print("  · 语义正确性（结论准不准 / 辨析对不对）不在本脚本判定范围，需人工审校")


if __name__ == "__main__":
    main()
