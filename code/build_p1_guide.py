#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子力学通识讲义改造 · P1 机械部分：三层阅读指引自动注入

设计原则（与方案一致，不推翻架构）：
- 单一数据源：各篇头部；脚本只注入统一的「三层阅读指引」模板，不改正文、不动引用、不改命名。
- 跳过已含标记篇（如 01 篇样板已手工三件套齐备），幂等可重跑。
- 「一句话结论」与「通俗说法辨析表」属语义内容，由逐篇人工填写，本脚本不碰。

运行：python code/build_p1_guide.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # code/ -> 项目根
MARK = "## 阅读指引（三层）"
GUIDE = (
    "## 阅读指引（三层）\n"
    "\n"
    "| 深度 | 阅读范围 | 你能带走什么 |\n"
    "|------|---------|------------|\n"
    "| 零门槛线 | §一 + §四 + §七 | 结论、实验数字、来龙去脉（不碰一个公式） |\n"
    "| 进阶线 | 加 §三 + §五 | 量级感、物理机制 |\n"
    "| 完整线 | 全部八节 | 完整推导与可解模型 |\n"
)


def inject(path: Path) -> str:
    """返回状态：'done' 注入成功 / 'skip' 已存在 / 'no_sec1' 无 §一 / 'err' 异常"""
    try:
        t = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"err:{e}"
    if MARK in t:
        return "skip"
    idx = t.find("## 一、概念与定位")
    if idx == -1:
        return "no_sec1"
    new = t[:idx] + GUIDE + "\n" + t[idx:]
    path.write_text(new, encoding="utf-8")
    return "done"


def main():
    notes = sorted(ROOT.glob("[0-9][0-9]_*_系统笔记.md"))
    done = skip = no_sec1 = err = 0
    for p in notes:
        st = inject(p)
        if st == "done":
            done += 1
            print(f"  + 注入三层指引：{p.name}")
        elif st == "skip":
            skip += 1
        elif st == "no_sec1":
            no_sec1 += 1
            print(f"  ✗ 无 §一，跳过：{p.name}")
        else:
            err += 1
            print(f"  ✗ {st}：{p.name}")
    print(f"\n完成：注入 {done} 篇，跳过(已含标记) {skip} 篇，无§一 {no_sec1} 篇，异常 {err} 篇")


if __name__ == "__main__":
    main()
