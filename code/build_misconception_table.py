#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《常见误区总表.md》：汇总 47 篇正文里的全部「通俗说法辨析」条目。

这是通识讲义改造的**旗舰资产**：单篇辨析只服务于那一篇，汇总表才让零门槛读者
能一次检索 141 条「这话听起来对、其实不严谨」的说法，也是本套笔记对抗
「科普误区」这一定位的可检验凭据。

设计原则（与 build_glossary.py 一致）：
1. **单一数据源**：条目全部从 47 篇正文的 `### 通俗说法辨析` 表格抽取，
   改正文后重跑即同步；不手工维护副本。
2. **诚实边界**：
   - 分组（部分）、统计（条数、机制分布）是可机械判定的事实，直接给出；
   - 「误区机制」一栏是**按正则模式做的描述性统计**，不是人工逐条分类，
     文档里明确标注，不假装是权威分类；
   - 不改写任何条目的措辞——条目由各篇作者（本轮改造）撰写，脚本只搬运。
3. 幂等：整文件重写，可反复重跑。

用法：python3 code/build_misconception_table.py
"""
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_p2 import CANON  # 权威部分定义，单一真源

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "常见误区总表.md"

MARK = "### 通俗说法辨析"
HEADER = "| 通俗说法 | 严谨表述 | 误区根源 |"

# 误区机制的**描述性**判据：仅用于统计分布，非人工逐条分类。
# 顺序敏感：先匹配的先归类。
MECHANISMS = [
    ("概念替换：把 A 当成 B", r"把.*?(当成|当|想成|视为)"),
    ("混淆：把两件事混为一谈", r"混淆|混为一谈|混同"),
    ("误认：以为是另一种机制", r"误以为|误用|误解|以为是"),
    ("忽略条件：漏掉边界/前提", r"忽略|未计|漏掉|忽视|不加区分"),
    ("外推过度：把局部当普遍", r"当成普遍|以偏概全|推广|一律|都"),
]


def split_row(row: str):
    """按未转义竖线切分（Markdown 中 \\| 是字面竖线）。"""
    parts = re.split(r"(?<!\\)\|", row.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def clean(s: str):
    """单元格清洗：压平换行与多余空白。"""
    return re.sub(r"\s{2,}", " ", s.replace("\n", " ")).strip()


def title_of(text: str, fallback: str):
    """从 H1 取标题，去掉后缀与括号内英文，便于表格显示。"""
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if not m:
        return fallback
    t = m.group(1).strip()
    t = t.replace("系统量子力学笔记", "").strip()
    if "（" in t:
        t = t.split("（")[0].strip()
    return t or fallback


def scan():
    """抽取全部条目：[(篇号, 标题, 文件路径, [三元组...]), ...]"""
    notes = sorted(ROOT.glob("[0-9][0-9]_*_系统笔记.md"))
    if len(notes) != 47:
        sys.exit(f"扫描到 {len(notes)} 篇，预期 47 篇")
    out = []
    for p in notes:
        no = p.name[:2]
        text = p.read_text(encoding="utf-8")
        if HEADER not in text:
            print(f"  ! {p.name} 辨析表列头不符，跳过")
            continue
        lines = text.split("\n")
        i = lines.index(HEADER) + 2  # 跳过表头与分隔行
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = split_row(lines[i])
            if len(cells) == 3:
                rows.append(tuple(clean(c) for c in cells))
            else:
                print(f"  ! {p.name} 跳过异常行（{len(cells)} 列）：{lines[i][:60]}")
            i += 1
        out.append((no, title_of(text, p.stem), p.name, rows))
    return out


def mechanism(cause: str):
    for name, pat in MECHANISMS:
        if re.search(pat, cause):
            return name
    return "其他（未匹配上述模式）"


def build(notes):
    total = sum(len(r) for *_, r in notes)
    L = []
    L.append("# 常见误区总表")
    L.append("")
    L.append("> 本篇由 `code/build_misconception_table.py` 从 47 篇正文的"
             "「通俗说法辨析」表汇总生成，属**派生资产**——不要手工编辑，重跑即覆盖。")
    L.append(">")
    L.append("> **诚实边界**：")
    L.append("> - 条目措辞**原样搬运**自各篇，脚本不改写、不增删、不润色；")
    L.append("> - 分组与统计（篇数、条数、机制分布）是可机械判定的事实；")
    L.append("> - 第三节的「误区机制」是**按正则模式做的描述性统计**，不是人工逐条分类，")
    L.append(">   同一条目可能同时符合多个模式，此处按首次匹配归类，仅供把握整体分布；")
    L.append("> - 本表判「表述是否严谨」，不判「该说法是否有教学价值」——")
    L.append(">   许多通俗说法是好的入门脚手架，问题只在于**不能被当成字面真理**。")
    L.append("")

    # 一、总览
    L.append("## 一、总览")
    L.append("")
    L.append(f"- 条目合计 **{total}** 条，覆盖 **{len(notes)}/47** 篇")
    L.append(f"- 每篇 3 条（改造方案约定的精选颗粒度）")
    L.append("")
    L.append("| 部分 | 篇号 | 条目数 |")
    L.append("|------|------|-------|")
    by_part = defaultdict(list)
    for no, *_ in notes:
        by_part[CANON[int(no)]].append(no)
    for part in sorted(by_part, key=lambda x: "一二三四五六".index(x[1])):
        nos = sorted(by_part[part])
        cnt = sum(len(r) for n, _, _, r in notes if n in nos)
        L.append(f"| {part} | {nos[0]}–{nos[-1]} | {cnt} |")
    L.append("")
    L.append("---")
    L.append("")

    # 二、按部分分组
    L.append("## 二、条目全集（按部分分组）")
    L.append("")
    L.append("「出处」列链接到对应篇目；点开可看到完整的严谨表述依据与参考文献。")
    L.append("")
    for part in sorted(by_part, key=lambda x: "一二三四五六".index(x[1])):
        nos = sorted(by_part[part])
        L.append(f"### {part}（{len(nos)} 篇）")
        L.append("")
        L.append("| # | 通俗说法 | 严谨表述 | 误区根源 | 出处 |")
        L.append("|---|---------|---------|---------|------|")
        k = 0
        for no, title, fname, rows in notes:
            if no not in nos:
                continue
            for say, strict, cause in rows:
                k += 1
                L.append(
                    f"| {k} | {say} | {strict} | {cause} | "
                    f"[第 {no} 篇]({fname}) |"
                )
        L.append("")
    L.append("---")
    L.append("")

    # 三、机制统计
    L.append("## 三、误区机制分布（描述性统计）")
    L.append("")
    L.append("按「误区根源」栏的文本模式自动归类，**首次匹配即归类**，"
             "非人工逐条判定。用途是把握整体分布，不宜当作单条目的权威分类。")
    L.append("")
    cnt = Counter()
    for *_, rows in notes:
        for _, _, cause in rows:
            cnt[mechanism(cause)] += 1
    L.append("| 误区机制 | 条目数 | 占比 |")
    L.append("|---------|-------|------|")
    for name, c in cnt.most_common():
        L.append(f"| {name} | {c} | {c / total * 100:.0f}% |")
    L.append("")
    L.append("**读法**：占比最高的机制提示了科普最容易出错的地方——"
             "多数误区不是「算错了」，而是**把一个东西当成了另一个东西**"
             "（概念替换 / 混淆 / 误认）。这三类合计通常占大头，"
             "也正是「通俗说法辨析表」存在的理由。")
    L.append("")
    L.append("---")
    L.append("")

    # 四、维护
    L.append("## 四、维护方式")
    L.append("")
    L.append("1. 本文件**整体由脚本生成**，不要手工编辑（重跑即覆盖）。")
    L.append("2. 想增改条目 → 改对应篇目 §一 的「通俗说法辨析」表，"
             "然后重跑 `python3 code/build_misconception_table.py`。")
    L.append("3. 条目数、部分分布、机制分布随正文自动同步，无需维护。")
    L.append("4. 增删条目后建议跑 `python3 code/check_spec_v12.py` 复核规范符合性。")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"*本篇由脚本生成 · 数据源为 47 篇正文 · 共 {total} 条 · "
             f"机制归类为描述性统计*")
    L.append("")
    return "\n".join(L), total


def main():
    notes = scan()
    doc, total = build(notes)
    OUTPUT.write_text(doc, encoding="utf-8")
    print(f"已生成 {OUTPUT.name}")
    print(f"  条目 {total} 条，覆盖 {len(notes)} 篇")
    for no, title, _, rows in notes:
        if len(rows) != 3:
            print(f"  ! 第 {no} 篇 {len(rows)} 条（预期 3 条）：{title}")
    print("  边界：条目原样搬运，机制归类为描述性统计，不人工润色")


if __name__ == "__main__":
    main()
