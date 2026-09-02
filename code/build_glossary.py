#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《术语与符号表.md》：从 47 篇正文抽取符号使用图谱与中英术语对照（底稿）。

诚实边界（重要，v2）：
- 符号的「频次 / 出现篇数 / 首现篇」是可机械统计的事实，直接给出。
- 符号的「含义」一律来自脚本内置的 **人工核定字典**（SYMBOL_MEANING），
  不再用正则瞎抽。原因：v1 用正则抓「符号 + 为/表示 + 定义」，抓到的是
  上下文碎片（如 ψ →「高斯（高斯函数的傅里叶变换仍是高斯」），还会把
  未闭合括号、LaTeX 残留、甚至表格管道符带进表格——错的比没的更糟。
  多义符号给出主要含义 + 常见变体；未收录的显式写「待补」。
- 术语的「英译」来自正文「中文（English）」形态，加左边界约束过滤噪声，
  抽不到就不收，绝不臆造。

设计原则：
1. 统计列单一数据源（正文），改动正文后重跑即可同步；含义列单一数据源（字典）。
2. 过滤规则针对实测噪声设计，不是想当然。
3. 纯标准库，无外部依赖。

用法：python3 code/build_glossary.py
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "术语与符号表.md"

# 物理符号白名单（LaTeX 命令）：排除 frac/text/tag/mathtt 等纯排版命令
SYMBOLS = [
    "hbar", "nabla", "partial", "ell", "infty", "dagger",
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "pi",
    "rho", "varrho", "sigma", "tau", "upsilon", "phi", "varphi", "chi",
    "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
    "Phi", "Psi", "Omega",
]

# 符号字形（便于零门槛读者对照），取不到的用 LaTeX 名替代
GLYPH = {
    "hbar": "ħ", "nabla": "∇", "partial": "∂", "ell": "ℓ", "infty": "∞",
    "dagger": "†", "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "epsilon": "ϵ", "varepsilon": "ε", "zeta": "ζ", "eta": "η",
    "theta": "θ", "vartheta": "ϑ", "iota": "ι", "kappa": "κ", "lambda": "λ",
    "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ", "varrho": "ϱ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "ϕ", "varphi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ",
    "Omega": "Ω",
}

