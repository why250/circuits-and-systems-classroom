"""Read saved schema-68 connectivity without depending on an older Canvas build."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'circuits/bjt-degenerated-differential-pair/CML buffer.icproj.json'


def extract():
    project = json.loads(SOURCE.read_text(encoding='utf-8'))
    doc = next(d for d in project['documents'] if d['id'] == project['topDocumentId'])
    parents = {}

    def key(endpoint):
        if 'terminal' in endpoint:
            return tuple(endpoint['terminal'])
        if 'junction' in endpoint:
            return ('junction', endpoint['junction'])
        raise ValueError(f'Unsupported electrical endpoint: {endpoint}')

    def find(k):
        parents.setdefault(k, k)
        if parents[k] != k:
            parents[k] = find(parents[k])
        return parents[k]

    def join(endpoints):
        keys = [key(e) for e in endpoints]
        for k in keys[1:]:
            parents[find(k)] = find(keys[0])

    for route in doc['routes']:
        endpoints = [route['start']]
        if 'end' in route:
            endpoints.append(route['end'])
        endpoints.extend({'junction': leg['junction']} for leg in route.get('legs', []) if 'junction' in leg)
        join(endpoints)
    for mode in ('contacts', 'unrouted'):
        for group in doc['connections'].get(mode, []):
            join(group)
    names = {}
    for terminal in doc['netlist']['terminals']:
        net = next(n for n in doc['nets'] if n['id'] == terminal['netId'])
        names[find(key(net['at']))] = terminal['name']
    ground = next(i for i in doc['instances'] if i['type'] == 'ground')
    names[find((ground['id'], '0'))] = '0'
    for transistor, terminal, name in [('Q1', 'E', 'e1'), ('Q2', 'E', 'e2'),
                                       ('Q3', 'C', 'x'), ('Q3', 'E', 'e3')]:
        names[find((transistor, terminal))] = name
    expected = {'Q1': ['voutn', 'vinp', 'e1', '0'],
                'Q2': ['voutp', 'vinn', 'e2', '0'], 'Q3': ['x', 'vb', 'e3', '0'],
                'RD1': ['VDD', 'voutn'], 'RD2': ['VDD', 'voutp'],
                'R1': ['e3', '0'], 'R2': ['e2', 'x'], 'R3': ['e1', 'x']}
    devices = {}
    structural = ['* Connectivity extracted from the supplied schema-68 project.',
                  '* Structural export only: external SKY130 model is not supplied.',
                  '.subckt cml_buffer VDD vinp vinn voutn voutp vb']
    defaults = project['defaults']['instancesByType']
    for instance in doc['instances']:
        kind = instance['type']
        if kind not in ('npn', 'resistor'):
            continue
        pins = ['C', 'B', 'E', 'S'] if kind == 'npn' else ['1', '2']
        nodes = [names[find((instance['id'], pin))] for pin in pins]
        name = instance['name']
        assert nodes == expected[name], (name, nodes)
        parameters = {**defaults.get(kind, {}).get('parameters', {}), **instance.get('parameters', {})}
        devices[name] = {'nodes': nodes, 'parameters': parameters}
        if kind == 'npn':
            target = instance.get('target', defaults[kind]['target'])
            model = next(s['name'] for s in project['externalSubcircuitDefinitions'] if s['id'] == target['definitionId'])
            structural.append(f'X{name} {" ".join(nodes)} {model} m={parameters["m"]}')
        else:
            structural.append(f'{name} {" ".join(nodes)} {parameters["value"].replace("kΩ", "k")}')
    structural.append('.ends cml_buffer')
    assert devices['RD1']['parameters']['value'] == devices['RD2']['parameters']['value'] == '1kΩ'
    assert all(devices[r]['parameters']['value'] == '50' for r in ('R1', 'R2', 'R3'))
    return {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'source_schema_version': project['schemaVersion'], 'project_name': project['name'],
            'devices': devices, 'checks': ['route/contact/unrouted connectivity matches expected topology',
                                         'resistor values match supplied project'],
            'substrate_note': 'Virtual S terminals in saved unrouted connections are grounded.',
            'model_status': 'SKY130 subcircuit declared; no model source, bias or load supplied'}, '\n'.join(structural) + '\n'


def schematic(directory):
    """Draw a connectivity-checked reconstruction, using physical NPN symbols."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(8.5, 7))
    ax.set_aspect('equal')
    ax.axis('off')
    color = '#20364b'

    def wire(xs, ys):
        ax.plot(xs, ys, color=color, lw=1.8)

    def resistor(x, top, bottom, label):
        mid = (top + bottom) / 2
        wire([x, x], [top, mid + .24])
        ax.add_patch(Rectangle((x-.12, mid-.24), .24, .48, fill=False, edgecolor=color, lw=1.8))
        wire([x, x], [mid-.24, bottom])
        ax.text(x+.22, mid, label, va='center', fontsize=11)

    def npn(x, y, label, side=-1):
        # Collector/emitter terminal coordinates are x,y+0.5 / x,y-0.5.
        bx = x + side*.45
        wire([bx, bx], [y-.27, y+.27])
        wire([bx, x, x], [y+.15, y+.35, y+.5])
        wire([bx, x, x], [y-.15, y-.35, y-.5])
        wire([bx+side*.45, bx], [y, y])
        ax.annotate('', xy=(x, y-.35), xytext=(bx*.3+x*.7, y-.29),
                    arrowprops=dict(arrowstyle='-|>', color=color, lw=1.5, mutation_scale=12))
        ax.text(x-side*.25, y, label, fontsize=12, va='center', ha='left' if side<0 else 'right')

    wire([-2, 2], [4.3, 4.3])
    ax.text(0, 4.45, '$V_{DD}$', fontsize=13, ha='center')
    for x, q, rd, re, inp, out, side in [(-1.6,'Q1','RD1','R3','$v_{inp}$','$v_{outn}$',-1),
                                      (1.6,'Q2','RD2','R2','$v_{inn}$','$v_{outp}$',1)]:
        resistor(x, 4.3, 3.1, rd+' = 1 kΩ')
        wire([x,x],[3.1,2.5])
        wire([x,x+side*.65],[3.1,3.1])
        ax.plot(x,3.1,'o',color=color,ms=4)
        ax.text(x+side*.72,3.1,out,ha='right' if side<0 else 'left',va='center',fontsize=12)
        npn(x,2,q,side)
        ax.text(x+side*1.02,2,inp,ha='right' if side<0 else 'left',va='center',fontsize=12)
        resistor(x,1.5,.4,re+' = 50 Ω')
    wire([-1.6,1.6],[.4,.4])
    ax.plot(0,.4,'o',color=color,ms=4)
    ax.text(.18,.57,'X',fontsize=12)
    wire([0,0],[.4,-.1])
    npn(0,-.6,'Q3')
    ax.text(-1.02,-.6,'$v_b$',ha='right',va='center',fontsize=12)
    resistor(0,-1.1,-2.1,'R1 = 50 Ω')
    for length,y in [(.35,-2.1),(.24,-2.2),(.12,-2.3)]:
        wire([-length,length],[y,y])
    ax.set(xlim=(-3.5,3.7),ylim=(-2.75,5))
    ax.set_title('BJT differential pair with emitter degeneration',fontsize=15,pad=16)
    fig.text(.5,.02,'Connectivity-checked reconstruction. SKY130 substrate terminals connect to ground.\nNo supply, bias or output capacitance was saved in the source project.',ha='center',fontsize=9)
    directory.mkdir(parents=True,exist_ok=True)
    for suffix in ('png','svg'):
        fig.savefig(directory/f'schematic.{suffix}',dpi=170,bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    report, text = extract()
    lab = ROOT/'simulations/bjt-degenerated-differential-pair'
    lab.mkdir(parents=True,exist_ok=True)
    (lab/'source-structural.cir').write_text(text,encoding='utf-8')
    (SOURCE.parent/'provenance.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    schematic(ROOT/'figures/bjt-degenerated-differential-pair')
    print(text)
