# -*- coding: utf-8 -*-
# P1 现状扫描：47篇 × P1各项（①–⑪）完成度
import re, glob, os, json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
notes = sorted(glob.glob('[0-9][0-9]_*.md'))
notes = [n for n in notes if not n.startswith('README')]

rows = []
for fp in notes:
    num = fp[:2]
    with open(fp, encoding='utf-8') as f:
        t = f.read()
    # P1-② 版本行（含变体）
    ver = bool(re.search(r'本篇版本[:：]', t))
    ver_v = re.search(r'本篇版本[:：]\s*v([0-9.]+)', t)
    ver_str = ver_v.group(1) if ver_v else ('?' if ver else '—')
    # P1-⑩ 中文括号编号（24xx）残留（排除"第 N 篇"类）
    cn_paren = len(re.findall(r'（(24[a-z]{2})）', t))
    # [24xx] 方括号编号体系
    sq_refs = set(re.findall(r'\[(24[a-z]{2})\]', t))
    # 第八节内容
    sec8 = re.search(r'(?:^|\n)##\s*八[、.．:：\s].*?(?=\n\*\*?本篇版本|\Z)', t, re.S)
    sec8_t = sec8.group(0) if sec8 else ''
    # S/A/B 分组标记（第八节内出现 S 级/A 级/B 级字样）
    sab = bool(re.search(r'[SAB]\s*[级类]', sec8_t))
    # 第八节 [已核实] 标记
    verified = len(re.findall(r'\[已核实\]|`已核实`', sec8_t))
    # 更新句（含变体）
    upd = bool(re.search(r'本[节篇][内内容]*[^。]*随[^。]*(研究|领域|观测)[^。]*更新', t))
    upd_quote = upd and bool(re.search(r'>\s*[^\n]*随[^\n]*更新', t))
    # \tag{} 公式编号数
    tags = len(re.findall(r'\\tag\{[^}]+\}', t))
    # 判据条目
    crit = bool(re.search(r'量子效应[^。\n]{0,10}(显著|明显)[^。\n]{0,6}(的)?判据|效应显著[^。\n]{0,4}判据|相对论效应[^。\n]{0,10}判据', t))
    # 头部验证依据行
    basis = re.search(r'验证依据[:：]\s*([^\n]+)', t)
    basis_str = basis.group(1)[:50] if basis else '—'

    rows.append({
        'num': num, 'file': fp, 'ver': ver_str, 'cn_paren': cn_paren,
        'n_sq': len(sq_refs), 'sab': sab, 'verified': verified,
        'upd': upd, 'upd_quote': upd_quote, 'tags': tags, 'crit': crit,
        'basis': basis_str,
    })

print(f"{'篇':<3}{'版本':<6}{'(24xx)':<7}{'[24xx]':<7}{'S/A/B':<6}{'已核实':<7}{'更新句':<6}{'引号':<5}{'tag':<5}{'判据':<5}")
for r in rows:
    print(f"{r['num']:<3}{r['ver']:<6}{r['cn_paren']:<7}{r['n_sq']:<7}{str(r['sab']):<6}{r['verified']:<7}{str(r['upd']):<6}{str(r['upd_quote']):<5}{r['tags']:<5}{str(r['crit']):<5}")

print()
print('=== 分组统计 ===')
sq_notes = [r['num'] for r in rows if r['n_sq'] > 0]
ay_notes = [r['num'] for r in rows if r['n_sq'] == 0]
print(f'编号体系篇（{len(sq_notes)}）: {" ".join(sq_notes)}')
print(f'作者-年份篇（{len(ay_notes)}）: {" ".join(ay_notes)}')
print()
print('无版本行:', ' '.join(r['num'] for r in rows if r['ver'] == '—'))
print('v1.1 篇:', ' '.join(r['num'] for r in rows if r['ver'] == '1.1'))
print('中文括号(24xx)残留:', ' '.join(f"{r['num']}({r['cn_paren']})" for r in rows if r['cn_paren'] > 0))
print('第八节无S/A/B分组:', ' '.join(r['num'] for r in rows if not r['sab']))
print('第八节无[已核实]:', ' '.join(r['num'] for r in rows if r['verified'] == 0))
print('无更新句:', ' '.join(r['num'] for r in rows if not r['upd']))
print('更新句非blockquote:', ' '.join(r['num'] for r in rows if r['upd'] and not r['upd_quote']))
print('tag=0 篇:', ' '.join(r['num'] for r in rows if r['tags'] == 0))
print('tag<5 篇:', ' '.join(f"{r['num']}({r['tags']})" for r in rows if 0 < r['tags'] < 5))
print('无判据条目(42-47):', ' '.join(r['num'] for r in rows if r['num'] in ('42','43','44','45','46','47','37','38') and not r['crit']))
