/** Export the user-supplied Gallery project using Analog Canvas' own packages.
 * Usage: node code/export_5t_ota.mjs [path/to/analog-canvas]
 * Requires the sibling repository's built packages; changes no files there.
 */
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const canvas = resolve(process.argv[2] ?? resolve(root, '..', 'analog-canvas'));
const moduleAt = name => import(pathToFileURL(resolve(canvas, 'packages', name, 'dist/index.js')).href);
const { parseProject, serializeProject } = await moduleAt('project-protocol');
const { validateProject } = await moduleAt('project-protocol');
const { compileSpiceSources, compareCircuitIR } = await moduleAt('spice');
const { builtInSymbols, createProjectSymbolResolver } = await moduleAt('symbols');
const { createFormalExportSource } = await moduleAt('exporters');
const { rasterizeSvgBytes } = await import(pathToFileURL(resolve(canvas, 'packages/exporters/dist/node.js')).href);
const { createDesignNetlistExport, analyzeDesignNetlist } = await moduleAt('netlist');
const file = resolve(root, 'circuits/5t-ota/Five-transistor OTA.icproj.json');
const text = await readFile(file, 'utf8');
const project = parseProject(text);
const document = project.documents.find(d => d.id === project.topDocumentId);
const resolver = createProjectSymbolResolver(project, builtInSymbols);
const formal = createFormalExportSource(document, resolver, { title: 'Five-transistor OTA — Gallery original', background: '#ffffff' });
const images = resolve(root, 'figures/5t-ota');
await mkdir(images, { recursive: true });
await writeFile(resolve(images, 'gallery-original.svg'), formal.svg);
await writeFile(resolve(images, 'gallery-original.png'), rasterizeSvgBytes(formal.svg, 1400));
const exported = createDesignNetlistExport(project, { format: 'spice', groundPin: 'pin' });
if (exported.status === 'ready') {
  await writeFile(resolve(root, 'simulations/5t-ota/gallery-original.cir'), exported.file.text);
}
const analysis = analyzeDesignNetlist(project, { format: 'spice', groundPin: 'pin' });
if (exported.status !== 'ready' || !analysis.ir) throw Error('Gallery netlist is not extractable');
const reference = `.subckt ota_5t VDD VSS vinp vinn vout vb
XM1 Y vinp X VSS sky130_fd_pr__nfet_01v8 l=0.5 w=4 nf=1 m=1
XM2 vout vinn X VSS sky130_fd_pr__nfet_01v8 l=0.5 w=4 nf=1 m=1
XM3 Y Y VDD VDD sky130_fd_pr__pfet_01v8 l=0.5 w=8 nf=1 m=1
XM4 vout Y VDD VDD sky130_fd_pr__pfet_01v8 l=0.5 w=8 nf=1 m=1
XM5 X vb VSS VSS sky130_fd_pr__nfet_01v8 l=1 w=8 nf=1 m=1
.ends ota_5t
`;
const compile = async text => {
  const result = await compileSpiceSources([{ path: 'check.cir', bytes: new TextEncoder().encode(text) }], 'check.cir');
  if (!result.successful || !result.ir) throw Error(JSON.stringify(result.diagnostics));
  return result.ir;
};
const originalCheck = compareCircuitIR(await compile(exported.file.text), await compile(reference), 'ota_5t');
if (originalCheck.status !== 'equal') throw Error(JSON.stringify(originalCheck));

