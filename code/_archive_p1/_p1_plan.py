# -*- coding: utf-8 -*-
# P1 迁移方案生成：26 篇作者-年份篇 每条目 → (编号, S/A/B级别, 已核实)
# 输出 code/_p1_full_plan.json + 人审清单
import re, os, json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def norm(s):
    return re.sub(r'[^a-z]', '', s.lower())

with open('参考文献.md', encoding='utf-8') as f:
    lines = f.read().split('\n')

# ---- 解析汇编：条目 + 章节级别 ----
comp = []          # (id, surname, year, sec_level, line)
level = None
subsec = ''
PUBLISHERS = r'University Press|Addison-Wesley|Basic Books|Cambridge|McGraw-Hill|Wiley|Pergamon|Van Nostrand|Prometheus|Dover|Prentice|Springer|World Scientific|North-Holland|Benjamin|Holt, Rinehart'
for line in lines:
    hm = re.match(r'^##\s*([SAB])级', line)
    if hm:
        level = hm.group(1); subsec = ''; continue
    sm = re.match(r'^###\s+(.+)$', line)
    if sm:
        subsec = sm.group(1); continue

    def classify(body):
        # 按文献类型定级（对齐基准篇分组惯例）
        if re.search(r'CODATA|PDG|Particle Data Group|NIST|Nobel', body):
            return 'S'
        if re.search(PUBLISHERS, body) and not re.search(r'\b(PRL|Phys\.\s*Rev|Nature|Science|Annalen|Zeitschrift|Proc\.|Z\.?\s*Phys|J\.\s*Phys|Lett\.)', body):
            return 'A'  # 教材/专著（无期刊信息）
        if re.search(r'arXiv|预印本|百科|Wikipedia|Stanford|科普|colloquy|专栏', body):
            return 'B'
        # 默认：期刊论文 → 奠基原始文献 S
        return 'S'

    m = re.match(r'^(\d{1,3})\.\s+(.+)$', line)
    if m:
        body = m.group(2)
        am = re.match(r"((?:von|da|de|van|'t)\s+[A-Z][A-Za-z\-\'’]+|[A-Z][A-Za-z\-\'’]+|Lüders)", body)
        ym = re.search(r'\((\d{4})\)', body)
        sn = norm(am.group(1)) if am else ''
        yr = ym.group(1) if ym else ''
        if sn and yr:
            lv = 'S' if '数据标准' in subsec else classify(body)
            if '教材' in subsec or '专著' in subsec:
                lv = 'A'
            comp.append((f'#{m.group(1)}', sn, yr, lv, line))
        continue
    m = re.match(r'^(24[a-z]{1,2})\.\s+(.+)$', line)
    if m:
        body = m.group(2)
        am = re.match(r"((?:von|da|de|van|'t)\s+[A-Z][A-Za-z\-\'’]+|[A-Z][A-Za-z\-\'’]+|Lüders)", body)
        ym = re.search(r'\((\d{4})\)', body)
        sn = norm(am.group(1)) if am else ''
        yr = ym.group(1) if ym else ''
        lv = classify(body)
        if '教材' in subsec or '专著' in subsec:
            lv = 'A'
        comp.append((m.group(1), sn, yr, lv, line))

print('汇编解析:', len(comp), '条')
keymap = {}
for eid, sn, yr, lv, ln in comp:
    keymap.setdefault((sn, yr), []).append((eid, lv))

# ---- 人工裁决修正（多候选/主序列优先/模糊匹配）----
FIX = {
    ('nielsen','2010'): ('#30','A'), ('lederman','2004'): ('#45','B'),
    ('codata','2018'): ('24hk','S'), ('codata','2022'): ('#1','S'),
    ('bohr','1913'): ('#5','S'), ('dirac','1928'): ('24bi','S'),
    ('born','1926'): ('24bb','S'), ('dirac','1930'): ('24bd','A'),
    ('brune','1996'): ('24ae','S'), ('dirac','1927'): ('24bn','S'),
}
# 30 篇多候选按合著者区分
FIX30 = {
    'grangier': ('#20','S'),   # Aspect, Grangier & Roger 1982
    'dalibard': ('#21','S'),   # Aspect, Dalibard & Roger 1982
}
# 32 篇 Bennett 1992 两篇区分
FIX32 = {
    'bessette': ('24an','S'),
    'mermin': ('24ay','S'),
}

AY_NOTES = ['01','02','03','04','05','06','07','08','09','10','11','16','18','19','21','22','23','29','30','31','32']
# 新编号池（从 24lb 起）
new_pool = [a+b for a in 'lmnopqrstuvw' for b in 'abcdefghijklmnopqrstuvwxyz']
used = set(eid for eid, _, _, _, _ in comp) | {'#30','#45','#1','#5','#20','#21','24hk','24bi','24bb','24bd','24ae','24bn','24an','24ay'}
new_ids = [x for x in new_pool if x not in used]

