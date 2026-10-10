"""Extract this schema-68 circuit, check connectivity and render its own symbols.

No Analog Canvas build is required. This deliberately supports only the supplied
flat document's terminal/junction routes and contacts; unsupported geometry fails.
The independently declared device tuples below guard the expected topology.
"""
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CIRCUITS = ROOT / 'circuits/source-degenerated-cascode'
LAB = ROOT / 'simulations/source-degenerated-cascode'
FIGURES = ROOT / 'figures/source-degenerated-cascode'
SOURCE = CIRCUITS / 'Source-degenerated cascode amplifier.icproj.json'


def si(value):
    match = re.fullmatch(r'([\d.eE+-]+)([a-zA-Z]*)', str(value))
    if not match:
        raise ValueError(f'Unsupported value {value}')
    multipliers = {'': 1, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'm': 1e-3, 'k': 1e3}
    return float(match[1]) * multipliers[match[2]]


def extract(project):
    if project['schemaVersion'] != 68 or len(project['documents']) != 1:
        raise ValueError('Expected flat schema-68 project')
    doc = project['documents'][0]
    if doc['id'] != project['topDocumentId']:
        raise ValueError('Wrong top document')
    instances = {i['id']: {**project['defaults']['instancesByType'].get(i['type'], {}), **i}
                 for i in doc['instances']}
    parent = {}

    def key(point):
        if set(point) == {'terminal'}:
            return tuple(point['terminal'])
        if set(point) == {'junction'}:
            return ('junction', point['junction'])
        raise ValueError(f'Unsupported route point: {point}')

    def find(a):
        parent.setdefault(a, a)
        if parent[a] != a:
            parent[a] = find(parent[a])
        return parent[a]

    def union(a, b):
        parent[find(a)] = find(b)

    for route in doc['routes']:
        if 'end' not in route or 'legs' in route:
            raise ValueError('Unsupported route geometry')
        union(key(route['start']), key(route['end']))
    for contacts in doc['connections'].values():
        for group in contacts:
            for point in group[1:]:
                union(key(group[0]), key(point))
    net_anchors = {n['id']: key(n['at']) for n in doc['nets']}
    for i in instances.values():
        if i['type'] == 'nmos':
            union((i['id'], 'B'), net_anchors[i['mosBulkBinding']['netId']])
    names = {}
    for port in doc['netlist']['terminals']:
        alias = {'Vb': 'VB', 'Vinp': 'VIN', 'Vout': 'OUT', 'VDD': 'VDD'}[port['name']]
        names[find(net_anchors[port['netId']])] = alias
    names[find(('GND1', '0'))] = 'VSS'
    names[find(('M1', 'D'))] = 'X'
    names[find(('M1', 'S'))] = 'E'

    def net(instance, pin):
        return names[find((instance, pin))]

    cards = []
    for i in instances.values():
        if i['type'] == 'nmos':
            pins = [net(i['id'], p) for p in ('D', 'G', 'S', 'B')]
            cards.append({'name': i['name'], 'nodes': pins, 'kind': 'mos',
                          'parameters': i['parameters'], 'target': i['target']})
        elif i['type'] == 'resistor':
            cards.append({'name': i['name'], 'nodes': [net(i['id'], p) for p in ('1', '2')],
                          'kind': 'resistor', 'parameters': i['parameters']})
    expected = {'M1': ['X', 'VIN', 'E', 'VSS'], 'M2': ['OUT', 'VB', 'X', 'VSS'],
                'RE': ['E', 'VSS'], 'RL': ['VDD', 'OUT']}
    if len(cards) != 4 or {c['name']: c['nodes'] for c in cards} != expected:
        raise ValueError(f'Circuit differs from independent reference: {cards}')
    for card in cards:
        if card['kind'] == 'mos':
            if not math.isclose(si(card['parameters']['w']), 1e-6) or not math.isclose(si(card['parameters']['l']), 150e-9):
                raise ValueError('Review changed W/L before regenerating')
            if card['parameters']['m'] != '1' or card['parameters'].get('nf', '1') != '1':
                raise ValueError('Only unit multiplicity supported')
        elif si(card['parameters']['value']) != 50:
            raise ValueError('Review changed resistor values before regenerating')
    mapping = {n['id']: names[find(key(n['at']))] for n in doc['nets']}
    return doc, instances, cards, mapping