// A separate teaching Project keeps the Gallery geometry, connectivity and W/L.
// Only model bindings change; original SKY130 source remains untouched.
const teaching = structuredClone(project);
teaching.id = 'project-classroom-5t-ota-educational';
teaching.name = 'Five-transistor OTA — educational LEVEL=1';
const td = teaching.documents.find(d => d.id === teaching.topDocumentId);
for (const instance of td.instances.filter(i => ['nmos', 'pmos'].includes(i.symbolId))) {
  instance.netlist = {
    binding: { kind: 'model', deviceClass: 'mos', name: instance.symbolId === 'nmos' ? 'NMOS_EDU' : 'PMOS_EDU' },
    parameters: { w: instance.netlist.parameters.w, l: instance.netlist.parameters.l, m: '1' },
  };
}
for (const [name, ref, offset] of [['X', 'M5', { x: 25, y: -25 }], ['Y', 'M1', { x: -20, y: -45 }]]) {
  const instance = td.instances.find(i => i.reference === ref);
  const net = td.nets.find(n => n.terminals.some(t => t.instanceId === instance.id && t.pinName === 'D'));
  const annotationId = `classroom-node-${name}`;
  td.annotations.push({ id: annotationId, kind: 'net-label', netId: net.id,
    binding: { kind: 'net-name', netId: net.id },
    anchor: { kind: 'object', objectId: instance.id, localOffset: offset,
              fallbackPosition: { x: instance.placement.position.x + offset.x, y: instance.placement.position.y + offset.y } },
    alignment: 'start', rotation: 0, locked: false });
  td.connectivityEvidence.push({ id: `classroom-node-name-${name}`, kind: 'name-claim', name,
    netId: net.id, owner: { kind: 'net-label', annotationId }, scope: 'local' });
}
const modelText = await readFile(resolve(root, 'simulations/5t-ota/models.lib'), 'utf8');
teaching.modelSources = [{ id: 'classroom-educational-mos', revision: 0, language: 'spice',
  entry: 'models.lib', files: [{ path: 'models.lib', text: modelText }], dependencies: [] }];
validateProject(teaching);
const teachingExport = createDesignNetlistExport(teaching, { format: 'spice', groundPin: 'pin' });
if (teachingExport.status !== 'ready') throw Error(JSON.stringify(teachingExport));
const teachingReference = `.subckt ota_5t VDD VSS vinp vinn vout vb
M1 Y vinp X VSS NMOS_EDU w=4u l=0.5u m=1
M2 vout vinn X VSS NMOS_EDU w=4u l=0.5u m=1
M3 Y Y VDD VDD PMOS_EDU w=8u l=0.5u m=1
M4 vout Y VDD VDD PMOS_EDU w=8u l=0.5u m=1
M5 X vb VSS VSS NMOS_EDU w=8u l=1u m=1
.ends ota_5t
`;
const teachingCheck = compareCircuitIR(await compile(teachingExport.file.text), await compile(teachingReference),
  'ota_5t', 'ota_5t', { declarations: false });
if (teachingCheck.status !== 'equal') throw Error(JSON.stringify(teachingCheck));
await writeFile(resolve(root, 'circuits/5t-ota/educational.icproj.json'), serializeProject(teaching));
const teachingFormal = createFormalExportSource(td, createProjectSymbolResolver(teaching, builtInSymbols),
  { title: 'Five-transistor OTA — educational model; X and Y named', background: '#ffffff' });
await writeFile(resolve(images, 'schematic.svg'), teachingFormal.svg);
await writeFile(resolve(images, 'schematic.png'), rasterizeSvgBytes(teachingFormal.svg, 1400));
await writeFile(resolve(root, 'simulations/5t-ota/ota-core.cir'),
  '* Generated from educational.icproj.json by code/export_5t_ota.mjs\n' +
  '* Gallery topology and W/L; primitive educational models replace SKY130.\n' + teachingExport.file.text);
const report = {
  source_url: 'https://analog-canvas.tokenzhang.com/g/tckfnzbrkf',
  source_file: 'Five-transistor OTA.icproj.json',
  source_sha256: createHash('sha256').update(text).digest('hex'),
  project_id: project.id, document_id: document.id,
  export_status: exported.status, diagnostics: exported.diagnostics,
  structural_verification: originalCheck,
  teaching_structural_verification: teachingCheck,
  node_mapping: { net0: 'X', net1: 'Y', M5: 'M_tail' },
  teaching_changes: 'SKY130 subcircuit calls replaced by educational MOS1 primitives; X/Y names added; W/L and connectivity preserved',
  devices: document.instances.filter(i => ['nmos', 'pmos'].includes(i.symbolId)).map(i => ({
    id: i.id, name: i.reference, polarity: i.symbolId, binding: i.netlist?.binding,
    parameters: i.netlist?.parameters, bulk: i.mosBulkBinding,
  })),
  extracted_cells: analysis.ir?.cells,
};
await writeFile(resolve(root, 'circuits/5t-ota/provenance.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ original: originalCheck, teaching: teachingCheck,
  devices: report.devices.map(d => ({ name: d.name, parameters: d.parameters })),
  source_sha256: report.source_sha256 }, null, 2));
