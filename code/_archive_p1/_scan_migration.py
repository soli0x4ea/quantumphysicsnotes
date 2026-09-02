# -*- coding: utf-8 -*-
# P1 迁移分析：26 篇作者-年份篇第八节条目 vs 汇编重合度 + 新编号分配
import re, os, json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def norm(s):
    return re.sub(r'[^a-z]', '', s.lower())

with open('参考文献.md', encoding='utf-8') as f:
    refs_text = f.read()

# 解析汇编：主序列 + 24xx 序列
# 主序列: "N. Author..." ; 24xx: "24xx. Author..."
comp_entries = []  # (id, first_author_surname, year, line)
for line in refs_text.split('\n'):
    m = re.match(r'^(\d{1,3})\.\s+(.+)$', line)
    if m:
        body = m.group(2)
        am = re.match(r'([A-Z][A-Za-z\-\'’]+)', body)
        ym = re.search(r'\((\d{4})\)', body)
        if am and ym:
            comp_entries.append((f'#{m.group(1)}', norm(am.group(1)), ym.group(1), line[:80]))
            continue
    m = re.match(r'^(24[a-z]{2})\.\s+(.+)$', line)
    if m:
        body = m.group(2)
        am = re.match(r'([A-Z][A-Za-z\-\'’]+)', body)
        ym = re.search(r'\((\d{4})\)', body)
        if am and ym:
            comp_entries.append((m.group(1), norm(am.group(1)), ym.group(1), line[:80]))

print(f'汇编解析条目: {len(comp_entries)}（主序列+24xx）')

# 键: (surname, year) -> [ids]
keymap = {}
for eid, sn, yr, ln in comp_entries:
    keymap.setdefault((sn, yr), []).append(eid)

AY_NOTES = ['01','02','03','04','05','06','07','08','09','10','11','16','18','19','21','22','23','29','30','31','32']
# 12/13/14/15/17 已有编号条目，单独处理
total_new, total_match = 0, 0
plan = {}
for num in AY_NOTES:
    fp = [f for f in os.listdir('.') if f.startswith(num + '_') and f.endswith('.md')][0]
    with open(fp, encoding='utf-8') as f:
        t = f.read()
    m = re.search(r'\n##\s*八[、.．:：\s].*', t, re.S)
    sec8 = m.group(0) if m else ''
    # 截断到版本行前
    sec8 = re.split(r'\n\*本篇版本|\n\*第 \d+ 篇', sec8)[0]
    items = []
    for line in sec8.split('\n'):
        ls = line.strip()
        if ls.startswith('- ') and not ls.startswith('- ['):
            # 作者-年份条目
            am = re.match(r'-\s+([A-Z][A-Za-z\-\'’\.]+(?:,|\s))', ls)
            ym = re.search(r'\((\d{4})\)', ls)
            if am and ym:
                surname = norm(am.group(1).rstrip(',. '))
                items.append((surname, ym.group(1), ls[:70]))
    new_items, match_items = [], []
    for sn, yr, ls in items:
        ids = keymap.get((sn, yr), [])
        if len(ids) == 1:
            match_items.append((sn, yr, ids[0], ls))
        elif len(ids) > 1:
            match_items.append((sn, yr, '/'.join(ids), ls))
        else:
            new_items.append((sn, yr, ls))
    total_new += len(new_items); total_match += len(match_items)
    plan[num] = {'match': match_items, 'new': new_items}
    flag = ' <<<多候选' if any('/' in m[2] for m in match_items) else ''
    print(f'第{num}篇: 条目{len(items)} 已在汇编{len(match_items)} 需新编号{len(new_items)}{flag}')
    for sn, yr, ls in new_items:
        print(f'    新: {sn} {yr} | {ls[:60]}')

print(f'\n合计: 已匹配 {total_match}，需新编号 {total_new}')

with open('code/_p1_migration_plan.json', 'w', encoding='utf-8') as f:
    json.dump(plan, f, ensure_ascii=False, indent=1)
print('迁移方案已存 code/_p1_migration_plan.json')