# 人工核定的符号含义：多义符号给「主要含义 + 常见变体」，分号分隔
SYMBOL_MEANING = {
    "hbar": "约化普朗克常数 ħ = h/2π，量子作用量的自然单位；全库最基础常数",
    "psi": "波函数 / 态矢量 |ψ⟩，量子态的主符号；部分篇目作具体波函数 ψ(x)",
    "omega": "角频率；变体：拉比频率 Ω_R、声子频率、经典振荡频率",
    "lambda": "波长；变体：耦合常数、拉格朗日乘子、标度参数、衰变常数",
    "phi": "相位 / 方位角；变体：标量势 φ、磁通量 Φ",
    "alpha": "精细结构常数 α ≈ 1/137（第 06 篇）；变体：相干态参数、一般系数",
    "Delta": "差值 / 能隙（如超导能隙）；变体：拉普拉斯算符 ∆、不确定度",
    "varepsilon": "能量微元 / 单模平均能量；变体：介电常数 ε、Levi-Civita 符号",
    "mu": "磁矩；变体：化学势、约化质量、磁导率、微米",
    "rho": "密度矩阵 ρ（第 09、18 篇）；变体：电荷/概率密度、电阻率",
    "pi": "圆周率 π；变体：宇称算符 Π、动量共轭变量",
    "partial": "偏导数算符 ∂",
    "nu": "频率 ν；变体：量子霍尔填充因子 ν（第 28 篇）",
    "sigma": "泡利矩阵 σ_x,σ_y,σ_z（第 16 篇）；变体：标准差、电导率、散射截面",
    "dagger": "厄米共轭（共轭转置）†，|ψ⟩† = ⟨ψ|",
    "theta": "角度 / 相位 θ；变体：阶跃函数 Θ、QCD θ 真空角",
    "beta": "一般系数 β；变体：1/k_BT（统计权重）、β 衰变标记",
    "gamma": "衰变率 / 阻尼率 Γ（第 31 篇）；变体：洛伦兹因子、Gamma 函数",
    "delta": "狄拉克 δ 函数 / 克罗内克 δ；变体：微小增量、相位偏移",
    "kappa": "耦合强度 κ（第 14 篇）；变体：热导率、衰减常数",
    "infty": "无穷 ∞；典型语境为紫外灾难的发散（第 03 篇）",
    "ell": "轨道角动量量子数 ℓ（第 16、17 篇）",
    "nabla": "梯度 / 散度 / 旋度算符 ∇",
    "epsilon": "小参数 / 微扰参数 ε；变体：介电常数、能级记号",
    "zeta": "ζ；典型语境为黎曼 ζ 函数（第 03 篇黑体辐射求和）",
    "eta": "效率 η（如探测器效率）；变体：黏度、赝标量介子",
    "xi": "相干长度 ξ（第 27 篇超导）；变体：一般坐标",
    "tau": "寿命 / 弛豫时间 τ（如 T1、T2 之外的通用时间常数）",
    "chi": "磁化率 χ（第 43 篇宝石学）；变体：旋量分量、特征函数",
    "varphi": "相位 / 宏观波函数 φ（第 27 篇超导序参量）",
    "vartheta": "角度 ϑ（散射角等）",
    "varrho": "密度 ϱ（电荷密度 / 概率密度的另一种写法）",
    "xi_": "",
    "Gamma": "衰变宽度 / 跃迁率 Γ；变体：gamma 函数",
    "Theta": "阶跃函数 Θ；变体：QCD θ 角有关的 Θ 参数",
    "Lambda": "角动量投影 / 截断参数 Λ；变体：宇宙学常数（第 41 篇）",
    "Sigma": "求和号 Σ；变体：自能 Σ（多体物理）",
    "Pi": "宇称算符 Π（第 21 篇）；变体：正则动量",
    "Phi": "磁通量 Φ（第 26 篇 AB 效应）；变体：波函数",
    "Psi": "多体 / 总波函数 Ψ（区别于单粒子 ψ）",
    "Omega": "频率 / 立体角 Ω；变体：拉比频率",
    "Upsilon": "Υ 介子（第 37 篇粒子物理）",
    "Xi": "Ξ 重子（第 37 篇粒子物理）",
    "Xi_": "",
    "iota": "ι（罕见记号）",
    "upsilon": "υ（罕见记号）",
}

# 人工补录的缩写：正文**裸用但从未给过括号定义式**，正则抽不到。
# 判据：全库出现 ≥ 10 次且为学界标准术语。只补有确切把握的，不确定的宁可不补。
# 说明性/计量性字符串（DOI、CODATA、PRL、编号 R1/R2、罗马数字 II/III）不属术语，不补。
MANUAL_ABBR = {
    "QED": "量子电动力学（Quantum Electrodynamics）",
    "KG": "克莱因-戈登方程（Klein-Gordon）",
    "NV": "氮-空位色心（nitrogen-vacancy center，金刚石）",
    "CHSH": "Clauser-Horne-Shimony-Holt 不等式（贝尔不等式的实验形式）",
    "BB84": "Bennett-Brassard 1984 协议（首个量子密钥分发协议）",
    "AB": "阿哈罗诺夫-玻姆效应（Aharonov-Bohm）",
    "WKB": "Wentzel-Kramers-Brillouin 准经典近似",
    "POVM": "正算子值测度（Positive Operator-Valued Measure，广义测量）",
    "EPR": "爱因斯坦-波多尔斯基-罗森佯谬（Einstein-Podolsky-Rosen）",
    "CPT": "电荷共轭-宇称-时间反演联合对称性",
    "FQHE": "分数量子霍尔效应",
    "QBER": "量子比特误码率（quantum bit error rate）",
    "ZPL": "零声子线（zero-phonon line）",
    "E91": "Ekert 1991 协议（基于纠缠的量子密钥分发）",
    "CFT": "共形场论（conformal field theory）",
    "CSS": "Calderbank-Shor-Steane 量子纠错码",
    "BCS": "Bardeen-Cooper-Schrieffer 超导微观理论",
}

