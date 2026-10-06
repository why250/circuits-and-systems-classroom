# 用自己的免费 Cloudflare Pages 发布

本项目已于 2026-10-05 发布为纯静态网站，项目名为 `why250-circuits-classroom`。

正式学习路线：<https://why250-circuits-classroom.pages.dev/learn/razavi/>。手机和电脑都可访问，本地电脑关机后仍可使用。首页、学习路线、研究笔记和互动实验已确认返回 HTTP 200。

学习路线现包含可点击的三分支路线图：共同基础 → ADC / PLL / 高速链路 → 系统补充与设计审查。节点显示按每周投入估算的周次和浏览器中的学习状态。手机展示所选方向的纵向路线，可在图内切换方向。图中箭头表示建议阅读顺序，具体先修以阶段详情为准。

路线图可导出 SVG 和 `.excalidraw` 文件。后者可用 Excalidraw 的“打开”功能导入编辑；导出包含全部方向与当时的完成记录，不包含个人学习笔记。导出图是独立快照，编辑不会回写网页。

## 首次连接

1. 在 <https://dash.cloudflare.com/sign-up> 注册账号并验证邮箱。无需添加域名或选择付费套餐。
2. 在仓库的 `web/` 目录运行下面的登录命令。
3. 按命令显示的设备授权地址与设备码，在浏览器完成登录和授权。密码和验证码只输入 Cloudflare 页面；设备码有有效期，过期后重新运行命令。

```powershell
node node_modules/wrangler/bin/wrangler.js login --device --browser=false --scopes account:read user:read pages:write
```

该连接申请读取账号与用户信息、管理 Pages 的权限。若有多个账号，设置所需的 `CLOUDFLARE_ACCOUNT_ID` 或按 CLI 提示选择目标账号。

## 自动构建并发布

```powershell
node scripts/deploy-pages.mjs
```

脚本使用已有依赖构建网页，将静态产物复制到 `.wrangler/standalone-pages-*`，检查免费版文件数量和单文件大小，附带 MIT 许可证，并在已登录账号内创建或复用 Pages 项目，然后发布生产版本。

新项目首次创建使用 `pages project create --force`，确保创建 Pages 项目并使用 `pages.dev` 地址。该参数仅用于首次创建；后续上传使用普通 `pages deploy`。

更新后重复运行同一命令即可。如果项目名不可用，指定新的名称：

```powershell
node scripts/deploy-pages.mjs --project your-unique-project-name
```

只构建并整理发布文件、不连接 Cloudflare：

```powershell
node scripts/deploy-pages.mjs --prepare-only
```

`SITE_URL` 根据所选项目设置，网站的 canonical 和 sitemap 使用自己的 `pages.dev` 地址。原项目的自定义域名绑定脚本不会运行。发布命令从隔离的静态目录执行，不上传原项目的 Pages Functions、Workers、账号凭据或本地学习笔记；浏览器中保存的个人进度和笔记仍留在相应设备。

## 不使用命令行：上传 ZIP

本次已准备 `reference/razavi-pages.zip`。注册后，在 Cloudflare 控制台进入 **Workers & Pages → 创建应用 → Pages → 上传静态资源**（界面文字可能不同），创建 `why250-circuits-classroom` 项目，上传 ZIP 并部署。

ZIP 顶层直接包含 `index.html`、`_astro/`、`learn/` 等文件；无需再次构建，也无需上传源码。项目名改变时，建议用 `--project` 参数重新构建，以更新 canonical 地址。

部署后首先检查首页、`/learn/razavi/`、研究笔记及互动实验。只有 Cloudflare 返回成功并验证网址可访问，才表示完成上线。

## 后续接入 GitHub 自动发布

目前先采用直接上传，避免在注册时额外配置 GitHub 授权及密钥。需要 GitHub 集成时，可新建 Git 集成的 Pages 项目：仓库根目录构建命令 `cd web && pnpm install --frozen-lockfile && pnpm build`，输出目录 `web/dist`，Node 24；设置 `SITE_URL` 为该项目正式网址。提交学习网页和所依赖的七份 Markdown 笔记。

保留上游版权与 MIT 许可。访客计数沿用原组件；未部署独立统计服务时显示占位符。免费静态托管不等于已配置账号系统或云端同步。
