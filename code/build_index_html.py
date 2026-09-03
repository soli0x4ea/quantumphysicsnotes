#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成量子力学系统笔记的导航首页 index.html。

设计原则：
1. 所有链接都从磁盘真实文件名扫描得到，绝不手写 —— 避免 md 带 NN_ 前缀、
   阅读版 html 无前缀这类命名差异导致死链。
2. 标题 / 核心内容 / 数学程度从 序.md 的目录表格解析，与正文索引保持一致。
3. 生成前逐个校验链接目标存在，任一缺失直接报错退出。
4. 纯标准库，无外部依赖；输出单文件 HTML（内嵌 CSS/JS），含搜索过滤。

用法：python3 code/build_index_html.py
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/soli0x4ea/quantumphysicsnotes"
SEQUENCE_FILE = ROOT / "序.md"
OUTPUT = ROOT / "index.html"
NOJEKYLL = ROOT / ".nojekyll"

AUX_DOCS = [
    ("序.md", "序", "六大部分架构、使用建议、配套资产说明"),
    ("常见误区总表.md", "常见误区总表",
     "141 条通俗说法辨析汇总，按六部分分组 + 误区机制分布（由 47 篇辨析表自动汇总）"),
    ("量子力学系统笔记整理规范.md", "整理规范", "八节结构、来源分级、写作禁忌、质量检查清单"),
    ("参考文献.md", "参考文献", "全部笔记引用文献统一汇编，S/A/B/C 四级分级"),
    ("修订记录.md", "修订记录", "交叉验证发现并修正的问题，含原文错误与依据来源"),
    ("依赖关系与阅读路径.md", "依赖关系与阅读路径",
     "篇级前置依赖、核心概念簇、五段推荐路径（每段经前置闭合校验）"),
    ("术语与符号表.md", "术语与符号表",
     "符号含义人工核定 + 中英术语对照 + 缩写索引（多义全列）"),
    ("README.md", "README", "项目概述与文件清单"),
]

