"""Subclass progression infrastructure; never grants content by itself.

Vanilla Shared/Progressions/Progressions.lsx has empty LifeDomain level 4
nodes with only Level, Name, ProgressionType, TableUUID and UUID attributes.
Edits preserve original bytes outside the inserted or explicitly changed nodes.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

NEW_LEVELS = (4, 5, 7, 8, 9, 11)
SUBCLASSES = ('TenderloinBiohazard', 'VeniceBoardwalkBrawler',
              'BARTPlatformMenace', 'OverpassRiverbedDweller')
_NODE = re.compile(r'<node id="Progression">(?:(?!<node).)*?</node>', re.S)
_FEATURES = {'Selectors', 'PassivesAdded', 'PassivesRemoved', 'Boosts'}


def _load(public_dir):
    path = Path(public_dir) / 'Progressions/Progressions.lsx'
    text = path.read_bytes().decode('utf-8')
    tree = ET.fromstring(text)
    parent = tree.find('./region[@id="Progressions"]/node[@id="root"]/children')
    if parent is None:
        raise ValueError('Progressions.lsx lacks Progressions/root/children')
    nodes = {}
    for node in parent.findall('./node[@id="Progression"]'):
        attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
        if attrs.get('Name') in SUBCLASSES:
            key = (attrs['Name'], int(attrs['Level']))
            if key in nodes:
                raise ValueError(f'Duplicate subclass progression: {key}')
            nodes[key] = node
    return path, text, nodes


def add_empty_subclass_nodes(public_dir, get_guid):
    """Append missing subclass levels using level-3 structural attributes."""
    path, text, nodes = _load(public_dir)
    newline = '\r\n' if '\r\n' in text else '\n'
    additions = []
    used = {a.get('value') for a in ET.fromstring(text).iter('attribute')
            if a.get('id') == 'UUID'}
    for name in SUBCLASSES:
        donor = nodes.get((name, 3))
        if donor is None:
            raise ValueError(f'Missing subclass progression donor: {name} level 3')
        for level in NEW_LEVELS:
            if (name, level) in nodes:
                continue
            uid = str(get_guid(f'HC_SubclassLevel_{name}_{level}'))
            if uid in used:
                raise ValueError(f'Duplicate progression UUID: {uid}')
            used.add(uid)
            lines = ['                <node id="Progression">']
            for attr in donor.findall('attribute'):
                key = attr.get('id')
                if key in _FEATURES:
                    continue
                copied = dict(attr.attrib)
                if key == 'Level':
                    copied['value'] = str(level)
                elif key == 'UUID':
                    copied['value'] = uid
                fields = ' '.join(f'{k}={quoteattr(v)}' for k, v in copied.items())
                lines.append(f'                    <attribute {fields}/>')
            lines.append('                </node>')
            additions.append(newline.join(lines) + newline)
    if additions:
        # The last children closing tag belongs to the root progression list.
        end = text.rfind('            </children>')
        if end < 0:
            raise ValueError('Progressions.lsx lacks root children closing tag')
        text = text[:end] + ''.join(additions) + text[end:]
        ET.fromstring(text)
        path.write_bytes(text.encode('utf-8'))


def apply_subclass_passives(public_dir, passives):
    """Merge ordered passive names, rejecting missing targets before writing."""
    path, text, nodes = _load(public_dir)
    targets = {}
    for name, levels in passives.items():
        for level, names in levels.items():
            key = (name, int(level))
            if key not in nodes:
                raise ValueError(f'Missing subclass progression: {name} level {level}')
            targets[key] = names

    def attach(match):
        block = match.group(0)
        attrs = {a.get('id'): a.get('value') for a in ET.fromstring(block).findall('attribute')}
        key = (attrs.get('Name'), int(attrs.get('Level', '0')))
        if key not in targets:
            return block
        old = attrs.get('PassivesAdded', '')
        merged = list(filter(None, old.split(';')))
        for name in targets[key]:
            if name and name not in merged:
                merged.append(name)
        value = ';'.join(merged)
        if value == old:
            return block
        line = f'<attribute id="PassivesAdded" type="LSString" value={quoteattr(value)}/>'
        if 'PassivesAdded' in attrs:
            return re.sub(r'<attribute id="PassivesAdded"[^>]*/>', lambda _: line, block, count=1)
        newline = '\r\n' if '\r\n' in text else '\n'
        return block.replace('<attribute id="Level"', line + newline + '                    <attribute id="Level"', 1)

    result = _NODE.sub(attach, text)
    if result != text:
        ET.fromstring(result)
        path.write_bytes(result.encode('utf-8'))
