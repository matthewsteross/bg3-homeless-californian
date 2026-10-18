"""Refresh test counts in the docs and write the Nexus package readme (lead tool, run before packaging).

python tools_release_docs.py            # updates README.md, TESTING.md, HANDOFF.md, validation/README.md counts
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def count_tests():
    out = {}
    for p in sorted((ROOT / 'validation').glob('test_*.py')):
        out[p.name] = len(re.findall(r'^\s+def test_', p.read_text(encoding='utf-8'), re.M))
    return out


def main():
    counts = count_tests()
    total = sum(counts.values())
    files = len(counts)
    print('tests', total, 'files', files)
    # validation/README: rewrite the intro sentence and the table
    p = ROOT / 'validation/README.md'
    t = p.read_text(encoding='utf-8')
    lines = t.split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('The suite has'))
    end = next(i for i in range(start, len(lines)) if lines[i].startswith('| File |'))
    intro = (f'The suite has **{total} tests** in {files} files (counted by `def test_` per file). The first files are the '
             'suite shipped in v0.4.0; everything after it is source-only until a release includes it: rounds 4-12, the four subclass '
             'expansions (levels 4-11, shared round-2 spells), the sound map, and every Meshy-generated prop (each prop has its own '
             'file with a Divine GR2 round trip, visual resource links, bounds, spell-patch and no-Patriot checks). All of it is '
             'file-level checking only and does not show that anything works in game.')
    table_rows = [l for l in lines[end:] if l.startswith('|')]
    known = {}
    for l in table_rows:
        m = re.match(r'\| `(test_[^`]+)` \| (\d+) \|(.*)\|', l)
        if m:
            known[m.group(1)] = m.group(3).strip()
    new_table = ['| File | Tests | Covers |', '|---|---:|---|']
    for name, n in counts.items():
        covers = known.get(name) or 'Source-only. See the module docstring of the matching hc_*.py file.'
        new_table.append(f'| `{name}` | {n} | {covers} |')
    new_table.append(f'| **Total** | **{total}** | |')
    tail_start = end + len(table_rows)
    lines = lines[:start] + [intro, ''] + new_table + lines[tail_start:]
    p.write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    for name in ('README.md', 'TESTING.md', 'HANDOFF.md'):
        q = ROOT / name
        s = q.read_text(encoding='utf-8')
        s2 = re.sub(r'\b322( file-level)? (unit )?tests', lambda m: f'{total}{m.group(1) or ""} {m.group(2) or ""}tests', s)
        s2 = re.sub(r'\b322 / 322', f'{total} / {total}', s2)
        if s2 != s:
            q.write_text(s2, encoding='utf-8', newline='\n')
            print('updated', name)


if __name__ == '__main__':
    main()