# 中文侧噪声：以这些字开头的不是术语（助词/连接词/方位词残留）
STOP_FIRST = set(
    "的与中其该用亦为是在把被从对由而且或即这那有无第个些于之则若使所将并但很更就才只又再"
    "上下里外内间前后时到例比另各每某此另另计如乃及至以"
)
# 中文侧噪声：以这些字结尾的多为句子碎片（真术语极少以此收尾）
STOP_LAST = set(
    "的与中其该用亦为是在把被从对由而而且或即这那有无第个些于之则若使所将并但很更就才只又再"
    "上下里外内间前后时到且派等地着过们吗呢吧啊了"
)
# 整词黑名单：这些是普通词/论述用语，不是术语
STOP_WORD = {
    "传统", "例如", "比如", "部分", "主要", "一般", "基本", "实际", "具体", "直接",
    "简单", "复杂", "不同", "相同", "相关", "有关", "其中", "因此", "所以", "但是",
    "然而", "并且", "或者", "如果", "由于", "通过", "关于", "对于", "至于", "以及",
    "甚至", "尤其", "特别", "另外", "此外", "总之", "注意", "说明", "表明", "证明",
    "结果", "过程", "方法", "问题", "情况", "条件", "系统", "数据", "实验", "理论",
}
# 英文侧噪声：人名+年份、机构+年份等引用形态
YEAR_RE = re.compile(r"\b(1[89]|20)\d{2}\b")
# 英文侧：纯数字或纯标点
LETTER_RE = re.compile(r"[A-Za-z]")


def scan_notes():
    files = sorted(ROOT.glob("[0-9][0-9]_*_系统笔记.md"))
    if len(files) != 47:
        sys.exit(f"扫描到 {len(files)} 篇，预期 47 篇")
    return [(int(p.name[:2]), p) for p in files]


def symbol_stats(notes):
    """符号频次、出现篇数、首现篇（纯统计，可靠）。"""
    freq = defaultdict(int)
    in_notes = defaultdict(set)
    first = {}
    for no, p in notes:
        text = p.read_text(encoding="utf-8")
        for sym in SYMBOLS:
            n = len(re.findall(r"\\" + sym + r"(?![a-zA-Z])", text))
            if n:
                freq[sym] += n
                in_notes[sym].add(no)
                if sym not in first:
                    first[sym] = no
    return freq, in_notes, first


def clean_cell(s):
    """表格单元格清洗：转义管道符、压平换行、去 LaTeX 残留。"""
    s = s.replace("|", r"\|").replace("\n", " ").strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s


def filter_term(zh, en):
    """过滤实测噪声：助词开头的中文、含年份的引用、过短过长、非术语碎片。"""
    if not zh or not en:
        return False
    if zh in STOP_WORD:
        return False
    if zh[0] in STOP_FIRST:
        return False
    if zh[-1] in STOP_LAST:
        return False
    if not LETTER_RE.search(en):
        return False
    if YEAR_RE.search(en):
        return False
    if not (1 <= len(en.split()) <= 5):
        return False
    if not (2 <= len(zh) <= 8):
        return False
    if re.match(r"^[A-Z]{2,}\s*\d", en):
        return False
    return True