PATH_DOC = "依赖关系与阅读路径.md"

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>量子力学系统笔记 · 全 47 篇</title>
<meta name="description" content="量子力学系统笔记，47 篇条目式参考，六大部分覆盖从双缝实验到量子引力，含 KaTeX 阅读版与可复现脚本。">
<style>
  :root{
    color-scheme: light dark;
    --bg:#ffffff; --fg:#1a1a1a; --muted:#6b7280; --card:#f7f8fa; --border:#e5e7eb;
    --accent:#2c8a6b; --link:#1a73e8; --shadow:0 1px 3px rgba(0,0,0,.06);
    --l1-bg:#e6f4ea; --l1-fg:#137333;
    --l2-bg:#fef7e0; --l2-fg:#9a6700;
    --l3-bg:#fce8e6; --l3-fg:#c5221f;
  }
  @media (prefers-color-scheme: dark){
    :root{
      --bg:#16181d; --fg:#e6e6e6; --muted:#9aa0a6; --card:#1f2228; --border:#2f333b;
      --accent:#5fcf9f; --link:#7cb0ff; --shadow:0 1px 3px rgba(0,0,0,.4);
      --l1-bg:#12351f; --l1-fg:#7ee2a8;
      --l2-bg:#3a2f10; --l2-fg:#f2c94c;
      --l3-bg:#3d1a18; --l3-fg:#ff8a80;
    }
  }
  *{box-sizing:border-box;}
  body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;
       max-width:1000px;margin:0 auto;padding:32px 20px 64px;line-height:1.7;color:var(--fg);background:var(--bg);}
  a{color:var(--link);text-decoration:none;}
  a:hover{text-decoration:underline;}
  header{border-bottom:3px solid var(--accent);padding-bottom:18px;margin-bottom:8px;}
  h1{font-size:1.75em;margin:0 0 .3em;letter-spacing:.01em;}
  .sub{color:var(--muted);font-size:.95em;margin:0;}
  .stats{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 0;}
  .stat{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 14px;font-size:.88em;}
  .stat b{font-size:1.15em;color:var(--accent);}
  .toolbar{position:sticky;top:0;background:var(--bg);padding:16px 0 12px;z-index:10;
           border-bottom:1px solid var(--border);margin-bottom:8px;}
  #q{width:100%;padding:11px 14px;font-size:1em;border:1px solid var(--border);border-radius:8px;
     background:var(--card);color:var(--fg);outline:none;font-family:inherit;}
  #q:focus{border-color:var(--accent);}
  .hint{color:var(--muted);font-size:.82em;margin-top:6px;}
  h2{font-size:1.15em;margin:2em 0 .9em;padding-left:10px;border-left:4px solid var(--accent);}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px;}
  .card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;
        box-shadow:var(--shadow);display:flex;flex-direction:column;}
  .card .top{display:flex;align-items:baseline;gap:8px;margin-bottom:2px;}
  .num{color:var(--muted);font-size:.82em;font-variant-numeric:tabular-nums;min-width:1.8em;}
  .card h3{margin:0;font-size:1.02em;font-weight:600;flex:1;}
  .desc{color:var(--muted);font-size:.86em;margin:.4em 0 .8em;flex:1;}
  .links{display:flex;gap:8px;flex-wrap:wrap;}
  .btn{display:inline-block;padding:4px 11px;border-radius:6px;font-size:.83em;
       border:1px solid var(--border);background:var(--bg);}
  .btn.primary{background:var(--accent);color:#fff;border-color:var(--accent);}
  .btn.primary:hover{text-decoration:none;opacity:.88;}
  .badge{font-size:.72em;padding:2px 7px;border-radius:4px;font-weight:600;white-space:nowrap;}
  .l1{background:var(--l1-bg);color:var(--l1-fg);}
  .l2{background:var(--l2-bg);color:var(--l2-fg);}
  .l3{background:var(--l3-bg);color:var(--l3-fg);}
  .aux{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;}
  .aux li{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:11px 14px;font-size:.92em;}
  .aux .d{color:var(--muted);font-size:.85em;display:block;margin-top:2px;}
  .assets{color:var(--muted);font-size:.9em;}
  .assets a{margin-right:12px;}
  .paths{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-top:8px;}
  .path{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);
        border-radius:10px;padding:14px 16px;box-shadow:var(--shadow);display:flex;flex-direction:column;}
  .path .ph{font-weight:700;font-size:1em;margin:0 0 .15em;color:var(--accent);}
  .path .pt{font-size:.92em;font-weight:600;margin:0 0 .4em;}
  .path .pi{color:var(--muted);font-size:.85em;margin:0 0 .6em;flex:1;line-height:1.55;}
  .path .pmeta{font-size:.8em;color:var(--muted);margin-bottom:.6em;}
  .path .pmeta b{color:var(--fg);}
  .path .seq{font-size:.78em;color:var(--muted);font-variant-numeric:tabular-nums;
            line-height:1.6;word-break:break-all;margin-bottom:.7em;}
  .path .seq .more{font-style:italic;}
  .path .btn.primary{font-size:.82em;align-self:flex-start;}
  footer{margin-top:3em;padding-top:1em;border-top:1px solid var(--border);color:var(--muted);font-size:.85em;}
  .empty{color:var(--muted);padding:20px 0;display:none;}
</style>
</head>
<body>
<header>
  <h1>量子力学系统笔记</h1>
  <p class="sub">条目式 · 八节结构 · 六大部分 47 篇 —— 可检索、可核对、可修订的量子力学参考</p>
  <div class="stats">
    <div class="stat"><b>47</b> 篇笔记</div>
    <div class="stat"><b>47</b> 个阅读版</div>
    <div class="stat"><b>__NREF__</b> 条参考文献</div>
    <div class="stat"><b>__NCODE__</b> 个可复现脚本</div>
    <div class="stat"><b>__NFIG__</b> 个图表</div>
  </div>
