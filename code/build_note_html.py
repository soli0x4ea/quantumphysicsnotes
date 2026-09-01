#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把一篇系统笔记 .md 打包成自包含的单文件 HTML 阅读器（KaTeX + marked）。
用法：
    python build_note_html.py <笔记.md> [输出.html]
输出 HTML 与 md 同级，通过相对路径引用 figures/ 下的图形资产。
"""

import sys
import os

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{
  --bg:#f4f5f7; --panel:#ffffff; --ink:#1c2024; --ink-dim:#5b6570;
  --line:#dfe3e8; --line-soft:#eef0f3; --accent:#1f5fa8; --accent-soft:#e8f0fa;
  --amber-bg:#fff8e6; --amber-line:#e5c168; --amber-ink:#6b5200;
  --green:#1c7a4a; --green-bg:#e8f5ee; --red:#b03030; --red-bg:#fdecec;
  --code-bg:#f6f7f9;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",Georgia,serif;
  background:var(--bg); color:var(--ink); line-height:1.85; font-size:16px;
  -webkit-font-smoothing:antialiased;
}
.layout{display:flex; max-width:1280px; margin:0 auto; gap:28px; padding:0 24px}
/* 侧栏目录 */
.toc{
  width:246px; flex-shrink:0; position:sticky; top:0; height:100vh;
  overflow-y:auto; padding:28px 0 40px; font-family:"Noto Sans SC","PingFang SC",sans-serif;
}
.toc h4{font-size:11px; letter-spacing:1.6px; color:var(--ink-dim); text-transform:uppercase;
  margin:0 0 12px; padding-left:2px; font-weight:600}
.toc a{
  display:block; font-size:13px; color:var(--ink-dim); text-decoration:none;
  padding:5px 10px; border-left:2px solid transparent; line-height:1.5;
}
.toc a:hover{color:var(--accent); background:var(--accent-soft)}
.toc a.sub{padding-left:24px; font-size:12.5px}
.toc a.active{color:var(--accent); border-left-color:var(--accent); background:var(--accent-soft); font-weight:600}
/* 正文 */
.main{flex:1; min-width:0; padding:28px 0 120px}
.paper{background:var(--panel); border:1px solid var(--line); border-radius:8px;
  padding:48px 56px; box-shadow:0 1px 3px rgba(16,24,40,.05)}
h1{font-size:27px; line-height:1.45; margin:0 0 18px; letter-spacing:.3px; font-weight:700}
h2{font-size:20px; margin:52px 0 18px; padding-bottom:9px; border-bottom:1.5px solid var(--ink);
  letter-spacing:.3px}
h3{font-size:16.5px; margin:32px 0 12px; color:var(--accent); font-weight:600}
h4{font-size:15px; margin:22px 0 10px; font-weight:600}
p{margin:0 0 15px; text-align:justify}
blockquote{
  margin:18px 0; padding:13px 18px; background:var(--amber-bg);
  border-left:3px solid var(--amber-line); border-radius:0 4px 4px 0; color:var(--amber-ink);
}
blockquote p{margin:0 0 8px} blockquote p:last-child{margin:0}
blockquote strong{color:#4a3800}
ul,ol{margin:0 0 15px; padding-left:26px}
li{margin:6px 0}
table{border-collapse:collapse; width:100%; margin:18px 0; font-size:14px;
  font-family:"Noto Sans SC","PingFang SC",sans-serif}
th{background:#f0f2f5; text-align:left; padding:9px 12px; border:1px solid var(--line); font-weight:600}
td{padding:9px 12px; border:1px solid var(--line); vertical-align:top}
tbody tr:nth-child(even){background:#fafbfc}
code{background:var(--code-bg); padding:2px 6px; border-radius:3px; font-size:13.5px;
  font-family:"SF Mono",Menlo,Consolas,monospace}
pre{background:var(--code-bg); padding:14px 16px; border-radius:5px; overflow-x:auto; margin:16px 0;
  border:1px solid var(--line-soft)}
pre code{background:none; padding:0}
hr{border:none; border-top:1px solid var(--line-soft); margin:34px 0}
strong{font-weight:700; color:#0f1419}
a{color:var(--accent)}
img{max-width:100%; margin:20px 0; border:1px solid var(--line); border-radius:6px; background:#fff}
.katex-display{margin:20px 0; overflow-x:auto; overflow-y:hidden; padding:2px 0}
.katex{font-size:1.045em}
.tag-note{font-family:"Noto Sans SC","PingFang SC",sans-serif; font-size:12px; color:var(--ink-dim);
  margin-top:40px; padding-top:16px; border-top:1px solid var(--line-soft); line-height:1.9}
@media(max-width:900px){
  .toc{display:none}
  .paper{padding:28px 22px}
  .layout{padding:0 12px}
}
</style>
</head>
<body>
<div class="layout">
  <nav class="toc"><h4>目录</h4><div id="toc"></div></nav>
  <main class="main"><article class="paper" id="content"></article></main>
</div>

<script type="text/plain" id="src">@@MD@@</script>
<script>
// 在 markdown 解析前抽出公式，用占位符保护，避免被 marked 当成强调语法破坏
function protectMath(src){
  var blocks = [];
  // 先抽块级 $$...$$（可跨行）
  src = src.replace(/\$\$([\s\S]+?)\$\$/g, function(m){
    blocks.push(m);
    return '%%MATH' + (blocks.length - 1) + '%%';
  });
  // 再抽行内 $...$（不含换行、内部不含 $）
  src = src.replace(/\$([^\$\n]+?)\$/g, function(m){
    blocks.push(m);
    return '%%MATH' + (blocks.length - 1) + '%%';
  });
  return { src: src, blocks: blocks };
}

function boot(){
  var raw = document.getElementById('src').textContent;
  // 记录标题锚点（在保护公式之前，避免影响）
  var md = raw.replace(/^(#{1,3})\s+(.+)$/gm, function(m, h, t){
    var id = 'h-' + t.replace(/[^\w一-龥]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40);
    return h + ' <span id="' + id + '"></span>' + t;
  });

  // 保护数学公式
  var prot = protectMath(md);
  md = prot.src;

  document.getElementById('content').innerHTML = marked.parse(md);

  // 还原数学公式占位符
  var content = document.getElementById('content');
  var html = content.innerHTML.replace(/%%MATH(\d+)%%/g, function(m, n){
    return prot.blocks[+n];
  });
  content.innerHTML = html;

  // 生成目录
  var hs = document.querySelectorAll('#content h2, #content h3');
  var toc = document.getElementById('toc'), tocHtml = '';
  hs.forEach(function(h){
    var sp = h.querySelector('span[id]');
    var id = sp ? sp.id : '';
    var cls = h.tagName === 'H3' ? 'sub' : '';
    tocHtml += '<a class="' + cls + '" href="#' + id + '">' + h.textContent.trim() + '</a>';
  });
  toc.innerHTML = tocHtml;

  // 图片路径：正文里写 figures/xxx.svg
  document.querySelectorAll('#content img').forEach(function(im){
    if(/^figures\//.test(im.getAttribute('src')||'')) return;
  });

  if (window.renderMathInElement) {
    renderMathInElement(document.getElementById('content'), {
      delimiters:[
        {left:'$$', right:'$$', display:true},
        {left:'$',  right:'$',  display:false}
      ],
      ignoredTags:['script','noscript','style','textarea','pre','code'],
      throwOnError:false
    });
  }

  // 滚动高亮
  var links = [].slice.call(toc.querySelectorAll('a'));
  window.addEventListener('scroll', function(){
    var cur = null;
    hs.forEach(function(h){
      if (h.getBoundingClientRect().top < 120) cur = h;
    });
    links.forEach(function(a){ a.classList.remove('active'); });
    if (cur){
      var sp = cur.querySelector('span[id]');
      var act = toc.querySelector('a[href="#' + (sp?sp.id:'') + '"]');
      if (act) act.classList.add('active');
    }
  }, {passive:true});
}
if (window.marked) boot();
else window.addEventListener('load', boot);
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        print("用法: python build_note_html.py <笔记.md> [输出.html]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".html"

    with open(src, encoding="utf-8") as f:
        md = f.read()

    title = md.lstrip().split("\n", 1)[0].replace("#", "").strip()
    # 防止 md 中出现 </script 提前闭合脚本块
    md = md.replace("</script", "<\\/script")

    # 用占位符替换而非 str.format，避免与 CSS/JS 中的花括号冲突
    html = TEMPLATE.replace("@@TITLE@@", title).replace("@@MD@@", md)

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("已生成：%s" % out)
    print("标题：%s" % title)
    print("字数：%d" % len(md))


if __name__ == "__main__":
    main()
