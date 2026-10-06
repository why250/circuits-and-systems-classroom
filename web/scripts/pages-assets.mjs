import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, statSync, copyFileSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

/** Stage only static assets. Running Wrangler here cannot pick up web/functions/. */
export function preparePagesAssets(webRoot) {
  const source = path.join(webRoot, 'dist');
  for (const file of ['index.html', 'learn/razavi/index.html']) {
    if (!existsSync(path.join(source, file))) throw new Error(`Build missing ${file}; run the Astro build first.`);
  }
  const stagingRoot = path.join(webRoot, '.wrangler');
  mkdirSync(stagingRoot, { recursive: true });
  const directory = mkdtempSync(path.join(stagingRoot, 'standalone-pages-'));
  const excluded = new Set(['_worker.js', '_routes.json', '.prerender', '.git', 'functions', 'worker']);
  for (const entry of readdirSync(source)) {
    if (!excluded.has(entry)) cpSync(path.join(source, entry), path.join(directory, entry), { recursive: true });
  }
  copyFileSync(path.join(webRoot, '..', 'LICENSE'), path.join(directory, 'LICENSE.txt'));
  // The API reference is hosted separately; static redirects preserve the lesson links.
  if (!existsSync(path.join(directory, 'doc/index.html'))) {
    const redirects = path.join(directory, '_redirects');
    const existing = existsSync(redirects) ? readFileSync(redirects, 'utf8') : '';
    writeFileSync(redirects, `${existing}\n/doc /doc/ 302\n/doc/* https://adctoolbox.tokenzhang.com/doc/:splat 302\n`);
  }
  let files = 0;
  let bytes = 0;
  function inspect(folder) {
    for (const entry of readdirSync(folder)) {
      const item = path.join(folder, entry);
      const stat = statSync(item);
      if (stat.isDirectory()) inspect(item);
      else {
        if (stat.size > 25 * 1024 * 1024) throw new Error(`Pages file exceeds 25 MiB: ${item}`);
        files++; bytes += stat.size;
      }
    }
  }
  inspect(directory);
  if (files > 20_000) throw new Error(`Pages Free file limit exceeded: ${files}`);
  return { directory, files, bytes };
}