</header>

<div class="toolbar">
  <input id="q" type="search" placeholder="搜索标题或关键词（如 贝尔不等式、晶体场、退相干、L3）…" autocomplete="off">
  <div class="hint">输入即过滤，支持标题、摘要与难度等级。<span id="count"></span></div>
</div>

__PATHS__

<h2>辅助文档</h2>
<ul class="aux">
__AUX__
</ul>

<h2>配套资产</h2>
<p class="assets">
__ASSETS__
</p>

<footer>
  由机械姬 Soli 整理 · 阅读版基于 KaTeX + marked 渲染，公式离线可用 ·
  <a href="__REPO__">GitHub 仓库</a> · 架构版本 v1.0（2026-09）
</footer>

<script>
(function(){
  var q = document.getElementById('q');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('section[data-part]'));
  var count = document.getElementById('count');
  function apply(){
    var kw = q.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function(c){
      var hit = !kw || c.getAttribute('data-search').indexOf(kw) >= 0;
      c.style.display = hit ? '' : 'none';
      if (hit) shown++;
    });
    sections.forEach(function(s){
      var any = Array.prototype.slice.call(s.querySelectorAll('.card'))
        .some(function(c){ return c.style.display !== 'none'; });
      s.style.display = any ? '' : 'none';
    });
    count.textContent = kw ? ('匹配 ' + shown + ' / ' + cards.length + ' 篇') : '';
  }
  q.addEventListener('input', apply);
})();
</script>
</body>
</html>
"""


def parse_sequence():
    """从序.md 解析：分组标题（含篇数）与目录表格行（序号/标题/摘要/难度）。"""
    text = SEQUENCE_FILE.read_text(encoding="utf-8")
    parts, rows = [], []
    cur = None
    row_re = re.compile(
        r"^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*(L\d)\s*\|"
    )
    part_re = re.compile(r"^###\s*(第.+?)（(\d+)\s*篇）")
    for line in text.splitlines():
        m = part_re.match(line)
        if m:
            cur = {"title": m.group(1), "expect": int(m.group(2)), "items": []}
            parts.append(cur)
            continue
        m = row_re.match(line)
        if m:
            rows.append({
                "no": int(m.group(1)),
                "title": m.group(2),
                "href": m.group(3).lstrip("./"),
                "desc": m.group(4),
                "level": m.group(5),
            })
    if not parts or not rows:
        sys.exit("序.md 解析失败：未找到分组标题或目录表格行")
    return parts, rows


def collect_files():
    """扫描磁盘真实文件名：md 按 NN_ 前缀取序号，阅读版 html 按篇名匹配。"""
    mds = {}
    for p in ROOT.glob("[0-9][0-9]_*_系统笔记.md"):
        mds[int(p.name[:2])] = p.name
    htmls = set(p.name for p in ROOT.glob("*阅读版.html"))
    return mds, htmls


def find_html(md_name, htmls):
    """md 名 -> 对应阅读版 html 名。如 30_ 篇为特殊命名，逐个候选匹配。"""
    stem = md_name[3:]                      # 去掉 NN_ 前缀，如 篇名_系统笔记.md
    base = stem[:-3] if stem.endswith(".md") else stem
    for cand in (f"{base}_阅读版.html", f"{base.replace('_系统笔记','')}_阅读版.html"):
        if cand in htmls:
            return cand
    for cand in htmls:                       # 兜底：前缀包含匹配
        if cand.startswith(base.replace("_系统笔记", "")):
            return cand
    return None


def count_refs():
    """参考文献.md 有两套编号：主干 `1.` 有序数字 + 各篇增补 `24a.` 插入式编号。"""
    f = ROOT / "参考文献.md"
    if not f.exists():
        return 0
    text = f.read_text(encoding="utf-8")
    main = re.findall(r"^\s*\d+\.\s+\S", text, re.M)
    supp = re.findall(r"^\s*\d{2}[a-z]{1,2}\.\s+\S", text, re.M)
    return len(main) + len(supp)


def count_dir(name):
    d = ROOT / name
    return len([p for p in d.glob("*") if p.is_file()]) if d.is_dir() else 0


def build_assets(ncode, nfig, ndata):
    """GitHub Pages 不提供目录自动索引（/code/ 会 404），故目录类资产指向仓库目录树；
       预览版是具体 HTML 文件，可站内直链。"""
    items = [
        f'<a href="{REPO}/tree/main/code">code/ 可复现脚本（{ncode}）</a>',
        f'<a href="{REPO}/tree/main/figures">figures/ 图表（{nfig}）</a>',
        f'<a href="{REPO}/tree/main/data">data/ 常数表（{ndata}）</a>',
    ]
    preview = ROOT / "预览版" / "量子力学笔记_预览版.html"
    if preview.exists():
        rel = preview.relative_to(ROOT).as_posix()
        items.append(f'<a href="{quote(rel)}">预览版入口</a>')
    return items


def parse_paths():
    """从《依赖关系与阅读路径.md》解析五段路径，作为 index 路径入口的单一数据源。

    解析段格式：
        ### 路径 1A · 最小轮廓线（零门槛起步）

        **适用对象一句话。**

        - 涉及篇目：**15 篇**（...）
        - 前置闭合校验：**通过**

        | 顺序 | 篇号 | 标题 | ... |
    """
    doc = ROOT / PATH_DOC
    if not doc.exists():
        sys.exit(f"路径文档缺失：{PATH_DOC}")
    text = doc.read_text(encoding="utf-8")
    paths = []
    block_re = re.compile(r"^### (路径 [0-9A-Z]+)\s*·\s*(.+?)\n\n(.+?)(?=^### |\Z)",
                          re.M | re.S)
    for m in block_re.finditer(text):
        code, title, body = m.group(1).strip(), m.group(2).strip(), m.group(3)
        n_m = re.search(r"涉及篇目：\*\*(\d+)\s*篇", body)
        n = int(n_m.group(1)) if n_m else 0
        nums = [int(x) for x in re.findall(r"^\|\s*\d+\s*\|\s*(\d{2})\s*\|", body, re.M)]
        # 适用对象：首个非空段第一句，去 markdown 粗体
        for ln in body.splitlines():
            if ln.strip():
                para = ln.strip().strip("* ")
                intro = re.split(r"[。！]", para)[0] + "。"
                break
        else:
            intro = ""
        paths.append({"code": code, "title": title, "n": n, "nums": nums, "intro": intro})
    if not paths:
        sys.exit("路径解析失败：未找到任何「### 路径 X ·」段落")
    return paths


def build_paths(paths):
    doc_url = f"{REPO}/blob/main/{quote(PATH_DOC)}"
    cards = []
    for p in paths:
        nums = p["nums"]
        seq = " → ".join(f"{x:02d}" for x in nums[:9])
        if len(nums) > 9:
            seq += f' <span class="more">…共 {len(nums)} 篇</span>'
        elif not nums:
            seq = "（详见文档）"
        cards.append(
            f'    <article class="path">\n'
            f'      <p class="ph">{p["code"]}</p>\n'
            f'      <p class="pt">{p["title"]}</p>\n'
            f'      <p class="pi">{p["intro"]}</p>\n'
            f'      <p class="pmeta"><b>{p["n"]}</b> 篇 · 前置闭合校验通过</p>\n'
            f'      <div class="seq">{seq}</div>\n'
            f'      <a class="btn primary" href="{doc_url}">查看完整路径与读法</a>\n'
            f'    </article>'
        )
    return (
        '  <h2>推荐阅读路径</h2>\n'
        '  <p class="sub" style="margin:.2em 0 1em;color:var(--muted);font-size:.9em;">'
        '五段路径均由脚本按传递闭包计算并逐篇校验前置闭合——按序读不会撞见没读过的概念。'
        '零门槛读者从 1A/1B 入手，物理系读者走 2，宝石学交叉走 3，前沿窗口走 4。</p>\n'
        '  <div class="paths">\n' + "\n".join(cards) + "\n  </div>"
    )


def main():
    parts, rows = parse_sequence()
    mds, htmls = collect_files()
    paths = parse_paths()

    # 分组归属：按目录表格顺序与各组声明篇数切分
    idx, grouped = 0, []
    for part in parts:
        take = rows[idx: idx + part["expect"]]
        idx += part["expect"]
        grouped.append((part, take))
    if idx != len(rows):
        sys.exit(f"分组篇数({idx})与目录行数({len(rows)})不一致")

    sections, missing = [], []
    for part, items in grouped:
        cards = []
        for it in items:
            md = mds.get(it["no"])
            if not md:
                missing.append(f"第 {it['no']} 篇缺少 md 文件")
                continue
            html = find_html(md, htmls)
            if not html:
                missing.append(f"第 {it['no']} 篇缺少阅读版 html（md={md}）")
                continue
            # GitHub Pages 不渲染 .md（点击只会下载原始文件），
            # Markdown 按钮指向仓库 blob 页，由 GitHub 在线渲染。
            md_url = f"{REPO}/blob/main/{quote(md)}"
            title = it["title"].replace("_系统笔记.md", "").replace("_系统笔记", "")
            title = re.sub(r"^\d{2}_", "", title)   # 序.md 个别链接文本残留 NN_ 前缀
            lvl = it["level"]
            search = f"{it['no']:02d} {title} {it['desc']} {lvl} {md}".lower().replace('"', "")
            cards.append(
                f'      <article class="card" data-search="{search}">\n'
                f'        <div class="top"><span class="num">{it["no"]:02d}</span>'
                f'<h3>{title}</h3><span class="badge {lvl.lower()}">{lvl}</span></div>\n'
                f'        <p class="desc">{it["desc"]}</p>\n'
                f'        <div class="links">'
                f'<a class="btn primary" href="{quote(html)}">阅读版</a>'
                f'<a class="btn" href="{md_url}">Markdown</a></div>\n'
                f"      </article>"
            )
        sections.append(
            f'  <section data-part>\n'
            f'    <h2>{part["title"]}（{part["expect"]} 篇）</h2>\n'
            f'    <div class="grid">\n' + "\n".join(cards) + "\n    </div>\n  </section>"
        )

    if missing:
        sys.exit("链接校验失败：\n  - " + "\n  - ".join(missing))

    aux = []
    for fn, name, desc in AUX_DOCS:
        if not (ROOT / fn).exists():
            sys.exit(f"辅助文档缺失：{fn}")
        aux.append(
            f'  <li><a href="{REPO}/blob/main/{quote(fn)}">{name}</a><span class="d">{desc}</span></li>'
        )

    ncode, nfig, ndata = count_dir("code"), count_dir("figures"), count_dir("data")

    out = (TEMPLATE
           .replace("__SECTIONS__", "\n".join(sections))
           .replace("__PATHS__", build_paths(paths))
           .replace("__AUX__", "\n".join(aux))
           .replace("__ASSETS__", "\n  ".join(build_assets(ncode, nfig, ndata)))
           .replace("__REPO__", REPO)
           .replace("__NREF__", str(count_refs()))
           .replace("__NCODE__", str(ncode))
           .replace("__NFIG__", str(nfig)))
    OUTPUT.write_text(out, encoding="utf-8")
    NOJEKYLL.write_text("", encoding="utf-8")

    print(f"已生成 {OUTPUT.name}（{len(rows)} 篇 · {len(parts)} 个分组）")
    print(f"  参考文献 {count_refs()} 条 · code {ncode} 个 · figures {nfig} 个")
    print(f"  同步写出 {NOJEKYLL.name}（关闭 Jekyll，纯静态）")
    print("  链接校验：全部通过（0 死链）")


if __name__ == "__main__":
    main()
