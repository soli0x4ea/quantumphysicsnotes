# -*- coding: utf-8 -*-
# P1/P2 机械批处理：
#   1) 中文括号 (24xx) -> [24xx]
#   2) 第八节 [已核实] 与汇编同步（仅汇编已核实条目补标）
#   3) 19 篇第八节按 S/A/B 显式分组重排（条目内容不改）
#   4) 更新句统一为基准 blockquote 句式（缺则补）
#   5) 版本行规范化（v1.0->v1.1 / v1.1->v1.2 / 变体行替换 / 缺则补）
import re, glob, os, json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------- 级别判定 ----------
full_plan = json.load(open('code/_p1_full_plan.json', encoding='utf-8'))
level_map = {}   # id -> level（来自迁移方案，人审过口径）
for art, info in full_plan.items():
    for e in info.get('entries', []):
        eid, lv = e.get('id'), e.get('level')
        if eid and lv and eid not in level_map:
            level_map[eid] = lv

PUBLISHERS = (r'University Press|Addison-Wesley|Basic Books|Cambridge|McGraw-Hill|Wiley|'
              r'Pergamon|Van Nostrand|Prometheus|Dover|Prentice|Springer|World Scientific|'
              r'North-Holland|Benjamin|Holt, Rinehart')
JOURNAL = (r'\b(PRL|Phys\.\s*Rev|Nature|Science|Annalen|Zeitschrift|Proc\.|Z\.?\s*Phys|'
           r'J\.\s*Phys|Lett\.|Philos\.|Rev\.\s*Mod|Opt\.|Appl\.\s*Phys|Sov\.\s*Phys)')
def classify(body):
    if re.search(r'CODATA|PDG|Particle Data Group|NIST|Nobel', body):
        return 'S'
    if re.search(PUBLISHERS, body) and not re.search(JOURNAL, body):
        return 'A'
    if re.search(r'arXiv|预印本|百科|Wikipedia|Stanford|科普|colloquy|专栏', body):
        return 'B'
    return 'S'

# ---------- 汇编核实状态 ----------
comp_ver = {}
for line in open('参考文献.md', encoding='utf-8'):
    m = re.match(r'^(24[a-z]{2})\.', line) or re.match(r'^#?(\d{1,3})\.\s', line)
    if m:
        comp_ver[m.group(1)] = ('已核实' in line)

GROUP_FILES = ['12','13','14','15','17','20','33','34','35','36','37','38','39','40',
               '41','43','44','46','47']
TAG_FILES    = {'12','13','15','17','44','47'}
CRIT_FILES   = {'42','44'}

HDR = {'S': '**S 级（奠基原始文献与标准数据）**',
       'A': '**A 级（同行评审研究与权威教材）**',
       'B': '**B 级（专著章节、教材与预印本）**'}
ENTRY_RE = re.compile(r'^\s*(?:-\s*)?(?:\[(24[a-z]{2})\]\s*|(24[a-z]{2})\.\s*|\[#?(\d{1,3})\]\s*|#(\d{1,3})\.\s*)')
YEAR_RE = re.compile(r'[（(](19|20)\d{2}[)）]')

def entry_id(line):
    m = ENTRY_RE.match(line)
    if not m:
        return None
    return next((g for g in m.groups() if g), None)

def entry_level(line):
    eid = entry_id(line)
    if eid and eid in level_map:
        return level_map[eid]
    return classify(line)

def split_sec8(text):
    m = re.search(r'^## 八[、.．][^\n]*$', text, re.M)
    if not m:
        return None
    return m

