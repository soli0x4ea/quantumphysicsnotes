# -*- coding: utf-8 -*-
"""
量子力学笔记预览版生成器
========================
复用《GemologyNotes-iOS-v2》的内容框架（content_data.json 六分类 + 侧栏 + 锁定 +
属性面板 + 明暗双主题），把《量子力学正式版》的 47 篇目录与已完成正文
编译为单文件 HTML 预览版。

视觉令牌 1:1 取自 GemologyNotes/Theme.swift（light/dark 两套 CSS 变量）；
侧栏结构对齐 SidebarView.swift（分类标题 + 计数徽标 + 圆点 + 徽标 + 锁定行）；
属性面板对齐 CrystalPanelView 的 crystal-info 布局。

用法：
    python3 build_preview_app.py
输出：
    ../预览版/量子力学笔记_预览版.html
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 量子力学正式版/
OUT_DIR = ROOT / "预览版"
OUT_FILE = OUT_DIR / "量子力学笔记_预览版.html"

# 已完成的正文（当前仅第 30 篇；后续每完成一篇，加入此表即可出现在侧栏可读区）
COMPLETED = {
    30: {
        "md": ROOT / "EPR佯谬与贝尔不等式_系统笔记.md",
        "props": {
            "数学程度": "L2（运算层）",
            "所属部分": "第四部分 量子信息与量子光学",
            "前置依赖": "第 9、11、16、29 篇",
            "定域隐变量界": "|S| ≤ 2（CHSH, 1969）",
            "量子力学上限": "2√2 ≈ 2.828427（Tsirelson 界）",
            "关键实验": "Aspect 1982：S = 2.697 ± 0.015",
            "漏洞闭合": "Hensen et al. 2015（Nature 526, 682）",
            "验证脚本": "code/EPR与Bell不等式_CHSH.py",
        },
    },
}

AUX_FILES = [
    ("序.md", "序"),
    ("量子力学系统笔记整理规范.md", "整理规范"),
    ("参考文献.md", "参考文献"),
    ("修订记录.md", "修订记录"),
    ("README.md", "README"),
]

# 六部分侧栏圆点色（对齐宝石学条目 color 字段的用途）
PART_COLORS = ["#4a9eff", "#9d7fe8", "#4fc08d", "#e8a84c", "#e86e5a", "#c9a84c"]


# ---------------------------------------------------------------- 目录解析

ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.+)\|\s*(.+?)\s*\|\s*(L\d)\s*\|\s*$")
LINK_RE = re.compile(r"^\s*\[(.+?)\]\(.+?\)\s*$")
HEAD_RE = re.compile(r"^###\s*(第[一二三四五六]部分)：(.+?)（(\d+)\s*篇）\s*$")


def parse_catalog(seq_md: str):
    """解析《序.md》目录 → [{title, count, notes:[{id,title,desc,level,done}]}]"""
    parts, cur = [], None
    for line in seq_md.splitlines():
        m = HEAD_RE.match(line.strip())
        if m:
            cur = {"title": m.group(2), "count": int(m.group(3)), "notes": []}
            parts.append(cur)
            continue
        m = ROW_RE.match(line.strip())
        if m and cur is not None:
            nid = int(m.group(1))
            cell = m.group(2)
            lm = LINK_RE.match(cell)
            done = lm is not None
            title = lm.group(1) if lm else cell.strip()
            cur["notes"].append({
                "id": nid,
                "title": title,
                "desc": m.group(3).strip(),
                "level": m.group(4),
                "done": done,
            })
    return parts


def build_sidebar(parts):
    """组装侧栏数据（对齐 content_data.json 的分类语义）"""
    cats = []
    for i, p in enumerate(parts):
        color = PART_COLORS[i % len(PART_COLORS)]
        files = []
        for n in p["notes"]:
            files.append({
                "file": f"note-{n['id']}",
                "name": f"{n['id']} · {n['title']}",
                "color": color,
                "level": n["level"],
                "done": n["done"] and (n["id"] in COMPLETED),
                "planned": n["done"] and not (n["id"] in COMPLETED),
                "desc": n["desc"],
                "part": i + 1,
            })
        open_n = sum(f["done"] for f in files)
        cats.append({
            "title": p["title"], "files": files,
            "countText": f"{open_n}/{len(files)}篇", "kind": "part",
        })
    aux = [{"file": f, "name": nm, "done": True, "kind": "aux"}
           for f, nm in AUX_FILES]
    cats.append({"title": "辅助文档", "files": aux,
                 "countText": f"{len(aux)}篇", "kind": "aux"})
    return cats


# ---------------------------------------------------------------- 内容嵌入

def load_article(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_figures() -> dict:
    """已完成笔记引用的 SVG 全部内联（预览版单文件，无外部依赖）"""
    figs = {}
    fig_dir = ROOT / "figures"
    if fig_dir.exists():
        for p in sorted(fig_dir.glob("*.svg")):
            figs[p.name] = p.read_text(encoding="utf-8")
    return figs


def json_safe(s: str) -> str:
    return s.replace("</", "<\\/")


# ---------------------------------------------------------------- HTML 模板

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>量子力学系统笔记 · 预览版</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
/* ===== 设计令牌：1:1 取自 GemologyNotes/Theme.swift ===== */
:root{
  --bg:#f7f5ef; --bg2:#ffffff; --bg3:#f0ece0; --bg4:#e4ddc8; --border:#d4cdb8;
  --gold:#a07c28; --gold2:#8a6520; --gold-dim:#b89848;
  --text:#2c2a25; --text-dim:#6b6659; --text-bright:#1a1814;
  --accent:#2563b8; --badge-blue-bg:rgba(37,99,184,.13);
  --purple:#a080c0;
  --crystal-bg1:#e8e2d0; --crystal-bg2:#d4ccb4; --ci-bg:rgba(255,253,246,.96);
  --overlay:rgba(0,0,0,.35); --shadow:rgba(0,0,0,.12);
}
[data-theme="dark"]{
  --bg:#1a1a1a; --bg2:#222222; --bg3:#2d2d2d; --bg4:#383838; --border:#404040;
  --gold:#c9a84c; --gold2:#e8c968; --gold-dim:#8a7235;
  --text:#d8d8d8; --text-dim:#909090; --text-bright:#f0f0f0;
  --accent:#4a9eff; --badge-blue-bg:rgba(74,158,255,.15);
  --purple:#a080c0;
  --crystal-bg1:#141414; --crystal-bg2:#1e1e1e; --ci-bg:rgba(26,26,26,.92);
  --overlay:rgba(0,0,0,.55); --shadow:rgba(0,0,0,.5);
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",Georgia,serif;
  background:var(--bg); color:var(--text); line-height:1.85; font-size:16px;
  -webkit-font-smoothing:antialiased;
}
button{font-family:inherit;cursor:pointer}
.app{display:flex;min-height:100vh}

/* ===== 侧栏（对齐 SidebarView：宽 260，分类标题金暗色 + 计数徽标） ===== */
.sidebar{
  width:260px;flex-shrink:0;background:var(--bg2);
  border-right:.5px solid var(--border);
  height:100vh;position:sticky;top:0;overflow-y:auto;
  display:flex;flex-direction:column;
  font-family:"Noto Sans SC","PingFang SC",sans-serif;
  padding:14px 0 6px;
}
.sidebar-scroll{flex:1;overflow-y:auto;padding:2px 0 10px}
.cat{padding:10px 0}
.cat-title{
  display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:0 16px 6px;
  font-size:11px;font-weight:600;color:var(--gold-dim);
  letter-spacing:2px;
}
.cat-count{
  font-size:10px;color:var(--text-dim);letter-spacing:0;
  padding:1px 6px;background:var(--bg4);border-radius:99px;
}
.nav-item{
  display:flex;align-items:center;gap:8px;width:100%;
  padding:7px 16px;border:none;background:none;text-align:left;
  color:var(--text-dim);font-size:13px;line-height:1.5;
  position:relative;
}
.nav-item .dot{
  width:8px;height:8px;border-radius:50%;flex-shrink:0;
  background:var(--dot,#b8e2ff);
}
.nav-item .nm{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nav-item .badge{
  font-size:9px;padding:1px 5px;border-radius:3px;flex-shrink:0;
  color:var(--accent);background:var(--badge-blue-bg);
}
.nav-item .badge.lvl{color:var(--purple);background:rgba(160,128,192,.12)}
.nav-item .lock{font-size:9px;opacity:.8;flex-shrink:0}
.nav-item.open{opacity:1}
.nav-item:not(.open){opacity:.35;cursor:default}
.nav-item.current{background:var(--bg3)}
.nav-item.current::before{
  content:"";position:absolute;left:0;top:0;bottom:0;
  width:3px;background:var(--gold);
}
.side-footer{
  border-top:.5px solid var(--border);
  padding:10px 16px;display:flex;align-items:center;gap:8px;
  color:var(--text-dim);font-size:12px;background:none;border-left:none;border-right:none;border-bottom:none;
  width:100%;
}
.side-footer .chev{margin-left:auto;font-size:9px}

/* ===== 正文区 ===== */
.doc-area{flex:1;min-width:0;overflow-y:auto;height:100vh}
.doc-inner{max-width:860px;margin:0 auto;padding:36px 34px 90px}

/* 属性面板（对齐 CrystalPanelView 的 crystal-info：金标题 + 属性键值网格） */
.crystal-panel{
  background:linear-gradient(180deg,var(--crystal-bg1),var(--crystal-bg2));
  border-radius:12px;padding:18px 20px 14px;margin-bottom:30px;
}
.ci-title{
  font-size:15px;font-weight:700;color:var(--gold);letter-spacing:1px;
  padding-bottom:8px;margin-bottom:10px;
  border-bottom:1px solid var(--gold-dim);
  display:flex;align-items:baseline;gap:8px;
}
.ci-title .ci-sub{font-size:11px;font-weight:400;color:var(--text-dim);letter-spacing:0}
.ci-grid{display:grid;grid-template-columns:auto 1fr;gap:4px 16px}
.ci-k{font-size:12px;color:var(--text-dim);white-space:nowrap;font-family:"Noto Sans SC","PingFang SC",sans-serif}
.ci-v{font-size:13px;color:var(--text);min-width:0}

/* 正文排版（金色标题体系对齐宝石学源码 index.html） */
.doc h1{font-size:24px;color:var(--gold);font-weight:700;line-height:1.5;margin:6px 0 18px}
.doc h2{
  font-size:20px;color:var(--gold2);margin:46px 0 16px;padding-bottom:9px;
  border-bottom:1.5px solid var(--gold-dim);letter-spacing:.3px;
}
.doc h3{font-size:17px;color:var(--text-bright);margin:32px 0 12px}
.doc h4{font-size:15px;color:var(--text-bright);margin:24px 0 10px}
.doc p{margin:12px 0}
.doc strong{color:var(--gold2);font-weight:700}
.doc blockquote{
  border-left:3px solid var(--gold);background:var(--bg2);
  padding:12px 18px;margin:16px 0;border-radius:0 8px 8px 0;color:var(--text);
}
.doc blockquote p{margin:6px 0}
.doc ul,.doc ol{padding-left:26px;margin:12px 0}
.doc li{margin:5px 0}
.doc code{
  font-family:"SF Mono",Menlo,Consolas,monospace;font-size:.86em;
  color:var(--accent);background:var(--bg3);padding:2px 6px;border-radius:4px;
}
.doc pre{
  background:var(--bg3);border:1px solid var(--border);border-radius:8px;
  padding:14px 16px;overflow-x:auto;margin:14px 0;
}
.doc pre code{background:none;color:var(--text);padding:0}
.doc table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px}
.doc th{background:var(--bg3);color:var(--text-bright);font-weight:600}
.doc th,.doc td{border:1px solid var(--border);padding:7px 11px;text-align:left;line-height:1.6}
.doc tr:nth-child(even) td{background:var(--bg2)}
.doc hr{border:none;border-top:1px solid var(--border);margin:30px 0}
.doc a{color:var(--accent);text-decoration:none}
.doc img{max-width:100%;height:auto}
.fig-slot{margin:18px 0;text-align:center}
.fig-slot svg{max-width:100%;height:auto;background:#fff;border-radius:8px}
[data-theme="dark"] .fig-slot svg{background:#ffffff}

/* 空态（对齐 ArticleView 的空态布局） */
.empty-state{
  min-height:60vh;display:flex;flex-direction:column;gap:12px;
  align-items:center;justify-content:center;text-align:center;padding:40px 20px;
}
.empty-state .icon{font-size:44px;color:var(--gold);line-height:1}
.empty-state .t1{font-size:22px;color:var(--text-bright)}
.empty-state .t2{font-size:13px;color:var(--text-dim);max-width:520px;line-height:1.9}

/* 移动端抽屉（对齐 RootView：<900pt 抽屉 280 + backdrop） */
.hamburger{
  display:none;position:fixed;top:14px;left:14px;z-index:40;
  width:38px;height:38px;border-radius:9px;border:1px solid var(--border);
  background:var(--bg2);color:var(--gold);font-size:17px;line-height:1;
}
.backdrop{display:none}
@media (max-width:900px){
  .hamburger{display:block}
  .sidebar{
    position:fixed;left:0;top:0;bottom:0;height:100%;z-index:50;
    width:280px;transform:translateX(-102%);transition:transform .25s ease;
    border-radius:0 16px 16px 0;
  }
  .sidebar.show{transform:translateX(0)}
  .backdrop.show{
    display:block;position:fixed;inset:0;background:var(--overlay);z-index:45;
  }
  .doc-area{height:auto;overflow:visible}
  .doc-inner{padding:64px 18px 80px}
}
</style>
</head>
<body>
<script type="application/json" id="content-data">@@DATA@@</script>

<button class="hamburger" id="hamburger" aria-label="打开侧边栏">☰</button>
<div class="backdrop" id="backdrop"></div>

<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-scroll" id="nav"></div>
    <button class="side-footer" id="themeBtn">
      <span id="themeIcon">◐</span><span id="themeLabel">切换明暗主题</span>
      <span class="chev">▸</span>
    </button>
  </aside>
  <main class="doc-area"><div class="doc-inner" id="doc"></div></main>
</div>

<script>
"use strict";
const DATA = JSON.parse(document.getElementById("content-data").textContent);

/* ===== 主题（持久化，对齐 gemThemeDark 语义） ===== */
const THEME_KEY = "qmThemeDark";
function applyTheme(dark){
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  document.getElementById("themeIcon").textContent = dark ? "☾" : "☀";
  try{ localStorage.setItem(THEME_KEY, dark ? "1" : "0"); }catch(e){}
}
let dark = false;
try{ dark = localStorage.getItem(THEME_KEY) === "1"; }catch(e){}
applyTheme(dark);
document.getElementById("themeBtn").onclick = () => { dark = !dark; applyTheme(dark); };

/* ===== 侧栏（对齐 SidebarView 行为：锁定行不可点、当前行金条高亮） ===== */
let currentFile = null;
const nav = document.getElementById("nav");
const sidebar = document.getElementById("sidebar");
const backdrop = document.getElementById("backdrop");

function closeDrawer(){ sidebar.classList.remove("show"); backdrop.classList.remove("show"); }
document.getElementById("hamburger").onclick = () => {
  sidebar.classList.toggle("show"); backdrop.classList.toggle("show");
};
backdrop.onclick = closeDrawer;

function renderNav(){
  let html = "";
  for(const cat of DATA.cats){
    html += `<div class="cat"><div class="cat-title"><span>${cat.title}</span><span class="cat-count">${cat.countText}</span></div>`;
    for(const f of cat.files){
      const open = !!f.done;
      const isCurrent = currentFile === f.file;
      let badge = "";
      if(f.done) badge = `<span class="badge">已撰</span>`;
      else if(f.planned) badge = `<span class="badge lvl">${f.level}</span>`;
      html += `<button class="nav-item ${open?"open":""} ${isCurrent?"current":""}"
        data-file="${f.file}" ${open?`data-open="1"`:""} style="--dot:${f.color||"#b8e2ff"}">
        <span class="dot"></span><span class="nm">${f.name}</span>
        ${badge}${open?"":`<span class="lock">🔒</span>`}</button>`;
    }
    html += `</div>`;
  }
  nav.innerHTML = html;
  nav.querySelectorAll(".nav-item[data-open]").forEach(el=>{
    el.onclick = () => { openArticle(el.dataset.file); closeDrawer(); };
  });
}

/* ===== 渲染（对齐 ContentService.mdContent + MarkdownBodyView 管线） ===== */
const doc = document.getElementById("doc");

function esc(s){ const d=document.createElement("div"); d.textContent=s; return d.innerHTML; }

function renderProps(file){
  const p = (DATA.props||{})[file];
  if(!p) return "";
  const rows = Object.entries(p).map(([k,v])=>
    `<div class="ci-k">${esc(k)}</div><div class="ci-v">${esc(v)}</div>`).join("");
  return `<div class="crystal-panel"><div class="ci-title">关键数值与定位
    <span class="ci-sub">crystal-info 对位面板</span></div>
    <div class="ci-grid">${rows}</div></div>`;
}

function renderArticle(file){
  const md = DATA.articles[file];
  const meta = DATA.meta[file] || {};
  if(md == null){
    const desc = meta.desc ? `<div class="t2">规划内容：${esc(meta.desc)}</div>` : "";
    doc.innerHTML = `<div class="empty-state"><div class="icon">📖</div>
      <div class="t1">本篇尚未撰写</div>${desc}
      <div class="t2">条目位置：第 ${meta.part||"—"} 部分 · 第 ${meta.id||"—"} 篇 · 数学程度 ${meta.level||"—"}<br>
      撰写进度见《序》卷尾：${DATA.progress}</div></div>`;
    return;
  }
  doc.innerHTML = `<div class="doc" id="mdhost">${renderProps(file)}</div>`;
  const host = document.getElementById("mdhost");
  host.insertAdjacentHTML("beforeend", marked.parse(md));
  // 内联图形：figures/*.svg 全部嵌入（对齐 figures 资产）
  host.querySelectorAll('img[src^="figures/"]').forEach(img=>{
    const name = img.getAttribute("src").slice("figures/".length);
    const svg = DATA.figures[name];
    if(svg){
      const slot = document.createElement("div");
      slot.className = "fig-slot";
      slot.innerHTML = svg;
      img.replaceWith(slot);
    }
  });
  // 内部跳转链接（./xxx.md 形式）→ 侧栏条目
  host.querySelectorAll('a[href$=".md"]').forEach(a=>{
    const target = decodeURIComponent(a.getAttribute("href").split("/").pop());
    const hit = DATA.cats.flatMap(c=>c.files).find(f=>f.file===target);
    if(hit && hit.done){ a.onclick=(e)=>{e.preventDefault(); openArticle(hit.file);}; }
    else { a.style.opacity=".55"; a.title="该条目尚未收录"; }
  });
  // 公式渲染（KaTeX auto-render，含 \tag 与 \text{中文}）
  const boot = ()=>{
    if(window.renderMathInElement){
      renderMathInElement(host,{
        delimiters:[
          {left:"$$",right:"$$",display:true},
          {left:"$",right:"$",display:false},
          {left:"\\(",right:"\\)",display:false},
        ],
        throwOnError:false, strict:"ignore",
      });
    }
  };
  window.katex ? boot() : window.addEventListener("load", boot);
  doc.parentElement.scrollTop = 0;
}

function openArticle(file){
  currentFile = file;
  renderNav();
  renderArticle(file);
}

/* ===== 启动（对齐 RootView：默认打开第一篇已完成条目） ===== */
renderNav();
const first = DATA.cats.flatMap(c=>c.files).find(f=>f.done);
if(first) openArticle(first.file);
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- 主流程

def main():
    seq_md = load_article(ROOT / "序.md")
    parts = parse_catalog(seq_md)
    total = sum(len(p["notes"]) for p in parts)
    done_ids = sorted(COMPLETED)
    assert total == 47, f"目录解析异常：{total} 篇（期望 47）"

    cats = build_sidebar(parts)

    articles = {}
    meta = {}
    for cat in cats:
        for f in cat["files"]:
            if f.get("kind") == "aux":
                src = ROOT / f["file"]
                if src.exists():
                    articles[f["file"]] = load_article(src)
                else:
                    articles[f["file"]] = f"（缺失文件：{f['file']}）"
                f["color"] = "#c9a84c"
            elif f["done"]:
                conf = COMPLETED[f["id"] if "id" in f else 30]
                # note-* 命名：id 从 file 提取
                nid = int(f["file"].split("-")[1])
                conf = COMPLETED[nid]
                articles[f["file"]] = load_article(conf["md"])
                meta[f["file"]] = {
                    "part": f.get("part"), "id": nid,
                    "level": f.get("level"), "desc": f.get("desc"),
                }
    # 侧栏数据里去掉内部字段（kind/planned 保留供 JS 用）
    props = {}
    for nid, conf in COMPLETED.items():
        props[f"note-{nid}"] = conf["props"]

    data = {
        "cats": cats,
        "articles": articles,
        "figures": load_figures(),
        "props": props,
        "meta": meta,
        "progress": f"{len(done_ids)} / {total} 篇",
    }

    html = (TEMPLATE
            .replace("@@DATA@@", json_safe(json.dumps(data, ensure_ascii=False)))
            .replace("@@TITLE@@", "量子力学系统笔记 · 预览版"))

    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    size_kb = OUT_FILE.stat().st_size // 1024
    print(f"已生成：{OUT_FILE}")
    print(f"篇目：{total} | 已嵌入正文：{sorted(COMPLETED)} | 辅助文档：{len(AUX_FILES)}")
    print(f"内联图形：{len(data['figures'])} 个 SVG | 体积：{size_kb} KB")


if __name__ == "__main__":
    main()
