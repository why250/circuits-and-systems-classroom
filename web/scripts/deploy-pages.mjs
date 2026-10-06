import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { preparePagesAssets } from './pages-assets.mjs';

const { values } = parseArgs({ options: {
  project: { type: 'string', default: 'why250-circuits-classroom' },
  'prepare-only': { type: 'boolean', default: false },
  help: { type: 'boolean', default: false },
} });
if (values.help) {
  console.log('node scripts/deploy-pages.mjs [--project your-pages-name] [--prepare-only]');
  process.exit(0);
}
const project = values.project;
if (!/^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$/.test(project)) throw new Error('Use a 2–63 character project name with lowercase letters, digits and hyphens.');
const webRoot = fileURLToPath(new URL('../', import.meta.url));
const node = process.execPath;
const wrangler = path.join(webRoot, 'node_modules/wrangler/bin/wrangler.js');
const env = { ...process.env, SITE_URL: `https://${project}.pages.dev` };
function run(script, args, cwd = webRoot, capture = false) {
  const result = spawnSync(node, [script, ...args], { cwd, env, stdio: capture ? 'pipe' : 'inherit', encoding: 'utf8' });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    if (capture) { process.stdout.write(result.stdout ?? ''); process.stderr.write(result.stderr ?? ''); }
    throw new Error(`Command failed with status ${result.status}: ${path.basename(script)}`);
  }
  return result.stdout ?? '';
}
run(path.join(webRoot, 'node_modules/astro/bin/astro.mjs'), ['build']);
const assets = preparePagesAssets(webRoot);
console.log(JSON.stringify({ project, site: env.SITE_URL, ...assets }, null, 2));
if (values['prepare-only']) process.exit(0);

const identity = run(wrangler, ['whoami'], assets.directory, true);
if (/not authenticated/i.test(identity)) {
  console.error('Cloudflare login is required. In web/, run:');
  console.error('node node_modules/wrangler/bin/wrangler.js login --device --browser=false --scopes account:read user:read pages:write');
  process.exit(2);
}
const projects = run(wrangler, ['pages', 'project', 'list'], assets.directory, true);
const projectPattern = new RegExp(`(?:^|[^a-z0-9-])${project}(?:$|[^a-z0-9-])`, 'm');
// Keep first-time creation on Pages so the requested pages.dev URL is used.
if (!projectPattern.test(projects)) run(wrangler, ['pages', 'project', 'create', project, '--production-branch', 'main', '--force'], assets.directory);
run(wrangler, ['pages', 'deploy', '.', '--project-name', project, '--branch', 'main', '--commit-dirty=true'], assets.directory);
console.log(`Learning roadmap: ${env.SITE_URL}/learn/razavi/`);