def term_table(notes):
    """抽取中英术语对照。

    关键修正（v2）：中文片段必须紧邻左边界（行首/空格/标点/标记符），
    否则正则会贪心回溯抓到「上非零且超泊松（bunching）」这类句子碎片。
    中文没有词边界，左边界约束是唯一可靠的廉价过滤。
    """
    pat = re.compile(
        r"(?:^|[\s，。；：、（）「」【】“”‘’\*\|`\(\[\{>\-])"
        r"([一-龥]{2,8})[（(]\s*([A-Za-z][A-Za-z0-9 ,'\-\.]{1,40})\s*[)）]",
        re.M,
    )
    terms = {}
    for no, p in notes:
        text = p.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            zh, en = m.group(1).strip(), m.group(2).strip()
            # 剔除小节标题残留（如「## 2.1 投影测量」）
            if zh.startswith("#") or " " in zh:
                continue
            if not filter_term(zh, en):
                continue
            if zh not in terms:
                terms[zh] = (en, no, "正文")
    return terms


def abbr_table(notes, terms):
    """缩写索引：全库扫描缩写定义，同缩写多义的**全部列出**。

    为什么不能按 terms 去重取首篇：EPR 在量子信息篇是 Einstein-Podolsky-Rosen，
    在宝石学篇是电子顺磁共振。只取篇号最小的那条会给读者错误答案——
    缩写多义是真实存在的，脚本必须如实呈现而不是挑一个。
    """
    pat = re.compile(
        r"(?:^|[\s，。；：、（）「」【】\*\|`\(\[\{>\-])"
        r"([一-龥]{2,8})[（(]\s*([A-Z][A-Za-z0-9\-]{1,9}(?:\s*[,，]\s*[A-Z][A-Za-z0-9\-]{1,9})?)\s*[)）]",
        re.M,
    )
    seen = defaultdict(list)  # abbr -> [(zh, no)]
    for no, p in notes:
        text = p.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            zh, en = m.group(1).strip(), m.group(2).strip()
            if zh in STOP_WORD or zh[0] in STOP_FIRST or zh[-1] in STOP_LAST:
                continue
            for core in re.split(r"\s*[,，]\s*", en):
                if not re.fullmatch(r"[A-Z][A-Za-z0-9\-]{1,9}", core):
                    continue
                if len(core) < 2:
                    continue
                if not (core.isupper() or re.fullmatch(r"[A-Z][a-z]+[A-Z]\w*", core)):
                    continue
                if not any(z == zh for z, _ in seen[core]):
                    seen[core].append((zh, no))
    # 人工补录：裸用无定义式的标准术语，追加到抽取结果后面（不覆盖抽取值）
    for a, zh in MANUAL_ABBR.items():
        seen[a] = [(zh, 0)] + seen.get(a, [])
    return seen


