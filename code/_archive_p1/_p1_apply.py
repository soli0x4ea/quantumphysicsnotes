# -*- coding: utf-8 -*-
# P1 第八节重写：按迁移方案给条目加编号前缀 + S/A/B 分组
# 用法: python _p1_apply.py <篇号> [--dry]
import re, os, json, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('code/_p1_full_plan.json', encoding='utf-8') as f:
    plan = json.load(f)

# 人工裁决覆盖
OVERRIDE = {
    ('07', 'schr1926'): '24bt',
    ('19', 'schr1926'): '24bv',
    ('29', 'schr1935'): '#14',
}

GROUP_TITLES = {
    'S': '**S 级（奠基原始文献与标准数据，均经检索核实卷期页）**',
    'A': '**A 级（同行评审研究与权威教材）**',
    'B': '**B 级（专著、教材、权威综述与专题文献）**',
}

def apply_note(num, dry=False):
    p = plan[num]
    fp = p['file']
    with open(fp, encoding='utf-8') as f:
        t = f.read()
    m = re.search(r'\n##\s*八[、.．:：\s].*', t, re.S)
    if not m:
        print(f'{num}: 未找到第八节'); return
    sec8_old = m.group(0)
    # 尾部（版本行等）分离
    tail_m = re.search(r'\n---\s*\n\*|\n\*本篇版本|\n\*第 \d+ 篇|\n\*数学程度', sec8_old)
    tail = ''
    sec8_body = sec8_old
    if tail_m:
        cut = sec8_old.index(tail_m.group(0))
        tail = sec8_old[cut:]
        sec8_body = sec8_old[:cut]

    entries = p['entries']
    # 重组：按级别分组
    out_lines = []
    lead = []  # 导语 blockquote
    # 保留原有的导语（第八节标题后首个 blockquote）
    body_entries = []
    for e in entries:
        if e['note'] == '导语/复用行(保留原样)':
            lead.append(e['line'])
        else:
            body_entries.append(e)

    def fmt(e):
        line = e['line']
        # 去掉旧前缀
        line = re.sub(r'^-\s+', '', line)
        line = re.sub(r'^#?(?:24[a-z]{1,2}|\d{1,3})\.\s+', '', line)
        line = re.sub(r'^>\s*复用[:：]\s*', '', line)
        eid = e['id']
        if not eid:
            return line  # 非标准条目保留原样
        return f'[{eid}] {line}'

    groups = {'S': [], 'A': [], 'B': [], '?': []}
    for e in body_entries:
        lv = e.get('level') or '?'
        groups[lv].append(fmt(e))

    new_sec8 = '\n## 八、参考文献\n'
    for l in lead:
        new_sec8 += '\n' + l + '\n'
    order = [lv for lv in 'SAB' if groups[lv]] + (['?'] if groups['?'] else [])
    for lv in order:
        if lv in GROUP_TITLES:
            new_sec8 += '\n' + GROUP_TITLES[lv] + '\n\n'
        elif lv == '?':
            new_sec8 += '\n**未分组（条目级别待人工核对）**\n\n'
        for ln in groups[lv]:
            new_sec8 += ln + '\n'
    new_sec8 = new_sec8.rstrip('\n') + '\n'
    new_full = t.replace(sec8_old, new_sec8 + (tail.lstrip('\n') if tail else ''))

    if dry:
        print(f'===== {num} {fp} 预览 =====')
        print(new_sec8[:2500])
        print('... 尾部:', (tail[:200] if tail else '(无)'))
        return
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_full)
    print(f'{num}: 已重写第八节（{len(body_entries)} 条目，S{len(groups["S"])}/A{len(groups["A"])}/B{len(groups["B"])}/?{len(groups["?"])}）')

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    for num in args:
        apply_note(num, dry)
