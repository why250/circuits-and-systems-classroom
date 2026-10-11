# Publish with your own free Cloudflare Pages account

This project was published as a purely static website on 2026-10-05 under the project name `why250-circuits-classroom`.

Production website: <https://why250-circuits-classroom.pages.dev/>. Astro uses this address by default for canonical URLs, Open Graph, and the sitemap. Override it with `SITE_URL` or `CF_PAGES_URL`.

Production learning roadmap: <https://why250-circuits-classroom.pages.dev/learn/razavi/>. It works on phones and computers and remains available when the local computer is off. The homepage, roadmap, research notes, and interactive experiments were confirmed to return HTTP 200.

The roadmap includes three clickable branches: shared foundations → ADC / PLL / high-speed links → system topics and design review. Nodes show estimated weeks based on weekly study time and browser-local learning status. Phones display the selected track vertically, with track switching inside the graph. Arrows indicate recommended reading order; stage details define specific prerequisites.

Export the graph as SVG or `.excalidraw`. Import the latter using Excalidraw's Open command to edit it. Exports contain all tracks and completion records at export time, but no personal learning notes. The exported graph is an independent snapshot; editing it does not update the webpage.

## First connection

1. Register at <https://dash.cloudflare.com/sign-up> and verify your email. No domain or paid plan is required.
2. Run the following login command from the repository's `web/` directory.
3. Complete sign-in and authorization in the browser using the device authorization URL and code shown by the command. Enter passwords and verification codes only on Cloudflare pages. Device codes expire; rerun the command if needed.

```powershell
node node_modules/wrangler/bin/wrangler.js login --device --browser=false --scopes account:read user:read pages:write
```

This connection requests permission to read account/user information and manage Pages. If you have multiple accounts, set the intended `CLOUDFLARE_ACCOUNT_ID` or choose the target account when prompted by the CLI.

## Build and publish automatically

```powershell
node scripts/deploy-pages.mjs
```

The script builds with existing dependencies, copies static output to `.wrangler/standalone-pages-*`, checks free-plan file counts and per-file sizes, includes the MIT license, creates or reuses a Pages project in the signed-in account, and publishes a production deployment.

Initial project creation uses `pages project create --force` to create a Pages project with a `pages.dev` address. This flag is only for initial creation; subsequent uploads use ordinary `pages deploy`.

Run the same command again after updates. If the project name is unavailable, specify another name:

```powershell
node scripts/deploy-pages.mjs --project your-unique-project-name
```

To build and prepare deployment files without connecting to Cloudflare:

```powershell
node scripts/deploy-pages.mjs --prepare-only
```

The selected project determines `SITE_URL`; canonical URLs and the sitemap use your own `pages.dev` address. The original project's custom-domain binding script does not run. Deployment executes from an isolated static directory and does not upload the original project's Pages Functions, Workers, account credentials, or local learning notes. Browser-saved personal progress and notes remain on their respective devices.

## Upload a ZIP without the command line

A package was prepared at `reference/razavi-pages.zip`. After registering, open **Workers & Pages → Create application → Pages → Upload static assets** in the Cloudflare dashboard (labels may vary), create `why250-circuits-classroom`, upload the ZIP, and deploy.

The ZIP root directly contains `index.html`, `_astro/`, `learn/`, and other files. No rebuild or source upload is required. If the project name changes, rebuild with `--project` to update canonical URLs.

After deployment, check the homepage, `/learn/razavi/`, research notes, and interactive experiments. Publication is complete only when Cloudflare reports success and the URLs are verified accessible.

## Add GitHub automatic deployment later

Direct upload is currently used to avoid extra GitHub authorization and secret configuration during registration. If GitHub integration is needed, create a Git-integrated Pages project with repository-root build command `cd web && pnpm install --frozen-lockfile && pnpm build`, output directory `web/dist`, and Node 24. Set `SITE_URL` to that project's production URL. Commit the learning pages and the seven Markdown notes they depend on.

Preserve upstream copyright and the MIT license. Reuse the visitor-counter component; without an independent analytics service, it shows a placeholder. Free static hosting does not imply configured user accounts or cloud synchronization.