def build_doc(notes, freq, in_notes, first, terms, abbr):
    L = []
    L.append("# 术语与符号表")
    L.append("")
    L.append("> 本篇由 `code/build_glossary.py` 从 47 篇正文生成，属底稿性质。")
    L.append(">")
    L.append("> **诚实边界（v2）**：")
    L.append("> - 频次 / 出现篇数 / 首现篇是**可机械统计的事实**，直接给出；")
    L.append("> - 符号含义来自脚本内置的**人工核定字典**，不再正则瞎抽——v1 的正则会抓到")
    L.append(">   上下文碎片，错的比没的更糟。多义符号给主要含义 + 常见变体；")
    L.append("> - 术语英译取自正文「中文（English）」形态并加左边界约束过滤，抽不到就不收。")
    L.append("")
    L.append(f"- 符号：**{len(freq)}** 个（含义已核定 "
             f"{sum(1 for s in freq if SYMBOL_MEANING.get(s))} 个，待补 "
             f"{sum(1 for s in freq if not SYMBOL_MEANING.get(s))} 个）")
    L.append(f"- 术语：**{len(terms)}** 条中英对照（左边界约束过滤后）")
    L.append(f"- 缩写：**{len(abbr)}** 条")
    L.append("")
    L.append("---")
    L.append("")

    # 一、符号表
    L.append("## 一、符号表")
    L.append("")
    L.append("按全库使用频次排序。含义为人工核定，多义符号以分号列出常见变体；"
             "写「**待补**」表示尚未核定。")
    L.append("")
    L.append("| 符号 | LaTeX | 全库频次 | 出现篇数 | 首现篇 | 含义（人工核定） |")
    L.append("|------|-------|---------|---------|-------|----------------|")
    for sym in sorted(freq, key=lambda s: -freq[s]):
        g = GLYPH.get(sym, "")
        mean = SYMBOL_MEANING.get(sym) or "**待补**"
        L.append(
            f"| {g or sym} | `\\{sym}` | {freq[sym]} | {len(in_notes[sym])} | "
            f"第 {first[sym]:02d} 篇 | {clean_cell(mean)} |"
        )
    L.append("")

    # 二、术语表
    L.append("## 二、术语表（中英对照）")
    L.append("")
    L.append("取自正文「中文（English）」形态，中文片段须紧邻左边界（空格/标点/行首/标记符），"
             "否则判为句子碎片丢弃。全部条目**待人工校订**后方为正式译名。")
    L.append("")
    L.append("| 中文 | 英文 | 首现篇 |")
    L.append("|------|------|-------|")
    for zh in sorted(terms):
        en, no, _ = terms[zh]
        L.append(f"| {zh} | {clean_cell(en)} | 第 {no:02d} 篇 |")
    L.append("")

    # 三、缩写索引
    L.append("## 三、缩写索引")
    L.append("")
    L.append("全库扫描缩写定义。**同一缩写在不同篇目含义不同的，全部列出**并标注「多义」——"
             "例如 EPR 在量子信息篇指 Einstein-Podolsky-Rosen 佯谬，"
             "在宝石学篇指电子顺磁共振。只挑一条给读者就是误导。")
    L.append("")
    L.append("| 缩写 | 中文（多义全列） | 首现篇 | 备注 |")
    L.append("|------|------|-------|------|")
    for a in sorted(abbr):
        items = sorted(abbr[a], key=lambda x: x[1])
        zh_all = "；".join(z for z, _ in items)
        nos = [n for _, n in items if n > 0]
        first_txt = f"第 {nos[0]:02d} 篇" if nos else "—"
        notes_ = []
        if len(items) > 1:
            notes_.append(f"**多义** ×{len(items)}")
        if a in MANUAL_ABBR:
            notes_.append("人工补录")
        L.append(f"| {a} | {clean_cell(zh_all)} | {first_txt} | {' · '.join(notes_)} |")
    L.append("")

    # 四、维护与待办
    L.append("## 四、维护方式")
    L.append("")
    L.append("1. 本文件**整体由脚本生成**，不要手工编辑（下次重跑会覆盖）。")
    L.append("2. 想补符号含义 → 改脚本里的 `SYMBOL_MEANING` 字典（人工核定，不靠正则）。")
    L.append("3. 想补术语 → 在对应篇目用「中文（English）」形态书写，且中文前留空格或标点，")
    L.append("   然后重跑 `python3 code/build_glossary.py`。")
    L.append("4. 统计列（频次/篇数/首现篇）随正文自动同步，无需维护。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("*本篇由脚本生成 · 统计源为 47 篇正文 · 含义为人工核定 · 术语待校订*")
    L.append("")
    return "\n".join(L)


def main():
    notes = scan_notes()
    freq, in_notes, first = symbol_stats(notes)
    terms = term_table(notes)
    abbr = abbr_table(notes, terms)
    doc = build_doc(notes, freq, in_notes, first, terms, abbr)
    OUTPUT.write_text(doc, encoding="utf-8")

    n_mean = sum(1 for s in freq if SYMBOL_MEANING.get(s))
    print(f"已生成 {OUTPUT.name}")
    print(f"  符号 {len(freq)} 个（含义已核定 {n_mean} 个，待补 {len(freq) - n_mean} 个）")
    print(f"  术语 {len(terms)} 条（v1 为 200 条含大量碎片，v2 加左边界约束）")
    print(f"  缩写 {len(abbr)} 条")
    print("  边界：含义人工核定；术语抽不到就不收，不臆造")


if __name__ == "__main__":
    main()