def render(project, doc, instances):
    """Use embedded symbol primitives and actual placements, with teaching labels."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="285 188 320 375" width="800" height="938">',
             '<rect x="285" y="188" width="320" height="375" fill="white"/>',
             '<g stroke="#172b46" stroke-width="1.7" fill="none" stroke-linejoin="round">']
    symbols = {d['symbol']['id']: d['symbol'] for d in project['componentDefinitions']}
    junctions = {j['id']: j['coordinate'] for j in doc['junctions']}

    def coordinate(point):
        if 'junction' in point:
            return junctions[point['junction']]
        ident, pin = point['terminal']
        inst = instances[ident]
        sym = symbols[inst['type']]
        pt = next(p['at'] for p in sym['pins'] if p['name'] == pin)
        dx, dy = pt['x'], pt['y']
        if inst.get('mirror') == 'horizontal':
            dx = -dx
        if inst.get('rotation', 0) != 0:
            raise ValueError('Rotation rendering not implemented for this source')
        return [inst['coordinate'][0] + dx, inst['coordinate'][1] + dy]

    for r in doc['routes']:
        a, b = coordinate(r['start']), coordinate(r['end'])
        if a[0] != b[0] and a[1] != b[1]:
            raise ValueError('Non-straight route needs an explicit renderer')
        parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>')
    for inst in instances.values():
        symbol = symbols[inst['type']]
        variant = next((v for v in symbol.get('variants', []) if v['id'] == inst.get('variant')), {})
        primitives = [p for p in symbol['primitives'] if p.get('part') not in variant.get('hiddenPrimitiveParts', [])]
        primitives += variant.get('additionalPrimitives', [])
        x, y = inst['coordinate']
        mirror = ' scale(-1 1)' if inst.get('mirror') == 'horizontal' else ''
        parts.append(f'<g transform="translate({x} {y}){mirror}">')
        for p in primitives:
            k = p['kind']
            if k == 'line':
                a, b = p['from'], p['to']
                parts.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}"/>')
            elif k in ('polyline', 'polygon'):
                points = ' '.join(f'{a},{b}' for a, b in p['points'])
                fill = '#172b46' if p.get('fill') == 'foreground' else 'none'
                parts.append(f'<{k} points="{points}" fill="{fill}"/>')
            elif k == 'circle':
                c = p['center']
                fill = '#172b46' if p.get('fill') == 'foreground' else 'none'
                parts.append(f'<circle cx="{c["x"]}" cy="{c["y"]}" r="{p["radius"]}" fill="{fill}"/>')
            elif k == 'path':
                parts.append(f'<path d="{html.escape(p["data"])}"/>')
            else:
                raise ValueError(f'Unsupported primitive {k}')
        parts.append('</g>')
    parts.append('<circle cx="410" cy="310" r="2.5" fill="#172b46"/></g>')
    parts.append('<g fill="#172b46" font-family="Arial, sans-serif" font-size="12">')
    for x, y, label in [(420,240,'VDD'),(420,278,'RL = 50 ohm'),(452,314,'OUT'),
                        (420,356,'M2 (common gate)'),(325,354,'VB'),(320,414,'VIN'),
                        (420,416,'M1 (common source)'),(420,466,'RE = 50 ohm'),
                        (420,390,'X'),(420,442,'E'),(293,208,'Source-degenerated NMOS cascode'),
                        (293,539,'M1/M2: W = 1 um, L = 0.15 um'),(293,554,'Both bodies: VSS; CL added in benches')]:
        parts.append(f'<text x="{x}" y="{y}">{html.escape(label)}</text>')
    parts.append('</g></svg>')
    return '\n'.join(parts)


def main():
    source = SOURCE.read_bytes()
    project = json.loads(source)
    doc, instances, cards, mapping = extract(project)
    LAB.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    original = ['* Extracted from original schema-68 JSON; requires SKY130 PDK.',
                '* Original global ground remains node 0; port order matches JSON.',
                '.subckt dut VB VIN OUT VDD']
    educational = ['* Generated by code/export_cascode.py; same D/G/S/B, W/L, R values.',
                   '* Global ground promoted to VSS port for negative-rail tests.',
                   '* RLVAL/REVAL overrides are explicit simulation experiments.',
                   '.subckt cascode VDD VSS VIN OUT VB params: RLVAL=50 REVAL=50']
    for c in cards:
        name, nodes = c['name'], c['nodes']
        if c['kind'] == 'mos':
            ext = next(e for e in project['externalSubcircuitDefinitions'] if e['id'] == c['target']['definitionId'])
            if ext['name'] != 'sky130_fd_pr__nfet_01v8':
                raise ValueError('Unexpected process device')
            if [p['name'] for p in ext['terminals']] != ['D','G','S','B']:
                raise ValueError('Unexpected PDK pin order')
            raw_nodes = ['0' if n == 'VSS' else n for n in nodes]
            original.append(f'X{name} {" ".join(raw_nodes)} {ext["name"]} w=1 l=0.15 nf=1 m=1')
            educational.append(f'{name} {" ".join(nodes)} NMOS_EDU w=1u l=150n m=1')
        else:
            raw_nodes = ['0' if n == 'VSS' else n for n in nodes]
            original.append(f'{name} {" ".join(raw_nodes)} 50')
            educational.append(f'{name} {" ".join(nodes)} {{{name}VAL}}')
    original.append('.ends dut')
    educational.append('.ends cascode')
    (LAB / 'original-sky130.cir').write_text('\n'.join(original)+'\n', encoding='utf-8')
    (LAB / 'cascode-core.cir').write_text('\n'.join(educational)+'\n', encoding='utf-8')
    teaching = copy.deepcopy(project)
    teaching['id'] = 'project-classroom-source-degenerated-cascode'
    teaching['name'] = 'Source-degenerated cascode amplifier - educational LEVEL=1'
    teaching['defaults']['instancesByType']['nmos']['target'] = {'kind': 'model', 'deviceClass': 'mos', 'name': 'NMOS_EDU'}
    # NF belongs to the SKY130 wrapper; a unit finger is already represented
    # by the primitive's unchanged total W. MOS1 does not need a wrapper NF.
    teaching['defaults']['instancesByType']['nmos']['parameters'].pop('nf', None)
    teaching['externalSubcircuitDefinitions'] = []
    model = (LAB / 'models.lib').read_text(encoding='utf-8')
    teaching['modelSources'] = [{'id': 'classroom-nmos', 'language': 'spice', 'entry': 'models.lib',
                               'revision': 0, 'dependencies': [], 'files': [{'path': 'models.lib', 'text': model}]}]
    _, _, teaching_cards, teaching_mapping = extract(teaching)
    if teaching_mapping != mapping or [(c['name'], c['nodes']) for c in teaching_cards] != [(c['name'], c['nodes']) for c in cards]:
        raise ValueError('Teaching project changed electrical connectivity')
    (CIRCUITS / 'educational.icproj.json').write_text(json.dumps(teaching, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (FIGURES / 'schematic.svg').write_text(render(project, doc, instances), encoding='utf-8')
    report = {'original_filename': '(a1) Folded-cascode amplifiers..icproj.json',
              'original_folder': 'circuits/folded-cascode-amp',
              'source_file': str(SOURCE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(source).hexdigest(),
              'original_bytes_preserved': True, 'original_metadata_title': project['name'],
              'topology': 'resistor-loaded source-degenerated NMOS cascode; single input/output',
              'structural_check': 'Four device tuples and inherited W/L/R/nf/m checked against independent reference',
              'teaching_structural_check': 'Teaching project re-extracted: same four terminal tuples, net mapping, W/L/R and effective unit multiplicity',
              'extractor_scope': 'Supplied flat schema-68 routes, contacts and bulk-net bindings; no general Canvas compiler used',
              'editable_teaching_status': 'Generated using schema-68 model binding; not round-tripped by Canvas in this checkout',
              'node_mapping': mapping, 'devices': cards,
              'teaching_changes': 'Primitive LEVEL=1 model replaces SKY130 binding; unit wrapper NF omitted, total W and m=1 preserved; external VSS port only in core; original dimensions and 50-ohm resistors preserved'}
    (CIRCUITS / 'provenance.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'source_sha256': report['source_sha256'], 'devices': cards}, indent=2))


if __name__ == '__main__':
    main()