def process(path, num):
    text = open(path, encoding='utf-8').read()
    orig = text
    changes = []

    # 1) 中文括号
    n_paren = len(re.findall(r'（(24[a-z]{2})）', text))
    if n_paren:
        text = re.sub(r'（(24[a-z]{2})）', r'[\1]', text)
        changes.append(f'中文括号引用统一为方括号（{n_paren} 处）')

    # ---- 第八节处理 ----
    m8 = split_sec8(text)
    if m8:
        head, body = text[:m8.end()], text[m8.end():]

        # 2) [已核实] 同步（逐行，仅限条目行）
        n_verif = 0
        out_lines = []
        for line in body.split('\n'):
            eid = entry_id(line) if line.strip() else None
            if eid and comp_ver.get(eid) and '已核实' not in line and not line.strip().startswith('>'):
                line = line.rstrip() + ' `[已核实]`'
                n_verif += 1
            out_lines.append(line)
        body = '\n'.join(out_lines)
        if n_verif:
            changes.append(f'[已核实] 标记与汇编同步（{n_verif} 条）')

        # 3) S/A/B 分组
        if num in GROUP_FILES:
            blocks = [b for b in re.split(r'\n\s*\n', body) if b.strip()]
            intro, entries, trailing = [], [], []
            seen_entry = False
            i = 0
            while i < len(blocks):
                b = blocks[i]
                first = b.strip().split('\n')[0]
                if entry_id(first) or ENTRY_RE.match(first):
                    seen_entry = True
                    entries.append(b)
                elif not seen_entry:
                    intro.append(b)
                elif first.strip().startswith('---') or first.strip().startswith('>') \
                     or (first.strip().startswith('*') and ('本篇版本' in b or 'v1.' in b)):
                    trailing = blocks[i:]
                    break
                elif first.strip().startswith('*') and ('复用' in b or '已引用' in b) and entries:
                    entries[-1] = entries[-1] + '\n\n' + b   # 复用声明附着前一条件
                elif first.strip().startswith('**') and '级（' in b:
                    pass  # 旧分组头，丢弃重排
                else:
                    trailing = blocks[i:]
                    break
                i += 1
            groups = {}
            for e in entries:
                groups.setdefault(entry_level(e.strip().split('\n')[0]), []).append(e)
            parts = []
            for b in intro:
                parts.append(b)
            for lv in ('S', 'A', 'B'):
                if lv in groups:
                    parts.append(HDR[lv])
                    parts.extend(groups[lv])
            body = '\n\n'.join(parts)
            if trailing:
                body += '\n\n' + '\n\n'.join(trailing)
            body = re.sub(r'\n{3,}', '\n\n', body)
            if not body.startswith('\n'):
                body = '\n' + body
            changes.append('第八节按 S/A/B 分组重排')

        text = head + body

    # 4) 更新句
    if re.search(r'^本节内容可能随研究进展(.*)更新。$', text, re.M):
        text = re.sub(r'^本节内容可能随研究进展(.*)更新。$',
                      r'> 本节内容随研究进展可能更新\1。', text, flags=re.M)
        changes.append('更新句统一为基准 blockquote 句式')
    elif not re.search(r'随研究进展[^。\n]*更新', text):
        m8 = split_sec8(text)
        if m8:
            text = text[:m8.start()] + '> 本节内容随研究进展可能更新。\n\n' + text[m8.start():]
            changes.append('第七节末补更新句')

    # 5) 版本行
    items = []
    if num in full_plan:
        items.append('正文与文献引用迁移为全局编号（方案 B）')
    if num in TAG_FILES:
        items.append('核心公式补 \\tag 编号')
    if num in CRIT_FILES:
        items.append('量子效应显著判据独立成条')
    items.extend(c for c in changes if not c.startswith('中文括号') or True)
    # 去重保序
    seen, dedup = set(), []
    for it in items:
        if it not in seen:
            seen.add(it); dedup.append(it)
    note = 'P1 整改轮：' + '、'.join(dedup)

    lines = text.rstrip('\n').split('\n')
    ver_re = re.compile(r'^\*[^*\n]*v(\d+)\.(\d+)[^*\n]*\*$')
    new_ver_line = None
    for idx in range(len(lines) - 1, max(len(lines) - 6, -1), -1):
        vm = ver_re.match(lines[idx].strip()) if idx >= 0 else None
        if vm:
            if '本篇版本：' in lines[idx]:
                major, minor = int(vm.group(1)), int(vm.group(2))
                new_ver = f'v{major}.{minor + 1}'
            else:
                new_ver = 'v1.1'
            lines[idx] = f'*本篇版本：{new_ver}，2026年9月2日（{note}）*'
            new_ver_line = True
            changes.append('版本行规范化')
            break
    if new_ver_line is None:
        lines.append('')
        lines.append(f'*本篇版本：v1.1，2026年9月2日（{note}）*')
        changes.append('文末补版本行')
    text = '\n'.join(lines) + '\n'

    if text != orig:
        open(path, 'w', encoding='utf-8').write(text)
    return changes

report = {}
for fp in sorted(glob.glob('[0-9][0-9]_*_系统笔记.md')):
    num = fp[:2]
    report[num] = process(fp, num)

for num in sorted(report):
    ch = report[num]
    print(num, ' | '.join(ch) if ch else '(无改动)')
