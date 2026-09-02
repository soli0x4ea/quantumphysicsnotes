# -*- coding: utf-8 -*-
# P1 整改：把脚本中与 data/constants_2018.json 逐位一致的硬编码常数
# 替换为 C["键"] 引用（tokenize 级替换，字符串与注释不动），然后重跑 diff 验证。
import glob, io, os, subprocess, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'code'))
from constants import C  # noqa: E402

PY = sys.executable
targets = []
for f in sorted(glob.glob(os.path.join(ROOT, 'code', '*.py'))):
    base = os.path.basename(f)
    if base.startswith('_') or base.startswith('build_') or base == 'constants.py':
        continue
    src = open(f, encoding='utf-8').read()
    if 'from constants import' in src:
        continue
    targets.append(f)

def patch(path):
    src = open(path, encoding='utf-8').read()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    # 值 -> 键（同一数值多键时取排序第一，常数表值互异，实际不会撞）
    val2key = {}
    for k in sorted(C):
        val2key.setdefault(C[k], k)
    repls = []
    for tok in toks:
        if tok.type != tokenize.NUMBER:
            continue
        try:
            val = float(tok.string)
        except ValueError:
            continue
        key = val2key.get(val)
        if key is None:
            continue
        repls.append((tok.start, tok.end, key))
    if not repls:
        return None
    # 从后往前替换
    lines = src.split('\n')
    for (sr, sc), (er, ec), key in sorted(repls, reverse=True):
        prefix = lines[sr - 1][:sc]
        suffix = lines[er - 1][ec:]
        lines[sr - 1] = f'{prefix}C["{key}"]{suffix}'
        # 同一行首个替换后，同行后续替换的列号会失效——按行内出现次数处理：
    # 上面按行替换对同行多个替换不安全，改用逐行重扫：
    src2 = '\n'.join(lines)
    return src2, len(repls)

def patch_line_safe(path):
    """逐 token 替换的行内多替换安全版：直接基于位置区间从后往前拼接。"""
    src = open(path, encoding='utf-8').read()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    val2key = {}
    for k in sorted(C):
        val2key.setdefault(C[k], k)
    repls = []
    for tok in toks:
        if tok.type != tokenize.NUMBER:
            continue
        try:
            val = float(tok.string)
        except ValueError:
            continue
        key = val2key.get(val)
        if key is None:
            continue
        repls.append((tok.start, tok.end, key))
    if not repls:
        return None
    # 绝对偏移：按 (row, col) 转偏移
    def off(pos):
        r, c = pos
        return line_off[r] + c
    lines = src.split('\n')
    line_off = {}
    o = 0
    for i, ln in enumerate(lines, 1):
        line_off[i] = o
        o += len(ln) + 1
    out = src
    for (s, e, key) in sorted(repls, key=lambda x: off(x[0]), reverse=True):
        out = out[:off(s)] + f'C["{key}"]' + out[off(e):]
    # 插入 import：首个 40 行内最后一个 import/from 行之后
    ls = out.split('\n')
    last_imp = None
    for i, ln in enumerate(ls[:40]):
        if ln.startswith('import ') or ln.startswith('from '):
            last_imp = i
    ins = 'from constants import C  # CODATA 2018 常数自 data/constants_2018.json 加载（本目录 constants.py）'
    if last_imp is None:
        ls.insert(0, ins)
    else:
        ls.insert(last_imp + 1, ins)
    return '\n'.join(ls), len(repls)

report = []
for f in targets:
    res = patch_line_safe(f)
    if res is None:
        continue
    new_src, n = res
    open(f, 'w', encoding='utf-8').write(new_src)
    report.append((os.path.basename(f), n))

for name, n in report:
    print(f'{name}: {n} 处替换')
print('共', len(report), '个脚本')