plan = {}
issues = []
for num in AY_NOTES:
    fp = [f for f in os.listdir('.') if f.startswith(num + '_') and f.endswith('.md')][0]
    with open(fp, encoding='utf-8') as f:
        t = f.read()
    m = re.search(r'\n##\s*八[、.．:：\s].*', t, re.S)
    sec8 = re.split(r'\n\*本篇版本|\n\*第 \d+ 篇|\n---\s*\n\*数学程度', m.group(0))[0] if m else ''
    # 当前本地分组状态
    groups = re.findall(r'\*\*([SAB])\s*级[^*]*\*\*', sec8)
    entries = []   # (原行, 编号, 级别, verified)
    cur_group = None
    for line in sec8.split('\n'):
        ls = line.strip()
        gm = re.match(r'\*\*([SAB])\s*级', ls)
        if gm:
            cur_group = gm.group(1); continue
        if re.match(r'^\*\*待回溯', ls):
            cur_group = 'B'; continue
        # 已有编号条目
        em = re.match(r'^#?(24[a-z]{1,2}|\d{1,3})\.\s+(.+)$', ls)
        if em:
            eid = em.group(1)
            if not eid.startswith('24') and not eid.startswith('#'):
                eid = '#' + eid
            entries.append({'line': ls, 'id': eid, 'level': cur_group, 'verified': '已核实' in ls, 'note': '已有编号'})
            continue
        # blockquote 导语/复用行
        if ls.startswith('>'):
            entries.append({'line': ls, 'id': None, 'level': cur_group, 'verified': False, 'note': '导语/复用行(保留原样)'})
            continue
        if ls.startswith('- '):
            am = re.match(r'-\s+((?:von|da|de|van|\'t)\s+[A-Z][A-Za-z\-\'’]+|[A-Z][A-Za-z\-\'’\.]+)', ls)
            ym = re.search(r'\((\d{4})\)', ls)
            if not (am and ym):
                entries.append({'line': ls, 'id': None, 'level': cur_group, 'verified': False, 'note': '非标准条目(人工处理)'})
                continue
            sn = norm(am.group(1).rstrip(',. '))
            yr = ym.group(1)
            # 30 篇 Aspect 1982 两条按合著者区分
            if num == '30' and sn == 'aspect' and yr == '1982':
                co = 'grangier' if 'grangier' in ls.lower() and 'dalibard' not in ls.lower() else 'dalibard'
                eid, lv = FIX30[co]
                entries.append({'line': ls, 'id': eid, 'level': cur_group or lv, 'verified': '已核实' in ls, 'note': '30篇合著者裁决'})
                continue
            if num == '32' and sn == 'bennett':
                co = 'bessette' if 'bessette' in ls.lower() else ('mermin' if 'mermin' in ls.lower() else None)
                if co:
                    eid, lv = FIX32[co]
                    entries.append({'line': ls, 'id': eid, 'level': cur_group or lv, 'verified': '已核实' in ls, 'note': '32篇合著者裁决'})
                    continue
            if (sn, yr) in FIX:
                eid, lv = FIX[(sn, yr)]
                entries.append({'line': ls, 'id': eid, 'level': cur_group or lv, 'verified': '已核实' in ls, 'note': '人工裁决匹配'})
                continue
            cands = keymap.get((sn, yr), [])
            if len(cands) == 1:
                eid, lv = cands[0]
                entries.append({'line': ls, 'id': eid, 'level': cur_group or lv, 'verified': '已核实' in ls, 'note': '唯一匹配'})
            elif len(cands) > 1:
                # 优先 24xx 两位字母新式编号 > 主序列 > 旧式
                pref = [c for c in cands if re.match(r'^24[a-z]{2}$', c[0])]
                pick = pref[0] if pref else sorted(cands, key=lambda c: (len(c[0]), c[0]))[0]
                issues.append(f'第{num}篇 ({sn},{yr}) 多候选 {[c[0] for c in cands]} → 取 {pick[0]}')
                entries.append({'line': ls, 'id': pick[0], 'level': cur_group or pick[1], 'verified': '已核实' in ls, 'note': f'多候选取{pick[0]}'})
            else:
                nid = new_ids.pop(0) if new_ids else 'EXHAUSTED'
                entries.append({'line': ls, 'id': nid, 'level': cur_group, 'verified': '已核实' in ls, 'note': f'新编号{nid}'})
                issues.append(f'第{num}篇 新编号 {nid}: {ls[:60]}')
    plan[num] = {'file': fp, 'has_groups': bool(groups), 'entries': entries}

print('\n=== 人审清单（新编号/多候选/人工裁决） ===')
for it in issues:
    print(it)

with open('code/_p1_full_plan.json', 'w', encoding='utf-8') as f:
    json.dump(plan, f, ensure_ascii=False, indent=1)
print('\n方案已存 code/_p1_full_plan.json')

# 统计
n_new = sum(1 for p in plan.values() for e in p['entries'] if e['note'].startswith('新编号'))
n_match = sum(1 for p in plan.values() for e in p['entries'] if e['id'] and e['note'] != '导语/复用行(保留原样)' and not e['note'].startswith('新编号'))
print(f'条目总数(编号化): {n_match + n_new}，其中新编号 {n_new}')
